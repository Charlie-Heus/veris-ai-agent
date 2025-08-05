from typing import Callable, List
from dataclasses import dataclass
from tools.rag import rag_extract_information
from tools.calculator import perform_financial_calculation, extract_numerical_values, format_financial_result
import json
from datetime import datetime
from pathlib import Path


# -------------------
# Logging System
# -------------------

class AgentLogger:
    def __init__(self, log_file: str = "logs/agent_execution.txt"):
        self.log_file = log_file
        self.execution_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.step_logs = []
        
        # Ensure logs directory exists
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        
        # Clear the log file at initialization (overwrite previous logs)
        self._clear_log_file()
    
    def _clear_log_file(self):
        """Clear the log file to start fresh."""
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write(f"NEW EXECUTION STARTED: {self.execution_id}\n")
                f.write(f"TIMESTAMP: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*80 + "\n\n")
        except Exception as e:
            print(f"Warning: Could not clear log file: {e}")
    
    def log_function_call(self, function_name: str, input_data: dict, return_data: dict, step_number: int = None):
        """Log a function call with input data and return values."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        log_entry = f"""
{'='*80}
FUNCTION CALL: {function_name}
TIMESTAMP: {timestamp}
STEP NUMBER: {step_number if step_number is not None else 'N/A'}
{'='*80}

INPUT DATA:
{json.dumps(input_data, indent=2)}

RETURN DATA:
{json.dumps(return_data, indent=2)}

{'='*80}
"""
        
        self.step_logs.append({
            "function_name": function_name,
            "timestamp": timestamp,
            "step_number": step_number,
            "input_data": input_data,
            "return_data": return_data
        })
        
        # Write to log file immediately
        self._write_to_file(log_entry)
    
    def log_decision(self, step_number: int, decision: str, reasoning: str):
        """Log a decision point in the process."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        decision_log = f"""
{'='*80}
DECISION POINT
TIMESTAMP: {timestamp}
STEP NUMBER: {step_number}
{'='*80}

DECISION: {decision}
REASONING: {reasoning}

{'='*80}
"""
        
        self.step_logs.append({
            "type": "DECISION",
            "timestamp": timestamp,
            "step_number": step_number,
            "decision": decision,
            "reasoning": reasoning
        })
        
        self._write_to_file(decision_log)
    
    def log_error(self, step_number: int, function_name: str, error_message: str, error_details: str = ""):
        """Log an error that occurred during execution."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        error_log = f"""
{'='*80}
ERROR
TIMESTAMP: {timestamp}
STEP NUMBER: {step_number}
FUNCTION: {function_name}
{'='*80}

ERROR MESSAGE: {error_message}
ERROR DETAILS: {error_details}

{'='*80}
"""
        
        self.step_logs.append({
            "type": "ERROR",
            "timestamp": timestamp,
            "step_number": step_number,
            "function_name": function_name,
            "error_message": error_message,
            "error_details": error_details
        })
        
        self._write_to_file(error_log)
    
    def log_execution_start(self, question: str, context_length: int):
        """Log the start of execution."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        start_log = f"""
{'='*80}
EXECUTION START
TIMESTAMP: {timestamp}
EXECUTION ID: {self.execution_id}
{'='*80}

QUESTION: {question}
CONTEXT LENGTH: {context_length} characters

{'='*80}
"""
        
        self.step_logs.append({
            "type": "EXECUTION_START",
            "timestamp": timestamp,
            "execution_id": self.execution_id,
            "question": question,
            "context_length": context_length
        })
        
        self._write_to_file(start_log)
    
    def log_execution_end(self, final_answer: str):
        """Log the end of execution."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        end_log = f"""
{'='*80}
EXECUTION END
TIMESTAMP: {timestamp}
EXECUTION ID: {self.execution_id}
{'='*80}

FINAL ANSWER: {final_answer}

{'='*80}
"""
        
        self.step_logs.append({
            "type": "EXECUTION_END",
            "timestamp": timestamp,
            "execution_id": self.execution_id,
            "final_answer": final_answer
        })
        
        self._write_to_file(end_log)
    
    def _write_to_file(self, log_entry: str):
        """Write a log entry to the log file."""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Warning: Could not write to log file: {e}")
    
    def get_execution_summary(self) -> dict:
        """Get a summary of the entire execution."""
        return {
            "execution_id": self.execution_id,
            "total_steps": len(self.step_logs),
            "steps": self.step_logs,
            "timestamp": datetime.now().isoformat()
        }
    
    def write_summary(self, summary_file: str = None):
        """Write a human-readable summary to a file."""
        if summary_file is None:
            summary_file = f"logs/execution_summary_{self.execution_id}.txt"
        
        summary = self.get_execution_summary()
        
        summary_text = f"""
{'='*80}
EXECUTION SUMMARY
{'='*80}

EXECUTION ID: {summary['execution_id']}
TOTAL STEPS: {summary['total_steps']}
TIMESTAMP: {summary['timestamp']}

STEP BREAKDOWN:
"""
        
        for i, step in enumerate(summary['steps']):
            if step.get('type') == 'EXECUTION_START':
                summary_text += f"\n{i+1}. EXECUTION START"
                summary_text += f"\n   Question: {step.get('question', 'N/A')}"
            elif step.get('type') == 'EXECUTION_END':
                summary_text += f"\n{i+1}. EXECUTION END"
                summary_text += f"\n   Final Answer: {step.get('final_answer', 'N/A')}"
            elif step.get('type') == 'DECISION':
                summary_text += f"\n{i+1}. DECISION (Step {step.get('step_number', 'N/A')})"
                summary_text += f"\n   Decision: {step.get('decision', 'N/A')}"
                summary_text += f"\n   Reasoning: {step.get('reasoning', 'N/A')}"
            elif step.get('type') == 'ERROR':
                summary_text += f"\n{i+1}. ERROR (Step {step.get('step_number', 'N/A')})"
                summary_text += f"\n   Function: {step.get('function_name', 'N/A')}"
                summary_text += f"\n   Error: {step.get('error_message', 'N/A')}"
            else:
                summary_text += f"\n{i+1}. {step.get('function_name', 'FUNCTION')} (Step {step.get('step_number', 'N/A')})"
        
        summary_text += f"\n\n{'='*80}"
        
        try:
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(summary_text)
            print(f"📋 Execution summary written to: {summary_file}")
        except Exception as e:
            print(f"Warning: Could not write summary file: {e}")


# Global logger instance
logger = AgentLogger()


# --------------------
#     Tool Definition
# --------------------

@dataclass
class Tool:
    name: str
    func: Callable[[str], str]



# -------------------
#     Prompt Builder
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



# --------------------
#     Response Parser
# --------------------

def parse_decision(response: str):
    if "USE_TOOL" in response:
        return "USE_TOOL", response.split("USE_TOOL:")[1].strip()
    elif "SYNTHESIZE" in response:
        return "SYNTHESIZE", response.split("SYNTHESIZE:")[1].strip()
    elif "NEED_MORE" in response:
        return "NEED_MORE", ""
    else:
        return "UNKNOWN", response



# --------------------
#     Basic/Assumption Flow Steps
# --------------------

def step1_formula_analysis(question: str, llm) -> dict:
    """Step 1: Get formula, key terms, and synonyms from LLM."""
    print(f"\n🔍 Step 1: Getting formula and deriving key terms...")
    
    formula_prompt = f"""
    You are a financial analysis expert. Given this question:
    
    QUESTION: {question}
    
    Please provide:
    1. The FORMULA required to calculate the answer
    2. The KEY TERMS needed from the formula (e.g., "revenue", "cost of goods sold")
    3. SYNONYMS for each key term (e.g., "revenue" → ["total revenue", "net sales", "sales"])
    
    Respond in this exact format:
    FORMULA: [the mathematical formula]
    KEY_TERMS: [term1, term2, term3, ...]
    SYNONYMS: {{"term1": ["synonym1", "synonym2"], "term2": ["synonym1", "synonym2"], ...}}
    """
    
    formula_response = llm.invoke(formula_prompt)
    print(f"📋 Formula Analysis:\n{formula_response}\n")
    
    # Parse the response to extract formula, key terms, and synonyms
    formula = ""
    key_terms = []
    synonyms = {}
    
    lines = formula_response.split('\n')
    for line in lines:
        line_stripped = line.strip()
        if line_stripped.startswith('FORMULA:'):
            formula = line_stripped.replace('FORMULA:', '').strip()
        elif line_stripped.startswith('KEY_TERMS:'):
            terms_str = line_stripped.replace('KEY_TERMS:', '').strip()
            key_terms = [term.strip() for term in terms_str.strip('[]').split(',')]
        elif line_stripped.startswith('SYNONYMS:'):
            # Try to parse the LLM's synonym response
            synonyms_str = line_stripped.replace('SYNONYMS:', '').strip()
            
            # If this line doesn't contain the full JSON, look for the complete JSON structure
            if not synonyms_str.startswith('{'):
                # Find the complete JSON structure in the response
                synonyms_start = formula_response.find('SYNONYMS:')
                if synonyms_start != -1:
                    synonyms_section = formula_response[synonyms_start:]
                    # Find the opening brace
                    brace_start = synonyms_section.find('{')
                    if brace_start != -1:
                        # Find the matching closing brace
                        brace_count = 0
                        brace_end = -1
                        for i, char in enumerate(synonyms_section[brace_start:], brace_start):
                            if char == '{':
                                brace_count += 1
                            elif char == '}':
                                brace_count -= 1
                                if brace_count == 0:
                                    brace_end = i + 1
                                    break
                        
                        if brace_end != -1:
                            synonyms_str = synonyms_section[brace_start:brace_end]
            
            try:
                # Try to parse as JSON
                import json
                synonyms = json.loads(synonyms_str)
            except:
                # If parsing fails, create synonyms based on key terms
                synonyms = {}
                for term in key_terms:
                    term_lower = term.lower()
                    if "revenue" in term_lower:
                        synonyms[term] = ["total revenue", "net sales", "sales", "revenue", "income"]
                    elif "cost" in term_lower and "goods" in term_lower:
                        synonyms[term] = ["cost of goods sold", "cogs", "merchandise costs", "cost of sales"]
                    elif "gross" in term_lower and "profit" in term_lower:
                        synonyms[term] = ["gross profit", "gross margin dollars", "gross income"]
                    elif "operating" in term_lower and "income" in term_lower:
                        synonyms[term] = ["operating income", "operating profit", "ebit"]
                    elif "net" in term_lower and "income" in term_lower:
                        synonyms[term] = ["net income", "net profit", "earnings", "net earnings"]
                    elif "ebitda" in term_lower:
                        synonyms[term] = ["ebitda", "earnings before interest taxes depreciation amortization"]
                    elif "depreciation" in term_lower:
                        synonyms[term] = ["depreciation", "depreciation and amortization", "d&a"]
                    else:
                        # Default: just use the term itself
                        synonyms[term] = [term.lower()]
    
    print(f"🎯 Formula: {formula}")
    print(f"🎯 Key Terms: {key_terms}")
    print(f"🎯 Synonyms: {synonyms}")
    
    return {
        "formula": formula,
        "key_terms": key_terms,
        "synonyms": synonyms,
        "llm_response": formula_response
    }


def step2_initial_rag_search(key_terms: list, synonyms: dict, context: str) -> dict:
    """Step 2: Search for key terms in context."""
    print(f"\n🔍 Step 2: Searching for key terms in context...")
    
    # Create a comprehensive search query from key terms and synonyms
    all_search_terms = []
    for term in key_terms:
        if term in synonyms:
            all_search_terms.extend(synonyms[term])
        else:
            all_search_terms.append(term)
    
    print(f"🔍 Searching for terms: {all_search_terms}")
    
    # Simple direct search for terms in context
    extracted_info = {}
    context_lower = context.lower()
    
    for term in all_search_terms:
        term_lower = term.lower()
        if term_lower in context_lower:
            # Find the position of the term
            pos = context_lower.find(term_lower)
            
            # Extract surrounding text (approximately 300 characters before and after)
            start = max(0, pos - 300)
            end = min(len(context), pos + len(term) + 300)
            
            # Try to find sentence boundaries
            start = context.rfind('.', start, pos) + 1 if context.rfind('.', start, pos) > start - 100 else start
            end = context.find('.', pos) + 1 if context.find('.', pos) < end + 100 else end
            
            relevant_text = context[start:end].strip()
            if relevant_text:
                extracted_info[term] = relevant_text
                print(f"✅ Found '{term}': {relevant_text[:100]}...")
    
    if extracted_info:
        print(f"\n📊 Extracted Information:")
        for term, text in extracted_info.items():
            print(f"  • {term}: {text}")
        
        # Convert dictionary to a single string
        extracted_text = "\n\n".join([f"{term}: {text}" for term, text in extracted_info.items()])
    else:
        print(f"\n❌ No relevant information found for any of the search terms")
        extracted_text = ""
    
    return extracted_text


def step3_attempt_answer(question: str, formula: str, extracted_info: str, llm) -> dict:
    """Step 3: Attempt to answer with extracted information."""
    print(f"\n🔍 Step 3: Attempting answer with extracted information...")
    
    # Prepare the extracted information for the LLM
    extracted_text = extracted_info if extracted_info else ""
    
    attempt_answer_prompt = f"""
    You are a financial analyst. Answer this question using ONLY the information provided below.
    
    QUESTION: {question}
    FORMULA: {formula}
    
    EXTRACTED INFORMATION:
    {extracted_text}
    
    Your task is to replace the variables in the formula with the correct numerical values from the extracted information.
    
    CRITICAL: You MUST use the exact formula provided above. Do not change the formula or calculate something different.
    
    If you have ALL necessary information to substitute values into the formula:
    - Replace each variable in the formula with its corresponding numerical value
    - Provide the substituted formula with actual numbers
    - Respond with: "CALCULATION_READY: [substituted formula with numerical values]"
    - Then add: "RESULT_EXPLANATION: [explanation of what values you found and how you substituted them into the formula]"
    
    IMPORTANT: Focus on substituting values, not calculating the final result. For example:
    - If formula is "Gross Profit = 254,453 - 222,358 - pre tax income"
    - And you find "INCOME BEFORE INCOME TAXES 9,740"
    - Then substitute: "CALCULATION_READY: Gross Profit = 254,453 - 222,358 - 9,740"
    - Explanation: "RESULT_EXPLANATION: I found pre tax income (INCOME BEFORE INCOME TAXES) of $9,740 million and substituted it into the formula."
    
    If you are MISSING information:
    - List what specific information is missing
    - Respond with: "MISSING_INFO: [list of missing terms]"
    
    If the information is insufficient or unclear:
    - Explain what additional information is needed
    - Respond with: "INSUFFICIENT_INFO: [explanation]"
    """
    
    attempt_result = llm.invoke(attempt_answer_prompt)
    print(f"📊 Attempt Result:\n{attempt_result}\n")
    
    # Parse the result to extract substituted formula and explanation
    simplified_answer = ""
    result_explanation = ""
    
    if "CALCULATION_READY:" in attempt_result:
        print(f"✅ Found substituted formula!")
        
        # Extract the substituted formula
        answer_part = attempt_result.split('CALCULATION_READY:')[1].strip()
        simplified_answer = answer_part.split('\n')[0].strip()  # Take just the first line
        
        # Extract the result explanation if present
        if "RESULT_EXPLANATION:" in attempt_result:
            explanation_part = attempt_result.split("RESULT_EXPLANATION:")[1].strip()
            result_explanation = explanation_part.split('\n')[0].strip()  # Take just the first line
        
        print(f"🎯 Substituted Formula: {simplified_answer}")
        if result_explanation:
            print(f"📝 Explanation: {result_explanation}")
    else:
        print(f"⚠️ No substituted formula found in response")
        simplified_answer = attempt_result
    
    return {
        "attempt_result": simplified_answer,
        "result_explanation": result_explanation
    }


def step4_targeted_rag_search(missing_terms: list, synonyms: dict, context: str) -> dict:
    """Step 4: Search for missing terms specifically."""
    print(f"\n🔍 Step 4: Targeted RAG search for missing terms...")
    
    print(f"🔍 Searching for missing terms: {missing_terms}")
    
    # Create synonyms for missing terms
    missing_search_terms = []
    for term in missing_terms:
        if term in synonyms:
            missing_search_terms.extend(synonyms[term])
        else:
            missing_search_terms.append(term)
    
    print(f"🔍 Expanded search terms: {missing_search_terms}")
    
    # Targeted search for missing terms
    additional_extracted_info = {}
    context_lower = context.lower()
    
    for term in missing_search_terms:
        term_lower = term.lower()
        if term_lower in context_lower:
            # Find the position of the term
            pos = context_lower.find(term_lower)
            
            # Extract surrounding text (approximately 300 characters before and after)
            start = max(0, pos - 300)
            end = min(len(context), pos + len(term) + 300)
            
            # Try to find sentence boundaries
            start = context.rfind('.', start, pos) + 1 if context.rfind('.', start, pos) > start - 100 else start
            end = context.find('.', pos) + 1 if context.find('.', pos) < end + 100 else end
            
            relevant_text = context[start:end].strip()
            if relevant_text:
                additional_extracted_info[term] = relevant_text
                print(f"✅ Found missing term '{term}': {relevant_text[:100]}...")
    
    if additional_extracted_info:
        print(f"\n📊 Additional Extracted Information:")
        for term, text in additional_extracted_info.items():
            print(f"  • {term}: {text}")
        
        step4_decision = "STEP_6"
        step4_reasoning = "Good results found from targeted RAG search"
        print(f"\n✅ Good results found! Would jump to Step 6")
    else:
        print(f"\n❌ No additional information found for missing terms")
        step4_decision = "STEP_5"
        step4_reasoning = "No additional information found, proceeding to LLM direct search"
        print(f"🔄 Would go to Step 5 (LLM direct context search)")
    
    return {
        "additional_extracted_info": additional_extracted_info,
        "decision": step4_decision,
        "reasoning": step4_reasoning
    }


def step5_llm_direct_search(question: str, formula: str, missing_terms: list, context: str, llm) -> dict:
    """Step 5: LLM searches context directly for missing terms."""
    print(f"\n🔍 Step 5: LLM direct context search for missing terms...")
    
    llm_search_prompt = f"""
    You are a financial analyst. Search through this context for specific missing information.
    
    QUESTION: {question}
    FORMULA: {formula}
    MISSING TERMS: {missing_terms}
    
    CONTEXT:
    {context[:8000]}  # Limit context for LLM processing
    
    Please search for and extract information about the missing terms.
    Focus on finding numerical values, time periods, and relevant data.
    
    Respond with the information you find in a clear, organized format.
    """
    
    llm_search_result = llm.invoke(llm_search_prompt)
    print(f"📊 LLM Direct Search Result:\n{llm_search_result}\n")
    
    print(f"✅ LLM direct search completed")
    
    return {
        "llm_search_result": llm_search_result
    }


def step6_llm_calculation(question: str, formula: str, key_terms: list, all_extracted_info: str, llm) -> dict:
    """Step 6: LLM performs calculation with all information."""
    print(f"\n🔍 Step 6: LLM calculation with all extracted information...")
    
    # Prepare all extracted information for the LLM
    all_extracted_text = all_extracted_info if all_extracted_info else ""
    
    llm_calculation_prompt = f"""
    You are a financial analyst. Perform the calculation using the formula and extracted information.
    
    QUESTION: {question}
    FORMULA: {formula}
    KEY TERMS NEEDED: {key_terms}
    
    ALL EXTRACTED INFORMATION:
    {all_extracted_text}
    
    Please:
    1. Identify the numerical values for each term in the formula
    2. Perform the calculation step by step
    3. Provide the final answer with proper formatting
    
    If you cannot perform the calculation due to missing or unclear information, clearly state what is missing.
    
    Respond with your calculation and answer in a clear, structured format.
    """
    
    llm_calculation_result = llm.invoke(llm_calculation_prompt)
    print(f"📊 LLM Calculation Result:\n{llm_calculation_result}\n")
    
    # Extract the numerical answer if possible
    import re
    
    # Look for common answer patterns
    answer_patterns = [
        r"answer[:\s]*\$?([0-9,]+\.?[0-9]*)\s*(?:billion|million|thousand)?",
        r"result[:\s]*\$?([0-9,]+\.?[0-9]*)\s*(?:billion|million|thousand)?",
        r"calculation[:\s]*\$?([0-9,]+\.?[0-9]*)\s*(?:billion|million|thousand)?",
        r"=\s*\$?([0-9,]+\.?[0-9]*)\s*(?:billion|million|thousand)?",
        r"gross profit[:\s]*\$?([0-9,]+\.?[0-9]*)\s*(?:billion|million|thousand)?"
    ]
    
    llm_numerical_answer = None
    for pattern in answer_patterns:
        match = re.search(pattern, llm_calculation_result.lower())
        if match:
            llm_numerical_answer = match.group(1)
            break
    
    if llm_numerical_answer:
        print(f"🎯 LLM Numerical Answer: {llm_numerical_answer}")
    else:
        print(f"⚠️ Could not extract numerical answer from LLM calculation")
    
    return {
        "llm_calculation_result": llm_calculation_result,
        "llm_numerical_answer": llm_numerical_answer
    }


def step7_calculator_calculation(formula: str, all_extracted_info: str) -> dict:
    """Step 7: Calculator performs the same calculation."""
    print(f"\n🔍 Step 7: Calculator tool calculation...")
    
    # Extract numerical values from the extracted information
    numerical_values = extract_numerical_values(all_extracted_info)
    print(f"📊 Extracted Numerical Values: {numerical_values}")
    
    # Perform the calculation using the calculator
    calculator_result = perform_financial_calculation(formula, numerical_values)
    
    if calculator_result is not None:
        # Format the result appropriately
        formatted_result = format_financial_result(calculator_result, "millions")
        print(f"🧮 Calculator Result: {formatted_result}")
        print(f"🎯 Calculator Numerical Answer: {calculator_result}")
    else:
        print(f"❌ Calculator could not perform the calculation")
        print(f"📋 Available values: {numerical_values}")
        print(f"📋 Formula: {formula}")
        formatted_result = "Calculation failed"
        calculator_result = None
    
    return {
        "calculator_result": calculator_result,
        "formatted_result": formatted_result,
        "numerical_values": numerical_values
    }


def step8_answer_comparison(llm_answer: str, calculator_answer: str, question: str, formula: str) -> str:
    """Step 8: Compare answers and return final result."""
    print(f"\n🔍 Step 8: Comparing LLM vs Calculator answers...")
    
    # Compare the two answers
    print(f"🤖 LLM Answer: {llm_answer}")
    print(f"🧮 Calculator Answer: {calculator_answer}")
    
    # Determine the best answer
    final_answer = None
    comparison_notes = ""
    
    if llm_answer is not None and calculator_answer is not None:
        # Both answers available - compare them
        try:
            llm_val = float(llm_answer)
            calc_val = float(calculator_answer)
            
            # Check if they're close (within 5% or $50 million)
            difference = abs(llm_val - calc_val)
            percent_diff = (difference / max(abs(calc_val), 1)) * 100
            
            if difference <= 50 or percent_diff <= 5:  # Within $50M or 5%
                final_answer = calculator_answer  # Prefer calculator for precision
                comparison_notes = f"✅ Both answers agree (difference: ${difference:.0f}M, {percent_diff:.1f}%). Using calculator result for precision."
            else:
                # Significant disagreement - use calculator but note the difference
                final_answer = calculator_answer
                comparison_notes = f"⚠️ Disagreement detected (LLM: {llm_val}, Calculator: {calc_val}, difference: ${difference:.0f}M). Using calculator result."
                
        except ValueError:
            # Can't compare numerically, use calculator if available
            if calculator_answer is not None:
                final_answer = calculator_answer
                comparison_notes = "⚠️ Could not compare numerically. Using calculator result."
            else:
                final_answer = llm_answer
                comparison_notes = "⚠️ Could not compare numerically. Using LLM result."
                
    elif calculator_answer is not None:
        # Only calculator result available
        final_answer = calculator_answer
        comparison_notes = "✅ Using calculator result (LLM result unavailable)."
        
    elif llm_answer is not None:
        # Only LLM result available
        final_answer = llm_answer
        comparison_notes = "✅ Using LLM result (calculator result unavailable)."
        
    else:
        # No numerical results available
        final_answer = "Unable to calculate"
        comparison_notes = "❌ No numerical results available from either method."
    
    # Format the final answer
    if final_answer != "Unable to calculate":
        try:
            final_val = float(final_answer)
            formatted_final_answer = format_financial_result(final_val, "millions")
        except ValueError:
            formatted_final_answer = str(final_answer)
    else:
        formatted_final_answer = final_answer
    
    # Output the final result
    print(f"\n{'='*60}")
    print(f"🎯 FINAL ANSWER")
    print(f"{'='*60}")
    print(f"Question: {question}")
    print(f"Formula: {formula}")
    print(f"Final Answer: {formatted_final_answer}")
    print(f"Comparison Notes: {comparison_notes}")
    print(f"{'='*60}")
    
    return formatted_final_answer


def find_formula(question: str, llm) -> dict:
    """Find the formula needed to answer the question."""
    print(f"\n🔍 Finding formula for question...")
    
    formula_prompt = f"""
    You are a financial analysis expert. Given this question:
    
    QUESTION: {question}
    
    Please determine the formula needed to calculate the answer.
    
    Respond in this exact format:
    FORMULA: [the mathematical formula]
    
    Examples:
    - For "What is Gross Profit?" → FORMULA: Gross Profit = Revenue - Cost of Goods Sold
    - For "What is Operating Margin?" → FORMULA: Operating Margin = Operating Income / Revenue
    - For "What is Net Income?" → FORMULA: Net Income = Revenue - Cost of Goods Sold - Operating Expenses
    """
    
    formula_response = llm.invoke(formula_prompt)
    print(f"📋 Formula Analysis:\n{formula_response}\n")
    
    # Parse the response to extract formula
    formula = ""
    
    lines = formula_response.split('\n')
    for line in lines:
        line_stripped = line.strip()
        if line_stripped.startswith('FORMULA:'):
            formula = line_stripped.replace('FORMULA:', '').strip()
            break
    
    print(f"🎯 Formula: {formula}")
    
    return {
        "formula": formula,
        "llm_response": formula_response
    }


def expanded_search_for_missing_info(missing_info: str, formula: str, context: str, llm) -> dict:
    """Perform an expanded search for missing information using comprehensive term generation."""
    print(f"\n🔍 Expanded search for missing information...")
    print(f"📋 Missing info: {missing_info}")
    
    # Generate comprehensive search terms for missing information
    expanded_search_prompt = f"""
    You are a financial analyst. Given this missing information and formula, generate a comprehensive list of search terms and synonyms.
    
    FORMULA: {formula}
    MISSING INFORMATION: {missing_info}
    
    Your task is to generate an expansive list of terms and synonyms that could be used to find the missing information in financial documents.
    
    For each missing term, provide:
    1. The original term
    2. Common variations and abbreviations
    3. Related financial terms
    4. Industry-specific synonyms
    5. Alternative phrasings
    
    Respond in this exact format:
    EXPANDED_TERMS: {{
        "term1": ["synonym1", "synonym2", "synonym3", ...],
        "term2": ["synonym1", "synonym2", "synonym3", ...],
        ...
    }}
    
    EXAMPLES:
    - For "Cost of Goods Sold" → ["COGS", "cost of sales", "direct costs", "inventory costs", "merchandise costs", "product costs", "cost of revenue"]
    - For "Total Revenue" → ["revenue", "sales", "net sales", "gross sales", "total sales", "income", "gross income", "net revenue"]
    - For "Operating Income" → ["operating profit", "EBIT", "earnings before interest and taxes", "operating earnings", "operating profit before tax"]
    
    Be comprehensive and include industry-standard variations.
    """
    
    expanded_terms_response = llm.invoke(expanded_search_prompt)
    print(f"📊 Expanded Terms Response:\n{expanded_terms_response}\n")
    
    # Debug: Print the raw response to see what the LLM actually returned
    print(f"🔍 DEBUG - Raw LLM Response Length: {len(expanded_terms_response)}")
    print(f"🔍 DEBUG - Contains 'EXPANDED_TERMS:': {'EXPANDED_TERMS:' in expanded_terms_response}")
    
    # Parse the expanded terms
    expanded_terms = {}
    try:
        # Find the EXPANDED_TERMS section
        if "EXPANDED_TERMS:" in expanded_terms_response:
            terms_section = expanded_terms_response.split("EXPANDED_TERMS:")[1].strip()
            # Find the JSON structure
            brace_start = terms_section.find('{')
            if brace_start != -1:
                # Find the matching closing brace
                brace_count = 0
                brace_end = -1
                for i, char in enumerate(terms_section[brace_start:], brace_start):
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            brace_end = i + 1
                            break
                
                if brace_end != -1:
                    terms_json = terms_section[brace_start:brace_end]
                    import json
                    expanded_terms = json.loads(terms_json)
    except Exception as e:
        print(f"⚠️ Could not parse expanded terms: {e}")
        # Fallback: create basic synonyms for missing terms
        missing_terms_list = [term.strip() for term in missing_info.split(',')]
        for term in missing_terms_list:
            term_lower = term.lower()
            if "revenue" in term_lower:
                expanded_terms[term] = ["revenue", "sales", "net sales", "gross sales", "total sales", "income"]
            elif "cost" in term_lower and "goods" in term_lower:
                expanded_terms[term] = ["cost of goods sold", "cogs", "cost of sales", "direct costs", "inventory costs"]
            elif "operating" in term_lower and "income" in term_lower:
                expanded_terms[term] = ["operating income", "operating profit", "ebit", "operating earnings"]
            elif "pre tax" in term_lower and "income" in term_lower:
                expanded_terms[term] = ["pre tax income", "pretax income", "earnings before taxes", "ebt", "income before taxes", "pre-tax earnings", "operating income", "operating profit", "income before income taxes", "income before taxes", "pretax earnings"]
            elif "income" in term_lower:
                expanded_terms[term] = ["income", "earnings", "profit", "net income", "net earnings", "operating income", "operating profit"]
            else:
                expanded_terms[term] = [term.lower()]
    
    print(f"🎯 Expanded Terms: {expanded_terms}")
    
    # Perform comprehensive search using expanded terms
    all_search_terms = []
    for term, synonyms in expanded_terms.items():
        all_search_terms.extend(synonyms)
    
    print(f"🔍 Searching for {len(all_search_terms)} expanded terms...")
    
    # Generate sub-component search terms
    sub_component_terms = []
    for term in all_search_terms:
        # Add the full term
        sub_component_terms.append(term)
        
        # Break down into words
        words = term.lower().split()
        
        # Add individual words (if they're meaningful)
        for word in words:
            if len(word) > 2 and word not in ['the', 'and', 'for', 'with', 'from', 'that', 'this', 'have', 'been', 'will', 'were', 'they', 'their', 'them', 'then', 'than']:
                sub_component_terms.append(word)
        
        # Add word pairs (bigrams)
        for i in range(len(words) - 1):
            bigram = f"{words[i]} {words[i+1]}"
            if len(bigram) > 4:  # Only meaningful pairs
                sub_component_terms.append(bigram)
        
        # Add word triplets (trigrams) for longer phrases
        for i in range(len(words) - 2):
            trigram = f"{words[i]} {words[i+1]} {words[i+2]}"
            if len(trigram) > 6:  # Only meaningful triplets
                sub_component_terms.append(trigram)
    
    # Remove duplicates while preserving order
    unique_search_terms = []
    seen = set()
    for term in sub_component_terms:
        if term.lower() not in seen:
            unique_search_terms.append(term)
            seen.add(term.lower())
    
    print(f"🔍 Now searching for {len(unique_search_terms)} terms (including sub-components)...")
    print(f"📋 Sample sub-components: {unique_search_terms[:10]}...")
    
    # Search for all terms in context
    found_info = {}
    context_lower = context.lower()
    
    for term in unique_search_terms:
        term_lower = term.lower()
        if term_lower in context_lower:
            # Find the position of the term
            pos = context_lower.find(term_lower)
            
            # Extract surrounding text (approximately 300 characters before and after)
            start = max(0, pos - 300)
            end = min(len(context), pos + len(term) + 300)
            
            # Try to find sentence boundaries
            start = context.rfind('.', start, pos) + 1 if context.rfind('.', start, pos) > start - 100 else start
            end = context.find('.', pos) + 1 if context.find('.', pos) < end + 100 else end
            
            relevant_text = context[start:end].strip()
            if relevant_text:
                found_info[term] = relevant_text
                print(f"✅ Found '{term}': {relevant_text[:100]}...")
    
    if found_info:
        print(f"\n📊 Found Information:")
        for term, text in found_info.items():
            print(f"  • {term}: {text[:100]}...")
        
        # Convert to string format with better organization
        found_text_parts = []
        for term, text in found_info.items():
            # Clean up the text and add it to the parts
            cleaned_text = text.strip()
            if cleaned_text:
                found_text_parts.append(cleaned_text)
        
        found_text = "\n\n".join(found_text_parts)
    else:
        print(f"\n❌ No additional information found with expanded search")
        found_text = ""
    
    return {
        "found_info": found_text
    }


def analyze_completeness(attempt_result: str, result_explanation: str, formula: str, question: str, llm) -> dict:
    """Analyze whether all necessary information was found for the calculation."""
    print(f"\n🔍 Analyzing completeness of information...")
    
    analysis_prompt = f"""
    You are a financial analyst. Analyze whether all necessary information was found to answer this question.
    
    QUESTION: {question}
    FORMULA: {formula}
    
    ATTEMPT RESULT: {attempt_result}
    RESULT EXPLANATION: {result_explanation}
    
    Your task is to determine if ALL necessary information was found to calculate the answer.
    
    Look for indicators like:
    - "not provided", "missing", "not found", "not available"
    - "partially substituted", "only some values", "incomplete"
    - "cannot calculate", "insufficient information"
    - "I can only provide", "I found X but Y is missing"
    
    Respond in this exact format:
    COMPLETENESS: [COMPLETE/INCOMPLETE]
    MISSING_INFO: [List specific missing information, or "None" if complete]
    REASONING: [Explain why the information is complete or incomplete]
    
    EXAMPLES:
    - If explanation says "Cost of Goods Sold is not provided" → COMPLETENESS: INCOMPLETE, MISSING_INFO: Cost of Goods Sold
    - If explanation says "I found all values and can calculate" → COMPLETENESS: COMPLETE, MISSING_INFO: None
    - If explanation says "partially substituted formula" → COMPLETENESS: INCOMPLETE, MISSING_INFO: [list what's missing]
    """
    
    analysis_response = llm.invoke(analysis_prompt)
    print(f"📊 Completeness Analysis:\n{analysis_response}\n")
    
    # Parse the response
    completeness = "INCOMPLETE"  # Default to incomplete for safety
    missing_info = ""
    reasoning = ""
    
    lines = analysis_response.split('\n')
    for line in lines:
        line_stripped = line.strip()
        if line_stripped.startswith('COMPLETENESS:'):
            completeness = line_stripped.replace('COMPLETENESS:', '').strip()
        elif line_stripped.startswith('MISSING_INFO:'):
            missing_info = line_stripped.replace('MISSING_INFO:', '').strip()
        elif line_stripped.startswith('REASONING:'):
            reasoning = line_stripped.replace('REASONING:', '').strip()
    
    # Determine next step based on completeness
    if completeness == "COMPLETE":
        next_step = "STEP_6"
        decision_reasoning = "All necessary information found and calculation can proceed"
    else:
        next_step = "STEP_4"
        decision_reasoning = f"Missing information: {missing_info}"
    
    print(f"🎯 Completeness: {completeness}")
    print(f"🎯 Missing Info: {missing_info}")
    print(f"🎯 Next Step: {next_step}")
    
    return {
        "completeness": completeness,
        "missing_info": missing_info,
        "reasoning": reasoning,
        "next_step": next_step,
        "decision_reasoning": decision_reasoning
    }



# --------------------
#     Main Flow Functions
# --------------------

def basic_or_assumption_question(question: str, context: str, llm, tools: List[Tool], max_iterations: int = 5):
    """Main orchestrator function that calls each step in order."""
    print(f"\n🔄 Running BASIC/ASSUMPTION flow...")
    print(f"📄 Using provided context ({len(context)} characters)")
    
    # Log the start of execution
    logger.log_execution_start(question, len(context))
    
    # Step 1: Formula analysis
    print(f"\n🔍 Step 1: Formula analysis...")
    step1_input = {"question": question}
    step1_result = step1_formula_analysis(question, llm)
    logger.log_function_call("step1_formula_analysis", step1_input, step1_result, 1)
    
    formula = step1_result["formula"]
    key_terms = step1_result["key_terms"]
    synonyms = step1_result["synonyms"]
    
    # Step 2: Initial RAG search
    print(f"\n🔍 Step 2: Initial RAG search...")
    step2_input = {
        "key_terms": key_terms,
        "synonyms": synonyms
    }
    step2_result = step2_initial_rag_search(key_terms, synonyms, context)
    logger.log_function_call("step2_initial_rag_search", step2_input, step2_result, 2)
    
    extracted_info = step2_result
    
    # Step 3: Attempt answer
    print(f"\n🔍 Step 3: Attempt answer...")
    step3_input = {
        "question": question,
        "formula": formula,
        "extracted_info": extracted_info[:200] + "..." if len(extracted_info) > 200 else extracted_info
    }
    step3_result = step3_attempt_answer(question, formula, extracted_info, llm)
    logger.log_function_call("step3_attempt_answer", step3_input, step3_result, 3)
    
    # Decision point: Analyze completeness of information
    print(f"\n🔍 Analyzing completeness of Step 3 results...")
    
    analysis_input = {
        "attempt_result": step3_result["attempt_result"],
        "result_explanation": step3_result["result_explanation"],
        "formula": formula,
        "question": question
    }
    # HARDCODED FOR TESTING - FORCE INCOMPLETE PATH
    analysis_result = {
        "completeness": "INCOMPLETE",
        "missing_info": "pre tax income",
        "reasoning": "Hardcoded for testing - forcing incomplete path",
        "next_step": "STEP_4",
        "decision_reasoning": "Missing information: pre tax income"
    }
    logger.log_function_call("analyze_completeness", analysis_input, analysis_result, 3.5)
    
    next_step = analysis_result["next_step"]
    decision_reasoning = analysis_result["decision_reasoning"]
    
    # Log the decision
    logger.log_decision(next_step, decision_reasoning, 3.5)
    
    if next_step == "STEP_6":
        # Use the substituted formula from Step 3 as the final result
        final_answer = step3_result["attempt_result"]
        all_extracted_info = extracted_info
    else:
        # Step 4: Expanded search for missing information
        print(f"\n🔍 Step 4: Expanded search for missing information...")
        
        # Use the missing info from the analysis
        missing_info = analysis_result["missing_info"]
        
        if missing_info:
            step4_input = {
                "missing_info": missing_info,
                "formula": formula,
                "context_length": len(context)
            }
            step4_result = expanded_search_for_missing_info(missing_info, formula, context, llm)
            logger.log_function_call("expanded_search_for_missing_info", step4_input, step4_result, 4)
            
            # Combine original extracted info with new found info
            if step4_result["found_info"]:
                all_extracted_info = extracted_info + "\n\n" + step4_result["found_info"]
                print(f"✅ Found additional information with expanded search!")
            else:
                all_extracted_info = extracted_info
                print(f"❌ No additional information found with expanded search")
        else:
            all_extracted_info = extracted_info
        
        print(f"🔍 DEBUG: Step 4 completed, about to enter Step 5 section...")
        
        # Step 5: Merge found information and attempt final calculation
        print(f"\n🔍 Step 5: Merging found information and attempting final calculation...")
        print(f"🔍 DEBUG: About to start Step 5...")
        
        # Combine original extracted info with newly found info
        all_extracted_info = extracted_info
        if step4_result and step4_result.get("found_info"):
            all_extracted_info = extracted_info + "\n\n" + step4_result["found_info"]
            print(f"✅ Combined original and newly found information!")
            print(f"📊 Found info length: {len(step4_result['found_info'])}")
        
        # HARDCODED FOR TESTING - TEST FORMULA WITH MISSING VALUE
        test_formula = "Gross Profit = 254,453 - 222,358 - pre tax income"
        print(f"🧪 Testing with formula: {test_formula}")
        print(f"🧪 DEBUG: Using test formula: '{test_formula}'")
        
        # Attempt to answer with the complete information
        step5_input = {
            "question": question,
            "formula": test_formula,  # Use test formula instead of original
            "all_extracted_info": all_extracted_info[:200] + "..." if len(all_extracted_info) > 200 else all_extracted_info
        }
        
        print(f"🧪 DEBUG: Calling step3_attempt_answer with test formula...")
        step5_result = step3_attempt_answer(question, test_formula, all_extracted_info, llm)
        logger.log_function_call("step5_final_attempt", step5_input, step5_result, 5)
        
        # Use Step 5 result as final answer
        final_answer = step5_result["attempt_result"]
        
        print(f"🎯 Step 5 completed! Final answer: {final_answer}")
        print(f"🔍 DEBUG: About to exit after Step 5...")
        
        # HARDCODED FOR TESTING - EXIT AFTER STEP 5
        exit()
    
    # # Step 4: Targeted RAG search for missing terms
    # print(f"\n🔍 Step 4: Targeted RAG search...")
    # missing_terms = []
    # if "MISSING_INFO:" in step3_result["attempt_result"]:
    #     missing_info = step3_result["attempt_result"].split("MISSING_INFO:")[1].strip()
    #     missing_terms = [term.strip() for term in missing_info.split(',')]
    # elif "INSUFFICIENT_INFO:" in step3_result["attempt_result"]:
    #     missing_terms = key_terms
    # 
    # step4_input = {
    #     "missing_terms": missing_terms,
    #     "synonyms": synonyms
    # }
    # step4_result = step4_targeted_rag_search(missing_terms, synonyms, context)
    # logger.log_function_call("step4_targeted_rag_search", step4_input, step4_result, 4)
    # 
    # additional_extracted_info = step4_result["additional_extracted_info"]
    # step4_decision = step4_result["decision"]
    # step4_reasoning = step4_result["reasoning"]
    # 
    # # Log decision from Step 4
    # logger.log_decision(4, step4_decision, step4_reasoning)
    # 
    # # Decision point: If good results from Step 4, jump to Step 6
    # if step4_decision == "STEP_6":
    #     # Combine the original extracted info with additional info
    #     if extracted_info and additional_extracted_info:
    #         all_extracted_info = extracted_info + "\n\n" + additional_extracted_info
    #         elif additional_extracted_info:
    #             all_extracted_info = additional_extracted_info
    #         else:
    #             all_extracted_info = extracted_info
    #     else:
    #         # Step 5: LLM direct search
    #         print(f"\n🔍 Step 5: LLM direct search...")
    #         step5_input = {
    #             "question": question,
    #             "formula": formula,
    #             "missing_terms": missing_terms
    #         }
    #         step5_result = step5_llm_direct_search(question, formula, missing_terms, context, llm)
    #         logger.log_function_call("step5_llm_direct_search", step5_input, step5_result, 5)
    #         
    #         # Combine all extracted info
    #         all_extracted_info = extracted_info  # Could enhance to include LLM search results
    # 
    # # Step 6: LLM calculation
    # print(f"\n🔍 Step 6: LLM calculation...")
    # step6_input = {
    #     "question": question,
    #     "formula": formula,
    #     "key_terms": key_terms,
    #     "extracted_info_length": len(str(all_extracted_info)) if all_extracted_info else 0
    # }
    # step6_result = step6_llm_calculation(question, formula, key_terms, all_extracted_info, llm)
    # logger.log_function_call("step6_llm_calculation", step6_input, step6_result, 6)
    # 
    # llm_numerical_answer = step6_result["llm_numerical_answer"]
    # 
    # # Step 7: Calculator calculation
    # print(f"\n🔍 Step 7: Calculator calculation...")
    # step7_input = {
    #     "formula": formula,
    #     "extracted_info_length": len(str(all_extracted_info)) if all_extracted_info else 0
    # }
    # step7_result = step7_calculator_calculation(formula, all_extracted_info)
    # logger.log_function_call("step7_calculator_calculation", step7_input, step7_result, 7)
    # 
    # calculator_result = step7_result["calculator_result"]
    # 
    # # Step 8: Answer comparison and final result
    # print(f"\n🔍 Step 8: Answer comparison...")
    # step8_input = {
    #     "llm_answer": llm_numerical_answer,
    #         "calculator_answer": calculator_result,
    #         "question": question,
    #         "formula": formula
    #     }
    #     final_answer = step8_answer_comparison(llm_numerical_answer, calculator_result, question, formula)
    #     step8_result = {
    #         "final_answer": final_answer,
    #         "formatted_final_answer": final_answer
    #     }
    #     logger.log_function_call("step8_answer_comparison", step8_input, step8_result, 8)
    
    # Write execution summary
    logger.log_execution_end(final_answer)
    
    return final_answer


def conceptual_question(question: str, llm, tools: List[Tool], max_iterations: int = 5):
    """
    Control flow for questions without context (conceptual questions).
    Agent needs to search for relevant information using tools.
    """
    print(f"\n🔍 Running CONCEPTUAL flow...")
    print(f"🔎 Agent will search for relevant information")
    
    tool_results = ""
    for i in range(1, max_iterations + 1):
        prompt = build_prompt(question, tool_results, i, max_iterations)
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



# --------------------
#     Agent Runner
# --------------------

def run_agent(question: str, context: str, llm, tools: List[Tool], max_iterations: int = 5):
    """
    Main agent function that determines control flow based on whether context is provided.
    
    Args:
        question: The question to answer
        context: The provided context (can be empty string)
        llm: The language model to use
        tools: List of available tools
        max_iterations: Maximum number of iterations
    
    Returns:
        str: The final answer
    """
    # Check if context is meaningful (not empty, None, or just whitespace)
    if context and context.strip() and context != 'No context available':
        return basic_or_assumption_question(question, context, llm, tools, max_iterations)
    else:
        return conceptual_question(question, llm, tools, max_iterations)