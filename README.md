# Liquid Notes

Apple Liquid Glaciers에서 영감을 받은 글래스모피즘 스타일의 노트 웹 애플리케이션입니다. 순수 Python WSGI 앱으로 동작하며 기본적으로 표준 라이브러리만으로 실행됩니다. 환경에 `psycopg` 혹은 `psycopg2`가 설치되어 있다면 PostgreSQL에도 연결할 수 있습니다.

## 주요 기능

- 제목과 내용을 입력해 노트 작성
- 작성된 노트 목록을 실시간 갱신하여 표시
- 노트 수정 및 삭제 기능
- SQLite(기본) 또는 PostgreSQL(옵션) 저장소

## 사전 준비

- Python 3.10 이상
- (선택) PostgreSQL 인스턴스와 `psycopg` / `psycopg2` 설치

## 실행 방법

1. 저장소 클론 후 프로젝트 루트로 이동합니다.
2. 다음 명령으로 서버를 실행합니다.

   ```bash
   python wsgi.py
   ```

   기본적으로 프로젝트 폴더 아래 `notes_dev.db` SQLite 파일이 생성됩니다.

3. 브라우저에서 `http://localhost:5000`으로 접속해 노트를 작성하고 관리할 수 있습니다.

### PostgreSQL 사용하기

PostgreSQL을 사용하려면 psycopg 호환 드라이버를 설치한 뒤 환경 변수로 연결 문자열을 지정합니다.

```bash
export DATABASE_URL="postgresql://USER:PASSWORD@HOST:PORT/DB_NAME"
python wsgi.py
```

드라이버가 설치되어 있지 않으면 애플리케이션이 실행 시 명확한 오류 메시지를 출력합니다.

## 테스트 실행

기본 제공되는 통합 테스트는 표준 라이브러리의 `unittest`로 작성되어 있습니다.

```bash
python -m unittest discover
```

## 프로젝트 구조

```
notes/
├── app/
│   ├── __init__.py
│   ├── server.py
│   ├── storage.py
│   └── static/
│       ├── css/style.css
│       ├── index.html
│       └── js/main.js
├── requirements.txt
└── wsgi.py
```

## 라이선스

이 프로젝트는 MIT 라이선스로 제공됩니다.
