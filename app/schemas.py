from pydantic import BaseModel

from typing import List, Union, Dict
from fastapi import Query


class Item(BaseModel):
    index: Union[int, None] = Query(description="페이징에 따른 순서")
    id: str = Query(description="고유 값")
    thumbnail: Union[str, None] = Query(description="문서 썸네일")
    title: Union[str, None] = Query(description="제목")
    contents: Union[str, None] = Query(description="내용")
    date: Union[str, None] = Query(description="날짜")
    file_play_time: Union[int, None] = Query(description="영상 길이")
    source: Union[str, None] = Query(description="출처")
    file: Union[str, None] = Query(description="원본 파일")


class Meta(BaseModel):
    code: str = Query(description="코드 값")
    message: str = Query(description="메세지")
    count: Union[int, None] = Query(description="검색 시 총 개수")


# 목록 조회
class CommonOut(BaseModel):
    meta: Union[Meta, None] = Query(description="code, message 값")
    data: Union[List, Item] = Query(description="검색 시 반환 데이터")


class CommonErrorOut(BaseModel):
    code: str
    message: str


# 상세 조회
class DetailCommonOut(BaseModel):
    meta: Union[Meta, None] = Query(description="code, message 값")
    data: Union[Dict, Item] = Query(description="검색 시 반환 데이터")


class DetailCommonErrorOut(BaseModel):
    code: str
    message: str
