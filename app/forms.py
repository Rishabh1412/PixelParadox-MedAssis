from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,RadioField,IntegerField,SelectField,DecimalField,FileField,DateTimeField,TextAreaField,FloatField,DateField,HiddenField
from wtforms.validators import Length, Email, Optional, DataRequired, ValidationError
from app import app
from app.models import User


class DiabetesForm(FlaskForm):

    username=StringField('Name:',validators=[DataRequired(),Length(max=100)])
    gender=RadioField('Gender:',validators=[DataRequired()],choices=['Male','Female'])
    age=IntegerField('Age:',validators=[DataRequired()])
    address=StringField('Address:',validators=[DataRequired(),Length(max=250)])
    pincode=IntegerField('Pincode:',validators=[DataRequired()])
    hypertension=RadioField('Hypertension:',validators=[DataRequired()],choices=['Yes','No'])
    previousHeartDisease=RadioField('Previous Heart Disease:',validators=[DataRequired()],choices=['Yes','No'])
    smoking_History=SelectField("Smoking History:",validators=[DataRequired()],choices=[('never','Never'),('former','Former'),('current','Current'),('notcurrent','Not Current'),('ever','Ever'),('other','Other')])
    weight=DecimalField("Weight (in kg):",validators=[DataRequired()],places=2)
    height=DecimalField("Height (in m):",validators=[DataRequired()],places=2)
    hba1clvl=SelectField("HbA1c Level:",validate_choice=[DataRequired()],choices=[('Below 3','below 3'),('3-4','3-4'),('4-5','4-5'),('5-6','5-6'),('6-7','6-7'),('7-8','7-8'),('8-9','8-9'),('Above 9','above 9')])
    blood_glucose=IntegerField('Blood Glucose Level:',validators=[DataRequired()])
    # email=StringField('Email',validators=[DataRequired(),Email(),Length(max=50)])
    phone=IntegerField('Phone Number:',validators=[DataRequired()])
    submit=SubmitField('Submit')

class LiverForm(FlaskForm):
    name=StringField('Name:',validators=[DataRequired(),Length(max=100)])
    age=IntegerField('Age:',validators=[DataRequired()])
    gender=RadioField('Gender:',validators=[DataRequired()],choices=['Male','Female'])
    address=StringField('Address:',validators=[DataRequired(),Length(max=250)])
    pincode=IntegerField('Pincode:',validators=[DataRequired()])
    total_protein=DecimalField('Total Proteins (g/dL):',validators=[DataRequired()],places=2)
    albumin=DecimalField('Albumin (g/dL):',validators=[DataRequired()],places=2)
    ag_ratio=DecimalField('A/G Ratio:',validators=[DataRequired()],places=2)
    total_bilirubin=DecimalField('Total Bilirubin (mg/dl):',validators=[DataRequired()],places=2)
    direct_bilirubin=DecimalField('Direct Bilirubin (mg/dl):',validators=[DataRequired()],places=2)
    alkaline_phosphate=IntegerField('Alkaline Phosphate (IU/L):',validators=[DataRequired()])
    sgpt=IntegerField('SGPT (U/L):',validators=[DataRequired()])
    sgot=IntegerField('SGOT (U/L):',validators=[DataRequired()])
    height=DecimalField("Height (in m):",validators=[DataRequired()],places=2)
    weight=DecimalField("Weight (in kg):",validators=[DataRequired()],places=2)
    phone=IntegerField('Phone Number:',validators=[DataRequired()])
    submit=SubmitField('Submit')

