def format_response_as_table(raw_response):
    # Check if the raw_response is None or empty
    if not raw_response:
        return "<p>No data available to display.</p>"
    
    # Split the response by newlines
    lines = raw_response.split("\n")
    
    # Initialize HTML sections
    formatted_html = ''
    table_html = ''
    formatted_html += "<div style='padding-top: 10px;'>"
    in_table = False
    after_heading = False
    column_names = []

    def clean_text(text):
        """Helper function to remove ** and * from the text."""
        return text.replace("**", "").replace("*", "")

    for line in lines:
        line = line.strip()

        # Check for section headings marked with ##
        if line.startswith("##"):
            after_heading = True
            formatted_html += f'<h3 style="font-weight: bold; margin-top: 20px; margin-bottom: 10px;">{clean_text(line[2:].strip())}</h3>'
            continue

        # Handle titles that are bold but not in table format
        if line.startswith("**") and line.endswith("**"):
            formatted_html += f'<h4 style="font-weight: bold; margin-top: 20px; margin-bottom: 10px;">{clean_text(line)}</h4>'
            continue

        # Formatting the response text before the table
        if not line.startswith("|") and not in_table:
            formatted_line = clean_text(line)
            formatted_html += f'<p style="margin-bottom: 10px;">{formatted_line}</p>'

        # Extract column names from the header row
        if line.startswith("|") and "---" not in line and not column_names:
            column_names = line.split("|")[1:-1]  # Split and ignore the leading and trailing pipes
            continue

        # Start table section after column names are found
        if line.startswith("|---"):
            in_table = True
            table_html += '<table style="width:100%; border-collapse: collapse; margin-top: 10px;"><thead><tr>'
            for header in column_names:
                table_html += f'<th style="border: 1px solid #ddd; padding: 8px; text-align: left; background-color: #f4f4f4;">{clean_text(header.strip())}</th>'
            table_html += '</tr></thead><tbody>'
            continue

        # Table content handling
        if line.startswith("|") and in_table and not line.startswith("|---"):
            columns = line.split("|")[1:-1]  # Split and ignore the leading and trailing pipes
            table_html += '<tr>'
            for column in columns:
                cleaned_column = clean_text(column.strip())
                table_html += f'<td style="border: 1px solid #ddd; padding: 8px;' \
                              f' text-align: left;' \
                              f'">{cleaned_column}</td>'
            table_html += '</tr>'

        elif in_table and line == "":
            in_table = False
            table_html += '</tbody></table>'
            formatted_html += table_html
            table_html = ''  # Reset table_html for the next potential table

    # Close the table if it wasn't closed already
    if '</tbody></table>' not in table_html and table_html:
        table_html += '</tbody></table>'
        formatted_html += table_html
    formatted_html += "</div>"

    return formatted_html
