from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agente_med.agent import AgenteMed
from agente_med.inference import bayesian_inference, cbr_search, detect_symptoms, forward_chaining
from agente_med.knowledge_base import load_knowledge_base


class InferenceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.kb = load_knowledge_base()

    def test_detects_symptoms_with_accents_and_synonyms(self) -> None:
        symptoms, evidence = detect_symptoms("Febre alta, tosse e dificuldade para respirar.", self.kb)
        self.assertIn("febre", symptoms)
        self.assertIn("tosse", symptoms)
        self.assertIn("falta_ar", symptoms)
        self.assertIn("dificuldade para respirar", evidence["falta_ar"])

    def test_forward_chaining_fires_covid_rule(self) -> None:
        facts, trace = forward_chaining(["febre", "tosse", "falta_ar"], self.kb)
        self.assertIn("suspeita_covid", facts)
        self.assertEqual(trace[0]["rule"], "R01")

    def test_bayesian_probabilities_are_normalized(self) -> None:
        result = bayesian_inference(["febre", "tosse", "falta_ar"], self.kb)
        total = sum(item["probability"] for item in result)
        self.assertAlmostEqual(total, 1.0, places=3)
        self.assertGreater(result[0]["probability"], 0)

    def test_cbr_returns_similar_cases(self) -> None:
        result = cbr_search(["febre", "manchas", "dor_muscular"], self.kb)
        self.assertEqual(result[0]["diagnosis"], "Dengue")
        self.assertGreater(result[0]["similarity"], 0.5)

    def test_agent_fallback_answer_mentions_safety(self) -> None:
        agent = AgenteMed(provider="local")
        answer, context = agent.respond("Sinto dor no peito e falta de ar.")
        self.assertIn("Recomendação de segurança", answer)
        self.assertIn("alerta_cardiaco", context["facts"])

    def test_detects_unprotected_sex_risk(self) -> None:
        agent = AgenteMed(provider="local")
        answer, context = agent.respond("transei sem camisinha")
        self.assertIn("sexo_sem_preservativo", context["symptoms"])
        self.assertIn("exposicao_sexual_de_risco", context["facts"])
        self.assertIn("72 horas", answer)

    def test_detects_eye_bleeding_alert(self) -> None:
        agent = AgenteMed(provider="local")
        answer, context = agent.respond("estou com o olho sangrando")
        self.assertIn("sangramento_ocular", context["symptoms"])
        self.assertIn("alerta_oftalmologico", context["facts"])
        self.assertIn("urgência", answer)


if __name__ == "__main__":
    unittest.main()
