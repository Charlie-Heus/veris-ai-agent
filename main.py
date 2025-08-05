from agent import run_agent, Tool
from tools.sec_search import sec_search_tool
from tools.web_search import web_search_tool
from tools.calculator import calculator_tool
from llm.minstral_ollama import get_llm
import json
from pathlib import Path


# -------------------
# Example Usage
# -------------------

if __name__ == "__main__":

    llm = get_llm()

    tools = [
        Tool(name="SEC_SEARCH", func=sec_search_tool),
        Tool(name="WEB_SEARCH", func=web_search_tool),
        Tool(name="CALCULATOR", func=calculator_tool),
    ]

    # Load the dataset
    data_path = Path("data/financeqa_test.jsonl")
    
    if not data_path.exists():
        print("Error: Dataset not found. Please run: python scripts/download_financeqa.py")
        exit()
    
    # Load the dataset
    data = []
    with open(data_path, 'r') as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    
    print(f"Dataset loaded: {len(data)} questions available")
    
    # 👇 Ask the user for a question number
    question_number = input("\nSelect a question by number from the list (1-148): ")
    
    try:
        question_number = int(question_number)
        
        if question_number < 1 or question_number > len(data):
            print(f"Error: Please enter a number between 1 and {len(data)}")
            exit()
        
        # Get the selected question (convert to 0-based index)
        question_index = question_number - 1
        question_data = data[question_index]
        
        # Display the selected question
        print(f"\n{'='*60}")
        print(f"SELECTED QUESTION #{question_number}")
        print(f"{'='*60}")
        
        print(f"Question Type: {question_data.get('question_type', 'N/A')}")
        print(f"Company: {question_data.get('company', 'N/A')}")
        print(f"File: {question_data.get('file_name', 'N/A')}")
        
        print(f"\nQUESTION:")
        print(question_data.get('question', 'N/A'))
        
        print(f"\nCONTEXT:")
        context = question_data.get('context', 'No context available')
        print(context)
        
        print(f"\nCHAIN OF THOUGHT:")
        chain_of_thought = question_data.get('chain_of_thought', 'No reasoning provided')
        print(chain_of_thought)
        
        print(f"\nEXPECTED ANSWER:")
        print(question_data.get('answer', 'No answer provided'))
        
        print(f"\n{'='*60}")
        
        # Extract the question text for the agent
        question = question_data.get('question', '')
        context = question_data.get('context', '')
        
        print(f"\nRunning AI Agent on this question...")
        
    except ValueError:
        print("Error: Please enter a valid number")
        exit()
    except Exception as e:
        print(f"Error: {e}")
        exit()

    exit()
    answer = run_agent(question, context, llm, tools)
    print("\nFinal Answer:", answer)