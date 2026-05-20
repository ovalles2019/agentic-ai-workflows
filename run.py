#!/usr/bin/env python3
"""Interactive runner for all agentic workflow examples."""

from __future__ import annotations

import argparse
import sys

EXAMPLES = {
    "1": ("langchain", "examples.01_langchain_single_agent", "Single agent (LangChain ReAct)"),
    "2": ("langgraph", "examples.02_langgraph_multi_agent", "Multi-agent graph (LangGraph)"),
    "3": ("crewai", "examples.03_crewai_multi_agent", "Role-based crew (CrewAI)"),
    "4": ("autogen", "examples.04_autogen_multi_agent", "Conversational team (AutoGen)"),
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run agentic AI workflow demos")
    parser.add_argument(
        "example",
        nargs="?",
        choices=["all", "langchain", "langgraph", "crewai", "autogen", "1", "2", "3", "4"],
        help="Which example to run (default: menu)",
    )
    parser.add_argument("--topic", help="Override RESEARCH_TOPIC")
    args = parser.parse_args()

    if not args.example:
        print("\nAgentic AI Workflow Demos\n")
        for key, (_, _, label) in EXAMPLES.items():
            print(f"  {key}. {label}")
        print("  all. Run every example")
        choice = input("\nSelect [1-4 or all]: ").strip().lower() or "1"
    else:
        choice = args.example.lower()

    to_run: list[str]
    if choice == "all":
        to_run = ["1", "2", "3", "4"]
    elif choice in EXAMPLES:
        to_run = [choice]
    else:
        alias = {name: key for key, (name, _, _) in EXAMPLES.items()}
        to_run = [alias[choice]]

    for key in to_run:
        _, module_name, label = EXAMPLES[key]
        print(f"\n{'=' * 60}\nRunning: {label}\n{'=' * 60}")
        module = __import__(module_name, fromlist=["run"])
        module.run(topic=args.topic)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
