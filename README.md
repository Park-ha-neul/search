# T3Q.search

## 개요
T3Q.search의 Back-End 서비스를 제공합니다.


## 개발 도구
- Git
- SourceTree
- PyCharm
- Python 3.7.6

## 개발환경 셋팅
- workspace 생성
  - `/project/t3q.factory/fastapi_workspace`
- git-clone
  - `GitLab`[FastAPI GitLab URL](http://lab.t3q.co.kr:9999/t3q_factory/fastapi) 접속
  - `GitLab`Clone > Clone with HTTP 주소 복사
  - `ScourceTree`ScourceTree > New tab > Clone
  - `ScourceTree`소스 경로에 Clone with HTTP 주소 붙여넣기
  - `ScourceTree`목적지 경로 > project workspace 경로
  - `ScourceTree`이름 생성 > 클론
- 패키지 설치 및 Interpreter 설정
  - 패키지 설치
    ```
    - cli 프로젝트 경로로 이동
    $ cd /project/t3q.factory/fastapi_workspace
  
    - 환경변수 설정
    $ PIPENV_VENV_IN_PROJECT=1
  
    - 패키지 설치 (Pipfile)
    $ pipenv install
  
    - 패키지 확인
    $ pipenv graph
    ```
  - `PyCharm`Open > `/project/t3q.factory/fastapi_workspace` > OK
  - `PyCharm`File > Settings > Python Interpreter > Add > Base Interpreter > `\project\t3q.factory\fastapi_workspace\.venv\Scripts\python.exe`

- 기동 및 테스트
  ```shell
  $pipenv run uvicorn app.main:app --reload --env-file .env
  ```
  - localhost:8000 접속
  - doc 확인 `localhost:8000/redoc`

- 기타 개발을 위해 필요한 사항 정리
```buildoutcfg

├── app         # "app" is a Python package
│   ├── __init__.py      # this file makes "app" a "Python package"
│   ├── main.py          # "main" module, e.g. import app.main
│   ├── dependencies.py  # "dependencies" module, e.g. import app.dependencies
│   └── routers          # "routers" is a "Python subpackage"
│   │   ├── __init__.py  # makes "routers" a "Python subpackage"
│   │   ├── items.py     # "items" submodule, e.g. import app.routers.items
│   │   └── users.py     # "users" submodule, e.g. import app.routers.users
│   └── internal         # "internal" is a "Python subpackage"
│       ├── __init__.py  # makes "internal" a "Python subpackage"
│       └── admin.py     # "admin" submodule, e.g. import app.internal.admin
```

# Dockerfile
- docker build
```shell
$ docker build -t fastapi_search:0.1 .
```
- docker run
```shell
$ docker run -p 8000:8000 --env-file=.env  --name fastapi_app fastapi_search:0.1
```

## requirement 생성
```shell
pipenv lock -r > requirements.txt
```

# 참고
- [FastAPI + PyDantic](https://buzzni.com/blog/47)
- [Best practices for structuring a FastAPI project](https://stackoverflow.com/questions/64943693/what-are-the-best-practices-for-structuring-a-fastapi-project)