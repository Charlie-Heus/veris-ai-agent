#!/usr/bin/env python3
"""
Script to download the FinanceQA dataset from Hugging Face.

This script downloads the FinanceQA dataset and provides utilities for
working with it in the context of our AI agent project.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any

from datasets import load_dataset
import pandas as pd


def download_financeqa_dataset(output_dir: str = "data/financeqa_benchmark") -> Dict[str, Any]:
    """
    Download the FinanceQA dataset from Hugging Face.
    
    Args:
        output_dir: Directory to save the dataset
        
    Returns:
        Dictionary containing dataset information
    """
    print("Downloading FinanceQA dataset from Hugging Face...")
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # Load the dataset
        dataset = load_dataset("AfterQuery/FinanceQA")
        
        print(f"Dataset loaded successfully!")
        print(f"Dataset info: {dataset}")
        
        # Save the dataset in different formats
        test_data = dataset['test']
        
        # Save as JSON
        json_path = output_path / "financeqa_test.json"
        test_data.to_json(json_path, orient='records', indent=2)
        print(f"Saved test data to {json_path}")
        
        # Save as CSV
        csv_path = output_path / "financeqa_test.csv"
        test_data.to_csv(csv_path, index=False)
        print(f"Saved test data to {csv_path}")
        
        # Create a summary
        summary = {
            "total_questions": len(test_data),
            "question_types": test_data['question_type'].count(),
            "companies": test_data['company'].nunique(),
            "file_types": test_data['file_name'].nunique(),
            "output_path": str(output_path)
        }
        
        # Save summary
        summary_path = output_path / "dataset_summary.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"Dataset summary saved to {summary_path}")
        print(f"Summary: {summary}")
        
        return {
            "dataset": dataset,
            "test_data": test_data,
            "summary": summary,
            "output_path": str(output_path)
        }
        
    except Exception as e:
        print(f"Error downloading dataset: {e}")
        return {}


def main():
    """Main function to download the FinanceQA dataset."""
    print("FinanceQA Dataset Downloader")
    print("="*40)
    
    # Download the dataset
    dataset_info = download_financeqa_dataset()
    
    if dataset_info:
        print(f"\nDataset downloaded successfully to: {dataset_info['output_path']}")
        print("You can now use this dataset to test your FinanceQA AI Agent!")
        print("\nTo explore the dataset, run: python scripts/explore_financeqa.py")
    else:
        print("Failed to download dataset. Please check your internet connection and try again.")


if __name__ == "__main__":
    main() 