import re
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class InformationRequirement:
    """Represents a specific information requirement identified by the LLM."""
    category: str  # e.g., "financial_metrics", "company_data", "market_context"
    requirement: str  # e.g., "Gross Profit", "Revenue growth rates"
    description: str = ""  # Optional description


class ContextRAG:
    """
    Retrieval-Augmented Generation system for extracting relevant information from context.
    Uses the LLM's information requirements to find and extract relevant data from the provided context.
    """
    
    def __init__(self):
        self.extracted_info = {}
    
    def parse_information_requirements(self, llm_response: str) -> List[InformationRequirement]:
        """
        Parse the LLM's information requirements response into structured requirements.
        
        Args:
            llm_response: The LLM's response about what information is needed
            
        Returns:
            List of InformationRequirement objects
        """
        requirements = []
        
        # Split by common section markers
        sections = re.split(r'\n\d+\.\s*', llm_response)
        
        for section in sections:
            if not section.strip():
                continue
                
            # Try to identify the category from the section
            category = self._identify_category(section)
            
            # Extract individual requirements from the section
            reqs = self._extract_requirements_from_section(section)
            
            for req in reqs:
                requirements.append(InformationRequirement(
                    category=category,
                    requirement=req,
                    description=section.strip()
                ))
        
        return requirements
    
    def _identify_category(self, section: str) -> str:
        """Identify the category of information from a section."""
        section_lower = section.lower()
        
        if any(word in section_lower for word in ['financial', 'metrics', 'ratios', 'margin', 'revenue', 'profit']):
            return "financial_metrics"
        elif any(word in section_lower for word in ['company', 'data', 'historical', 'cogs']):
            return "company_data"
        elif any(word in section_lower for word in ['market', 'industry', 'average', 'benchmark']):
            return "market_context"
        elif any(word in section_lower for word in ['assumption', 'assume', 'constant']):
            return "assumptions"
        else:
            return "general"
    
    def _extract_requirements_from_section(self, section: str) -> List[str]:
        """Extract specific requirements from a section."""
        requirements = []
        
        # Look for bullet points or numbered items
        lines = section.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('-') or line.startswith('•'):
                # Extract the requirement after the bullet
                req = line[1:].strip()
                if req:
                    requirements.append(req)
            elif re.match(r'^\d+\.', line):
                # Extract the requirement after the number
                req = re.sub(r'^\d+\.\s*', '', line)
                if req:
                    requirements.append(req)
        
        return requirements
    
    def extract_relevant_information(self, context: str, requirements: List[InformationRequirement]) -> Dict[str, Any]:
        """
        Extract relevant information from context based on the requirements.
        
        Args:
            context: The provided context (financial documents, etc.)
            requirements: List of InformationRequirement objects
            
        Returns:
            Dictionary of extracted information organized by category
        """
        extracted_info = {
            "financial_metrics": [],
            "company_data": [],
            "market_context": [],
            "assumptions": [],
            "general": []
        }
        
        # Convert context to lowercase for case-insensitive search
        context_lower = context.lower()
        
        print(f"🔍 DEBUG: Searching context ({len(context)} characters)")
        print(f"🔍 DEBUG: Looking for {len(requirements)} requirements")
        
        for req in requirements:
            print(f"🔍 DEBUG: Searching for requirement: '{req.requirement}' in category '{req.category}'")
            
            # Search for the requirement in the context
            relevant_text = self._find_relevant_text(context, context_lower, req.requirement)
            
            if relevant_text:
                print(f"✅ DEBUG: Found relevant text for '{req.requirement}'")
                extracted_info[req.category].append({
                    "requirement": req.requirement,
                    "extracted_text": relevant_text,
                    "description": req.description
                })
            else:
                print(f"❌ DEBUG: No relevant text found for '{req.requirement}'")
        
        return extracted_info
    
    def _find_relevant_text(self, context: str, context_lower: str, requirement: str) -> str:
        """
        Find relevant text in the context for a specific requirement.
        
        Args:
            context: Original context
            context_lower: Lowercase context for searching
            requirement: The specific requirement to search for
            
        Returns:
            Relevant text from the context
        """
        # Create search terms from the requirement
        search_terms = self._generate_search_terms(requirement)
        
        print(f"🔍 DEBUG: Generated search terms: {search_terms}")
        
        for term in search_terms:
            if term.lower() in context_lower:
                print(f"✅ DEBUG: Found term '{term}' in context")
                # Find the position of the term
                pos = context_lower.find(term.lower())
                
                # Extract surrounding text (approximately 200 characters before and after)
                start = max(0, pos - 200)
                end = min(len(context), pos + len(term) + 200)
                
                # Try to find sentence boundaries
                start = self._find_sentence_start(context, start)
                end = self._find_sentence_end(context, end)
                
                return context[start:end].strip()
            else:
                print(f"❌ DEBUG: Term '{term}' not found in context")
        
        return ""
    
    def _generate_search_terms(self, requirement: str) -> List[str]:
        """Generate search terms from a requirement."""
        terms = [requirement]
        
        # Add common variations
        if "gross profit" in requirement.lower():
            terms.extend(["gross profit", "gross margin", "revenue", "sales"])
        elif "revenue" in requirement.lower():
            terms.extend(["revenue", "sales", "income"])
        elif "margin" in requirement.lower():
            terms.extend(["margin", "profit", "gross", "net"])
        elif "growth" in requirement.lower():
            terms.extend(["growth", "increase", "decrease", "change"])
        elif "cost" in requirement.lower():
            terms.extend(["cost", "expense", "cogs", "cost of goods sold"])
        
        return terms
    
    def _find_sentence_start(self, text: str, pos: int) -> int:
        """Find the start of a sentence around the given position."""
        # Look for sentence endings before the position
        for i in range(pos, max(0, pos - 100), -1):
            if text[i] in '.!?':
                return i + 1
        return max(0, pos - 100)
    
    def _find_sentence_end(self, text: str, pos: int) -> int:
        """Find the end of a sentence around the given position."""
        # Look for sentence endings after the position
        for i in range(pos, min(len(text), pos + 100)):
            if text[i] in '.!?':
                return i + 1
        return min(len(text), pos + 100)
    
    def format_extracted_information(self, extracted_info: Dict[str, Any]) -> str:
        """
        Format the extracted information into a readable string.
        
        Args:
            extracted_info: Dictionary of extracted information
            
        Returns:
            Formatted string of extracted information
        """
        formatted = []
        
        for category, items in extracted_info.items():
            if items:
                formatted.append(f"\n{category.upper().replace('_', ' ')}:")
                for item in items:
                    formatted.append(f"  • {item['requirement']}: {item['extracted_text']}")
        
        return "\n".join(formatted) if formatted else "No relevant information found in context."


def rag_extract_information(context: str, llm_requirements: str) -> str:
    """
    Main function to extract relevant information from context based on LLM requirements.
    
    Args:
        context: The provided context (financial documents, etc.)
        llm_requirements: The LLM's response about what information is needed
        
    Returns:
        Formatted string of extracted relevant information
    """
    rag = ContextRAG()
    
    # Parse the LLM's requirements
    requirements = rag.parse_information_requirements(llm_requirements)
    
    print(f"🔍 DEBUG: Parsed {len(requirements)} requirements from LLM response")
    for i, req in enumerate(requirements):
        print(f"  {i+1}. Category: {req.category}, Requirement: {req.requirement}")
    
    # Extract relevant information from context
    extracted_info = rag.extract_relevant_information(context, requirements)
    
    # Format and return the results
    return rag.format_extracted_information(extracted_info)
