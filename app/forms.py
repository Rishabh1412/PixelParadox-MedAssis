from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,RadioField,IntegerField,SelectField,DecimalField,FileField,DateTimeField,TextAreaField,FloatField,DateField,HiddenField
from wtforms.validators import Length, Email, Optional, DataRequired, ValidationError
from app import app
from app.models import User

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

class UserProfileForm(FlaskForm):
    gender=RadioField('Gender:',validators=[Optional()],choices=['Male','Female'])
    age = IntegerField('Age', validators=[Optional()])
    height = FloatField('Height (in cm)', validators=[Optional()])
    weight = FloatField('Weight (in kg)', validators=[Optional()])
    pincode = IntegerField('Pincode', validators=[Optional()])
    phone = IntegerField('Phone', validators=[Optional()])
    city = StringField("City", validators=[Optional()])
    submit = SubmitField('Update Profile')

class DiabetesForm(FlaskForm):

    username=StringField('Name',validators=[DataRequired(),Length(max=100)])
    gender=RadioField('Gender',validators=[DataRequired()],choices=['Male','Female'])
    age=IntegerField('Age',validators=[DataRequired()])
    address=StringField('Address',validators=[DataRequired(),Length(max=250)])
    pincode=IntegerField('Pincode',validators=[DataRequired()])
    hypertension=RadioField('Hypertension',validators=[DataRequired()],choices=['Yes','No'])
    previousHeartDisease=RadioField('Previous Heart Disease',validators=[DataRequired()],choices=['Yes','No'])
    smoking_History=SelectField("Smoking History",validators=[DataRequired()],choices=[('never','Never'),('former','Former'),('current','Current'),('notcurrent','Not Current'),('ever','Ever'),('other','Other')])
    weight=DecimalField("Weight (in kg)",validators=[DataRequired()],places=2)
    height=DecimalField("Height (in m)",validators=[DataRequired()],places=2)
    hba1clvl=SelectField("HbA1c Level",validate_choice=[DataRequired()],choices=[('Below 3','below 3'),('3-4','3-4'),('4-5','4-5'),('5-6','5-6'),('6-7','6-7'),('7-8','7-8'),('8-9','8-9'),('Above 9','above 9')])
    blood_glucose=IntegerField('Blood Glucose Level',validators=[DataRequired()])
    phone=IntegerField('Phone Number',validators=[DataRequired()])
    submit=SubmitField('Submit')

class KidneyForm(FlaskForm):
    username=StringField('Name',validators=[DataRequired(),Length(max=100)])
    gender=RadioField('Gender',validators=[DataRequired()],choices=['Male','Female'])
    height=DecimalField("Height (in m)",validators=[DataRequired()],places=2)
    weight=DecimalField("Weight (in kg)",validators=[DataRequired()],places=2)
    smoke_alco=RadioField('Smoking and Alcohol History',validators=[DataRequired()],choices=['Smoking','Alcohol','Both','None'])
    age=IntegerField('Age',validators=[DataRequired()])
    physical_activity=IntegerField('Physical Activity (Weekly)',validators=[DataRequired()])
    kidney_diet_score=IntegerField('Kidney Diet Score (0-10)',validators=[DataRequired()])
    fhkd=RadioField("Famliy History Kidney Disease",validators=[DataRequired()],choices=['Yes','No'])
    fhh=RadioField("Famliy History Hypertension",validators=[DataRequired()],choices=['Yes','No'])
    fhd=RadioField("Famliy History Diabetes",validators=[DataRequired()],choices=['Yes','No'])

    urinary_tract=RadioField('Urinary Tract Infections',validators=[DataRequired()],choices=['Yes','No'])
    systoyic_bp=IntegerField('Systoyic BP(mmHg)',validators=[DataRequired()])
    diastotic_bp=IntegerField('Diastotic BP(mmHg)',validators=[DataRequired()])
    fasting_blood_sugar=DecimalField('Fasting Blood Sugar',validators=[DataRequired()],places=2)
    hba1clvl=DecimalField("HbA1c Level",validators=[DataRequired()],places=2)
    serum_creative=DecimalField('Serum Creatinine(mg/dL)',validators=[DataRequired()],places=2)
    bunlvl=DecimalField('BUN Level',validators=[DataRequired()],places=2)
    gfr=DecimalField('GFR (ml/min/1.73m^2)',validators=[DataRequired()],places=2)
    protein_in_urine=DecimalField('Protein in Urine(g/day)',validators=[DataRequired()],places=2)
    serum_electrolyes_sodium=DecimalField('Serum Electrolytes Sodium(mEq/L)',validators=[DataRequired()],places=2)
    serum_electrolyes_potassium=DecimalField('Serum Electrolytes Potassium(mEq/L)',validators=[DataRequired()],places=2)
    haemoglobin_lvl=DecimalField('Haemoglobin Level(g/dL)',validators=[DataRequired()],places=2)
    cholestrol_lvl=DecimalField('Cholestrol Level(mg/dL)',validators=[DataRequired()],places=2)
    diuretics=RadioField('Diuretics',validators=[DataRequired()],choices=['Yes','No'])
    edema=RadioField('Edema',validators=[DataRequired()],choices=['Yes','No'])
    muscle=SelectField('Muscle cramps',validators=[DataRequired()],choices=[('low','Low'),('moderate','Moderate'),('high','High')])
    itching=SelectField('Itching score',validators=[DataRequired()],choices=[('low','Low'),('moderate','Moderate'),('high','High')])
    submit=SubmitField('Submit')
