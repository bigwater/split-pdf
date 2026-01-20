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
7. Synergistic Activities

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
