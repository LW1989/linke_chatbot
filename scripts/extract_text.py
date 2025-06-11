#!/usr/bin/env python3
"""
extract_text.py
--------------------------------
Extract specific text passages from HTML files, focusing on content like resolutions and decisions,
while ignoring general HTML content.

Usage:
    python extract_text.py

Dependencies:
    pip install beautifulsoup4
"""

import os
import re
import logging
from bs4 import BeautifulSoup

# === CONFIGURATION ============================================================
INPUT_DIR = "internal_docs"  # Directory containing HTML files
OUTPUT_DIR = "extracted_text"  # Directory to save extracted text
# ==============================================================================

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def extract_text(html_file: str) -> str:
    """
    Extract specific text passages from an HTML file.
    """
    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.extract()

    # Get text
    text = soup.get_text()

    # Break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # Break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # Drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)

    # Extract specific passages (e.g., resolutions, decisions)
    # This is a simple example; you may need to adjust the regex based on your specific needs
    passages = re.findall(r'Beschluss.*?$', text, re.MULTILINE | re.DOTALL)

    return '\n'.join(passages)


def process_files() -> None:
    """
    Process all HTML files in the input directory and save extracted text to the output directory.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for filename in os.listdir(INPUT_DIR):
        if filename.endswith('.html'):
            input_path = os.path.join(INPUT_DIR, filename)
            output_path = os.path.join(OUTPUT_DIR, filename.replace('.html', '.txt'))

            logger.info(f"Processing {filename}")
            extracted_text = extract_text(input_path)

            if extracted_text.strip():  # Only save if the extracted text is not empty
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(extracted_text)
            else:
                logger.warning(f"No text extracted from {filename}, skipping.")

    logger.info(f"Extracted text saved in: {os.path.abspath(OUTPUT_DIR)}")


if __name__ == "__main__":
    process_files() 