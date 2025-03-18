import pdfplumber
import re

def extract_text_from_pdf(file_path, clean=True, word_count=False, start_page=None, end_page=None):
    """
    Extract text from PDF with optional cleaning, word count, and page range.
    
    Args:
        file_path (str): Path to the PDF file
        clean (bool): Whether to clean the extracted text
        word_count (bool): Whether to return word count information
        start_page (int, optional): First page to extract (1-based index). None means start from beginning.
        end_page (int, optional): Last page to extract (1-based index). None means extract to end.
    
    Returns:
        text (str) or tuple: Extracted text or (text, count) if word_count is True
    """
    with pdfplumber.open(file_path) as pdf:
        # Convert 1-based page indices to 0-based for pdfplumber
        pdf_start = (start_page - 1) if start_page is not None else 0
        pdf_end = end_page if end_page is not None else len(pdf.pages)
        
        # Ensure page indices are within bounds
        pdf_start = max(0, min(pdf_start, len(pdf.pages) - 1))
        pdf_end = max(pdf_start + 1, min(pdf_end, len(pdf.pages)))
        
        text = ''
        for i in range(pdf_start, pdf_end):
            text += pdf.pages[i].extract_text() + "\n"
    
    if clean:
        text = clean_pdf_text(text)
    
    if word_count:
        count = count_words(text)
        return text, count
    
    return text

def count_words(text):
    """
    Count the number of words in the text.
    
    Args:
        text (str): Text to count words in
    
    Returns:
        dict: Dictionary with word count statistics
    """
    # Remove punctuation marks and normalize spaces to get accurate word count
    clean_text = re.sub(r'[^\w\s]', ' ', text)
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    words = clean_text.split()
    
    return {
        'total_words': len(words),
        'unique_words': len(set(words)),
        'characters': len(text),
        'characters_no_spaces': len(text.replace(' ', '').replace('\n', '')),
    }

def clean_pdf_text(text):
    """Apply all cleaning operations to extracted PDF text."""
    text = remove_page_numbers(text)
    text = normalize_whitespace(text)
    text = remove_hidden_characters(text)
    text = join_hyphenated_words(text)
    return text

def remove_page_numbers(text):
    """Remove common page number patterns."""
    # Remove standalone numbers (typical page numbers)
    text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
    
    # Remove "Page X" or "Page X of Y" patterns
    text = re.sub(r'\n\s*[Pp]age\s+\d+(\s+of\s+\d+)?\s*\n', '\n', text)
    
    return text

def normalize_whitespace(text):
    """Normalize whitespace in text."""
    # Replace multiple spaces with a single space
    text = re.sub(r' +', ' ', text)
    
    # Replace multiple newlines with a single newline
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Remove whitespace at the beginning and end of lines
    text = re.sub(r'^\s+|\s+$', '', text, flags=re.MULTILINE)
    
    return text

def remove_hidden_characters(text):
    """Remove hidden and control characters."""
    # Remove non-printable ASCII characters (except newlines and tabs)
    text = re.sub(r'[\x00-\x09\x0b\x0c\x0e-\x1f\x7f]', '', text)
    
    # Remove zero-width characters and other problematic Unicode
    text = re.sub(r'[\u200b\u200c\u200d\ufeff\u2060\u00ad]', '', text)
    
    return text

def join_hyphenated_words(text):
    """Join words that are hyphenated at line breaks."""
    # Pattern matches: word-\n word
    text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)
    
    return text

