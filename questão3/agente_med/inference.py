"""Motores locais de inferência usados pelo agente."""

from __future__ import annotations

import math
import re
import unicodedata
from typing import Any


def normalize_text(text: str) -> str:
    """Normaliza acentos, caixa e pontuação para busca por termos."""
    without_accents = unicodedata.normalize("NFKD", text)
    ascii_text = without_accents.encode("ascii", "ignore").decode("ascii")
    lowered = ascii_text.lower().replace("_", " ")
    return re.sub(r"[^a-z0-9]+", " ", lowered).strip()


def detect_symptoms(text: str, kb: dict[str, Any]) -> tuple[list[str], dict[str, list[str]]]:
    """Detecta sintomas no texto por palavras-chave e sinônimos cadastrados."""
    normalized = f" {normalize_text(text)} "
    detected: list[str] = []
    evidence: dict[str, list[str]] = {}

    for symptom in kb["symptoms"]:
        symptom_id = symptom["id"]
        terms = [symptom_id, symptom["label"], *symptom.get("synonyms", [])]
        matches: list[str] = []
        for term in terms:
            normalized_term = normalize_text(term)
            if not normalized_term:
                continue
            if f" {normalized_term} " in normalized:
                matches.append(term)

        if matches:
            detected.append(symptom_id)
            evidence[symptom_id] = sorted(set(matches))

    return detected, evidence


def forward_chaining(
    initial_facts: list[str],
    kb: dict[str, Any],
) -> tuple[set[str], list[dict[str, Any]]]:
    """Aplica regras SE-ENTAO até atingir ponto fixo."""
    facts = set(initial_facts)
    trace: list[dict[str, Any]] = []
    fired_rules: set[str] = set()

    changed = True
    while changed:
        changed = False
        for rule in kb["rules"]:
            if rule["id"] in fired_rules:
                continue
            conditions = set(rule["conditions"])
            if conditions.issubset(facts):
                facts.add(rule["conclusion"])
                fired_rules.add(rule["id"])
                changed = True
                trace.append(
                    {
                        "rule": rule["id"],
                        "conditions": rule["conditions"],
                        "conclusion": rule["conclusion"],
                        "confidence": rule["confidence"],
                        "explanation": rule["explanation"],
                        "hypothesis": rule.get("hypothesis"),
                    }
                )

    return facts, trace


def backward_chaining(
    goal: str,
    known_facts: set[str],
    kb: dict[str, Any],
) -> dict[str, Any]:
    """Tenta provar uma conclusão ou hipótese a partir dos fatos conhecidos."""
    supports = _goal_supports(goal, kb)
    targets = supports if supports else [goal]
    attempts = [_prove_target(target, known_facts, kb, []) for target in targets]
    proved_attempts = [attempt for attempt in attempts if attempt["proved"]]

    if proved_attempts:
        best = max(proved_attempts, key=lambda item: item["confidence"])
        return {
            "goal": goal,
            "proved": True,
            "confidence": best["confidence"],
            "path": best["path"],
            "missing": [],
        }

    missing = sorted({item for attempt in attempts for item in attempt["missing"]})
    return {
        "goal": goal,
        "proved": False,
        "confidence": 0.0,
        "path": [],
        "missing": missing,
    }


def evaluate_hypotheses(
    facts: set[str],
    trace: list[dict[str, Any]],
    kb: dict[str, Any],
) -> list[dict[str, Any]]:
    """Calcula evidências para as hipóteses clínicas cadastradas."""
    conclusions = {item["conclusion"] for item in trace}
    results: list[dict[str, Any]] = []

    for hypothesis in kb["hypotheses"]:
        supports = set(hypothesis["supports"])
        matched = sorted(supports.intersection(conclusions.union(facts)))
        backward = backward_chaining(hypothesis["id"], facts, kb)
        rule_confidences = [
            item["confidence"]
            for item in trace
            if item["conclusion"] in supports or item.get("hypothesis") == hypothesis["id"]
        ]
        score = sum(rule_confidences) / len(rule_confidences) if rule_confidences else 0.0
        if backward["proved"]:
            score = max(score, backward["confidence"])

        results.append(
            {
                "id": hypothesis["id"],
                "name": hypothesis["name"],
                "description": hypothesis["description"],
                "matched_supports": matched,
                "score": round(score, 3),
                "backward": backward,
            }
        )

    return sorted(results, key=lambda item: item["score"], reverse=True)