class KidneyForm(FlaskForm):
    username=StringField('Name:',validators=[DataRequired(),Length(max=100)])
    gender=RadioField('Gender:',validators=[DataRequired()],choices=['Male','Female'])
    height=DecimalField("Height (in m):",validators=[DataRequired()],places=2)
    weight=DecimalField("Weight (in kg):",validators=[DataRequired()],places=2)
    smoke_alco=RadioField('Smoking and Alcohol History:',validators=[DataRequired()],choices=['Smoking','Alcohol','Both','None'])
    age=IntegerField('Age:',validators=[DataRequired()])
    physical_activity=IntegerField('Physical Activity (Weekly):',validators=[DataRequired()])
    kidney_diet_score=IntegerField('Kidney Diet Score (0-10):',validators=[DataRequired()])
    fhkd=RadioField("Famliy History Kidney Disease:",validators=[DataRequired()],choices=['Yes','No'])
    fhh=RadioField("Famliy History Hypertension:",validators=[DataRequired()],choices=['Yes','No'])
    fhd=RadioField("Famliy History Diabetes:",validators=[DataRequired()],choices=['Yes','No'])

    urinary_tract=RadioField('Urinary Tract Infections:',validators=[DataRequired()],choices=['Yes','No'])
    systoyic_bp=IntegerField('Systoyic BP(mmHg):',validators=[DataRequired()])
    diastotic_bp=IntegerField('Diastotic BP(mmHg):',validators=[DataRequired()])
    fasting_blood_sugar=DecimalField('Fasting Blood Sugar:',validators=[DataRequired()],places=2)
    hba1clvl=DecimalField("HbA1c Level:",validators=[DataRequired()],places=2)
    serum_creative=DecimalField('Serum Creatinine(mg/dL):',validators=[DataRequired()],places=2)
    bunlvl=DecimalField('BUN Level:',validators=[DataRequired()],places=2)
    gfr=DecimalField('GFR (ml/min/1.73m^2):',validators=[DataRequired()],places=2)
    protein_in_urine=DecimalField('Protein in Urine(g/day):',validators=[DataRequired()],places=2)
    serum_electrolyes_sodium=DecimalField('Serum Electrolytes Sodium(mEq/L):',validators=[DataRequired()],places=2)
    serum_electrolyes_potassium=DecimalField('Serum Electrolytes Potassium(mEq/L):',validators=[DataRequired()],places=2)
    haemoglobin_lvl=DecimalField('Haemoglobin Level(g/dL):',validators=[DataRequired()],places=2)
    cholestrol_lvl=DecimalField('Cholestrol Level(mg/dL):',validators=[DataRequired()],places=2)
    diuretics=RadioField('Diuretics:',validators=[DataRequired()],choices=['Yes','No'])
    edema=RadioField('Edema:',validators=[DataRequired()],choices=['Yes','No'])
    muscle=SelectField('Muscle cramps:',validators=[DataRequired()],choices=[('low','Low'),('moderate','Moderate'),('high','High')])
    itching=SelectField('Itching score:',validators=[DataRequired()],choices=[('low','Low'),('moderate','Moderate'),('high','High')])
    submit=SubmitField('Submit')


class XrayForm(FlaskForm):
    username=StringField('Name:',validators=[DataRequired(),Length(max=100)])
    gender=RadioField('Gender:',validators=[DataRequired()],choices=['Male','Female'])
    age=IntegerField('Age:',validators=[DataRequired()])
    height=DecimalField("Height (in m):",validators=[DataRequired()],places=2)
    weight=DecimalField("Weight (in kg):",validators=[DataRequired()],places=2)
    x_ray=FileField('X-Ray Image:',validators=[DataRequired()])
    submit=SubmitField('Submit')



class SignUpForm(FlaskForm):
    def validate_username(self, username_to_check):
        with app.app_context():
            user=User.query.filter_by(username=username_to_check.data).first()

            if user:
                raise ValidationError('Username Already Exists !!!')
            
    def validate_email_address(self, email_address_to_check):
        with app.app_context():
            email=User.query.filter_by(email_address=email_address_to_check.data).first()

            if email:
                raise ValidationError('Email Address already exists !!!')
            
    username=StringField('Username',validators=[DataRequired(),Length(max=100)],render_kw={"placeholder":"Enter username"})
    email_address=StringField('Email',validators=[DataRequired(),Email(),Length(max=50)],render_kw={"placeholder": "Enter your email"})
    password=PasswordField('Password',validators=[DataRequired(),Length(max=8)],render_kw={"placeholder": "Enter your password"})
    submit=SubmitField('Sign Up')

class SignInForm(FlaskForm):
    username=StringField('Username',validators=[DataRequired(),Length(max=50)],render_kw={"placeholder": "Enter username"})
    password=PasswordField('Password',validators=[DataRequired()],render_kw={"placeholder": "Enter your password"})
    submit=SubmitField('Login')



class OtpForm(FlaskForm):
    otp1 = StringField('', validators=[DataRequired(),Length(max=1)])
    otp2 = StringField('', validators=[DataRequired(),Length(max=1)])
    otp3 = StringField('', validators=[DataRequired(),Length(max=1)])
    otp4 = StringField('', validators=[DataRequired(),Length(max=1)])
    otp5 = StringField('', validators=[DataRequired(),Length(max=1)])
    otp6 = StringField('', validators=[DataRequired(),Length(max=1)])

    submit = SubmitField('Verify')


class ReminderForm(FlaskForm):
    medicine=StringField('Medicine Name : ',validators=[DataRequired(),Length(max=50)])
    reminder_time = DateTimeField('Send Time (YYYY-MM-DD HH:MM:SS)', format='%Y-%m-%d %H:%M:%S', validators=[DataRequired()])
    submit=SubmitField('Set Reminder')

