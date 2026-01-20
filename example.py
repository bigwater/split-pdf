#!/usr/bin/env python3
"""
Example usage of the PDF Splitter tool
"""

from pdf_splitter import split_pdf

# Example: Split a PDF
if __name__ == "__main__":
    # Replace 'proposal.pdf' with your actual PDF file
    input_file = "proposal.pdf"
    output_directory = "split_pdfs"
    
    try:
        results = split_pdf(input_file, output_directory)
        print(f"\nSuccessfully split PDF into {len(results)} components:")
        for component_name, output_path in results:
            print(f"  ✓ {component_name}")
    except FileNotFoundError as e:
        print(f"Error: {e}")
