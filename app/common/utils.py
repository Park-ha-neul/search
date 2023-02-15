# <dictionary>d의 value 값이 None 인 경우 ""로 변경
def dict_convert_none_to_empty_str(d):
    if isinstance(d, dict):
        for k in d:
            if d[k] is None:
                d[k] = ""
            else:
                dict_convert_none_to_empty_str(d[k])
    elif isinstance(d, list):
        for v in d:
            dict_convert_none_to_empty_str(v)


# 페이지 계산식
def page_formula(paging, count_per_page):
    # rdbms (next_token) : end_index = (paging * count_per_page)
    # es (size):  end_index = count_per_page

    # es 조회 시 index 0부터 조회
    start_index = (paging - 1) * count_per_page
    end_index = count_per_page

    return start_index, end_index


# 음성 데이터 의 5분단위 동영상 파일 가져 오기
def get_video_origin_file_path(wav_file_path, data_type):
    """
    hdfs 의 음성 데이터(wav) 의 원본 (mp4) 파일 경로를 찾는다
    :param
      - wav_file_path: 음성 데이터
      - data_type: 실시간 영상 데이터 처리를 위한 유형 중분류(301 : 실시간, 303: 배치)
    :return: 5분 단위(mp4)
    """

    # 실시간 데이터 일 경우 wav 파일 경로의 상위 경로 폴더명.mp4, 배치 영상일 경우 wav 파일 확장자 를 mp4로 변경
    if data_type == "301":
        file_name = wav_file_path.split("/")[-1]
        return_path = wav_file_path.replace("/" + file_name, ".mp4")
    else:
        return_path = wav_file_path.replace(".wav", ".mp4")

    return return_path


# 썸네일 경로 변경
def change_path_to_thumbnail(file_path):

    return_path = file_path

    if file_path:

        sub_path = file_path.split("/")

        if sub_path:
            file_name = sub_path[-1]

            prefix = file_name.split(".")[0]

            change_path = f"{prefix}/thumbnail/{file_name}"

            sub_path[-1] = change_path

            return_path = "/".join(sub_path)

    return return_path


# 동영상 썸네일 가져오기
def video_path_to_thumbnail(file_path):
    """
    video 의 file_path 음성 데이터(wav) 의 썸네일(jpg) 파일 경로를 찾는다
    :param wav_file_path: 음성 데이터
    :return: 썸네일 이미지(jpg)
    """

    file_name = file_path.split("/")[-1]
    return_path = file_path.replace(
        file_name, "snapshot-300/thumbnail/snapshot-300.jpg"
    )

    return return_path
