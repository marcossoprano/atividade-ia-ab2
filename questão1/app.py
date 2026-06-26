"""
Sistema Especialista em Diagnóstico Médico - Flask App
Integração com DeepSeek LLM para chat interativo
"""

import os
import json
import uuid
from flask import Flask, render_template, request, jsonify, session
from questão1.inference_engine import InferenceEngine

# ---------------------------------------------------------------------------
# DeepSeek LLM client (OpenAI-compatible)
# ---------------------------------------------------------------------------

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


def get_deepseek_client():
    api_key = os.environ.get("sk-9ee97c68205e414f99a1b59acde4e176")
    if not api_key:
        return None
    if not HAS_OPENAI:
        return None
    return openai.OpenAI(api_key=api_key, base_url="https://api.deepseek.com")


def deepseek_chat(messages: list[dict], system_prompt: str = "") -> str:
    client = get_deepseek_client()
    if not client:
        return None

    full_messages = []
    if system_prompt:
        full_messages.append({"role": "system", "content": system_prompt})
    full_messages.extend(messages)

    try:
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=full_messages,
            temperature=0.7,
            max_tokens=1024,
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"[Erro na comunicação com DeepSeek: {str(e)}]"


# ---------------------------------------------------------------------------
# Flask app
# ---------------------------------------------------------------------------

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")
app.config["SESSION_TYPE"] = "filesystem"

# Armazenamento em memória para sessões de inferência
_sessions: dict[str, InferenceEngine] = {}

SYSTEM_PROMPT = (
    "Você é um assistente médico virtual chamado Dr. IA, integrado a um Sistema Especialista "
    "baseado em regras para diagnóstico médico. Você deve ser empático, claro e sempre lembrar "
    "que suas recomendações são informativas e não substituem consulta médica. "
    "Responda em português do Brasil. Seja conciso e didático."
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_or_create_engine(session_id: str) -> InferenceEngine:
    if session_id not in _sessions:
        engine = InferenceEngine()
        _sessions[session_id] = engine
    return _sessions[session_id]


def _build_context_for_llm(engine: InferenceEngine) -> str:
    result = engine._build_result()
    wm = engine.working_memory
    lines = []
    lines.append("=== FATOS CONHECIDOS ===")
    for attr, val in wm.items():
        lines.append(f"- {attr}: {val}")
    lines.append("")
    if result["diagnoses"]:
        lines.append("=== DIAGNÓSTICOS ATUAIS ===")
        for d in result["diagnoses"]:
            lines.append(f"- {d['name']} ({d['type']})")
            lines.append(f"  Tratamento: {d.get('treatment', '')}")
    else:
        lines.append("=== NENHUM DIAGNÓSTICO AINDA ===")
    lines.append("")
    lines.append("=== REGRAS DISPARADAS ===")
    for r in engine.fired_rules:
        lines.append(f"- {r['id']}: {r['name']}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Rotas
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/session/new", methods=["POST"])
def new_session():
    session_id = str(uuid.uuid4())
    engine = _get_or_create_engine(session_id)
    engine.reset()
    # Executar primeiro passo para obter a primeira pergunta
    step = engine.run_session_step()
    return jsonify({"session_id": session_id, **step})


@app.route("/api/session/<session_id>/answer", methods=["POST"])
def answer(session_id):
    engine = _get_or_create_engine(session_id)
    data = request.get_json() or {}
    attribute = data.get("attribute")
    value = data.get("value")

    if not attribute or not value:
        return jsonify({"error": "attribute e value são obrigatórios"}), 400

    step = engine.run_session_step(attribute, value)
    return jsonify(step)


@app.route("/api/session/<session_id>/explain/why", methods=["GET"])
def explain_why(session_id):
    engine = _get_or_create_engine(session_id)
    attribute = request.args.get("attribute")
    if not attribute:
        return jsonify({"error": "attribute é obrigatório"}), 400
    explanation = engine._explain_why(attribute)
    return jsonify({"attribute": attribute, "explanation": explanation})


@app.route("/api/session/<session_id>/explain/how", methods=["GET"])
def explain_how(session_id):
    engine = _get_or_create_engine(session_id)
    attribute = request.args.get("attribute", "suspeita")
    value = request.args.get("value")
    if not value:
        return jsonify({"error": "value é obrigatório"}), 400
    result = engine.explain_how(attribute, value)
    return jsonify(result)


@app.route("/api/session/<session_id>/result", methods=["GET"])
def get_result(session_id):
    engine = _get_or_create_engine(session_id)
    result = engine._build_result()
    return jsonify(result)


@app.route("/api/session/<session_id>/reset", methods=["POST"])
def reset_session(session_id):
    engine = _get_or_create_engine(session_id)
    engine.reset()
    step = engine.run_session_step()
    return jsonify(step)


@app.route("/api/session/<session_id>/chat", methods=["POST"])
def chat(session_id):
    engine = _get_or_create_engine(session_id)
    data = request.get_json() or {}
    user_message = data.get("message", "").strip()
    if not user_message:
        return jsonify({"error": "message é obrigatório"}), 400

    # Contexto do sistema especialista para o LLM
    context = _build_context_for_llm(engine)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Contexto do sistema especialista:\n{context}\n\nPergunta do usuário: {user_message}"},
    ]

    llm_response = deepseek_chat(messages)
    if llm_response is None:
        # Fallback: resposta do próprio sistema especialista
        fallback = _fallback_response(user_message, engine)
        return jsonify({"response": fallback, "source": "fallback"})

    return jsonify({"response": llm_response, "source": "deepseek"})


def _fallback_response(user_message: str, engine: InferenceEngine) -> str:
    msg_lower = user_message.lower()
    result = engine._build_result()

    if "diagnóstico" in msg_lower or "diagnostico" in msg_lower:
        if result["diagnoses"]:
            names = ", ".join([d["name"] for d in result["diagnoses"]])
            return f"Com base nos sintomas informados, as hipóteses diagnósticas são: {names}. Lembre-se: isso não substitui uma consulta médica."
        return "Ainda não temos informações suficientes para um diagnóstico. Por favor, continue respondendo às perguntas."

    if "tratamento" in msg_lower or "tratar" in msg_lower:
        if result["diagnoses"]:
            treatments = [d.get("treatment", "") for d in result["diagnoses"]]
            return f"Tratamento sugerido: {'; '.join(treatments)}. Consulte um médico para prescrição adequada."
        return "Precisamos de mais informações para sugerir um tratamento."

    if "por que" in msg_lower or "porque" in msg_lower:
        return "Estou fazendo perguntas para avaliar hipóteses diagnósticas baseadas em regras médicas. Cada resposta ajuda a confirmar ou descartar possíveis doenças."

    if "como" in msg_lower:
        return "O diagnóstico é obtido através de encadeamento de regras (forward e backward chaining) sobre uma base de conhecimento com mais de 80 regras e 20 doenças."

    return "Sou o Dr. IA, assistente integrado ao Sistema Especialista. Estou aqui para ajudar. Pode me perguntar sobre o diagnóstico, tratamento ou o funcionamento do sistema."


@app.route("/api/kb/rules", methods=["GET"])
def list_rules():
    with open("knowledge_base.json", "r", encoding="utf-8") as f:
        kb = json.load(f)
    return jsonify({"count": len(kb["rules"]), "rules": kb["rules"]})


@app.route("/api/kb/hypotheses", methods=["GET"])
def list_hypotheses():
    with open("knowledge_base.json", "r", encoding="utf-8") as f:
        kb = json.load(f)
    return jsonify({"count": len(kb["hypotheses"]), "hypotheses": kb["hypotheses"]})


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
