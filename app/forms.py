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
