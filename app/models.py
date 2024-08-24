from app import db, session
from app import bcrypt
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id=db.Column(db.Integer(), primary_key=True)
    username=db.Column(db.String(length=30), nullable=False, unique=True)
    email_address=db.Column(db.String(length=50), nullable=False, unique=True)
    password_hash=db.Column(db.String(length=60), nullable=False)
    gender=db.Column(db.String(length=50), nullable=True)
    age=db.Column(db.Integer(), nullable=True)
    height=db.Column(db.Float(), nullable=True)
    weight=db.Column(db.Float(), nullable=True)
    pincode=db.Column(db.Integer(), nullable=True)
    phone=db.Column(db.Integer(), nullable=True)
    city=db.Column(db.String(length=50), nullable=True)

    @property
    def password(self):
        return self.password
    
    @password.setter
    def password(self, plain_text_password):
        self.password_hash=bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)
