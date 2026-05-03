import fitz  # PyMuPDF

def extract_text_with_spans(pdf_bytes: bytes):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    blocks = []
    current_char_index = 0
    
    for page_num, page in enumerate(doc):
        # Extract blocks of text
        page_blocks = page.get_text("blocks")
        for b in page_blocks:
            if b[6] == 0:  # Ensure it's a text block, not an image
                text = b[4].replace('\n', ' ').strip()
                if text:
                    start_idx = current_char_index
                    end_idx = current_char_index + len(text)
                    blocks.append({
                        "text": text,
                        "start_char": start_idx,
                        "end_char": end_idx,
                        "page": page_num + 1
                    })
                    current_char_index = end_idx + 1 # +1 for space
    return blocks