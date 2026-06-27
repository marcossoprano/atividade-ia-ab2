"""Carregamento da base de conhecimento do AgenteMed."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DEFAULT_KB_PATH = Path(__file__).resolve().parent / "data" / "knowledge_base.json"


def load_knowledge_base(path: str | Path | None = None) -> dict[str, Any]:
    """Carrega a base JSON e valida os blocos mínimos esperados."""
    kb_path = Path(path) if path else DEFAULT_KB_PATH
    with kb_path.open("r", encoding="utf-8") as file:
        data: dict[str, Any] = json.load(file)

    required_sections = [
        "metadata",
        "symptoms",
        "rules",
        "hypotheses",
        "bayesian_network",
        "cases",
    ]
    missing = [section for section in required_sections if section not in data]
    if missing:
        joined = ", ".join(missing)
        raise ValueError(f"Base de conhecimento incompleta. Faltando: {joined}")

    return data

