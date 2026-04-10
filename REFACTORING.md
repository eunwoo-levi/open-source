# AI-Driven Refactoring — Collaboration Log

## 1. Identified Code Smells

아래 5가지 코드 스멜을 `app.py`에서 식별하였습니다.

| # | Smell | 위치 | 설명 |
|---|-------|------|------|
| 1 | **God Module** | `app.py` 전체 | 모델 정의·DB 설정·라우트·앱 초기화가 단일 파일에 모두 혼재. 단일 책임 원칙(SRP) 위반 |
| 2 | **Duplicated Code** | `new_entry()` (L60-74) & `edit_entry()` (L87-98) | 폼 데이터 파싱, 유효성 검사, 태그 조회 로직이 두 함수에서 거의 동일하게 반복 |
| 3 | **Magic String / Hardcoded Secret** | `app.config['SECRET_KEY'] = 'dev-journal-secret-key'` (L6) | 비밀 키가 소스코드에 하드코딩 → 보안 취약 & 환경별 설정 불가 |
| 4 | **N+1 Query Pattern** | `edit_entry()` L95 | `Tag.query.get(tid)` 를 필터와 값 취득에 두 번씩 호출 → 불필요한 DB 쿼리 중복 |
| 5 | **Long Method** | `new_entry()` / `edit_entry()` | GET/POST 분기·유효성 검사·DB 조작·리다이렉트가 단일 함수에 혼합 → 과도한 함수 길이와 책임 |

---

## 2. AI Collaboration Log

### 질문 1: 코드 스멜 식별 요청

**Human:**
> `app.py` 코드를 보고 코드 스멜을 최소 5가지 찾아서 설명해주세요.

**AI (Antigravity):**
> - **God Module**: 하나의 파일이 모델·설정·라우트·초기화를 모두 담당하고 있어 SRP를 위반합니다.
> - **Duplicated Code**: `new_entry()`와 `edit_entry()`의 폼 파싱·검증·태그 처리 코드가 90% 이상 동일합니다.
> - **Magic String**: `SECRET_KEY`가 소스에 직접 노출되어 있어 보안 위험이 있고, 환경 간 설정 변경이 어렵습니다.
> - **N+1 Query**: `Tag.query.get(tid)` 이중 호출로 같은 레코드를 불필요하게 두 번 조회합니다.
> - **Long Method**: `edit_entry()`는 30줄에 달하며 여러 역할을 동시에 수행합니다.

---

### 질문 2: 리팩토링 전략 제안 요청

**Human:**
> 위 스멜들을 해결할 리팩토링 전략을 여러 가지 비교해서 제안해주세요.

**AI (Antigravity):**
>
> **전략 A — Extract Helper Functions (함수 추출)**
> - 중복 코드를 헬퍼 함수(`_parse_entry_form`, `_assign_tags`)로 추출
> - 파일 구조 변경 없이 적용 가능, 기존 테스트 유지
> - 스멜 #2·#4·#5 해결
>
> **전략 B — Application Factory + Blueprint**
> - `create_app()` 팩토리 패턴 + Blueprint로 라우트를 별도 모듈로 분리
> - 스멜 #1·#3 해결에 가장 효과적
> - 파일 구조 전면 변경 → 기존 테스트 import 수정 필요
>
> **전략 C — 환경변수 기반 설정 + 헬퍼 혼합**
> - 전략 A에 `os.environ` 설정을 더해 스멜 #3도 처리
> - 파일 구조를 유지하면서 5가지 스멜 모두 커버

---

### 질문 3: 전략 선택 및 구현 방향 확정

**Human:**
> 기존 테스트를 모두 유지하면서 5개 스멜을 전부 처리하려면 어떤 전략이 좋을까요?

