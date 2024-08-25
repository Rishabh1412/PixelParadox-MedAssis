from app import db, session
from app import bcrypt
from flask_login import UserMixin
from datetime import datetime,timedelta


class User(db.Model, UserMixin):
    id=db.Column(db.Integer(), primary_key=True)
    username=db.Column(db.String(length=30), nullable=False, unique=True)
    email_address=db.Column(db.String(length=50), nullable=False, unique=True)
    password_hash=db.Column(db.String(length=60), nullable=False)
    checkups=db.relationship('Checkup', backref='patient_checked', lazy=True)
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

class Doctor(db.Model, UserMixin):
    id=db.Column(db.Integer(), primary_key=True)
    username=db.Column(db.String(length=30), nullable=False, unique=True)
    email_address=db.Column(db.String(length=50), nullable=False, unique=True)
    password_hash=db.Column(db.String(length=60), nullable=False)
    specialization=db.Column(db.String(length=100))
    pincode=db.Column(db.Integer())
    gender=db.Column(db.String(length=50), nullable=True)
    age=db.Column(db.Integer())
    availability=db.Column(db.String(), default="Yes")
    phone=db.Column(db.Integer(), nullable=True)
    city=db.Column(db.String(length=50), nullable=True)
    slots=db.relationship('Appointment', backref="appointments", lazy=True)

    @property
    def password(self):
        return self.password
    
    @password.setter
    def password(self, plain_text_password):
        self.password_hash=bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)
    
class Shop(db.Model, UserMixin):
    id=db.Column(db.Integer(), primary_key=True)
    username=db.Column(db.String(length=30), nullable=False, unique=True)
    email_address=db.Column(db.String(length=50), nullable=False, unique=True)
    password_hash=db.Column(db.String(length=60), nullable=False)

    @property
    def password(self):
        return self.password
    
    @password.setter
    def password(self, plain_text_password):
        self.password_hash=bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)

class Appointment(db.Model):
    id=db.Column(db.Integer(), primary_key=True)
    slot1=db.Column(db.Boolean(), default=False)    #10-1030
    slot2=db.Column(db.Boolean(), default=False)    #1030-11
    slot3=db.Column(db.Boolean(), default=False)    
    slot4=db.Column(db.Boolean(), default=False)    
    slot5=db.Column(db.Boolean(), default=False)    #12-1230
    slot6=db.Column(db.Boolean(), default=False)    #1230-1
    slot7=db.Column(db.Boolean(), default=False)    #4-430
    slot8=db.Column(db.Boolean(), default=False)    #430-5
    slot9=db.Column(db.Boolean(), default=False)    #5-530
    slot10=db.Column(db.Boolean(), default=False)   #530-6
    slot11=db.Column(db.Boolean(), default=False)   #6-630
    slot12=db.Column(db.Boolean(), default=False)   #630-7
    slot13=db.Column(db.Boolean(), default=False)   #7-730
    slot14=db.Column(db.Boolean(), default=False)   #730-8
    slot15=db.Column(db.Boolean(), default=False)   #8-830
    slot16=db.Column(db.Boolean(), default=False)   #830-9
    slot17=db.Column(db.Boolean(), default=False)   #9-930
    slot18=db.Column(db.Boolean(), default=False)   #930-10
    doctor_id=db.Column(db.Integer(), db.ForeignKey('doctor.id'))

class Checkup(db.Model):
    form_id=db.Column(db.Integer(), primary_key=True)
    name=db.Column(db.String(), nullable=False)
    age=db.Column(db.Integer(), nullable=False)
    gender=db.Column(db.String(), nullable=False)
    smoking_history=db.Column(db.String(), nullable=False)
    hypertension=db.Column(db.Integer(), nullable=False)
    heart_disease=db.Column(db.Integer(), nullable=False)
    blood_glucose=db.Column(db.Float(), nullable=False)
    weight=db.Column(db.Float(), nullable=False)
    height=db.Column(db.Float(), nullable=False)
    hba1c=db.Column(db.String(), nullable=False)
    diabetes=db.Column(db.Integer(), nullable=False)
    patient_id=db.Column(db.Integer(), db.ForeignKey('user.id'))

