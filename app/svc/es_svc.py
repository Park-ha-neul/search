import logging
import os
import sys

from elasticsearch import Elasticsearch
from app.common import utils as cu

from app.constants import (
    META_CODE_SUCCESS,
    META_CODE_FAIL,
    DATA_SRC_CODE,
    TYPE_CODE_DOCUMENT,
    TYPE_CODE_IMAGE,
    TYPE_CODE_VIDEO,
    TYPE_CODE_AUDIO,
    MOU_FILE_INDEX,
)

ES_URL = os.getenv("ES_URL")
es = Elasticsearch(ES_URL)


class EsSvc:
    @classmethod
    def get_item_es_data(cls, index, query):
        """
        ID 로 상세 데이터 조회
        :param index: es index
        :param query: es body
        :return: result
        """

        code = ""
        message = ""
        data = {}

        result = {
            "meta": {"code": code, "message": message},
            "data": data,
        }

        try:
            res = es.search(index=index, body=query)
            options = res.__getitem__("hits").get("hits")

            field_data = {}

            # 데이터 가 없는 경우 예외 처리
            if len(options) == 0:

                result["meta"]["code"] = "fail"
                result["meta"]["message"] = "data is not find"
                result["data"] = options

            else:
                options = res.__getitem__("hits").get("hits")[0]

                _source = options.get("_source")

                field_data["id"] = _source.get("id")

                # 원본 파일 경로 (동영상 일 경우 mp4 파일로 변환해서 전달 필요)
                file_path = _source.get("file_path")
                if file_path:
                    if _source.get("data_type_l_cd") == TYPE_CODE_VIDEO:
                        # 영상 실시간 데이터 처리를 위한 유형중분류 전달 필요
                        data_type = _source.get("data_type_m_cd")
                        field_data["file"] = "/stream{}".format(
                            cu.get_video_origin_file_path(file_path, data_type)
                        )
                    elif _source.get("data_type_l_cd") == TYPE_CODE_AUDIO:
                        field_data["file"] = "/stream{}".format(file_path)
                    else:
                        field_data["file"] = "/file{}".format(file_path)

                title = _source.get("title")  # 제목
                if title:
                    field_data["title"] = title

                contents = _source.get("content")  # 텍스트 원문
                if contents:
                    field_data["contents"] = contents

                # 출처 대분류
                field_data["data_src_l_cd"] = DATA_SRC_CODE.get("data_src_l_cd").get(
                    _source.get("data_src_l_cd")
                )

                # 출처 중분류
                field_data["data_src_m_cd"] = DATA_SRC_CODE.get("data_src_m_cd").get(
                    _source.get("data_src_m_cd")
                )

                # 출처 소분류
                field_data["data_src_s_cd"] = DATA_SRC_CODE.get("data_src_s_cd").get(
                    _source.get("data_src_s_cd")
                )

                # 출처 url
                field_data["source_url"] = _source.get("url")

                # date 포맷 변경이 안되는 경우 예외 처리
                if options.get("fields") is None:
                    field_data["date"] = _source.get("event_date")
                else:
                    field_data["date"] = options.get("fields").get("event_date")[
                        0
                    ]  # 날짜

                # parent_id
                field_data["parent_id"] = _source.get("parent_id")

                # file_data 의 value 값이 None 일 경우 "" 로 변경
                cu.dict_convert_none_to_empty_str(field_data)

            result["meta"]["code"] = META_CODE_SUCCESS
            result["meta"]["message"] = "data"
            result["data"] = field_data

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.info(exc_type, file_name, exc_tb.tb_lineno)

            result["meta"]["code"] = META_CODE_FAIL
            #        result["meta"]["message"] = "data is not find"
            result["meta"]["message"] = str(e)

        return result

    @classmethod
    def get_keyword_data(cls, contents, keyword):

        _start = 0
        _end = 0

        _start = contents.find(keyword) - 90
        if _start < 0:
            _end = 0 - _start
            _start = 0

        _end = _end + contents.find(keyword) + 30
        if _end > len(contents):
            _end = len(contents)

        return contents[_start:_end]

    @classmethod
    def get_item_es_list(cls, index, query, keyword):
        code = ""
        count = 0
        data = []

        result = {
            "meta": {"code": code, "message": "data", "count": count},
            "data": data,
        }

        try:

            res = es.search(index=index, body=query)
            options = res.__getitem__("hits").get("hits")
            count = res.__getitem__("hits").get("total").get("value")

            for idx, item in enumerate(options):
                field_data = {}

                _source = item.get("_source")
                _fields = item.get("fields")

                # 파일 ID
                field_data["id"] = _source.get("id")

                # 제목
                title = _source.get("title")
                if title:
                    field_data["title"] = _source.get("title")

                # 텍스트 원문 (keyword 포함 기준 으로 앞 뒤 120자 뽑기)
                contents = _source.get("content")
                if contents:
                    if len(contents) > 120:
                        contents = "{} ...".format(
                            cls.get_keyword_data(contents, keyword)
                        )

                    field_data["contents"] = contents

                # 수집 일시
                if item.get("fields") is not None:
                    field_data["date"] = _fields.get("event_date")[0]
                else:
                    field_data["date"] = _source.get("event_date")

                # 원본 파일 경로 (동영상 일 경우 mp4 파일로 변환해서 전달 필요)
                file_path = _source.get("file_path")
                if file_path:
                    # 추후 음성인 경우 에도 목록 조회 시 원본 파일 경로 안 보이게 수정 필요
                    if _source.get("data_type_l_cd") in {
                        TYPE_CODE_DOCUMENT,
                        TYPE_CODE_IMAGE,
                        TYPE_CODE_AUDIO,
                    }:
                        field_data["file"] = "/file{}".format(file_path)

                # 파일 영상 길이
                file_play_time = _source.get("file_play_time")
                if file_play_time:
                    field_data["file_play_time"] = file_play_time

                # 문서(B001) 목록에 thumbnail 경로 추가
                if _source.get("data_type_l_cd") == TYPE_CODE_DOCUMENT:
                    parent_id_query = cls.get_parent_id_query(
                        _source.get("id"), TYPE_CODE_IMAGE, 1
                    )

                    result = cls.get_item_es_data(MOU_FILE_INDEX, parent_id_query)

                    if result.get("data").get("file"):
                        _file_path = result.get("data").get("file")
                        field_data["thumbnail"] = cu.change_path_to_thumbnail(
                            _file_path
                        )

                # 이미지(B004) 목록에 thumbnail 경로 추가
                if _source.get("data_type_l_cd") == TYPE_CODE_IMAGE:
                    if _source.get("file_path"):
                        _file_path = "/file{}".format(_source.get("file_path"))
                        field_data["thumbnail"] = cu.change_path_to_thumbnail(
                            _file_path
                        )
                # 동영상(B003) 목록에 thumbnail 경로 추가
                elif _source.get("data_type_l_cd") == TYPE_CODE_VIDEO:
                    file_path = _source.get("file_path")
                    if file_path:
                        _file_path = "/file{}".format(_source.get("file_path"))
                        field_data["thumbnail"] = cu.video_path_to_thumbnail(_file_path)

                # field_data 의 value 값이 None 일 경우 "" 로 변경
                cu.dict_convert_none_to_empty_str(field_data)

                data.append(field_data)

            result["meta"]["code"] = META_CODE_SUCCESS
            result["meta"]["count"] = count
            result["data"] = data

        except Exception as e:
            result["meta"]["code"] = META_CODE_FAIL
            result["meta"]["message"] = str(e)

        return result

    @classmethod
    def get_match_content_list_query(cls, start_index, end_index, data_type, keyword):

        query = {
            "from": start_index,
            "size": end_index,
            "track_total_hits": "true",
            "query": {
                "bool": {
                    "filter": [{"term": {"data_type_l_cd": data_type}}],
                    "should": [
                        {"match": {"title": {"query": keyword}}},
                        {"match_phrase": {"title": {"query": keyword}}},
                        {"match": {"content": {"query": keyword}}},
                        {"match_phrase": {"content": {"query": keyword}}},
                    ],
                    "minimum_should_match": 1,
                }
            },
            "docvalue_fields": [
                {"field": "event_date", "format": "yyyy-MM-dd HH:mm:ss"}
            ],
        }

        return query

    @classmethod
    def get_semantic_list_query(
        cls, start_index, end_index, data_type, embedding_data, document_id=None
    ):

        query = {
            "from": start_index,
            "size": end_index,
            "query": {
                "script_score": {
                    "query": {
                        "bool": {
                            "filter": [
                                {"exists": {"field": "ai_embedding_vector_avg"}},
                                {"term": {"data_type_l_cd": data_type}},
                            ]
                        }
                    },
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'ai_embedding_vector_avg') + 1.0",
                        "params": {"query_vector": embedding_data},
                    },
                }
            },
            "docvalue_fields": [
                {"field": "event_date", "format": "yyyy-MM-dd HH:mm:ss"}
            ],
        }

        if document_id:
            query["query"]["script_score"]["query"]["bool"]["must_not"] = [
                {"term": {"_id": {"value": document_id}}}
            ]

        return query

    @classmethod
    def get_match_id_detail_query(cls, id):

        query = {
            "query": {"term": {"_id": id}},
            "docvalue_fields": [
                {"field": "event_date", "format": "yyyy-MM-dd HH:mm:ss"}
            ],
        }

        return query

    @classmethod
    def get_parent_id_query(cls, id, data_type, size=None):

        query = {
            "query": {
                "bool": {
                    "filter": [
                        {"match": {"data_type_l_cd": data_type}},
                        {"match": {"parent_id": id}},
                    ]
                }
            },
            "docvalue_fields": [
                {"field": "event_date", "format": "yyyy-MM-dd HH:mm:ss"}
            ],
        }

        if size:
            query["size"] = size

        return query

    @classmethod
    def get_search_by_date_in_desc_query(cls, start_index, end_index, data_type):

        query = {
            "from": start_index,
            "size": end_index,
            "sort": [{"event_date": {"order": "desc"}}],
            "query": {"bool": {"filter": [{"match": {"data_type_l_cd": data_type}}]}},
            "docvalue_fields": [
                {"field": "event_date", "format": "yyyy-MM-dd HH:mm:ss"}
            ],
        }

        return query

    # 인기 검색어 쿼리
    @classmethod
    def get_popular_query(cls, start_date, end_date, size):

        query = {
            "size": 0,
            "query": {
                "bool": {
                    "must": [],
                    "filter": [{"range": {"col_dt": {"lte": end_date}}}],
                }
            },
            "aggs": {
                "order_by_title": {
                    "terms": {
                        "size": size,
                        "field": "search_word",
                        "order": {"_count": "desc"},
                    }
                }
            },
        }

        if start_date:
            query["query"]["bool"]["filter"][0]["range"]["col_dt"]["gte"] = start_date

        return query
