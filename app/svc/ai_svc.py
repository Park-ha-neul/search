import requests
import json
import sys
import os
import logging


VECTOR_EMBEDDING_URL = os.getenv("VECTOR_EMBEDDING_URL")
VECTOR_EMBEDDING_DOCUMENT_URL = os.getenv("VECTOR_EMBEDDING_DOCUMENT_URL")
RELATED_WORD_URL = os.getenv("RELATED_WORD_URL")


class AiSvc:
    @classmethod
    def get_vector_embedding(cls, keyword):
        print("called Ai get_vector_embedding")

        data = {"data": f"[['{keyword}']]"}

        headers = {"Content-type": "application/json;charset=UTF-8"}

        embedding_data = None
        try:
            response = requests.post(
                url=VECTOR_EMBEDDING_URL,
                json=data,
                headers=headers,
            )

            res = response.json()
            embedding_data = res[0][0]["value"]["embedding"]
            embedding_data = json.loads(embedding_data)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.info(exc_type, file_name, exc_tb.tb_lineno)

            embedding_data = None
        return embedding_data

    @classmethod
    def get_vector_embedding_document(cls, contents):
        print("called Ai get_vector_embedding_document")

        data = {"data": f"[['{contents}']]"}

        headers = {"Content-type": "application/json;charset=UTF-8"}

        embedding_data = None
        try:
            response = requests.post(
                url=VECTOR_EMBEDDING_DOCUMENT_URL,
                json=data,
                headers=headers,
            )

            res = response.json()
            embedding_data = res[0][0]["value"]["embedding"]
            embedding_data = json.loads(embedding_data)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.info(exc_type, file_name, exc_tb.tb_lineno)

            embedding_data = None
        return embedding_data

    @classmethod
    def get_related_word_list(cls, keyword):
        print("called Ai get_related_word_list")

        data = {"data": f"[['{keyword}']]"}

        headers = {"Content-type": "application/json;charset=UTF-8"}
        related_data = []
        try:
            response = requests.post(
                url=RELATED_WORD_URL,
                json=data,
                headers=headers,
            )

            res = response.json()
            related_data = res["related_word"]

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.info(exc_type, file_name, exc_tb.tb_lineno)

            related_data = []
        return related_data
