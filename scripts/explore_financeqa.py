#!/usr/bin/env python3
"""
FinanceQA Dataset Explorer

This script provides utilities for exploring and analyzing the FinanceQA dataset
that has already been downloaded to data/financeqa_benchmark/.
"""

import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any


def load_dataset(data_path: str = "data/financeqa_benchmark") -> pd.DataFrame:
    """
    Load the FinanceQA dataset from the downloaded files.
    
    Args:
        data_path: Path to the dataset directory
        
    Returns:
        DataFrame containing the dataset
    """
    data_dir = Path(data_path)
    
    # Try CSV first (more reliable)
    csv_path = data_dir / "financeqa_test.csv"
    if csv_path.exists():
        print(f"Loading dataset from {csv_path}")
        return pd.read_csv(csv_path)
    
    # Try JSON as fallback
    json_path = data_dir / "financeqa_test.json"
    if json_path.exists():
        print(f"Loading dataset from {json_path}")
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            return pd.DataFrame(data)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            print("Trying to load as CSV instead...")
            # If JSON fails, try to load the CSV that should also exist
            if csv_path.exists():
                return pd.read_csv(csv_path)
            else:
                raise FileNotFoundError(f"Could not load dataset from {data_path}")
    
    raise FileNotFoundError(f"No dataset found in {data_path}")


def explore_basic_stats(df: pd.DataFrame):
    """Display basic statistics about the dataset."""
    print("\n" + "="*50)
    print("FINANCEQA DATASET EXPLORATION")
    print("="*50)
    
    print(f"\n📊 Basic Statistics:")
    print(f"  Total questions: {len(df)}")
    print(f"  Columns: {list(df.columns)}")
    
    # Question type distribution
    if 'question_type' in df.columns:
        try:
            type_counts = df['question_type'].value_counts()
            print(f"\n📝 Question Types:")
            for q_type, count in type_counts.items():
                percentage = (count / len(df)) * 100
                print(f"  {q_type}: {count} ({percentage:.1f}%)")
        except Exception as e:
            print(f"  Error analyzing question types: {e}")
    
    # Company distribution
    if 'company' in df.columns:
        try:
            companies = df['company'].dropna().unique()
            print(f"\n🏢 Companies ({len(companies)} total):")
            for company in sorted(companies):
                count = len(df[df['company'] == company])
                print(f"  {company}: {count} questions")
        except Exception as e:
            print(f"  Error analyzing companies: {e}")
    
    # File types
    if 'file_name' in df.columns:
        try:
            file_types = df['file_name'].dropna().unique()
            print(f"\n📄 File Types ({len(file_types)} total):")
            for file_type in sorted(file_types):
                count = len(df[df['file_name'] == file_type])
                print(f"  {file_type}: {count} questions")
        except Exception as e:
            print(f"  Error analyzing file types: {e}")


def show_sample_questions(df: pd.DataFrame, num_samples: int = 5):
    """Display sample questions from the dataset."""
    print(f"\n🔍 Sample Questions (showing {num_samples}):")
    print("-" * 50)
    
    for i, (_, row) in enumerate(df.head(num_samples).iterrows(), 1):
        print(f"\n{i}. Question Type: {row.get('question_type', 'N/A')}")
        print(f"   Company: {row.get('company', 'N/A')}")
        print(f"   Question: {row.get('question', 'N/A')}")
        print(f"   Answer: {row.get('answer', 'N/A')}")
        
        # Show context preview if available
        if 'context' in row and pd.notna(row['context']) and row['context']:
            context_preview = str(row['context'])[:200] + "..." if len(str(row['context'])) > 200 else str(row['context'])
            print(f"   Context Preview: {context_preview}")
        
        print("-" * 30)


