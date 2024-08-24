from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
# from flask_login import LoginManager
from flask_socketio import SocketIO, join_room, leave_room, send
from flask_apscheduler import APScheduler
from datetime import datetime
import time


app=Flask(__name__)
app.config['SECRET_KEY'] = '89d2be80b2a972451fda9bf50e85c94cc374fc79239b966d'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///model.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db=SQLAlchemy(app)
bcrypt=Bcrypt(app)
socketio = SocketIO(app)

from app.models import Reminder
from app.reminderFunction import send_email

scheduler=APScheduler()

def check_and_send_emails():
    with app.app_context():
        pending_emails=Reminder.query.filter(Reminder.reminder_time<=datetime.now(), Reminder.sent==False).all()
        for email in pending_emails:
            send_email(email.email_address, email.medicine)
            email.sent=True
            db.session.commit()

scheduler.add_job(id='EmailJob', func=check_and_send_emails, trigger='interval', seconds=60)
scheduler.start()

from app import routes

# if __name__=="__main__":
#     app.run(debug=True)
