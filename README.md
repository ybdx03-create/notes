# Liquid Notes

Apple Liquid Glaciers에서 영감을 받은 글래스모피즘 스타일의 노트 웹 애플리케이션입니다. Flask와 SQLAlchemy로 구성되어 있으며 PostgreSQL을 기본 데이터베이스로 사용할 수 있습니다.

## 주요 기능

- 제목과 내용을 입력해 노트 작성
- 작성된 노트 목록을 실시간 갱신하여 표시
- 노트 수정 및 삭제 기능
- PostgreSQL과 호환되는 SQLAlchemy 모델 구조

## 사전 준비

1. Python 3.10+
2. PostgreSQL 인스턴스 (예: 로컬 Docker 또는 클라우드)
3. 가상환경(선택) 설정

## 실행 방법

```bash
python -m venv .venv
source .venv/bin/activate  # Windows는 .venv\\Scripts\\activate
pip install -r requirements.txt
```

PostgreSQL 연결 문자열을 `DATABASE_URL` 환경 변수로 지정합니다.

```bash
export DATABASE_URL="postgresql+psycopg2://USER:PASSWORD@HOST:PORT/DB_NAME"
```

> 참고: 빠른 체험을 위해 환경 변수를 지정하지 않으면 로컬 파일(`sqlite:///notes_dev.db`)을 사용합니다. 실제 배포 환경에서는 반드시 PostgreSQL 연결 정보를 설정하세요.

서버 실행:

```bash
python wsgi.py
```

브라우저에서 `http://localhost:5000`으로 접속하면 앱을 사용할 수 있습니다.

## 데이터베이스 마이그레이션

간단한 프로젝트이므로 Flask 시작 시 자동으로 테이블을 생성합니다. 필요하다면 Alembic 등 마이그레이션 도구를 추가해 확장할 수 있습니다.

## 프로젝트 구조

```
notes/
├── app/
│   ├── __init__.py
│   ├── database.py
│   ├── models.py
│   ├── routes.py
│   ├── static/
│   │   ├── css/style.css
│   │   └── js/main.js
│   └── templates/
│       ├── base.html
│       └── index.html
├── requirements.txt
└── wsgi.py
```

## 라이선스

이 프로젝트는 MIT 라이선스로 제공됩니다.
