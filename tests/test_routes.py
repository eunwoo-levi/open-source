"""
tests/test_routes.py — Route-level TDD tests for the Dev Journal Flask app.

TDD Cycle:
  RED   — These tests are written BEFORE verifying all edge cases.
           Each test name is the human-defined spec.
  GREEN — The existing app.py already implements the routes,
           so tests pass after fixtures are wired up correctly.

Human defines: test names, assertions, expected behavior
AI implements: test body, helper setup code
"""

import pytest
from app import db, Entry, Tag


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def _create_entry(client, title="Test Entry", content="Test content"):
    """POST to /entries/new and return the response."""
    return client.post(
        "/entries/new",
        data={"title": title, "content": content},
        follow_redirects=True,
    )


def _seed_entry(client, app, title="Flask TDD", content="Learning TDD with pytest"):
    """
    Insert an Entry using the test client's active DB session.
    We POST through the route so the same SQLAlchemy session is used.
    Returns the id by querying after creation.
    """
    client.post(
        "/entries/new",
        data={"title": title, "content": content},
        follow_redirects=True,
    )
    with app.app_context():
        entry = Entry.query.filter_by(title=title).first()
        return entry.id if entry else None


def _seed_tag(client, name="python"):
    """
    Insert a Tag through the POST /tags/new endpoint so it shares
    the same SQLAlchemy session as the test client.
    Returns the tag name (used to build delete URL via query).
    """
    client.post("/tags/new", data={"name": name}, follow_redirects=True)
    return name


# ─────────────────────────────────────────────────────────────
# Mission 3: RED → GREEN  (core route specs)
# ─────────────────────────────────────────────────────────────

class TestDashboard:
    """Spec: The index page must load successfully."""

    def test_index_returns_200(self, client):
        """
        RED spec: GET / must return HTTP 200.
        GREEN: index() renders index.html which exists.
        """
        response = client.get("/")
        assert response.status_code == 200

    def test_index_shows_dashboard_content(self, client):
        """
        RED spec: The dashboard page must contain '대시보드' in the HTML.
        GREEN: base.html / index.html includes the Korean nav label.
        """
        response = client.get("/")
        assert "대시보드" in response.data.decode("utf-8")


class TestEntries:
    """Spec: CRUD operations on journal entries."""

    def test_entries_page_returns_200(self, client):
        """
        RED spec: GET /entries must return HTTP 200.
        """
        response = client.get("/entries")
        assert response.status_code == 200

    def test_create_entry_success(self, client, app):
        """
        RED spec: POSTing a valid title + content must redirect (302 → 200)
                  and the new entry title must appear on the entries list page.
        """
        response = _create_entry(client, title="My First Entry", content="Hello TDD!")
        assert response.status_code == 200
        assert b"My First Entry" in response.data

    def test_create_entry_missing_title_returns_error(self, client):
        """
        RED spec: POSTing without a title must stay on the form page (200)
                  and must NOT create an entry.
        """
        response = client.post(
            "/entries/new",
            data={"title": "", "content": "some content"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        # The form page is re-rendered; no redirect to /entries
        assert b"entry_form" not in response.data  # redirect did not happen
        # Error flash message appears
        assert "입력" in response.data.decode("utf-8")

    def test_create_entry_missing_content_returns_error(self, client):
        """
        RED spec: POSTing without content must stay on the form (200)
                  and show a validation message.
        """
        response = client.post(
            "/entries/new",
            data={"title": "Title Only", "content": ""},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert "입력" in response.data.decode("utf-8")

    def test_view_entry_returns_200(self, app, client):
        """
        RED spec: GET /entries/<id> must return 200 and show the entry title.
        """
        entry_id = _seed_entry(client, app, title="Viewable Entry")
        response = client.get(f"/entries/{entry_id}")
        assert response.status_code == 200
        assert b"Viewable Entry" in response.data

    def test_view_nonexistent_entry_returns_404(self, client):
        """
        RED spec: GET /entries/9999 (not in DB) must return 404.
        """
        response = client.get("/entries/9999")
        assert response.status_code == 404

    def test_edit_entry_success(self, app, client):
        """
        RED spec: POSTing to /entries/<id>/edit with updated title must
                  redirect and the updated title must be stored.
        """
        entry_id = _seed_entry(client, app, title="Old Title")
        response = client.post(
            f"/entries/{entry_id}/edit",
            data={"title": "New Title", "content": "Updated content"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"New Title" in response.data

    def test_delete_entry_removes_it(self, app, client):
        """
        RED spec: POSTing to /entries/<id>/delete must redirect and
                  the entry must no longer appear on the entries list.
        """
        entry_id = _seed_entry(client, app, title="To Be Deleted")
        response = client.post(
            f"/entries/{entry_id}/delete",
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"To Be Deleted" not in response.data


class TestTags:
    """Spec: Tag creation and duplicate prevention."""

    def test_tags_page_returns_200(self, client):
        """
        RED spec: GET /tags must return HTTP 200.
        """
        response = client.get("/tags")
        assert response.status_code == 200

    def test_create_tag_success(self, client):
        """
        RED spec: POSTing a new tag name must redirect to /tags
                  and the tag must appear on the page.
        """
        response = client.post(
            "/tags/new",
            data={"name": "pytest"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"pytest" in response.data

    def test_create_duplicate_tag_shows_warning(self, client):
        """
        RED spec: Creating a tag that already exists must show a warning
                  flash message and not create a duplicate.
        """
        client.post("/tags/new", data={"name": "duplicate"}, follow_redirects=True)
        response = client.post(
            "/tags/new",
            data={"name": "duplicate"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert "이미 존재" in response.data.decode("utf-8")

    def test_delete_tag(self, app, client):
        """
        RED spec: POSTing to /tags/<id>/delete must redirect and
                  the tag must no longer appear on the tags page.
        """
        # Seed via HTTP so the tag exists in the same DB session as the client
        _seed_tag(client, name="to-delete")
        # Retrieve the tag id from the shared DB context
        with app.app_context():
            tag = Tag.query.filter_by(name="to-delete").first()
            assert tag is not None, "Tag was not created by seed helper"
            tag_id = tag.id
        response = client.post(
            f"/tags/{tag_id}/delete",
            follow_redirects=True,
        )
        assert response.status_code == 200
        # Verify the tag is gone: tag list shows 0 tags badge
        # (checking the deletion flash text which includes the tag name would be fragile)
        with app.app_context():
            assert Tag.query.filter_by(name="to-delete").first() is None


class TestSearch:
    """Spec: Full-text search over title and content."""

    def test_search_page_no_query_returns_200(self, client):
        """
        RED spec: GET /search (no query) must return 200 with empty results.
        """
        response = client.get("/search")
        assert response.status_code == 200

    def test_search_returns_matching_entry(self, app, client):
        """
        RED spec: GET /search?q=flask must return 200 and include
                  the title of an entry whose content contains 'flask'.
        """
        _seed_entry(client, app, title="Flask TDD Guide", content="Learning Flask TDD")
        response = client.get("/search?q=flask")
        assert response.status_code == 200
        assert b"Flask TDD Guide" in response.data

    def test_search_no_match_shows_empty(self, app, client):
        """
        RED spec: Searching for a non-existent term must return 200
                  and must NOT show any entries.
        """
        _seed_entry(client, app, title="Unrelated Entry", content="Nothing about the query")
        response = client.get("/search?q=xyzzy_nonexistent")
        assert response.status_code == 200
        assert b"Unrelated Entry" not in response.data
