#!/usr/bin/env python3
"""Tạo fixture repo multi-module có circular dependency cho graph_deps test."""
from pathlib import Path

repo = Path(__file__).resolve().parent.parent / "fixtures" / "repos" / "multi-module-sample"
repo.mkdir(parents=True, exist_ok=True)
(repo / "core").mkdir(exist_ok=True)
(repo / "services").mkdir(exist_ok=True)
(repo / "utils").mkdir(exist_ok=True)

(repo / "core" / "__init__.py").write_text("")
(repo / "core" / "models.py").write_text(
    "from services import notifications\n\nclass User:\n    pass\n")
(repo / "core" / "config.py").write_text("DEBUG = True\n")
(repo / "services" / "__init__.py").write_text("")
(repo / "services" / "notifications.py").write_text(
    "from core.models import User\nfrom utils.helpers import fmt\n\ndef notify(u): pass\n")
(repo / "utils" / "__init__.py").write_text("")
(repo / "utils" / "helpers.py").write_text("def fmt(x): return str(x)\n")
(repo / "main.py").write_text(
    "from core.models import User\nfrom services.notifications import notify\nprint('ok')\n")
print("fixture multi-module-sample created")
