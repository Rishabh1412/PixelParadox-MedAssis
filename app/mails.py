import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(to_address, subject, message):
    from_address = "anujlearningemail@gmail.com"  
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_user = "anujlearningemail@gmail.com"
    smtp_password = "nbjyzmasfzjsbbtm"

    # Create the email message container
    msg = MIMEMultipart('alternative')
    msg['From'] = from_address
    msg['To'] = to_address
    msg['Subject'] = subject

    # Attach both plain text and HTML versions of the message
    text_part = MIMEText(message, 'plain')
    html_part = MIMEText(f"<html><body>{message}</body></html>", 'html')
    msg.attach(text_part)
    msg.attach(html_part)

    try:
        # Connect to the Gmail SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Start TLS encryption (corrected method call)
        server.login(smtp_user, smtp_password)  # Log in to the SMTP server
        server.sendmail(from_address, to_address, msg.as_string())  # Send the email
        server.quit()  # Close the connection to the server
        print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")
