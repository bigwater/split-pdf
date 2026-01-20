# PDF Splitter Tool

A Python tool that splits a multi-section PDF into separate PDFs based on predefined components.

## Features

- **Automatic Section Detection**: Finds and extracts sections like "Project Summary", "Project Description", etc.
- **Clean Output**: Creates separate PDF files for each component
- **Flexible Output**: Specify custom output directory
- **Error Handling**: Gracefully handles edge cases

## Supported Components

The tool recognizes and separates the following sections:

1. Project Summary
2. Project Description
3. References Cited
4. Data Management and Sharing Plan
5. Mentoring Plan
6. Project Personnel and Partner Organizations
7. Facilities, Equipment and Other Resources
8. Synergistic Activities

## Splitting Rules

### Fixed Components (Order Guaranteed)
- **Project Summary**: Page 1 (automatic)
- **Project Description**: Pages 2-16 (automatic, always 15 pages)
- **References Cited**: Pages 17+ until next section (automatic detection)

### Variable Components (Order Not Determined)
- **Data Management and Sharing Plan**
- **Mentoring Plan**
- **Project Personnel and Partner Organizations**
- **Facilities, Equipment and Other Resources**
- **Synergistic Activities**

### Detection Algorithm
1. Extract pages 1, 2-16 automatically for Summary and Description
2. Extract pages 17+ as References Cited until next section is detected
3. Detect remaining variable sections using fuzzy matching (approx. 70% similarity)
4. Each section ends where the next one begins
5. Last section extends to the end of the document

### Key Requirements
- **Each component must start on a new page** (guaranteed in input)
- **Component names are approximate** (fuzzy matching handles variations like "Project Summary" vs "Summary of the Project")
- **No explicit section headers required** (except for the 5 variable components)

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Command Line

```bash
python pdf_splitter.py input.pdf output_directory
```

Example:
```bash
python pdf_splitter.py proposal.pdf ./split_pdfs
```

### As a Python Module

```python
from pdf_splitter import split_pdf

results = split_pdf("proposal.pdf", "output_dir")
for component_name, filepath in results:
    print(f"{component_name}: {filepath}")
```

## How It Works

1. Reads the input PDF file
2. Scans each page for component section headers
3. Identifies page boundaries where each section begins
4. Extracts pages for each section into a separate PDF file
5. Saves output PDFs with sanitized component names

## Output

Output files are named based on the component, with spaces replaced by underscores:
- `project_summary.pdf`
- `project_description.pdf`
- `references_cited.pdf`
- `data_management_and_sharing_plan.pdf`
- `mentoring_plan.pdf`
- `project_personnel_and_partner_organizations.pdf`
- `synergistic_activities.pdf`

## Requirements

- Python 3.6+
- PyPDF2

## Customization

To modify the component names or add new sections, edit the `COMPONENTS` list in `pdf_splitter.py`:

```python
COMPONENTS = [
    "Project Summary",
    "Project Description",
    # ... add or modify components here
]
```

## Limitations

- Each component must start on a new page (as required)
- Component names are matched case-insensitively
- OCR is not performed (text must be selectable in the PDF)

## License

MIT
