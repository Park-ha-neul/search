import os

from datetime import datetime, timedelta

from typing import Union
from fastapi import APIRouter, Query
from elasticsearch import Elasticsearch

from app.schemas import CommonOut, DetailCommonOut
from app.common import utils as cu

from app.svc.ai_svc import AiSvc as aiSvc
from app.svc.es_svc import EsSvc as esSvc

from app.constants import MOU_FILE_INDEX, TYPE_CODE_IMAGE, T3Q_SEARCH_WORD_INDEX


router = APIRouter(
    prefix="/search",
    tags=["검색"],
    responses={404: {"description": "Not found"}},
)

ES_URL = os.getenv("ES_URL")
es = Elasticsearch(ES_URL)


# 통합 검색 API
@router.get(
    "/",
    summary="통합 검색",
    response_model=DetailCommonOut,
    response_model_exclude_none=True,
)
async def get_integrated(
    keyword: Union[str, None] = Query(default="", description="검색어"),
    paging: Union[int, None] = Query(
        default=1, description="페이지, 다음 페이지를 호출 하기 위한 키값. 첫 페이지 호출 시에는 넣지 않거나 1 입력"
    ),
    count_per_page: Union[int, None] = Query(
        default=10, description="페이지 당 건 수", le=100
    ),
    semantic: bool = Query(default=False, description="의미 기반 체크 여부"),
):

    vector_embedding = []
    count = 0
    documents = {}
    videos = {}
    images = {}
    audios = {}

    # 페이징 처리
    start_index, end_index = cu.page_formula(paging, count_per_page)

    # index: 테이블 명
    index = "mou_file_index_basic"

    ##
    # 데이터 타입 임시 분류
    # B001: 문서, B003: 영상, B004: 이미지, B006: 음성
    data_type_l_cd = ["B001", "B003", "B004", "B006"]

    # 지능형 검색 모델 API: input - {keyword}, output - 벡터 추출 [-0.5066, 0.3507, ... ]
    # 의미 기반 검색
    if semantic:
        vector_embedding = aiSvc.get_vector_embedding(keyword)

    for data_type in data_type_l_cd:

        # 검색어 있는지 확인
        if keyword:

            # 의미 기반 검색
            if semantic:

                # vector embedding 여부 체크
                if vector_embedding:
                    query = esSvc.get_semantic_list_query(
                        start_index, end_index, data_type, vector_embedding
                    )
                    result = esSvc.get_item_es_list(index, query, keyword)
                else:
                    result = {
                        "meta": {"count": 0},
                    }

            else:

                query = esSvc.get_match_content_list_query(
                    start_index, end_index, data_type, keyword
                )

                result = esSvc.get_item_es_list(index, query, keyword)
        else:
            body = esSvc.get_search_by_date_in_desc_query(
                start_index, end_index, data_type
            )

            result = esSvc.get_item_es_list(MOU_FILE_INDEX, body, keyword)

        count += result.get("meta").get("count")

        # 문서 및 이미지 처리
        if data_type == "B001":

            # 문서
            documents = result

            # 이미지
            image_result = {
                "meta": {"code": "success", "message": "data", "count": count},
                "data": [],
            }

            # 문서 id를 parent_id로 가지고 있는 이미지 목록 조회
            for data in result.get("data"):
                parent_id_query = {
                    "query": {
                        "bool": {
                            "filter": [
                                {"match": {"data_type_l_cd": TYPE_CODE_IMAGE}},
                                {"match": {"parent_id": data.get("id")}},
                            ]
                        }
                    },
                    "docvalue_fields": [
                        {"field": "event_date", "format": "yyyy-MM-dd HH:mm:ss"}
                    ],
                }

                get_list_by_parent_id = esSvc.get_item_es_list(
                    MOU_FILE_INDEX, parent_id_query, keyword
                )

                images = get_list_by_parent_id.get("data")

                for item in images:
                    image_result["data"].append(item)

            image_result["meta"]["count"] = len(image_result["data"])
            images = image_result

            count += len(image_result["data"])

        # 영상 처리
        elif data_type == "B003":
            videos = result
        # 음성 처리
        elif data_type == "B006":
            audios = result

    return {
        "meta": {"code": "success", "message": "data", "count": count},
        "data": {
            "documents": documents,
            "images": images,
            "videos": videos,
            "audios": audios,
        },
    }


# 자동 완성 API
@router.get(
    "/ac",
    summary="자동 완성",
    response_model=CommonOut,
    response_model_exclude_none=True,
)
async def get_auto_complete(
    keyword: str = Query(description="자동 완성을 원하는 검색어"),
    count_per_page: Union[int, None] = Query(
        default=10, description="페이지 당 건수", le=100
    ),
):
    # 입력한 keyword 값으로 연관 검색어 조회
    body = {
        "suggest": {
            "s1": {
                "prefix": keyword,
                "completion": {
                    "field": "title_completion",
                    "size": count_per_page,
                },  # 5개로 제한
            }
        }
    }

    res = es.search(index=MOU_FILE_INDEX, body=body)
    options = res.__getitem__("suggest").get("s1")[0].get("options")
    item_completion = []
    for item in options:
        item_completion.append(item.get("_source").get("title_completion"))

    return {"meta": {"code": "success", "message": "data"}, "data": item_completion}


# 연관어 API
@router.get(
    "/related_word",
    summary="연관 검색어",
    response_model=CommonOut,
    response_model_exclude_none=True,
)
async def related_word(
    keyword: str = Query(description="연관 검색어"),
):
    # 입력한 keyword 값으로 연관 검색어 조회
    related_words = aiSvc.get_related_word_list(keyword)

    return {"meta": {"code": "success", "message": "data"}, "data": related_words}


# 인기 검색어 API
@router.get(
    "/popular",
    summary="인기 검색어",
    response_model=CommonOut,
    response_model_exclude_none=True,
)
async def related_word(
    start_date: Union[str, None] = Query(default=None, description="시작 일자"),
    end_date: Union[str, None] = Query(default=None, description="종료 일자"),
):
    """
    최신 일자순 조회 Top 5 \n
    날짜 형식:  yyyy-MM-dd
    """

    data = []
    fmt = "%Y-%m-%d"
    size = 5

    today = datetime.now().strftime(fmt)

    # 매개 변수 날짜 포맷 체크
    try:
        start_date = datetime.strptime(start_date, fmt)
        start_date = start_date.strftime(fmt)
    except TypeError:
        start_date = None
    except ValueError:
        start_date = None

    try:
        end_date = datetime.strptime(end_date, fmt)
        end_date = end_date.strftime(fmt)
    except TypeError:
        end_date = today
    except ValueError:
        end_date = today

    # 입력값 없을 경우: 최근 ~ 1주일
    if start_date is None and end_date is today:
        start_date = (datetime.now() - timedelta(days=7)).strftime(fmt)

    query = esSvc.get_popular_query(start_date, end_date, size)

    res = es.search(index=T3Q_SEARCH_WORD_INDEX, body=query)
    options = res.__getitem__("aggregations").get("order_by_title").get("buckets")

    if options:
        for row in options:
            data.append(row.get("key"))

    return {"meta": {"code": "success", "message": "popular search data"}, "data": data}
