"""Orquestração do agente conversacional AgenteMed."""

from __future__ import annotations

import json
from typing import Any

from .inference import (
    bayesian_inference,
    cbr_search,
    detect_symptoms,
    evaluate_hypotheses,
    explain_how,
    forward_chaining,
)
from .knowledge_base import load_knowledge_base
from .llm_client import LLMError, LocalFallbackLLMClient, make_llm_client


SYSTEM_PROMPT = """Voce e o AgenteMed, um agente educacional de IA.
Voce deve analisar sintomas apenas para fins academicos, nunca como diagnostico final.
Use o contexto computado localmente como fonte principal: regras disparadas, Bayes,
CBR e hipoteses. Seja claro, explique "por que" novas perguntas sao uteis e
"como" chegou a uma conclusao. Sempre recomende avaliacao profissional em sinais
de gravidade."""


class AgenteMed:
    """Agente que combina LLM opcional com inferência local explicável."""

    def __init__(self, kb_path: str | None = None, provider: str | None = None) -> None:
        self.kb = load_knowledge_base(kb_path)
        self.llm_client = make_llm_client(provider)
        self.history: list[dict[str, str]] = []

    def analyze(self, user_text: str) -> dict[str, Any]:
        """Executa todos os métodos locais antes de chamar o LLM."""
        symptoms, evidence = detect_symptoms(user_text, self.kb)
        facts, trace = forward_chaining(symptoms, self.kb)
        bayes = bayesian_inference(symptoms, self.kb)
        similar_cases = cbr_search(symptoms, self.kb)
        hypotheses = evaluate_hypotheses(facts, trace, self.kb)

        return {
            "input": user_text,
            "symptoms": symptoms,
            "evidence": evidence,
            "facts": sorted(facts),
            "rules_fired": trace,
            "bayes": bayes,
            "similar_cases": similar_cases,
            "hypotheses": hypotheses,
            "how": explain_how(trace),
        }

    def respond(self, user_text: str) -> tuple[str, dict[str, Any]]:
        """Gera resposta final usando LLM externo ou fallback local."""
        context = self.analyze(user_text)
        prompt = self._build_user_prompt(user_text, context)

        try:
            if isinstance(self.llm_client, LocalFallbackLLMClient):
                raise LLMError("Modo local.")
            answer = self.llm_client.complete(SYSTEM_PROMPT, prompt, self.history[-8:])
        except LLMError:
            answer = self._fallback_answer(context)

        self.history.append({"role": "user", "content": user_text})
        self.history.append({"role": "assistant", "content": answer})
        return answer, context

    def _build_user_prompt(self, user_text: str, context: dict[str, Any]) -> str:
        compact_context = {
            "sintomas_detectados": context["symptoms"],
            "regras_disparadas": context["rules_fired"],
            "bayes_top3": context["bayes"][:3],
            "casos_cbr_top3": context["similar_cases"],
            "hipoteses": context["hypotheses"][:3],
        }
        return (
            f"Mensagem do usuario: {user_text}\n\n"
            "[CONTEXTO COMPUTADO LOCALMENTE]\n"
            f"{json.dumps(compact_context, ensure_ascii=False, indent=2)}\n\n"
            "Responda em portugues, com analise, raciocinio, pergunta de seguimento "
            "e recomendacao de seguranca."
        )

    def _fallback_answer(self, context: dict[str, Any]) -> str:
        symptoms = context["symptoms"]
        top_bayes = context["bayes"][:3]
        top_cases = [case for case in context["similar_cases"] if case["similarity"] > 0]
        top_hypotheses = [item for item in context["hypotheses"] if item["score"] > 0]

        if not symptoms:
            return (
                "Não identifiquei sintomas cadastrados na mensagem. Descreva sinais como "
                "febre, tosse, falta de ar, dor no peito, olho sangrando, sexo sem camisinha, "
                "manchas, náusea ou dor abdominal. "
                "Se houver sintoma intenso ou piora rápida, procure atendimento profissional."
            )

        symptom_names = ", ".join(symptoms)
        lines = [
            "Análise educacional do AgenteMed",
            "",
            f"Sintomas detectados: {symptom_names}.",
            "",
            "Raciocínio local:",
        ]

        if context["rules_fired"]:
            for item in context["rules_fired"]:
                confidence = int(item["confidence"] * 100)
                lines.append(
                    f"- Regra {item['rule']} disparou {item['conclusion']} "
                    f"com confiança de {confidence}%."
                )
        else:
            lines.append("- Nenhuma regra SE-ENTAO foi satisfeita integralmente.")

        lines.append("")
        lines.append("Inferência bayesiana:")
        for item in top_bayes:
            lines.append(f"- {item['disease']}: {item['probability'] * 100:.1f}%")

        if top_cases:
            lines.append("")
            lines.append("Casos similares:")
            for case in top_cases[:3]:
                lines.append(
                    f"- {case['id']} ({case['diagnosis']}): "
                    f"{case['similarity'] * 100:.1f}% de similaridade."
                )

        if top_hypotheses:
            lines.append("")
            lines.append("Hipóteses simbólicas mais fortes:")
            for hypothesis in top_hypotheses[:3]:
                lines.append(
                    f"- {hypothesis['name']} "
                    f"(score {hypothesis['score'] * 100:.0f}%)."
                )

        lines.append("")
        lines.append("Por quê perguntar mais?")
        lines.append(self._next_question(symptoms, top_hypotheses))
        lines.append("")
        lines.append("Como cheguei nisso?")
        lines.append(context["how"])
        lines.append("")
        lines.append(
            self._safety_recommendation(symptoms)
        )
        return "\n".join(lines)

    def _next_question(
        self,
        symptoms: list[str],
        top_hypotheses: list[dict[str, Any]],
    ) -> str:
        if "sexo_sem_preservativo" in symptoms:
            return "Preciso saber há quantas horas foi a relação, se há risco de gravidez e se houve exposição a sangue/sêmen, porque PEP para HIV e contracepção de emergência dependem do tempo."
        if "sangramento_ocular" in symptoms:
            return "Perguntaria se há dor, alteração na visão, trauma, produto químico ou uso de lente de contato, porque esses sinais mudam a urgência oftalmológica."
        if "falta_ar" in symptoms or "dor_peito" in symptoms:
            return "Quero saber se há piora ao esforço, desmaio ou dor irradiando, porque isso muda a urgência."
        if top_hypotheses and top_hypotheses[0]["id"] == "H4":
            return "Vale perguntar sobre manchas, sangramento e dor abdominal, porque ajudam a separar dengue comum de sinais de alarme."
        if "febre" in symptoms and "rigidez_nuca" not in symptoms:
            return "Perguntaria sobre rigidez na nuca e confusão mental para checar sinais infecciosos graves."
        if "tosse" in symptoms:
            return "Perguntaria sobre falta de ar e perda de olfato/paladar para refinar hipóteses respiratórias."
        return "Perguntaria sobre duração, intensidade e sintomas associados para reduzir hipóteses concorrentes."

    def _safety_recommendation(self, symptoms: list[str]) -> str:
        if "sexo_sem_preservativo" in symptoms:
            return (
                "Recomendação de segurança: isto é uma simulação acadêmica. Se a relação "
                "foi há até 72 horas e houve possível exposição ao HIV, procure urgência "
                "ou serviço especializado para avaliar PEP. Se há risco de gravidez, "
                "contracepção de emergência pode ser considerada até 5 dias, quanto antes "
                "melhor. Também é prudente fazer orientação/testes para ISTs."
            )
        if "sangramento_ocular" in symptoms:
            return (
                "Recomendação de segurança: isto é uma simulação acadêmica. Sangramento "
                "no olho deve ser avaliado com urgência se houver dor, alteração da visão, "
                "trauma, produto químico, lente de contato, dor de cabeça forte ou olho "
                "muito vermelho. Evite esfregar o olho."
            )
        return (
            "Recomendação de segurança: isto é uma simulação acadêmica. "
            "Procure atendimento médico, especialmente se houver falta de ar, "
            "dor no peito, rigidez na nuca, sangramento, confusão ou piora rápida."
        )
