# Purpose: check every template exists, has its header, and fits the print limits.
# Book: National AI Strategy in Practice, Chapters 1, 5-9, 11, 12
# Licence: MIT (see LICENSE)
from pathlib import Path

import pytest

TEMPLATES = Path(__file__).resolve().parent.parent / "templates"
PRINTED = {"strategy-on-a-page.md", "data-sharing-agreement.md",
           "algorithmic-impact-assessment.md", "ai-procurement-clauses.md",
           "delivery-unit-charter.md"}
ALL = PRINTED | {"data-centre-readiness-checklist.md", "civil-service-ai-curriculum.md",
                 "sandbox-application.md", "five-year-review-tor.md"}
LEGAL = {"data-sharing-agreement.md", "ai-procurement-clauses.md",
         "algorithmic-impact-assessment.md", "sandbox-application.md"}


@pytest.mark.parametrize("name", sorted(ALL))
def test_template(name):
    text = (TEMPLATES / name).read_text(encoding="utf-8")
    lines = text.splitlines()
    assert "Book: National AI Strategy in Practice, Chapter" in lines[1]
    assert "Licence: MIT" in lines[1]
    assert 80 <= len(lines) <= (150 if name in PRINTED else 200)
    if name in LEGAL:
        assert "not legal advice" in text
