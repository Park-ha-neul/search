from app.svc.ai_svc import AiSvc as aiSvc
from app.constants import MOU_FILE_INDEX, TYPE_CODE_DOCUMENT


def test_get_sentence_embedding_model_data():
    # input : keyword
    # output : embedding_data []

    keyword = "배구"
    vector_embedding = aiSvc.get_vector_embedding(keyword)
    if vector_embedding:
        print("success : ", vector_embedding)
    else:
        print(None)
