import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import schedule
import time

def send_email():
    # Email configuration
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_user = 'anujlearningemail@gmail.com'
    smtp_password = 'nbjyzmasfzjsbbtm'
    from_email = 'anujlearningemail@gmail.com'
    to_email = 'espi3088@gmail.com'
    
    # Create the email
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = 'Scheduled Email'
    body = 'Drink Water'
    msg.attach(MIMEText(body, 'plain'))
    
    # Send the email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
            print('Email sent successfully!')
    except Exception as e:
        print(f'Failed to send email: {e}')

# Schedule the email to be sent at a specific time
schedule.every().day.at("11:45").do(send_email)  # Set the desired time here

while True:
    schedule.run_pending()
    time.sleep(60)  # Wait a minute before checking again