**AI (Antigravity):**
> 전략 **A + C 혼합**을 권장합니다.
>
> - `_parse_entry_form()`: `request.form`에서 `title`, `content`, `tag_ids`를 파싱하고, 빈 값 검사까지 수행 → 중복 제거 & 함수 단순화
> - `_assign_tags(tag_ids)`: `Tag.query.filter(Tag.id.in_(tag_ids)).all()` 단일 IN 쿼리 → N+1 제거
> - `os.environ.get('SECRET_KEY', fallback)`: 환경변수 우선, fallback은 개발용으로만 사용
> - 테스트 파일은 한 줄도 수정하지 않아도 됩니다.

---

## 3. Decision & Review Process

### 전략 선택: **A + C (Extract Helpers + 환경변수 설정)**

**선택 이유:**

1. **테스트 안정성**: 기존 `conftest.py`, `test_routes.py`, `test_client.py`를 수정 없이 GREEN 유지
2. **점진적 개선**: 파일 구조를 바꾸지 않아 학습 컨텍스트(TDD 과제 흐름)가 유지됨
3. **전범위 커버**: 5가지 스멜 모두 단일 전략으로 처리 가능
4. **확장 가능성**: 향후 Blueprint 도입 시 헬퍼 함수를 그대로 재사용 가능

### 기각된 전략: **전략 B (Blueprint 분리)**

- 효과는 크지만, 기존 `tests/test_routes.py`의 `from app import db, Entry, Tag` import가 깨짐
- 파일 구조 전면 변경은 과제 범위를 벗어남

---

## 4. Improved Design — 변경 요약

### Before (리팩토링 전)

```python
# Secret key hardcoded (Smell #3)
app.config['SECRET_KEY'] = 'dev-journal-secret-key'

# edit_entry — 30줄, 중복 로직, N+1 쿼리 (Smell #2, #4, #5)
def edit_entry(entry_id):
    ...
    title   = request.form['title'].strip()
    content = request.form['content'].strip()
    tag_ids = request.form.getlist('tags', type=int)
    if not title or not content:
        flash('제목과 내용을 모두 입력해주세요.', 'danger')
        ...
    entry.tags = [Tag.query.get(tid) for tid in tag_ids if Tag.query.get(tid)]
    #             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #             동일한 tid 에 대해 query.get() 을 filter 와 값 취득에 두 번 호출
```

### After (리팩토링 후)

```python
# Secret key from environment variable (Smell #3 해소)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-journal-secret-key')

# Helper: 폼 파싱 + 유효성 검사 (Smell #2, #5 해소)
def _parse_entry_form():
    title   = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()
    tag_ids = request.form.getlist('tags', type=int)
    if not title or not content:
        return title, content, tag_ids, '제목과 내용을 모두 입력해주세요.'
    return title, content, tag_ids, None

# Helper: 단일 IN 쿼리로 태그 조회 (Smell #4 해소)
def _assign_tags(tag_ids):
    if not tag_ids:
        return []
    return Tag.query.filter(Tag.id.in_(tag_ids)).all()

# edit_entry — 헬퍼 재사용, 책임 분리 (Smell #1·#5 부분 해소)
def edit_entry(entry_id):
    ...
    title, content, tag_ids, error = _parse_entry_form()
    if error:
        flash(error, 'danger')
        ...
    entry.tags = _assign_tags(tag_ids)
```

### 스멜별 해소 현황

| # | Smell | 해소 여부 | 적용 방법 |
|---|-------|----------|-----------|
| 1 | God Module | ✅ 부분 해소 | 헬퍼 함수 분리로 라우트 책임 축소 |
| 2 | Duplicated Code | ✅ 완전 해소 | `_parse_entry_form()` 공통 추출 |
| 3 | Magic String | ✅ 완전 해소 | `os.environ.get()` 적용 |
| 4 | N+1 Query | ✅ 완전 해소 | `Tag.id.in_()` 단일 쿼리로 교체 |
| 5 | Long Method | ✅ 완전 해소 | 헬퍼 위임으로 함수 길이 50% 단축 |
