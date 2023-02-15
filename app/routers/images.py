from fastapi import APIRouter, Query
from typing import Union

from app.schemas import CommonOut, DetailCommonOut
from app.common import utils as cu

from app.constants import MOU_FILE_INDEX, TYPE_CODE_IMAGE, TYPE_CODE_DOCUMENT
from app.svc.es_svc import EsSvc as esSvc
from app.svc.ai_svc import AiSvc as aiSvc


router = APIRouter(
    prefix="/images",
    tags=["Search Images"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "/",
    summary="이미지 목록 조회",
    response_model=CommonOut,
    response_model_exclude_none=True,
)
async def read_images(
    keyword: Union[str, None] = Query(default="", description="검색어"),
    paging: Union[int, None] = Query(
        default=1, description="페이지, 다음 페이지 를 호출 하기 위한 키값. 첫 페이지 호출 시에는 넣지 않거나 1 입력"
    ),
    countPerPage: Union[int, None] = Query(default=10, description="페이지 당 건수", le=100),
    semantic: bool = Query(default=False, description="의미 기반 체크 여부"),
):

    start_index, end_index = cu.page_formula(paging, countPerPage)

    ##
    # 문서 목록 조회 (doc list)

    result = {
        "meta": {"code": "success", "message": "data", "count": 0},
        "data": [],
    }

    doc_result = {}

    # 검색어 있는지 확인
    if keyword:
        # 문서 목록 조회
        if semantic:
            vector_embedding = aiSvc.get_vector_embedding(keyword)

            # vector embedding 여부 체크
            if vector_embedding:
                body = esSvc.get_semantic_list_query(
                    start_index, end_index, TYPE_CODE_DOCUMENT, vector_embedding
                )
                doc_result = esSvc.get_item_es_list(MOU_FILE_INDEX, body, keyword)
            else:
                doc_result = {"meta": {"count": 0}, "data": []}

        else:

            body = esSvc.get_match_content_list_query(
                start_index, end_index, TYPE_CODE_DOCUMENT, keyword
            )

            doc_result = esSvc.get_item_es_list(MOU_FILE_INDEX, body, keyword)
    else:
        body = esSvc.get_search_by_date_in_desc_query(
            start_index, end_index, TYPE_CODE_DOCUMENT
        )

        doc_result = esSvc.get_item_es_list(MOU_FILE_INDEX, body, keyword)

    # 문서 id를 parent_id로 가지고 있는 이미지 목록 조회
    for data in doc_result.get("data"):

        parent_id_query = esSvc.get_parent_id_query(data.get("id"), TYPE_CODE_IMAGE)

        get_list_by_parent_id = esSvc.get_item_es_list(
            MOU_FILE_INDEX, parent_id_query, keyword
        )

        images = get_list_by_parent_id.get("data")

        for item in images:
            result["data"].append(item)

    result["meta"]["count"] = len(result["data"])

    return result


@router.get(
    "/{image_id}",
    summary="이미지 상세 조회",
    response_model=DetailCommonOut,
    response_model_exclude_none=True,
)
async def read_image(image_id: str = Query(description="이미지 id")):

    # 상세 조회 (id 검색 시)
    query = esSvc.get_match_id_detail_query(image_id)

    result = esSvc.get_item_es_data(MOU_FILE_INDEX, query)

    doc_query = esSvc.get_match_id_detail_query(result.get("data").get("parent_id"))

    doc_result = esSvc.get_item_es_data(MOU_FILE_INDEX, doc_query)

    result["data"]["title"] = doc_result.get("data").get("title")
    result["data"]["content"] = doc_result.get("data").get("contents")

    return result
