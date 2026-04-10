<div align="center">

# 📓 Dev Journal

**Flask + SQLite 기반의 개인 개발 일지 웹 애플리케이션**

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=flat-square&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)
[![Docs](https://img.shields.io/badge/Docs-GitHub%20Pages-0366d6?style=flat-square&logo=read-the-docs&logoColor=white)](https://eunwoo-levi.github.io/open-source/)
[![Swagger](https://img.shields.io/badge/API-Swagger%20UI-85EA2D?style=flat-square&logo=swagger&logoColor=black)](http://localhost:5001/apidocs)

</div>

---

## ✨ 주요 기능

| 기능 | 설명 |
|------|------|
| 📊 **대시보드** | 전체 일지 수, 태그 수, 최근 활동 요약 |
| 📝 **일지 관리** | 일지 작성 / 조회 / 수정 / 삭제 (CRUD) |
| 🏷️ **태그 관리** | 태그 추가·삭제 및 태그별 일지 필터링 |
| 🔍 **전문 검색** | 제목·내용 대상 실시간 키워드 검색 |
| 📖 **API 문서** | Swagger UI(`/apidocs`)에서 API 직접 테스트 |
| 📚 **코드 문서** | Sphinx로 자동 생성된 HTML 기술 문서 |

---

## 🛠️ 기술 스택

- **Backend**: Python 3.9+, Flask 3.0, Flask-SQLAlchemy 3.1
- **Database**: SQLite (개발) — 환경변수로 PostgreSQL 전환 가능
- **Frontend**: Bootstrap 5.3, Jinja2 템플릿
- **API Docs**: [Flasgger](https://github.com/flasgger/flasgger) (Swagger UI)
- **Code Docs**: [Sphinx](https://www.sphinx-doc.org/) + sphinx-rtd-theme
- **Testing**: Pytest + pytest-flask (TDD 방식)
- **CI/CD**: GitHub Actions → GitHub Pages 자동 배포

---

## 📚 문서

| 문서 | 링크 |
|------|------|
| 📖 **Sphinx 코드 문서** | [GitHub Pages](https://eunwoo-levi.github.io/open-source/) |
| 🔌 **Swagger API 문서** | [로컬 서버 실행 후 `/apidocs`](http://localhost:5001/apidocs) |
| 🔧 **리팩토링 기록** | [REFACTORING.md](REFACTORING.md) |

---

## 🚀 설치 및 실행

### 사전 요구사항

- Python 3.9 이상
- pip

### 1단계: 저장소 클론

```bash
git clone https://github.com/eunwoo-levi/open-source.git
cd open-source
```

### 2단계: 가상환경 생성 및 활성화 (권장)

```bash
# 가상환경 생성
python3 -m venv venv

# 활성화 (macOS/Linux)
source venv/bin/activate

# 활성화 (Windows)
venv\Scripts\activate
```

### 3단계: 의존성 설치

```bash
pip install -r requirements.txt
```

### 4단계: 환경변수 설정 (선택)

```bash
cp .env.example .env
# .env 파일을 열어 값 수정
```

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `SECRET_KEY` | `dev-journal-secret-key` | Flask 세션 키 |
| `DATABASE_URL` | `sqlite:///journal.db` | 데이터베이스 URL |

### 5단계: 서버 실행

```bash
python3 app.py
```

| 서비스 | URL |
|--------|-----|
| 웹 애플리케이션 | http://localhost:5001 |
| Swagger API 문서 | http://localhost:5001/apidocs |

---

## 🧪 테스트 실행

```bash
pytest -v
```

> 테스트는 인메모리 SQLite를 사용하므로 프로덕션 DB에 영향 없음.

---

## 📁 프로젝트 구조

```
open-source/
├── app.py                  # Flask 앱: 모델, 헬퍼, 라우트
├── conftest.py             # Pytest 픽스처
├── requirements.txt        # Python 의존성
├── .env.example            # 환경변수 예시
├── .github/
│   └── workflows/
│       └── docs.yml        # Sphinx 자동 빌드 & GitHub Pages 배포
├── docs/                   # Sphinx 문서 소스
│   ├── conf.py             # Sphinx 설정
│   ├── index.rst           # 메인 목차
│   ├── introduction.rst    # 소개 페이지
│   └── modules.rst         # 모듈 API 레퍼런스
├── tests/                  # Pytest 테스트
│   ├── test_routes.py      # 라우트 통합 테스트
│   └── test_client.py      # 클라이언트 테스트
├── templates/              # Jinja2 HTML 템플릿
│   ├── base.html
│   ├── index.html          # 대시보드
│   ├── entries.html        # 일지 목록
│   ├── entry_detail.html   # 일지 상세
│   ├── entry_form.html     # 일지 작성/수정 폼
│   ├── tags.html           # 태그 관리
│   └── search.html         # 검색
└── instance/
    └── journal.db          # SQLite DB (자동 생성, gitignore)
```

---

## 🔌 API 엔드포인트

전체 API 명세는 서버 실행 후 **[Swagger UI](http://localhost:5001/apidocs)** 에서 직접 테스트 가능합니다.

| Method | Endpoint | 설명 |
|--------|----------|------|
| `GET` | `/` | 대시보드 |
| `GET` | `/entries` | 일지 목록 (태그 필터링 지원) |
| `GET/POST` | `/entries/new` | 일지 생성 |
| `GET` | `/entries/<id>` | 일지 상세 조회 |
| `GET/POST` | `/entries/<id>/edit` | 일지 수정 |
| `POST` | `/entries/<id>/delete` | 일지 삭제 |
| `GET` | `/tags` | 태그 목록 |
| `POST` | `/tags/new` | 태그 생성 |
| `POST` | `/tags/<id>/delete` | 태그 삭제 |
| `GET` | `/search?q=키워드` | 전문 검색 |
| `GET` | `/apidocs` | Swagger UI |

---

## 🤝 개발 기록

이 프로젝트는 오픈소스 수업의 Mini-Project 시리즈로 진행되었습니다:

- **Part 1~2**: Flask 웹앱 기본 구조 구축
- **Part 3**: TDD (Pytest) 적용 및 AI 협업 리팩토링 → [REFACTORING.md](REFACTORING.md)
- **Part 4**: Sphinx 코드 문서화, Flasgger API 문서화, README 포트폴리오 강화

---

## 📄 License

[MIT License](LICENSE) © 2024 Dev Journal Contributors
