import os

from typing import Union
from fastapi import APIRouter, Query
from elasticsearch import Elasticsearch

from app.schemas import CommonOut, DetailCommonOut
from app.common import utils as cu
from app.svc.es_svc import EsSvc as esSvc

from app.svc.ai_svc import AiSvc as aiSvc

from app.constants import TYPE_CODE_DOCUMENT, TYPE_CODE_IMAGE
from app.constants import MOU_FILE_INDEX, MOU_BIZ_INDEX, DATA_SRC_CODE


router = APIRouter(
    prefix="/documents",
    tags=["Search Documents"],
    responses={404: {"description": "Not found"}},
)

ES_URL = os.getenv("ES_URL")

es = Elasticsearch(ES_URL)


@router.get(
    "/", summary="문서 목록 조회", response_model=CommonOut, response_model_exclude_none=True
)
async def read_documents(
    keyword: Union[str, None] = Query(default="", description="검색어"),
    paging: Union[int, None] = Query(
        default=1, description="페이지, 다음 페이지 를 호출 하기 위한 키값. 첫 페이지 호출 시에는 넣지 않거나 1 입력"
    ),
    count_per_page: Union[int, None] = Query(
        default=10, description="페이지 당 건수", le=100
    ),
    semantic: bool = Query(default=False, description="의미 기반 체크 여부"),
):
    start_index, end_index = cu.page_formula(paging, count_per_page)

    # 검색어 있을 경우
    if keyword:

        # 의미 기반 검색
        if semantic:
            vector_embedding = aiSvc.get_vector_embedding(keyword)

            # vector embedding 여부 체크
            if vector_embedding:
                body = esSvc.get_semantic_list_query(
                    start_index, end_index, TYPE_CODE_DOCUMENT, vector_embedding
                )
                result = esSvc.get_item_es_list(MOU_FILE_INDEX, body, keyword)
            else:
                result = {
                    "meta": {"count": 0},
                }

        else:

            body = esSvc.get_match_content_list_query(
                start_index, end_index, TYPE_CODE_DOCUMENT, keyword
            )

            result = esSvc.get_item_es_list(MOU_FILE_INDEX, body, keyword)

    # 검색어 없는 경우
    else:
        body = esSvc.get_search_by_date_in_desc_query(
            start_index, end_index, TYPE_CODE_DOCUMENT
        )

        result = esSvc.get_item_es_list(MOU_FILE_INDEX, body, keyword)

    return result


@router.get(
    "/{document_id}",
    summary="문서 상세 조회",
    response_model=DetailCommonOut,
    response_model_exclude_none=True,
)
async def read_document(document_id: str = Query(description="문서 id")):
    # 상세 조회 (id 검색 시)
    body = {
        "query": {"term": {"_id": document_id}},
        "docvalue_fields": [{"field": "event_date", "format": "yyyy-MM-dd HH:mm:ss"}],
    }

    # 출처 조회 쿼리
    source_query = {
        "query": {
            "bool": {
                "must": [
                    {"match": {"data_type_l_cd": TYPE_CODE_DOCUMENT}},
                    {"term": {"_id": document_id}},
                ]
            }
        }
    }

    # 유사 문서 index, default=5
    start_index = 0
    end_index = 5

    # 문서 상세 정보 조회
    return_data = esSvc.get_item_es_data(MOU_FILE_INDEX, body)
    keyword = return_data.get("data").get("title")

    # 데이터 출처 처리
    return_biz_data = esSvc.get_item_es_data(MOU_BIZ_INDEX, source_query)

    source = return_biz_data["data"].get("source_url")
    if source:
        return_data["data"]["source_url"] = source

    # 연관 이미지 목록 조회, default=10
    query = associative_image_list_query(document_id)
    associative_images = esSvc.get_item_es_list(MOU_FILE_INDEX, query, keyword)
    return_data["data"]["associative_images"] = associative_images

    # 유사 문서 목록 조회
    contents = return_data.get("data").get("contents")
    vector_embedding = aiSvc.get_vector_embedding_document(contents)

    # vector embedding 여부 체크
    if vector_embedding:
        body = esSvc.get_semantic_list_query(
            start_index, end_index, TYPE_CODE_DOCUMENT, vector_embedding, document_id
        )
        similar_documents = esSvc.get_item_es_list(MOU_FILE_INDEX, body, keyword)
    else:
        similar_documents = {
            "meta": {"count": 0},
        }

    return_data["data"]["similar_documents"] = similar_documents

    return return_data


def associative_image_list_query(document_id):

    query = {
        "from": 0,
        "size": 10,
        "query": {
            "bool": {
                "filter": [
                    {"match": {"data_type_l_cd": TYPE_CODE_IMAGE}},
                    {"match": {"parent_id": document_id}},
                ]
            }
        },
        "docvalue_fields": [{"field": "event_date", "format": "yyyy-MM-dd HH:mm:ss"}],
    }

    return query
