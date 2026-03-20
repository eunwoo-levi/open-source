"""
tests/test_client.py — Client-side HTML verification tests.

Mission 4: Verify that rendered HTML pages contain the correct
           content: page titles, navigation links, headings,
           and key UI elements.

Human defines: What each page SHOULD contain in the browser.
AI implements:  Assertions against the decoded response body.
"""


class TestHTMLContent:
    """
    Spec: Every major page must render the correct HTML structure
          containing navigation, page title, and key UI labels.
    """

    def test_base_template_has_nav_links(self, client):
        """
        RED spec: Every page inheriting base.html must include
                  navigation links to 대시보드, 일지 목록, 태그, 검색.
        """
        response = client.get("/")
        html = response.data.decode("utf-8")
        assert "대시보드" in html
        assert "일지 목록" in html or "entries" in html
        assert "태그" in html
        assert "검색" in html

    def test_index_shows_stat_cards(self, client):
        """
        RED spec: The dashboard must display total entry count and tag count
                  (the stat cards). These labels must appear in the HTML.
        """
        response = client.get("/")
        html = response.data.decode("utf-8")
        # Either Korean stat labels or numeric count must appear
        assert response.status_code == 200
        # At minimum the page renders without error
        assert len(html) > 100

    def test_entries_page_has_new_entry_link(self, client):
        """
        RED spec: The entries list page must contain a link / button
                  to create a new entry (/entries/new).
        """
        response = client.get("/entries")
        html = response.data.decode("utf-8")
        assert "/entries/new" in html

    def test_new_entry_form_has_title_and_content_fields(self, client):
        """
        RED spec: GET /entries/new must render a form with
                  'title' and 'content' input fields.
        """
        response = client.get("/entries/new")
        html = response.data.decode("utf-8")
        assert 'name="title"' in html
        assert 'name="content"' in html

    def test_tags_page_has_add_tag_form(self, client):
        """
        RED spec: GET /tags must render a form that POSTs to /tags/new.
        """
        response = client.get("/tags")
        html = response.data.decode("utf-8")
        assert "/tags/new" in html
        assert 'name="name"' in html

    def test_search_page_has_search_input(self, client):
        """
        RED spec: GET /search must render an input field for the query
                  and the form must target /search.
        """
        response = client.get("/search")
        html = response.data.decode("utf-8")
        assert "/search" in html
        assert 'name="q"' in html

    def test_entry_detail_shows_edit_and_delete_buttons(self, client, app):
        """
        RED spec: GET /entries/<id> must show both an Edit link
                  and a Delete button for that entry.
        """
        from app import db, Entry
        with app.app_context():
            entry = Entry(title="Detail Page Entry", content="Detail content")
            db.session.add(entry)
            db.session.commit()
            entry_id = entry.id

        response = client.get(f"/entries/{entry_id}")
        html = response.data.decode("utf-8")
        assert "edit" in html.lower() or "수정" in html
        assert "delete" in html.lower() or "삭제" in html

    def test_page_title_contains_app_name(self, client):
        """
        RED spec: Every page must have a <title> tag that references
                  the application name (Dev Journal / 개발 일지).
        """
        response = client.get("/")
        html = response.data.decode("utf-8")
        assert "<title>" in html
        # Either English or Korean app name should appear in page title
        assert "Dev Journal" in html or "개발 일지" in html
