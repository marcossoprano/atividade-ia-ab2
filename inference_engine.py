"""
Motor de Inferência - Sistema Especialista em Diagnóstico Médico
Implementa: Forward Chaining, Backward Chaining e Estratégia Híbrida
"""

import json
import copy
from typing import Optional


class InferenceEngine:
    def __init__(self, kb_path: str = "knowledge_base.json"):
        with open(kb_path, "r", encoding="utf-8") as f:
            self.kb = json.load(f)

        self.rules = self.kb["rules"]
        self.hypotheses = {h["id"]: h for h in self.kb["hypotheses"]}
        self.questions_def = self.kb.get("questions", {})

        # Estado da sessão de inferência
        self.working_memory: dict[str, str] = {}
        self.fired_rules: list[dict] = []
        self.inference_trace: list[dict] = []
        self.pending_questions: list[str] = []
        self.asked_attributes: set[str] = set()

    # ------------------------------------------------------------------
    # Gerenciamento de sessão
    # ------------------------------------------------------------------

    def reset(self):
        self.working_memory = {}
        self.fired_rules = []
        self.inference_trace = []
        self.pending_questions = []
        self.asked_attributes = set()

    def add_fact(self, attribute: str, value: str, source: str = "user"):
        # Para atributos de conclusão (suspeita, confirmacao), acumular múltiplos valores
        if attribute in ("suspeita", "confirmacao"):
            existing = self.working_memory.get(attribute, "")
            values = set(existing.split(",") if existing else [])
            values.add(value)
            self.working_memory[attribute] = ",".join(sorted(values))
        else:
            self.working_memory[attribute] = value
        self.inference_trace.append({
            "type": "fact",
            "attribute": attribute,
            "value": value,
            "source": source,
        })

    # ------------------------------------------------------------------
    # Verificação de condições
    # ------------------------------------------------------------------

    def _condition_satisfied(self, condition: dict) -> bool:
        attr = condition["attribute"]
        val = condition["value"]
        return self.working_memory.get(attr) == val

    def _all_conditions_satisfied(self, rule: dict) -> bool:
        return all(self._condition_satisfied(c) for c in rule["conditions"])

    def _applicable_rules(self) -> list[dict]:
        fired_ids = {r["id"] for r in self.fired_rules}
        return [
            r for r in self.rules
            if self._all_conditions_satisfied(r) and r["id"] not in fired_ids
        ]

    # ------------------------------------------------------------------
    # Forward Chaining
    # ------------------------------------------------------------------

    def forward_chain(self) -> list[dict]:
        """
        Encadeamento para frente: aplica todas as regras cujas condições
        são satisfeitas pelos fatos na memória de trabalho.
        Repete até estabilização (ponto fixo).
        """
        new_conclusions = []
        changed = True
        while changed:
            changed = False
            for rule in self._applicable_rules():
                conclusion = rule["conclusion"]
                self.add_fact(
                    conclusion["attribute"],
                    conclusion["value"],
                    source=f"rule:{rule['id']}",
                )
                self.fired_rules.append(rule)
                self.inference_trace.append({
                    "type": "rule_fired",
                    "rule_id": rule["id"],
                    "rule_name": rule["name"],
                    "conclusion": conclusion,
                    "explanation": rule.get("explanation", ""),
                    "treatment": rule.get("treatment", ""),
                })
                new_conclusions.append(rule)
                changed = True
        return new_conclusions

    # ------------------------------------------------------------------
    # Backward Chaining
    # ------------------------------------------------------------------

    def backward_chain(self, goal_attribute: str, goal_value: str,
                       depth: int = 0, visited: Optional[set] = None) -> bool:
        """
        Encadeamento para trás: tenta provar (goal_attribute = goal_value)
        verificando se alguma regra conclui isso e se suas condições podem ser
        satisfeitas recursivamente.
        """
        if visited is None:
            visited = set()

        goal_key = f"{goal_attribute}={goal_value}"
        if goal_key in visited:
            return False
        visited.add(goal_key)

        # Fato já conhecido
        if self.working_memory.get(goal_attribute) == goal_value:
            return True

        # Buscar regras que concluem o objetivo
        supporting_rules = [
            r for r in self.rules
            if r["conclusion"]["attribute"] == goal_attribute
            and r["conclusion"]["value"] == goal_value
        ]

        for rule in supporting_rules:
            if self._try_prove_rule(rule, depth, visited):
                # Disparar a regra
                if rule["id"] not in {r["id"] for r in self.fired_rules}:
                    conclusion = rule["conclusion"]
                    self.add_fact(
                        conclusion["attribute"],
                        conclusion["value"],
                        source=f"backward:rule:{rule['id']}",
                    )
                    self.fired_rules.append(rule)
                    self.inference_trace.append({
                        "type": "rule_fired_backward",
                        "rule_id": rule["id"],
                        "rule_name": rule["name"],
                        "conclusion": conclusion,
                        "explanation": rule.get("explanation", ""),
                        "treatment": rule.get("treatment", ""),
                    })
                return True

        return False

    def _try_prove_rule(self, rule: dict, depth: int, visited: set) -> bool:
        for condition in rule["conditions"]:
            attr = condition["attribute"]
            val = condition["value"]
            if not self.backward_chain(attr, val, depth + 1, visited):
                return False
        return True

    # ------------------------------------------------------------------
    # Estratégia Híbrida
    # ------------------------------------------------------------------

    def hybrid_chain(self) -> dict:
        """
        Estratégia híbrida:
        1. Forward chaining com fatos do usuário para inferir suspeitas iniciais.
        2. Backward chaining para confirmar hipóteses suspeitas.
        3. Novo round de forward chaining com fatos confirmados.
        """
        # Fase 1 – forward inicial
        self.forward_chain()

        # Fase 2 – backward para hipóteses ainda não provadas
        hypotheses_ids = list(self.hypotheses.keys())
        for hyp_id in hypotheses_ids:
            if self.working_memory.get("suspeita") == hyp_id:
                # Tentar confirmar via backward
                self.backward_chain("confirmacao", hyp_id)

        # Fase 3 – forward novamente para propagar novas conclusões
        self.forward_chain()

        return self._build_result()

    # ------------------------------------------------------------------
    # Coleta de perguntas necessárias
    # ------------------------------------------------------------------

    def get_next_question(self, strategy: str = "hybrid") -> Optional[dict]:
        """
        Identifica o próximo atributo a perguntar ao usuário.
        Prioriza atributos que aparecem em mais regras não disparadas.
        """
        # Atributos já conhecidos
        known = set(self.working_memory.keys())

        # Atributos necessários em regras ainda não disparadas
        attr_count: dict[str, int] = {}
        for rule in self.rules:
            # Pular regras já disparadas
            if rule["id"] in {r["id"] for r in self.fired_rules}:
                continue
            # Verificar se a regra ainda pode ser disparada (não contradita)
            potentially_useful = True
            for cond in rule["conditions"]:
                attr = cond["attribute"]
                if attr in known and self.working_memory[attr] != cond["value"]:
                    potentially_useful = False
                    break
            if not potentially_useful:
                continue

            for cond in rule["conditions"]:
                attr = cond["attribute"]
                if attr not in known and attr not in self.asked_attributes:
                    attr_count[attr] = attr_count.get(attr, 0) + 1

        if not attr_count:
            return None

        # Escolher o atributo que aparece em mais regras
        best_attr = max(attr_count, key=lambda a: attr_count[a])
        self.asked_attributes.add(best_attr)

        question_def = self.questions_def.get(best_attr)
        if question_def:
            # Verificar dependência
            dep = question_def.get("depends_on")
            if dep and self.working_memory.get(dep["attribute"]) != dep["value"]:
                # Pular esta pergunta
                self.working_memory[best_attr] = "desconhecido"
                return self.get_next_question(strategy)

            return {
                "attribute": best_attr,
                "text": question_def["text"],
                "options": question_def["options"],
                "values": question_def["values"],
                "why": self._explain_why(best_attr),
            }

        return {
            "attribute": best_attr,
            "text": f"O paciente apresenta {best_attr}?",
            "options": ["Sim", "Não"],
            "values": ["sim", "nao"],
            "why": self._explain_why(best_attr),
        }

    # ------------------------------------------------------------------
    # Mecanismo de Explicação
    # ------------------------------------------------------------------

    def _explain_why(self, attribute: str) -> str:
        """
        Responde POR QUÊ determinada pergunta foi feita.
        """
        relevant_rules = []
        for rule in self.rules:
            for cond in rule["conditions"]:
                if cond["attribute"] == attribute:
                    relevant_rules.append(rule)
                    break

        if not relevant_rules:
            return f"O atributo '{attribute}' é necessário para a avaliação diagnóstica."

        hypothesis_names = []
        for rule in relevant_rules[:3]:
            conclusion_val = rule["conclusion"]["value"]
            hyp = self.hypotheses.get(conclusion_val)
            if hyp:
                hypothesis_names.append(hyp["name"])
            else:
                hypothesis_names.append(conclusion_val)

        unique_hyps = list(dict.fromkeys(hypothesis_names))
        hyps_str = ", ".join(unique_hyps[:3])
        return (
            f"Estou investigando as hipóteses: {hyps_str}. "
            f"A presença ou ausência de '{attribute}' é uma condição necessária "
            f"para avaliar essas hipóteses."
        )

    def explain_how(self, conclusion_attribute: str, conclusion_value: str) -> dict:
        """
        Responde COMO determinada conclusão foi obtida.
        """
        supporting_rules = [
            r for r in self.fired_rules
            if r["conclusion"]["attribute"] == conclusion_attribute
            and r["conclusion"]["value"] == conclusion_value
        ]

        if not supporting_rules:
            return {
                "conclusion": f"{conclusion_attribute} = {conclusion_value}",
                "rules_used": [],
                "explanation": "Esta conclusão não foi atingida pelo motor de inferência na sessão atual.",
            }

        rules_info = []
        for rule in supporting_rules:
            conditions_text = " E ".join(
                [f"{c['attribute']} = {c['value']}" for c in rule["conditions"]]
            )
            rules_info.append({
                "rule_id": rule["id"],
                "rule_name": rule["name"],
                "conditions": rule["conditions"],
                "conditions_text": conditions_text,
                "explanation": rule.get("explanation", ""),
                "treatment": rule.get("treatment", ""),
            })

        hyp = self.hypotheses.get(conclusion_value)
        hyp_name = hyp["name"] if hyp else conclusion_value

        return {
            "conclusion": f"{hyp_name}",
            "conclusion_raw": f"{conclusion_attribute} = {conclusion_value}",
            "rules_used": rules_info,
            "explanation": (
                f"A conclusão '{hyp_name}' foi obtida porque "
                + " e ".join([f"a regra {r['rule_id']} ({r['rule_name']}) foi ativada" for r in rules_info])
                + " a partir dos fatos informados durante a consulta."
            ),
        }

    # ------------------------------------------------------------------
    # Construção do resultado final
    # ------------------------------------------------------------------

    def _build_result(self) -> dict:
        diagnoses = []
        confirmations = []

        # Parse suspeitas (podem ser múltiplas, separadas por vírgula)
        suspeita_vals = self.working_memory.get("suspeita", "")
        for val in (suspeita_vals.split(",") if suspeita_vals else []):
            val = val.strip()
            if not val:
                continue
            hyp = self.hypotheses.get(val)
            if hyp:
                how = self.explain_how("suspeita", val)
                diagnoses.append({
                    "type": "suspeita",
                    "id": val,
                    "name": hyp["name"],
                    "description": hyp["description"],
                    "how": how,
                    "treatment": self._get_treatment_for(val),
                })

        confirmacao_vals = self.working_memory.get("confirmacao", "")
        for val in (confirmacao_vals.split(",") if confirmacao_vals else []):
            val = val.strip()
            if not val:
                continue
            hyp = self.hypotheses.get(val)
            if hyp:
                how = self.explain_how("confirmacao", val)
                confirmations.append({
                    "type": "confirmacao",
                    "id": val,
                    "name": hyp["name"],
                    "description": hyp["description"],
                    "how": how,
                    "treatment": self._get_treatment_for(val),
                })

        # Unificar suspeitas e confirmações
        all_diagnoses = confirmations + diagnoses

        # Agrupar por hipótese base (removendo sufixos de gravidade/subtipo)
        grouped: dict[str, dict] = {}
        for d in all_diagnoses:
            base_id = d["id"].replace("_grave", "").replace("_avancada", "").replace("_bacteriana", "").replace("_viral", "").replace("_atipica", "")
            if base_id not in grouped:
                grouped[base_id] = d
            # Preferir confirmação sobre suspeita
            elif d["type"] == "confirmacao" and grouped[base_id]["type"] == "suspeita":
                grouped[base_id] = d
            # Preferir grave/avancada sobre base se já é confirmação
            elif d["type"] == grouped[base_id]["type"] and "grave" in d["id"]:
                grouped[base_id] = d

        return {
            "diagnoses": list(grouped.values()),
            "fired_rules": [
                {
                    "id": r["id"],
                    "name": r["name"],
                    "explanation": r.get("explanation", ""),
                }
                for r in self.fired_rules
            ],
            "working_memory": dict(self.working_memory),
            "inference_trace": self.inference_trace,
        }

    def _get_treatment_for(self, diagnosis_id: str) -> str:
        for rule in self.fired_rules:
            if rule["conclusion"]["value"] == diagnosis_id:
                return rule.get("treatment", "Consulte um médico para avaliação.")
        # Fallback para suspeita base
        base_id = diagnosis_id.split("_")[0]
        for rule in self.fired_rules:
            if rule["conclusion"]["value"].startswith(base_id):
                return rule.get("treatment", "Consulte um médico para avaliação.")
        return "Consulte um médico para avaliação e tratamento adequado."

    # ------------------------------------------------------------------
    # API de alto nível para a sessão de consulta
    # ------------------------------------------------------------------

    def run_session_step(self, attribute: str = None, value: str = None) -> dict:
        """
        Processa um passo da sessão de consulta:
        - Se (attribute, value) fornecidos, registra o fato e executa inferência.
        - Retorna a próxima pergunta ou o resultado final.
        """
        if attribute and value:
            self.add_fact(attribute, value)

        # Executar forward chaining com fatos atuais
        self.forward_chain()

        # Verificar se já temos diagnóstico suficiente
        result = self._build_result()
        if result["diagnoses"]:
            # Tentar confirmar com backward chaining
            for d in result["diagnoses"]:
                self.backward_chain("confirmacao", d["id"])
            self.forward_chain()
            result = self._build_result()

        # Próxima pergunta
        next_q = self.get_next_question()

        return {
            "next_question": next_q,
            "current_result": result,
            "has_diagnosis": len(result["diagnoses"]) > 0,
            "working_memory": dict(self.working_memory),
        }

    def get_all_attributes(self) -> list[str]:
        attrs = set()
        for rule in self.rules:
            for cond in rule["conditions"]:
                attrs.add(cond["attribute"])
        return sorted(attrs)

    def get_attributes_for_hypothesis(self, hypothesis_id: str) -> list[str]:
        attrs = []
        for rule in self.rules:
            if rule["conclusion"]["value"] == hypothesis_id:
                for cond in rule["conditions"]:
                    if cond["attribute"] not in attrs:
                        attrs.append(cond["attribute"])
        return attrs