def analyze_by_question_type(df: pd.DataFrame):
    """Analyze questions by their type."""
    if 'question_type' not in df.columns:
        print("No question_type column found in dataset.")
        return
    
    try:
        print(f"\n📈 Analysis by Question Type:")
        print("=" * 40)
        
        for q_type in df['question_type'].dropna().unique():
            type_df = df[df['question_type'] == q_type]
            print(f"\n{q_type.upper()} Questions ({len(type_df)} total):")
            
            # Show sample questions for this type
            for i, (_, row) in enumerate(type_df.head(3).iterrows(), 1):
                print(f"  {i}. {row.get('question', 'N/A')}")
                print(f"     Answer: {row.get('answer', 'N/A')}")
            
            if len(type_df) > 3:
                print(f"  ... and {len(type_df) - 3} more")
    except Exception as e:
        print(f"Error analyzing by question type: {e}")


def analyze_by_company(df: pd.DataFrame):
    """Analyze questions by company."""
    if 'company' not in df.columns:
        print("No company column found in dataset.")
        return
    
    try:
        print(f"\n🏢 Analysis by Company:")
        print("=" * 30)
        
        for company in sorted(df['company'].dropna().unique()):
            company_df = df[df['company'] == company]
            print(f"\n{company} ({len(company_df)} questions):")
            
            # Show question types for this company
            if 'question_type' in company_df.columns:
                type_counts = company_df['question_type'].value_counts()
                for q_type, count in type_counts.items():
                    print(f"  {q_type}: {count}")
            
            # Show sample question
            sample = company_df.iloc[0]
            print(f"  Sample: {sample.get('question', 'N/A')}")
    except Exception as e:
        print(f"Error analyzing by company: {e}")


def search_questions(df: pd.DataFrame, search_term: str):
    """Search for questions containing specific terms."""
    print(f"\n🔍 Searching for questions containing '{search_term}':")
    print("=" * 50)
    
    try:
        # Search in questions
        matching_questions = df[df['question'].str.contains(search_term, case=False, na=False)]
        
        if len(matching_questions) == 0:
            print("No questions found matching the search term.")
            return
        
        print(f"Found {len(matching_questions)} matching questions:")
        
        for i, (_, row) in enumerate(matching_questions.iterrows(), 1):
            print(f"\n{i}. Type: {row.get('question_type', 'N/A')}")
            print(f"   Company: {row.get('company', 'N/A')}")
            print(f"   Question: {row.get('question', 'N/A')}")
            print(f"   Answer: {row.get('answer', 'N/A')}")
    except Exception as e:
        print(f"Error searching questions: {e}")


def create_sample_file(df: pd.DataFrame, output_file: str = "data/sample_questions.txt"):
    """Create a file with sample questions for testing."""
    try:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Select diverse sample questions
        sample_questions = []
        
        # Get questions from each type
        for q_type in df['question_type'].dropna().unique():
            type_questions = df[df['question_type'] == q_type]
            sample_questions.extend(type_questions['question'].head(3).tolist())
        
        # Write to file
        with open(output_path, 'w') as f:
            f.write("# Sample FinanceQA Questions for Testing\n\n")
            for i, question in enumerate(sample_questions, 1):
                f.write(f"{i}. {question}\n")
        
        print(f"\n✅ Sample questions saved to {output_path}")
        print(f"   Total sample questions: {len(sample_questions)}")
    except Exception as e:
        print(f"Error creating sample file: {e}")


def main():
    """Main exploration function."""
    print("FinanceQA Dataset Explorer")
    print("=" * 40)
    
    try:
        # Load dataset
        df = load_dataset()
        print(f"✅ Dataset loaded successfully! Shape: {df.shape}")
        
        # Basic exploration
        explore_basic_stats(df)
        
        # Show sample questions
        show_sample_questions(df)
        
        # Analyze by question type
        analyze_by_question_type(df)
        
        # Analyze by company
        analyze_by_company(df)
        
        # Create sample file
        create_sample_file(df)
        
        # Interactive search
        print(f"\n🔍 Interactive Search:")
        print("Enter a search term to find specific questions (or 'quit' to exit):")
        
        while True:
            search_term = input("\nSearch term: ").strip()
            if search_term.lower() == 'quit':
                break
            if search_term:
                search_questions(df, search_term)
        
        print("\n✅ Exploration completed!")
        
    except Exception as e:
        print(f"❌ Error exploring dataset: {e}")
        print("Make sure the dataset is downloaded to data/financeqa_benchmark/")


if __name__ == "__main__":
    main() 