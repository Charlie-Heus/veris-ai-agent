from typing import Callable, List
from dataclasses import dataclass



# -------------------
# Tool Definition
# -------------------

@dataclass
class Tool:
    name: str
    func: Callable[[str], str]



# -------------------
# Prompt Builder
# -------------------

def build_prompt(question: str, context: str, iteration: int, max_iterations: int) -> str:
    return f"""
                You are a financial analysis AI.

                QUESTION: {question}
                ITERATION: {iteration}/{max_iterations}
                CONTEXT SO FAR: {context}

                Available tools:
                - SEC_SEARCH: Search SEC filings
                - WEB_SEARCH: Search the web
                - CALCULATOR: Perform financial calculations

                What should you do next? Choose ONE:
                A) USE_TOOL: [tool_name] with [parameters]
                B) SYNTHESIZE: Create final answer
                C) NEED_MORE: Explain what additional info is needed

                Respond with your decision and reasoning.
            """



# -------------------
# Response Parser
# -------------------

def parse_decision(response: str):
    if "USE_TOOL" in response:
        return "USE_TOOL", response.split("USE_TOOL:")[1].strip()
    elif "SYNTHESIZE" in response:
        return "SYNTHESIZE", response.split("SYNTHESIZE:")[1].strip()
    elif "NEED_MORE" in response:
        return "NEED_MORE", ""
    else:
        return "UNKNOWN", response



# -------------------
# Agent Runner
# -------------------

def run_agent(question: str, context: str, llm, tools: List[Tool], max_iterations: int = 5):
    tool_results = ""
    for i in range(1, max_iterations + 1):
        prompt = build_prompt(question, tool_results or context, i, max_iterations)
        response = llm.invoke(prompt)
        print(f"\n[Iteration {i}] LLM Response:\n{response}\n")

        decision_type, detail = parse_decision(response)

        if decision_type == "USE_TOOL":
            try:
                tool_name, tool_input = detail.split("with", 1)
                tool_name = tool_name.strip()
                tool_input = tool_input.strip()
                tool = next(t for t in tools if t.name == tool_name)
                result = tool.func(tool_input)
                tool_results += f"\n[{tool_name} used] {result}"
            except Exception as e:
                tool_results += f"\n[ERROR] Failed to use tool: {e}"
        elif decision_type == "SYNTHESIZE":
            return detail.strip()
        elif decision_type == "NEED_MORE":
            tool_results += "\n[Agent] Requested more info. Skipping."
        else:
            tool_results += "\n[ERROR] Could not parse decision."

    return "Agent failed to synthesize a final answer in time."