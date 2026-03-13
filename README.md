# 개발 일지 (Dev Journal)

Flask와 SQLite 기반의 개인 개발 일지 웹 애플리케이션입니다.

## 기능

- **대시보드** — 전체 일지 수, 태그 수, 최근 일지 요약
- **일지 관리** — 일지 작성 / 조회 / 수정 / 삭제 (CRUD)
- **태그 관리** — 태그 추가·삭제 및 태그별 필터링
- **검색** — 제목·내용 전문 검색

## 기술 스택

- Python 3.7+
- Flask 3.0
- Flask-SQLAlchemy 3.1 (SQLite)
- Bootstrap 5.3

## 설치 및 실행

```bash
# 1. 저장소 클론
git clone https://github.com/yourusername/dev-journal.git
cd dev-journal

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 서버 실행
python app.py
```

브라우저에서 `http://localhost:5001` 접속

## 프로젝트 구조

```
.
├── app.py              # Flask 앱, 모델, 라우트
├── requirements.txt
├── static/
│   └── css/style.css
├── templates/
│   ├── base.html
│   ├── index.html        # 대시보드
│   ├── entries.html      # 일지 목록
│   ├── entry_detail.html # 일지 상세
│   ├── entry_form.html   # 일지 작성/수정 폼
│   ├── tags.html         # 태그 관리
│   └── search.html       # 검색
└── instance/
    └── journal.db        # SQLite DB (자동 생성)
```

## 데이터 초기화

`instance/journal.db` 파일을 삭제하면 DB가 초기화됩니다.

## License

MIT License
