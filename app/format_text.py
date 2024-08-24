import re

def format_text(text):
    # Replace ** with <strong> and </strong> tags
    formatted_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    
    # Add <br> tags after each numbered point
    formatted_text = re.sub(r'(\d+\.\s)', r'<br><br>\1', formatted_text)
    
    # Replace multiple <br> tags with a single <br> for consistent spacing
    formatted_text = re.sub(r'(<br>\s*){2,}', '<br>', formatted_text)

    formatted_text = re.sub(r"\s\*\s", r"<br>", formatted_text)


    # Clean up any leading or trailing whitespace
    formatted_text = formatted_text.strip()
    
    return formatted_text