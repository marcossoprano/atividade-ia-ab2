#!/usr/bin/env python3
"""Interface CLI do AgenteMed."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from agente_med.agent import AgenteMed
    from agente_med.inference import bayesian_inference, cbr_search, forward_chaining
else:
    from .agent import AgenteMed
    from .inference import bayesian_inference, cbr_search, forward_chaining


DEMO_INPUTS = [
    "Tenho febre, tosse e falta de ar ha tres dias.",
    "Estou com febre alta, manchas na pele e dor muscular.",
    "Sinto dor no peito e falta de ar quando caminho.",
]


def main() -> None:
    parser = argparse.ArgumentParser(description="AgenteMed - Questão 3")
    parser.add_argument("--demo", action="store_true", help="executa uma demonstração guiada")
    parser.add_argument(
        "--provider",
        choices=["local", "ollama", "openai", "anthropic"],
        help="provedor LLM",
    )
    parser.add_argument("--kb", help="caminho alternativo para knowledge_base.json")
    args = parser.parse_args()

    agent = AgenteMed(kb_path=args.kb, provider=args.provider)

    if args.demo:
        run_demo(agent)
        return

    run_chat(agent)


def run_demo(agent: AgenteMed) -> None:
    print_header(agent)
    print("Modo demonstração\n")
    for sample in DEMO_INPUTS:
        print(f"> Usuário: {sample}")
        answer, _ = agent.respond(sample)
        print(answer)
        print("\n" + "-" * 72 + "\n")


def run_chat(agent: AgenteMed) -> None:
    print_header(agent)
    print("Digite /ajuda para comandos ou /sair para encerrar.\n")

    while True:
        try:
            user_text = input("Você: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nEncerrando.")
            return

        if not user_text:
            continue
        if user_text in {"/sair", "sair", "exit", "quit"}:
            print("Encerrando.")
            return
        if user_text.startswith("/"):
            handle_command(agent, user_text)
            continue

        answer, _ = agent.respond(user_text)
        print("\nAgenteMed:")
        print(answer)
        print()


def handle_command(agent: AgenteMed, command: str) -> None:
    parts = command.split()
    name = parts[0].lower()
    args = parts[1:]

    if name == "/ajuda":
        print(COMMAND_HELP)
    elif name == "/regras":
        for rule in agent.kb["rules"]:
            print(
                f"{rule['id']}: SE {', '.join(rule['conditions'])} "
                f"ENTAO {rule['conclusion']} ({int(rule['confidence'] * 100)}%)"
            )
    elif name == "/hipoteses":
        for hypothesis in agent.kb["hypotheses"]:
            print(f"{hypothesis['id']} - {hypothesis['name']}: {hypothesis['description']}")
    elif name == "/casos":
        for case in agent.kb["cases"]:
            print(f"{case['id']} - {case['diagnosis']}: {', '.join(case['symptoms'])}")
    elif name == "/bayes":
        show_bayes(agent, args)
    elif name == "/cbr":
        show_cbr(agent, args)
    elif name == "/forward":
        show_forward(agent, args)
    else:
        print("Comando não reconhecido. Digite /ajuda.")
    print()


def show_bayes(agent: AgenteMed, symptoms: list[str]) -> None:
    if not symptoms:
        print("Uso: /bayes febre tosse falta_ar")
        return
    for item in bayesian_inference(symptoms, agent.kb):
        print(f"{item['disease']}: {item['probability'] * 100:.1f}%")


def show_cbr(agent: AgenteMed, symptoms: list[str]) -> None:
    if not symptoms:
        print("Uso: /cbr febre tosse falta_ar")
        return
    for case in cbr_search(symptoms, agent.kb):
        print(f"{case['id']} - {case['diagnosis']}: {case['similarity'] * 100:.1f}%")


def show_forward(agent: AgenteMed, facts: list[str]) -> None:
    if not facts:
        print("Uso: /forward febre tosse falta_ar")
        return
    _, trace = forward_chaining(facts, agent.kb)
    if not trace:
        print("Nenhuma regra disparada.")
        return
    for item in trace:
        print(f"{item['rule']} -> {item['conclusion']} ({int(item['confidence'] * 100)}%)")


def print_header(agent: AgenteMed) -> None:
    provider = getattr(agent.llm_client, "provider", "local")
    print("=" * 72)
    print("AgenteMed - Questão 3 | Agente baseado em LLM")
    print(f"Base: {agent.kb['metadata']['name']} | Provedor: {provider}")
    print("=" * 72)


COMMAND_HELP = """Comandos:
  /regras                         Lista regras SE-ENTAO
  /hipoteses                      Lista hipóteses do sistema
  /casos                          Lista casos CBR
  /bayes febre tosse              Executa Bayes diretamente
  /cbr febre tosse falta_ar       Busca casos similares
  /forward febre tosse falta_ar   Executa encadeamento para frente
  /sair                           Encerra"""


if __name__ == "__main__":
    main()