class Kidney(db.Model):
    form_id=db.Column(db.Integer(), primary_key=True)
    name=db.Column(db.String(), nullable=False)
    age=db.Column(db.Integer(), nullable=False)
    gender=db.Column(db.String(), nullable=False)
    height=db.Column(db.Float(), nullable=False)
    weight=db.Column(db.Float(), nullable=False)
    smok_alc=db.Column(db.String(), nullable=False)
    physical_act=db.Column(db.Integer(), nullable=False)
    kidney_diet=db.Column(db.Integer(), nullable=False)
    fhkd=db.Column(db.String(), nullable=False)
    fhh=db.Column(db.String(), nullable=False)
    fhd=db.Column(db.String(), nullable=False)
    urinary=db.Column(db.String(), nullable=False)
    systolic_bp=db.Column(db.Integer(), nullable=False)
    diastolic_bp=db.Column(db.Integer(), nullable=False)
    blood_sugar=db.Column(db.Integer(), nullable=False)
    hba1c=db.Column(db.Float(), nullable=False)
    serum=db.Column(db.Float(), nullable=False)
    bun_lvl=db.Column(db.Float(), nullable=False)
    gfr=db.Column(db.Float(), nullable=False)
    protein_urine=db.Column(db.Float(), nullable=False)
    sodium_electrolyte=db.Column(db.Float(), nullable=False)
    potassium_electrolyte=db.Column(db.Float(), nullable=False)
    hemoglobin=db.Column(db.Float(), nullable=False)
    cholesterol=db.Column(db.Float(), nullable=False)
    diuretics=db.Column(db.String(), nullable=False)
    edema=db.Column(db.String(), nullable=False)
    muscle_cramps=db.Column(db.String(), nullable=False)
    itching=db.Column(db.String(), nullable=False)
    kidney_per=db.Column(db.Float(), nullable=False)
    patient_id=db.Column(db.Integer(), db.ForeignKey('user.id'))

class Liver(db.Model):
    form_id=db.Column(db.Integer(), primary_key=True)
    name=db.Column(db.String(), nullable=False)
    age=db.Column(db.Integer(), nullable=False)
    gender=db.Column(db.String(), nullable=False)
    total_protein=db.Column(db.Float(), nullable=False)
    albumin=db.Column(db.Float(), nullable=False)
    ag_ratio=db.Column(db.Float(), nullable=False)
    total_bilirubin=db.Column(db.Float(), nullable=False)
    direct_bilirubin=db.Column(db.Float(), nullable=False)
    alkaline_phosphate=db.Column(db.Integer(), nullable=False)
    sgpt=db.Column(db.Integer(), nullable=False)
    sgot=db.Column(db.Integer(), nullable=False)
    height=db.Column(db.Float(), nullable=False)
    weight=db.Column(db.Float(), nullable=False)
    liver_per=db.Column(db.Float(), nullable=False)
    patient_id=db.Column(db.Integer(), db.ForeignKey('user.id'))
    
class Reminder(db.Model):
    reminder_id=db.Column(db.Integer(), primary_key=True)
    #name=db.Column(db.String(), nullable=False)
    email_address=db.Column(db.String(length=50), nullable=False)
    medicine=db.Column(db.String(length=50), nullable=False)
    reminder_time=db.Column(db.DateTime(), nullable=False)
    sent=db.Column(db.Boolean(), default=False)
    

class Message(db.Model):
    __tablename__ = 'message'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    author = db.relationship('User', backref=db.backref('messages', lazy=True))

class FormMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    medicine_name = db.Column(db.String(120), nullable=False)
    user_name = db.Column(db.String(120), nullable=False)
    user_pincode = db.Column(db.String(10), nullable=False)
    user_city = db.Column(db.String(120), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=(datetime.utcnow())+ timedelta(hours=5, minutes=30))
    location = db.Column(db.String(120), nullable=True)
    shop_name = db.Column(db.String(120), nullable=True)
    msg_type = db.Column(db.String(10),nullable=True)
    price=db.Column(db.Float(),nullable=True)

