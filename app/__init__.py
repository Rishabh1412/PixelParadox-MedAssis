from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app=Flask(__name__)
app.config['SECRET_KEY'] = '89d2be80b2a972451fda9bf50e85c94cc374fc79239b966d'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///model.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db=SQLAlchemy(app)
bcrypt=Bcrypt(app)

from app import routes
