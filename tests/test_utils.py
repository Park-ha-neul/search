from app.common import utils as cu


def test_dict_convert_none_to_empty_str():
    test_dict = {
        "meta": {"message": None, "count": 0},
        "data": [
            {
                "title": None,
            }
        ],
    }

    cu.dict_convert_none_to_empty_str(test_dict)

    assert test_dict == {
        "meta": {"message": "", "count": 0},
        "data": [
            {
                "title": "",
            }
        ],
    }


def test_page_formula():
    # rdbms : end_index = (paging * count_per_page)
    # es :  end_index = count_per_page

    paging = 2
    count_per_page = 10

    start_index, end_index = cu.page_formula(paging, count_per_page)

    assert start_index == 10 and end_index == 10


def test_get_audio_origin_file_path():
    # 음성(웝본 file_path 구하는 방법) : 기존 file_path 끝에서 2번째에 해당 하는 문자열 + mp3
    # 기존 file_path = /fpms/C001/204/2499/mp3/2022/05/09/2022062800010001/2022062800010001_sub_0.wav
    # mp3 file_path = /fpms/C001/204/2499/mp3/2022/05/09/2022062800010001.mp3

    input_wav = (
        "/fpms/C001/204/2499/mp3/2022/05/09/2022062800010001/2022062800010001_sub_0.wav"
    )
    output_mp3 = cu.get_audio_origin_file_path(input_wav)

    assert output_mp3 == "/fpms/C001/204/2499/mp3/2022/05/09/2022062800010001.mp3"


def test_change_path_to_thumbnail():
    # 음성(웝본 file_path 구하는 방법) : 기존 file_path 끝에서 2번째에 해당 하는 문자열 + mp3
    # 기존 file_path = /fpms/C001/204/2499/mp3/2022/05/09/2022062800010001/2022062800010001_sub_0.wav
    # mp3 file_path = /fpms/C001/204/2499/mp3/2022/05/09/2022062800010001.mp3

    input_path = "/file/fcms/C003/304/3401/post/2022/01/13/reassessing-the-role-of-the-el/img/reassessing-the-role-of-the-el_1.jpg"
    output_path = cu.change_path_to_thumbnail(input_path)

    assert (
        output_path
        == "/file/fcms/C003/304/3401/post/2022/01/13/reassessing-the-role-of-the-el/img/reassessing-the-role-of-the-el_1/thumbnail/reassessing-the-role-of-the-el_1.jpg"
    )