class UserProfileForm(FlaskForm):
    gender=RadioField('Gender:',validators=[Optional()],choices=['Male','Female'])
    age = IntegerField('Age', validators=[Optional()])
    height = FloatField('Height (in cm)', validators=[Optional()])
    weight = FloatField('Weight (in kg)', validators=[Optional()])
    pincode = IntegerField('Pincode', validators=[Optional()])
    phone = IntegerField('Phone', validators=[Optional()])
    city = StringField("City", validators=[Optional()])
    submit = SubmitField('Update Profile')


class DoctorProfileForm(FlaskForm):
    gender=RadioField('Gender:',validators=[Optional()],choices=['Male','Female'])
    age = IntegerField('Age', validators=[Optional()])
    specialization = StringField('Specialization: ',validators=[Optional()])
    pincode = IntegerField('Pincode', validators=[Optional()])
    phone = IntegerField('Phone', validators=[Optional()])
    available=RadioField('Available:',validators=[Optional()],choices=['Yes','No'])
    city = StringField("City", validators=[Optional()])
    submit = SubmitField('Update Profile')

class FeedbackForm(FlaskForm):
    feedback=StringField('',validators=[DataRequired(),Length(max=200)], render_kw={"placeholder": "Enter your feedback here..."})
    submit=SubmitField('Send Feedback')

class ChatbotForm(FlaskForm):
    botinput=StringField('',validators=[DataRequired()],render_kw={"placeholder": "Send Message..."})
    submit=SubmitField('Send')

class DietChart(FlaskForm):
    age=IntegerField('Age: ',validators=[DataRequired()],render_kw={"placeholder": "Your Age"})
    weight=FloatField('Weight: ',validators=[DataRequired()],render_kw={"placeholder":"Your weight"})
    height=FloatField('Height: ',validators=[DataRequired()],render_kw={"placeholder":"Your height"})
    disease=StringField('Disease: ',validators=[DataRequired()],render_kw={'placeholder':"Disease..."})
    allergy=StringField('Allergy: ',validators=[DataRequired()],render_kw={'placeholder':"Allergies (if any)"})
    preference=StringField('Preferrence: ',validators=[DataRequired()],render_kw={'placeholder':"Veg/Non-Veg..."})
    region=StringField('Region: ',validators=[DataRequired()],render_kw={'placeholder':"Your region"})
    submit=SubmitField('Prepare Chart')

class UserAskForm(FlaskForm):
    user_name = StringField('Name', validators=[DataRequired(), Length(max=120)], 
                            render_kw={"placeholder": "Enter your name"})
    medicine_name = StringField('Medicine Name',validators=[DataRequired(), Length(max=120)], 
                                render_kw={"placeholder": "Enter the name of the medicine"})
    user_pincode = StringField('Pincode', 
                               validators=[DataRequired(), Length(max=10)], 
                               render_kw={"placeholder": "Enter your pincode"})
    user_city = StringField('City', 
                            validators=[DataRequired(), Length(max=120)], 
                            render_kw={"placeholder": "Enter your city"})
    submit = SubmitField('Submit')

class RetailerReplyForm(FlaskForm):
    user_name = StringField('Name', 
                            validators=[DataRequired(), Length(max=120)], 
                            render_kw={"placeholder": "Enter your name"})
    medicine_name = StringField('Medicine Name', 
                                validators=[DataRequired(), Length(max=120)], 
                                render_kw={"placeholder": "Enter the name of the medicine"})
    user_pincode = StringField('Pincode', 
                               validators=[DataRequired(), Length(max=10)], 
                               render_kw={"placeholder": "Enter your pincode"})
    user_city = StringField('City', 
                            validators=[DataRequired(), Length(max=120)], 
                            render_kw={"placeholder": "Enter your city"})
    address = StringField('Address', 
                          validators=[DataRequired(), Length(max=200)], 
                          render_kw={"placeholder": "Enter the full address of your shop"})
    shop_name = StringField('Shop Name', 
                            validators=[DataRequired(), Length(max=120)], 
                            render_kw={"placeholder": "Enter the name of your shop"})
    price=FloatField('Price',validators=[DataRequired()],render_kw={"placeholder": "Enter the price"})
    submit = SubmitField('Submit')

class AppointmentForm(FlaskForm):
    time_slot = RadioField('Time Slot',
                           validators=[DataRequired()],
                           render_kw={"class": "d-flex gap-2 w-100", "style": "overflow-x: auto;"})

    date = DateField('Date', format='%Y-%m-%d', 
                     validators=[DataRequired()], 
                     render_kw={"class": "px-3 py-2 bg-light border-0 rounded-pill"})
    
    doctorId = HiddenField('Doctor ID', validators=[DataRequired()])

    submit = SubmitField('Fix Appointment')