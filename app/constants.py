# app/constants.py

TYPE_CODE_DOCUMENT = "B001"
TYPE_CODE_IMAGE = "B004"
TYPE_CODE_VIDEO = "B003"
TYPE_CODE_AUDIO = "B006"

# 수집 데이터 분류 체계 정리_V.0.2.4
DATA_SRC_CODE = {
    "data_src_l_cd": {"C001": "국내", "C003": "해외", "C004": "수집 클라이언트", "C999": "기타"},
    "data_src_m_cd": {
        "202": "정부/공공기관",
        "203": "연구기관",
        "204": "언론사",
        "205": "SNS",
        "206": "RDBMS 시스템",
        "207": "SFTP 시스템",
        "208": "RSS",
        "301": "해외 정부기관",
        "302": "국제기구",
        "303": "언론사",
        "304": "연구기관",
        "401": "윈도우시스템",
        "999": "기타",
    },
    "data_src_s_cd": {
        "2201": "문화체육관광부",
        "2202": "기상청",
        "2301": "대외경제정책연구원(KIEP)",
        "2302": "한국문화관광연구원",
        "2401": "한겨례",
        "2402": "조선일보",
        "2403": "연합뉴스",
        "2404": "ZDNet",
        "2499": "기타",
        "2501": "트위터",
        "2601": "",
        "2701": "",
        "2801": "",
        "3101": "미국 국무부",
        "3201": "",
        "3301": "",
        "3401": "한미경제연구소(KEI)",
        "4101": "",
    },
}

META_CODE_SUCCESS = "SUCCESS"
META_CODE_FAIL = "FAIL"

MOU_FILE_INDEX = "mou_file_index"
MOU_BIZ_INDEX = "mou_biz_index"
T3Q_SEARCH_WORD_INDEX = "t3q_search_word_index"
