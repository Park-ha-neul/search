from app.svc.es_svc import EsSvc as esSvc
from app.constants import MOU_FILE_INDEX, TYPE_CODE_DOCUMENT


def test_get_document_data():
    document_id = "nams_2402_sports_F22PEK6IXBGFRA5GBWVG6VUSR4"
    body = {
        "query": {"term": {"_id": document_id}},
        "docvalue_fields": [{"field": "event_date", "format": "yyyy-MM-dd HH:mm:ss"}],
    }

    res = esSvc.get_item_es_data(MOU_FILE_INDEX, body)


def test_get_document_list():
    keyword = "코로나"
    start_index = 0
    end_index = 10

    query = {
        "from": start_index,
        "size": end_index,
        "query": {
            "bool": {
                "filter": [
                    {"match": {"data_type_l_cd": TYPE_CODE_DOCUMENT}},
                    {"match": {"content": keyword}},
                ]
            }
        },
        "docvalue_fields": [{"field": "event_date", "format": "yyyy-MM-dd HH:mm:ss"}],
    }

    res = esSvc.get_item_es_list(MOU_FILE_INDEX, query)

    print(res)
