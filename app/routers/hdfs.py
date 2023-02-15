import os
import requests
import tempfile

from typing import BinaryIO, Tuple
from starlette.background import BackgroundTasks

from fastapi.responses import StreamingResponse, FileResponse
from fastapi import Query, APIRouter, Request, HTTPException, status


router = APIRouter(
    prefix="",
    tags=["Search Hdfs"],
    responses={404: {"description": "Not found"}},
)

web_hdfs_url = os.getenv("HDFS_URL")


def remove_file(path: str) -> None:
    os.unlink(path)


@router.get(
    "/file/{file_path:path}",
    description="원본 파일 경로 입력 시 파일 preview",
    include_in_schema=False,
)
async def get_Origin_File(
    background_tasks: BackgroundTasks,
    file_path: str = Query(description="다운로드 할 원본 파일 경로"),
):
    # HDFS URL
    req_url = web_hdfs_url + file_path + "?op=OPEN"
    res = requests.get(req_url)

    # 임시 파일 생성 후 리소스를 저장
    tmp = tempfile.NamedTemporaryFile(mode="wb", delete=False)
    tmp.write(res.content)

    # 임시 파일을 요청 이후에 삭제 하기 위한 Task 등록
    background_tasks.add_task(remove_file, tmp.name)

    file_name = file_path.split("/")[-1]

    # 임시 파일을 리턴
    res = FileResponse(tmp.name, filename=file_name)
    # res = FileResponse(tmp.name)

    return res


def send_bytes_range_requests(
    file_obj: BinaryIO,
    start: int,
    end: int,
    chunk_size: int = 10_000,
):
    """
    Send a file in chunks using Range Requests specification RFC7233

    `start` and `end` parameters are inclusive due to specification
    """
    with file_obj as f:
        f.seek(start)
        # 현재 커서 위치 - f.tell()
        while f.tell() <= end:
            read_size = min(chunk_size, end + 1 - f.tell())
            yield f.read(read_size)


def _get_range_header(range_header: str, file_size: int) -> Tuple[int, int]:
    def _invalid_range():
        return HTTPException(
            status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
            detail=f"Invalid request range (Range:{range_header!r})",
        )

    try:
        h = range_header.replace("bytes=", "").split("-")
        start = int(h[0]) if h[0] != "" else 0
        end = int(h[1]) if h[1] != "" else int(file_size) - 1
    except ValueError:
        raise _invalid_range()

    if start > end or start < 0 or end > int(file_size) - 1:
        raise _invalid_range()
    return start, end


def range_requests_response(
    request: Request,
    file_path: str,
    content_type: str,
):
    """Returns StreamingResponse using Range Requests of a given file"""

    # 파일 경로
    tmp_name = tempfile.gettempdir() + f"/stream/{file_path}"
    # C:\Users\T3Q-DU~1\AppData\Local\Temp/stream/fpms/C001/204/2499/mp4/2022/06/27/2022062800110001/2022062800110001_sub_900.mp4

    # 파일 체크
    if not os.path.isfile(tmp_name):
        # HDFS URL
        req_url = web_hdfs_url + file_path + "?op=OPEN"
        res = requests.get(req_url)

        # 경로 체크 or 생성
        _path = tmp_name.split("/")
        _path = "/".join(_path[:-1])
        if not os.path.isdir(_path):
            os.makedirs(_path)

        # todo: 생성된 임시 파일에 대한 일괄 삭제 필요
        with open(tmp_name, "w+b") as f:
            f.write(res.content)

    # 전체 길이
    file_size = os.stat(tmp_name).st_size

    # e.g.) bytes=31981568-
    range_header = request.headers.get("range")

    headers = {
        "content-type": content_type,
        "accept-ranges": "bytes",
        "content-encoding": "identity",
        "content-length": str(file_size),
        "access-control-expose-headers": (
            "content-type, accept-ranges, content-length, "
            "content-range, content-encoding"
        ),
    }
    start = 0
    end = file_size - 1
    status_code = status.HTTP_200_OK

    if range_header is not None:
        start, end = _get_range_header(range_header, file_size)
        size = end - start + 1
        headers["content-length"] = str(size)
        headers["content-range"] = f"bytes {start}-{end}/{file_size}"
        status_code = status.HTTP_206_PARTIAL_CONTENT

    return StreamingResponse(
        send_bytes_range_requests(open(tmp_name, mode="rb"), start, end),
        headers=headers,
        status_code=status_code,
    )


@router.get(
    "/stream/{file_path:path}",
    description="영상 streaming 처리를 위한 api",
    include_in_schema=False,
)
async def stream_media(
    request: Request,
    file_path: str = Query(description="파일 경로"),
):

    # content_type check
    media_type = file_path.split(".")[-1]

    content_type = "video/mp4" if media_type == "mp4" else "audio/wav"

    return range_requests_response(
        request,
        file_path=file_path,
        content_type=content_type,
    )
