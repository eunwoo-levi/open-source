Introduction
============

**Dev Journal** is a personal developer journal web application built with Flask and SQLite.
It was developed with Test-Driven Development (TDD) practices and follows clean code principles.

Features
--------

- **Dashboard** — Overview of total entries, tags, and recent activity
- **Journal Entries** — Full CRUD support (Create, Read, Update, Delete)
- **Tag Management** — Add and delete tags; filter entries by tag
- **Full-Text Search** — Search across entry title and content
- **Interactive API Docs** — Swagger UI powered by Flasgger at ``/apidocs``

Technology Stack
----------------

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Component
     - Technology
   * - Web Framework
     - `Flask 3.0 <https://flask.palletsprojects.com/>`_
   * - ORM / Database
     - Flask-SQLAlchemy 3.1 + SQLite
   * - Frontend
     - Bootstrap 5.3
   * - API Documentation
     - Flasgger (Swagger UI)
   * - Code Documentation
     - Sphinx + sphinx-rtd-theme
   * - Testing
     - Pytest + pytest-flask

Project Structure
-----------------

.. code-block:: text

    open-source/
    ├── app.py              # Flask application: models, helpers, routes
    ├── conftest.py         # Pytest fixtures
    ├── requirements.txt    # Python dependencies
    ├── docs/               # Sphinx documentation source
    │   ├── conf.py
    │   ├── index.rst
    │   ├── introduction.rst
    │   └── modules.rst
    ├── tests/              # Test suite
    │   ├── test_routes.py
    │   └── test_client.py
    ├── templates/          # Jinja2 HTML templates
    └── static/             # CSS and static assets

Quick Start
-----------

.. code-block:: bash

    # 1. Clone the repository
    git clone https://github.com/eunwoo-levi/open-source.git
    cd open-source

    # 2. Install dependencies
    pip install -r requirements.txt

    # 3. Run the development server
    python app.py

Open your browser at ``http://localhost:5001``.

Development Workflow
--------------------

This project uses a Git branching strategy:

- ``main`` — Stable production-ready code
- ``feature/*`` — New features
- ``refactor`` — Code smell fixes and refactoring
- ``test`` — TDD implementation
- ``docs/sphinx-flasgger-readme`` — Documentation improvements

Commit messages follow the `Conventional Commits <https://www.conventionalcommits.org/>`_ standard.
