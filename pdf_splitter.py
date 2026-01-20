"""
PDF Splitter Tool

Splits a PDF document into multiple PDFs based on component sections.
Each component starts on a new page.
"""

import PyPDF2
import re
from pathlib import Path
from typing import List, Dict, Tuple
from difflib import SequenceMatcher


class PDFSplitter:
    """Splits a PDF into separate PDFs based on section headers."""
    
    # Component names to search for (order matters for fallback matching)
    COMPONENTS = [
        "Project Summary",
        "Project Description",
        "References Cited",
        "Data Management and Sharing Plan",
        "Mentoring Plan",
        "Project Personnel and Partner Organizations",
        "Facilities, Equipment and Other Resources",
        "Synergistic Activities"
    ]
    
    def __init__(self, input_pdf_path: str):
        """
        Initialize the PDF splitter.
        
        Args:
            input_pdf_path: Path to the input PDF file
        """
        self.input_pdf_path = Path(input_pdf_path)
        if not self.input_pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {input_pdf_path}")
        
        self.reader = PyPDF2.PdfReader(self.input_pdf_path)
        self.num_pages = len(self.reader.pages)
    
    def extract_text_from_page(self, page_num: int) -> str:
        """Extract text from a specific page."""
        try:
            return self.reader.pages[page_num].extract_text()
        except Exception as e:
            print(f"Warning: Could not extract text from page {page_num}: {e}")
            return ""
    
    def find_section_boundaries(self, similarity_threshold: float = 0.7) -> Dict[str, int]:
        """
        Find which page each component starts on using fuzzy matching.
        
        Args:
            similarity_threshold: Minimum similarity score (0-1) to consider a match
        
        Returns:
            Dictionary mapping component name to page number (0-indexed)
        """
        return self.find_section_boundaries_from_page(0, self.COMPONENTS, similarity_threshold)
    
    def find_section_boundaries_from_page(self, start_page: int, components: List[str],
                                          similarity_threshold: float = 0.7) -> Dict[str, int]:
        """
        Find which page each component starts on, starting from a given page.
        
        Args:
            start_page: Page to start searching from (0-indexed)
            components: List of component names to search for
            similarity_threshold: Minimum similarity score (0-1) to consider a match
        
        Returns:
            Dictionary mapping component name to page number (0-indexed)
        """
        section_pages = {}
        
        for page_num in range(start_page, self.num_pages):
            text = self.extract_text_from_page(page_num)
            text_lines = text.split('\n')
            
            # Check each line on the page for approximate component matches
            for line in text_lines:
                line_lower = line.lower().strip()
                if not line_lower or len(line_lower) < 5:  # Skip empty lines or very short lines
                    continue
                
                # Check each component name
                for component in components:
                    if component not in section_pages:
                        # Use fuzzy matching
                        similarity = self._calculate_similarity(
                            line_lower, 
                            component.lower()
                        )
                        
                        if similarity >= similarity_threshold:
                            section_pages[component] = page_num
                            print(f"Found '{component}' on page {page_num + 1} "
                                  f"(match: '{line[:60]}...' with score {similarity:.2f})")
                            break  # Found a match for this line, move to next line
        
        return section_pages
    
    @staticmethod
    def _calculate_similarity(text1: str, text2: str) -> float:
        """
        Calculate similarity between two strings using SequenceMatcher.
        
        Args:
            text1: First string
            text2: Second string
        
        Returns:
            Similarity score from 0 to 1
        """
        return SequenceMatcher(None, text1, text2).ratio()
    
    def split_pdf(self, output_dir: str = None, similarity_threshold: float = 0.7) -> List[Tuple[str, Path]]:
        """
        Split the PDF into separate files for each component.
        
        Args:
            output_dir: Directory to save the split PDFs. Defaults to current directory.
            similarity_threshold: Minimum similarity score (0-1) to consider a match for fuzzy matching
        
        Returns:
            List of tuples (component_name, output_file_path)
        """
        if output_dir is None:
            output_dir = "."
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Handle fixed components first
        results = []
        current_page = 0
        
        # 1. Overview/Summary - First page
        results.append(self._extract_and_save_component(
            "Project Summary",
            0,
            1,
            output_path
        ))
        current_page = 1
        
        # 2. Description - Always 15 pages starting from page 2 (index 1)
        results.append(self._extract_and_save_component(
            "Project Description",
            1,
            16,  # Pages 2-16 (15 pages total)
            output_path
        ))
        current_page = 16
        
        # 3. Find remaining sections using fuzzy matching (order not determined)
        remaining_components = [
            "Data Management and Sharing Plan",
            "Mentoring Plan",
            "Project Personnel and Partner Organizations",
            "Facilities, Equipment and Other Resources",
            "Synergistic Activities"
        ]
        
        section_pages = self.find_section_boundaries_from_page(
            current_page,
            remaining_components,
            similarity_threshold
        )
        
        print(f"\nDetected {len(section_pages)} additional sections:")
        for component, page in sorted(section_pages.items(), key=lambda x: x[1]):
            print(f"  - {component}: page {page + 1}")
        
        # Sort and extract remaining sections by page order (not by component order)
        sorted_sections = sorted(section_pages.items(), key=lambda x: x[1])
        
        for idx, (component_name, start_page) in enumerate(sorted_sections):
            # Determine end page
            if idx + 1 < len(sorted_sections):
                end_page = sorted_sections[idx + 1][1]  # Start of next section
            else:
                end_page = self.num_pages  # Last page of document
            
            results.append(self._extract_and_save_component(
                component_name,
                start_page,
                end_page,
                output_path
            ))
        
        return results
    
    def _extract_and_save_component(self, component_name: str, start_page: int, 
                                     end_page: int, output_path: Path) -> Tuple[str, Path]:
        """Extract pages and save as PDF file."""
        writer = PyPDF2.PdfWriter()
        
        # Add pages from start_page to end_page (exclusive)
        for page_num in range(start_page, min(end_page, self.num_pages)):
            writer.add_page(self.reader.pages[page_num])
        
        # Generate output filename
        safe_name = self._sanitize_filename(component_name)
        output_file = output_path / f"{safe_name}.pdf"
        
        # Write to file
        with open(output_file, 'wb') as f:
            writer.write(f)
        
        num_pages = min(end_page, self.num_pages) - start_page
        print(f"Created: {output_file} (pages {start_page + 1}-{min(end_page, self.num_pages)}, {num_pages} pages)")
        
        return (component_name, output_file)
    
    @staticmethod
    def _sanitize_filename(name: str) -> str:
        """Convert component name to safe filename."""
        # Replace spaces and special characters with underscores
        safe_name = re.sub(r'[^\w\s-]', '', name)
        safe_name = re.sub(r'[-\s]+', '_', safe_name)
        return safe_name.lower()


def split_pdf(input_pdf: str, output_dir: str = None, similarity_threshold: float = 0.7) -> List[Tuple[str, Path]]:
    """
    Convenience function to split a PDF.
    
    Args:
        input_pdf: Path to input PDF
        output_dir: Directory for output PDFs (optional)
        similarity_threshold: Minimum similarity score (0-1) for fuzzy matching
    
    Returns:
        List of tuples (component_name, output_file_path)
    """
    splitter = PDFSplitter(input_pdf)
    return splitter.split_pdf(output_dir, similarity_threshold)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python pdf_splitter.py <input_pdf> [output_dir]")
        print("\nExample: python pdf_splitter.py proposal.pdf ./output")
        sys.exit(1)
    
    input_pdf = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "split_pdfs"
    
    print(f"Splitting {input_pdf}...")
    results = split_pdf(input_pdf, output_dir)
    
    print(f"\nSuccessfully created {len(results)} PDFs:")
    for component, filepath in results:
        print(f"  - {component}: {filepath}")
