"""Command line interface for Mistral OCR."""

import argparse
import sys
import re
import base64
from pathlib import Path
import os
from mistralai import Mistral
from dotenv import load_dotenv

def extract_arxiv_id(url):
    """Extract arXiv ID from URL."""
    pattern = r'(\d{4}\.\d{4,5})'
    match = re.search(pattern, url)
    return match.group(1) if match else None

def parse_pages(pages_str):
    """Parse pages string into a list of integers."""
    if not pages_str:
        return None
    
    pages = []
    parts = pages_str.split(',')
    
    for part in parts:
        part = part.strip()
        if '-' in part:
            start, end = map(int, part.split('-'))
            pages.extend(range(start, end + 1))
        else:
            pages.append(int(part))
    
    return sorted(list(set(pages)))  # Remove duplicates and sort

def process_document(client, source, pages=None, include_base64=False):
    """Process document from URL or local file with page selection and base64 option."""
    # Check if source is a local file
    if os.path.isfile(source):
        # For local files, convert to base64 and use URL endpoints
        with open(source, "rb") as f:
            file_content = f.read()
            
        # For image files
        if source.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            document = {
                "type": "image_url",
                "image_url": f"data:image/{source.split('.')[-1]};base64,{base64.b64encode(file_content).decode('utf-8')}"
            }
        else:
            # For PDFs and other documents
            document = {
                "type": "document_url",
                "document_url": f"data:application/pdf;base64,{base64.b64encode(file_content).decode('utf-8')}",
                "document_name": os.path.basename(source)
            }
    else:
        # For URLs
        if source.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            document = {
                "type": "image_url",
                "image_url": source
            }
        else:
            document = {
                "type": "document_url",
                "document_url": source,
                "document_name": os.path.basename(source)
            }
    
    if pages:
        document["pages"] = pages
    
    print(f"Processing OCR with document type: {document['type']}, include_image_base64={include_base64}")
    return client.ocr.process(
        model="mistral-ocr-latest",
        document=document,
        include_image_base64=include_base64
    )

def save_output(identifier, ocr_response, include_images=False):
    """Save OCR output to folder structure with image debugging."""
    if not identifier or not ocr_response or not hasattr(ocr_response, 'pages'):
        print("Error: Invalid OCR response or identifier")
        return
    
    # Create output directory
    output_dir = Path(f"output_{identifier}")
    output_dir.mkdir(exist_ok=True)
    
    # Process each page
    for page in ocr_response.pages:
        page_num = page.index
        
        # Save Markdown
        md_filename = output_dir / f"page_{page_num:03d}.md"
        try:
            with open(md_filename, 'w', encoding='utf-8') as f:
                f.write(page.markdown)
            print(f"Saved Markdown to {md_filename}")
        except Exception as e:
            print(f"Error saving Markdown file {md_filename}: {e}")
        
        # Handle images if requested
        if include_images and hasattr(page, 'images') and page.images:
            print(f"Processing {len(page.images)} images on page {page_num}")
            for idx, image_data in enumerate(page.images):
                if hasattr(image_data, 'image_base64') and image_data.image_base64:
                    # Strip the data URI prefix if present
                    base64_str = image_data.image_base64
                    if base64_str.startswith('data:image/jpeg;base64,'):
                        base64_str = base64_str[len('data:image/jpeg;base64,'):]
                    img_filename = output_dir / f"page_{page_num:03d}_img_{idx:03d}.jpg"
                    try:
                        with open(img_filename, 'wb') as f:
                            f.write(base64.b64decode(base64_str))
                    except Exception as e:
                        print(f"Error saving image {img_filename}: {e}")

def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description='Extract text from images and documents using Mistral OCR')
    parser.add_argument('source', type=str, help='Source to process (URL, image file, or PDF file)')
    parser.add_argument('--pages', type=str, help='Pages to process (e.g., "0", "0-2", "0,2,4")')
    parser.add_argument('--images', action='store_true', help='Include base64 images in output')
    
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        print("Error: MISTRAL_API_KEY not found in .env file", file=sys.stderr)
        sys.exit(1)
    
    # Initialize Mistral client
    client = Mistral(api_key=api_key)
    
    try:
        source = args.source
        
        # Determine if source is a URL or local file and set identifier
        if source.startswith(('http://', 'https://')):
            # Source is a URL
            identifier = extract_arxiv_id(source)
            if not identifier:
                print("Warning: Could not extract arXiv ID from URL, using URL as identifier")
                identifier = source.split('/')[-1].split('.')[0]  # Extract filename without extension
        else:
            # Source is a local file
            if not os.path.exists(source):
                print(f"Error: File '{source}' does not exist", file=sys.stderr)
                sys.exit(1)
            identifier = Path(source).stem  # Use filename without extension
        
        # Parse pages argument
        pages = parse_pages(args.pages)
        
        # Process the document
        ocr_response = process_document(client, source, pages, args.images)
        
        if ocr_response and ocr_response.pages:
            print("OCR processing completed successfully")
            save_output(identifier, ocr_response, include_images=args.images)
        else:
            print("Error: OCR processing failed or returned no content", file=sys.stderr)
            sys.exit(1)
            
    except Exception as e:
        print(f"Error during OCR processing: {e}", file=sys.stderr)
        sys.exit(1)
    
if __name__ == '__main__':
    main() 