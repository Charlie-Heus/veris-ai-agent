import re
from typing import Dict, Any, Optional


def extract_numerical_values(extracted_info: str) -> Dict[str, float]:
    """
    Extract numerical values from the extracted information.
    
    Args:
        extracted_info: String of extracted text
        
    Returns:
        Dictionary mapping terms to numerical values
    """
    numerical_values = {}
    
    if not extracted_info:
        return numerical_values
    
    # Common patterns for extracting numbers
    patterns = [
        r'\$?([0-9,]+\.?[0-9]*)\s*(?:billion|B)',  # $2.5 billion or 2.5B
        r'\$?([0-9,]+\.?[0-9]*)\s*(?:million|M)',   # $180 million or 180M
        r'\$?([0-9,]+\.?[0-9]*)\s*(?:thousand|K)',  # $500 thousand or 500K
        r'\$?([0-9,]+\.?[0-9]*)',                    # Plain numbers
    ]
    
    text_lower = extracted_info.lower()
    
    # Look for specific terms and their values
    term_patterns = {
        'revenue': [
            r'total revenue\s*\$?([0-9,]+\.?[0-9]*)',
            r'net sales\s*\$?([0-9,]+\.?[0-9]*)',
            r'revenue\s*\$?([0-9,]+\.?[0-9]*)'
        ],
        'cost of goods sold': [
            r'merchandise costs\s*\$?([0-9,]+\.?[0-9]*)',
            r'cost of goods sold\s*\$?([0-9,]+\.?[0-9]*)',
            r'cogs\s*\$?([0-9,]+\.?[0-9]*)'
        ],
        'operating income': [
            r'operating income\s*\$?([0-9,]+\.?[0-9]*)',
            r'ebit\s*\$?([0-9,]+\.?[0-9]*)'
        ],
        'gross profit': [
            r'gross profit\s*\$?([0-9,]+\.?[0-9]*)',
            r'gross margin\s*\$?([0-9,]+\.?[0-9]*)'
        ]
    }
    
    # Extract values for specific terms
    for term, patterns_list in term_patterns.items():
        for pattern in patterns_list:
            match = re.search(pattern, text_lower)
            if match:
                value_str = match.group(1).replace(',', '')
                value = float(value_str)
                
                # Convert to millions if in billions
                if 'billion' in text_lower or 'B' in text_lower:
                    value *= 1000
                elif 'thousand' in text_lower or 'K' in text_lower:
                    value /= 1000
                
                numerical_values[term] = value
                break
    
    # If no specific terms found, try general patterns
    if not numerical_values:
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                value_str = match.group(1).replace(',', '')
                value = float(value_str)
                
                # Convert to millions if in billions
                if 'billion' in text_lower or 'B' in text_lower:
                    value *= 1000
                elif 'thousand' in text_lower or 'K' in text_lower:
                    value /= 1000
                
                numerical_values['general'] = value
                break
    
    return numerical_values


def calculator_tool(calculation_input: str) -> str:
    """
    Calculator tool that can perform financial calculations.
    
    Args:
        calculation_input: String describing the calculation to perform
        
    Returns:
        String result of the calculation
    """
    try:
        # For now, we'll use a simple approach
        # In a full implementation, you might want to use a more sophisticated calculator
        return f"Calculator result: {calculation_input}"
    except Exception as e:
        return f"Calculator error: {str(e)}"


def perform_financial_calculation(formula: str, numerical_values: Dict[str, float]) -> Optional[float]:
    """
    Perform a financial calculation using the formula and numerical values.
    
    Args:
        formula: The formula to evaluate (e.g., "Revenue - COGS")
        numerical_values: Dictionary of term -> numerical value
        
    Returns:
        Calculated result or None if calculation fails
    """
    try:
        # Simple formula evaluation for common financial calculations
        formula_lower = formula.lower()
        
        if "revenue" in formula_lower and "cogs" in formula_lower or "cost" in formula_lower:
            # Gross Profit = Revenue - COGS
            revenue = numerical_values.get('revenue', 0)
            cogs = numerical_values.get('cost of goods sold', numerical_values.get('cogs', 0))
            return revenue - cogs
            
        elif "operating income" in formula_lower or "ebit" in formula_lower:
            # EBIT = Operating Income
            return numerical_values.get('operating income', 0)
            
        elif "ebitda" in formula_lower:
            # EBITDA = EBIT + Depreciation & Amortization
            ebit = numerical_values.get('operating income', 0)
            d_and_a = numerical_values.get('depreciation', 0)
            return ebit + d_and_a
            
        elif "margin" in formula_lower:
            # Margin calculations
            if "operating margin" in formula_lower:
                operating_income = numerical_values.get('operating income', 0)
                revenue = numerical_values.get('revenue', 1)  # Avoid division by zero
                return (operating_income / revenue) * 100
            elif "gross margin" in formula_lower:
                gross_profit = numerical_values.get('gross profit', 0)
                revenue = numerical_values.get('revenue', 1)
                return (gross_profit / revenue) * 100
                
        else:
            # Generic calculation - try to evaluate the formula
            # This is a simplified approach
            return None
            
    except Exception as e:
        print(f"Calculation error: {e}")
        return None


def format_financial_result(result: float, unit: str = "millions") -> str:
    """
    Format a financial result with appropriate units.
    
    Args:
        result: The numerical result
        unit: The unit to format in (millions, billions, etc.)
        
    Returns:
        Formatted result string
    """
    if unit == "millions":
        if abs(result) >= 1000:
            return f"${result/1000:.1f} billion"
        else:
            return f"${result:.0f} million"
    elif unit == "billions":
        return f"${result:.1f} billion"
    elif unit == "percent":
        return f"{result:.2f}%"
    else:
        return f"${result:.2f}"