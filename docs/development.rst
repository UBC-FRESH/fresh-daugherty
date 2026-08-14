Development
===========

Local verification gate::

   python -m ruff check .
   python -m pytest
   sphinx-build -b html docs _build/html -W
   python -m build
   twine check dist/*

Governance and the development workflow are documented in ``AGENTS.md`` and
``CONTRIBUTING.md``.