def bayesian_inference(symptoms: list[str], kb: dict[str, Any]) -> list[dict[str, Any]]:
    """Calcula P(doenca|sintomas) com Naive Bayes simplificado."""
    diseases = kb["bayesian_network"]["diseases"]
    if not symptoms:
        total_prior = sum(disease["prior"] for disease in diseases)
        return [
            {
                "disease": disease["name"],
                "probability": round(disease["prior"] / total_prior, 4),
            }
            for disease in diseases
        ]

    log_scores: list[tuple[str, float]] = []
    for disease in diseases:
        prior = max(disease["prior"], 1e-9)
        log_score = math.log(prior)
        likelihoods = disease.get("likelihoods", {})
        for symptom in symptoms:
            likelihood = max(likelihoods.get(symptom, 0.04), 1e-9)
            log_score += math.log(likelihood)
        log_scores.append((disease["name"], log_score))

    max_log = max(score for _, score in log_scores)
    exp_scores = [(name, math.exp(score - max_log)) for name, score in log_scores]
    total = sum(score for _, score in exp_scores)

    return sorted(
        [
            {
                "disease": name,
                "probability": round(score / total, 4),
            }
            for name, score in exp_scores
        ],
        key=lambda item: item["probability"],
        reverse=True,
    )


def cbr_search(
    symptoms: list[str],
    kb: dict[str, Any],
    top_k: int = 3,
) -> list[dict[str, Any]]:
    """Busca casos semelhantes usando similaridade de Jaccard."""
    query = set(symptoms)
    results: list[dict[str, Any]] = []

    for case in kb["cases"]:
        case_symptoms = set(case["symptoms"])
        union = query.union(case_symptoms)
        score = len(query.intersection(case_symptoms)) / len(union) if union else 0.0
        results.append(
            {
                "id": case["id"],
                "diagnosis": case["diagnosis"],
                "symptoms": case["symptoms"],
                "recommendation": case["recommendation"],
                "similarity": round(score, 4),
            }
        )

    return sorted(results, key=lambda item: item["similarity"], reverse=True)[:top_k]


def explain_how(trace: list[dict[str, Any]]) -> str:
    """Gera explicação textual do caminho das regras disparadas."""
    if not trace:
        return "Nenhuma regra foi disparada com os sintomas informados."

    lines = ["Caminho de inferência:"]
    for item in trace:
        conditions = ", ".join(item["conditions"])
        confidence = int(item["confidence"] * 100)
        lines.append(
            f"- {item['rule']}: SE {conditions} ENTAO {item['conclusion']} "
            f"({confidence}%)."
        )
    return "\n".join(lines)


def _goal_supports(goal: str, kb: dict[str, Any]) -> list[str]:
    for hypothesis in kb["hypotheses"]:
        if goal in {hypothesis["id"], hypothesis["name"]}:
            return list(hypothesis["supports"])
    return []


def _prove_target(
    target: str,
    known_facts: set[str],
    kb: dict[str, Any],
    stack: list[str],
) -> dict[str, Any]:
    if target in known_facts:
        return {"proved": True, "confidence": 1.0, "path": [], "missing": []}

    if target in stack:
        return {"proved": False, "confidence": 0.0, "path": [], "missing": [target]}

    candidate_rules = [rule for rule in kb["rules"] if rule["conclusion"] == target]
    if not candidate_rules:
        return {"proved": False, "confidence": 0.0, "path": [], "missing": [target]}

    attempts: list[dict[str, Any]] = []
    for rule in candidate_rules:
        child_paths: list[dict[str, Any]] = []
        missing: list[str] = []
        confidences = [rule["confidence"]]
        all_proved = True

        for condition in rule["conditions"]:
            child = _prove_target(condition, known_facts, kb, [*stack, target])
            if child["proved"]:
                child_paths.extend(child["path"])
                confidences.append(child["confidence"])
            else:
                all_proved = False
                missing.extend(child["missing"])

        if all_proved:
            path = [
                *child_paths,
                {
                    "rule": rule["id"],
                    "conditions": rule["conditions"],
                    "conclusion": rule["conclusion"],
                    "confidence": rule["confidence"],
                },
            ]
            attempts.append(
                {
                    "proved": True,
                    "confidence": min(confidences),
                    "path": path,
                    "missing": [],
                }
            )
        else:
            attempts.append(
                {
                    "proved": False,
                    "confidence": 0.0,
                    "path": [],
                    "missing": missing,
                }
            )

    proved = [attempt for attempt in attempts if attempt["proved"]]
    if proved:
        return max(proved, key=lambda item: item["confidence"])

    return {
        "proved": False,
        "confidence": 0.0,
        "path": [],
        "missing": sorted({item for attempt in attempts for item in attempt["missing"]}),
    }

