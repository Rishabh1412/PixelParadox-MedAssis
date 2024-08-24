import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(to_email, medicine_name):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_user = 'anujlearningemail@gmail.com'
    smtp_password = 'nbjyzmasfzjsbbtm'
    from_email = 'anujlearningemail@gmail.com'
    
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = 'Medicine Reminder'
    
    body = f'''
    <html>
    <body>
        <h2 style="color: #2E86C1;">Medicine Reminder</h2>
        <p>Hi there,</p>
        <p>This is a friendly reminder to take your medicine: <strong>{medicine_name}</strong>.</p>
        <p>It's important to stay on track with your medication to ensure the best health outcomes.</p>
        <p>If you've already taken your medicine, you can disregard this message.</p>
        <br>
        <p>Stay healthy!</p>
        <p>Best regards,<br>From Medassis</p>
    </body>
    </html>
    '''
    
    msg.attach(MIMEText(body, 'html'))
    
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
            print('Email sent successfully!')
    except Exception as e:
        print(f'Failed to send email: {e}')

