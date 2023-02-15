from typing import Union
from fastapi import APIRouter, Query

from app.schemas import CommonOut, DetailCommonOut
from app.common import utils as cu

from app.svc.es_svc import EsSvc as esSvc
from app.svc.ai_svc import AiSvc as aiSvc

from app.constants import TYPE_CODE_AUDIO
from app.constants import MOU_FILE_INDEX


router = APIRouter(
    prefix="/audios",
    tags=["Search Audios"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "/", summary="음성 목록 조회", response_model=CommonOut, response_model_exclude_none=True
)
async def read_documents(
    keyword: Union[str, None] = Query(default="", description="검색어"),
    paging: Union[int, None] = Query(
        default=1, description="페이지, 다음 페이지를 호출하기 위한 키값. 첫 페이지 호출시에는 넣지 않거나 1 입력"
    ),
    count_per_page: Union[int, None] = Query(default=10, description="페이지당건수", le=100),
    semantic: bool = Query(default=False, description="의미 기반 체크 여부"),
):
    start_index, end_index = cu.page_formula(paging, count_per_page)

    # 검색어 있는지 확인
    if keyword:

        # 의미 기반 검색
        if semantic:
            vector_embedding = aiSvc.get_vector_embedding(keyword)

            # vector embedding 여부 체크
            if vector_embedding:
                body = esSvc.get_semantic_list_query(
                    start_index, end_index, TYPE_CODE_AUDIO, vector_embedding
                )
                result = esSvc.get_item_es_list(MOU_FILE_INDEX, body, keyword)
            else:
                result = {
                    "meta": {"count": 0},
                }

        else:

            body = esSvc.get_match_content_list_query(
                start_index, end_index, TYPE_CODE_AUDIO, keyword
            )

            result = esSvc.get_item_es_list(MOU_FILE_INDEX, body, keyword)
    else:
        body = esSvc.get_search_by_date_in_desc_query(
            start_index, end_index, TYPE_CODE_AUDIO
        )

        result = esSvc.get_item_es_list(MOU_FILE_INDEX, body, keyword)

    return result


@router.get(
    "/{audio_id}",
    summary="음성 상세 조회",
    response_model=DetailCommonOut,
    response_model_exclude_none=True,
)
async def read_document(audio_id: str = Query(description="음성 id")):

    # 상세 조회 (id 검색 시)
    query = esSvc.get_match_id_detail_query(audio_id)

    result = esSvc.get_item_es_data(MOU_FILE_INDEX, query)

    return result
