from app import app,db, session
from flask import render_template, redirect, url_for, flash, request, jsonify
from app.forms import OtpForm, SignInForm, SignUpForm, UserProfileForm, DiabetesForm
from app.models import User, Checkup
import random
import pickle
from app.mails import send_email
from functools import wraps
import numpy as np

model = pickle.load(open('./app/static/model.pkl', 'rb'))
scaler = pickle.load(open('./app/static/scaler.pkl', 'rb'))

user_details=[]
get_otp=[]
phone=0
pincode=0
email=""
pred=0
name=[]


def get_current_user():
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

def login_required_user(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/home')
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/dashboard')
@login_required_user
def dashboard():
    return render_template('dashboard.html')

@app.route('/profile')
def profile():
    return render_template('Profile.html')

@app.route('/sign-in', methods=['GET','POST'])
def login():
    form=SignInForm()
    if form.validate_on_submit():
        with app.app_context():
            attempted_user=User.query.filter_by(username=form.username.data).first()
            if attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data):
                session['user_id']=attempted_user.id
                flash(f'You have successfully logged in as : {attempted_user.username}' , category='success')
                return redirect(url_for('dashboard'))
            else:
                flash(f'Username and password do not match ! Please try again', category='error')
                flash(f'OTP does not match', category='error')

    return render_template('signin.html',signin=form)

@app.route('/sign-up', methods=['GET','POST'])
def signup():
    form=SignUpForm()
    if form.validate_on_submit():
        global user_details
        user_details.append(form.username.data)
        user_details.append(form.email_address.data)
        user_details.append(form.password.data)
        global otp
        otp=random.randint(100000, 999999)
        get_otp.append(otp)
        send_email(form.email_address.data,"Medassis Verification", f"Welcome to Medassis !!!\n Your OTP for verification is {otp}. Please enter your OTP to create an account.")
        return redirect(url_for('otp'))
            
        #else:
           # flash(f"Wrong OTP eneted !!! Please enter it correctly", category='error')
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='error')

    return render_template('signup.html',signup=form)

@app.route('/otp', methods=['GET','POST'])
def otp():
    otpform=OtpForm()
    if otpform.validate_on_submit():
        global user_details
        global get_otp
        print("IN OTP")
        # Access form data
        otpnum=int(str(otpform.otp1.data)+str(otpform.otp2.data)+str(otpform.otp3.data)+str(otpform.otp4.data)+str(otpform.otp5.data)+str(otpform.otp6.data))
        
        print(otpnum)
        print(get_otp)
        if(otpnum==get_otp[0]):
            with app.app_context():
                user_data=User(username=user_details[0],
                                email_address=user_details[1],
                                password=user_details[2])
                            
                db.session.add(user_data)
                db.session.commit()
                # login_user(user_data)
                session['user_id']=user_data.id
                
                user_details.pop()
                user_details.pop()
                user_details.pop()
                get_otp.pop()
            
            return redirect(url_for('dashboard'))
        flash(f"Wrong OTP entered !!! Please enter a valid OTP !!!", category='error')
    return render_template('otp.html',otpform=otpform)

@app.route('/logout')
@login_required_user
def logout():
    print("Logout")
    session.pop('user_id', None)
    return redirect(url_for('home'))


@app.route('/diabetes-form', methods=['GET','POST'])
def diabetes():
    diabetesform=DiabetesForm()
    if diabetesform.validate_on_submit():
        username=diabetesform.username.data
        global name
        name.append(username)
        gender=diabetesform.gender.data
        age=diabetesform.age.data
        address=diabetesform.address.data
        global pincode
        global email
        global phone

        pincode = diabetesform.pincode.data
        hypertension = diabetesform.hypertension.data
        previousHeartDisease = diabetesform.previousHeartDisease.data
        smoking_History = diabetesform.smoking_History.data
        weight = diabetesform.weight.data
        height = diabetesform.height.data
        hba1clvl = diabetesform.hba1clvl.data
        blood_glucose = diabetesform.blood_glucose.data
        email = get_current_user().email_address
        phone = diabetesform.phone.data

        if len(username) < 2:
            flash("Username must be greater than 4 characters.", category='error')
        elif (age) >= 150:
            flash("Age value exceeded", category='error')
        elif (height)>3:
            flash("Invalid Height Input.", category='error')
        elif (blood_glucose) > 700:
            flash("Invalid blood glucose level", category='error')
        else:
            flash("Form Submited!", category='success')
            if hypertension=="Yes":
                hypertension_int=1
            else:
                hypertension_int=0
            
            if previousHeartDisease=="Yes":
                heart_disease=1
            else:
                heart_disease=0

            if gender=="Male":
                gender_int=1
            else:
                gender_int=0

            if smoking_History=="Other":
                smk_curr=0
                smk_ever=0
                smk_former=0
                smk_never=0
                smk_nt_curr=0

            elif smoking_History=="Current":
                smk_curr=1
                smk_ever=0
                smk_former=0
                smk_never=0
                smk_nt_curr=0

            elif smoking_History=="Ever":
                smk_curr=0
                smk_ever=1
                smk_former=0
                smk_never=0
                smk_nt_curr=0
            
            elif smoking_History=="Former":
                smk_curr=0
                smk_ever=0
                smk_former=1
                smk_never=0
                smk_nt_curr=0

            elif smoking_History=="Never":
                smk_curr=0
                smk_ever=0
                smk_former=0
                smk_never=1
                smk_nt_curr=0

            else:
                smk_curr=0
                smk_ever=0
                smk_former=0
                smk_never=0
                smk_nt_curr=1

            bmi=weight/(height*height)
            if bmi>34:
                wgt_over=1
                wgt_under=0
            
            elif bmi<14:
                wgt_over=0
                wgt_under=1

            else:
                wgt_over=0
                wgt_under=0

            if hba1clvl=="Below 3":
                hba1c_4=0
                hba1c_5=0
                hba1c_6=0
                hba1c_7=0
                hba1c_8=0
                hba1c_9=0

            elif hba1clvl=="3-4":
                hba1c_4=1
                hba1c_5=0
                hba1c_6=0
                hba1c_7=0
                hba1c_8=0
                hba1c_9=0

            elif hba1clvl=="4-5":
                hba1c_4=0
                hba1c_5=1
                hba1c_6=0
                hba1c_7=0
                hba1c_8=0
                hba1c_9=0

            elif hba1clvl=="5-6":
                hba1c_4=0
                hba1c_5=0
                hba1c_6=1
                hba1c_7=0
                hba1c_8=0
                hba1c_9=0

            elif hba1clvl=="6-7":
                hba1c_4=0
                hba1c_5=0
                hba1c_6=0
                hba1c_7=1
                hba1c_8=0
                hba1c_9=0

            elif hba1clvl=="7-8":
                hba1c_4=0
                hba1c_5=0
                hba1c_6=0
                hba1c_7=0
                hba1c_8=1
                hba1c_9=0

            else:
                hba1c_4=0
                hba1c_5=0
                hba1c_6=0
                hba1c_7=0
                hba1c_8=0
                hba1c_9=1

            query = np.array([age,hypertension_int,heart_disease,blood_glucose,gender_int,smk_curr,smk_ever,smk_former,smk_never,smk_nt_curr,wgt_over,wgt_under,hba1c_4,hba1c_5,hba1c_6,hba1c_7,hba1c_8,hba1c_9])

            query = query.reshape(1,18)
            input_trf=scaler.transform(query)
            prediction=model.predict(input_trf)
            global pred
            pred=prediction

            print(pred)

            
            with app.app_context():
                checkup_data=Checkup(age=age,
                                    name=username,
                                    gender=gender,
                                    hypertension=hypertension,
                                    heart_disease=previousHeartDisease,
                                    smoking_history=smoking_History,
                                    blood_glucose=blood_glucose,
                                    weight=weight,
                                    height=height,
                                    hba1c=hba1clvl,
                                    diabetes=pred,
                                    patient_id=get_current_user().id)
                db.session.add(checkup_data)
                db.session.commit()
                
            
            if prediction[0]==0:
                flash(f"Your chances of diabetes is low !!!", category="success")
            else:
                flash(f"Your cances of diabetes is high !!!", category="error")

            send_email(email,"Medassis Report", f"Name : {username}\n Gender : {gender}\n Age : {age}\n Hypertension : {hypertension}\n Previous Heart Disease : {previousHeartDisease}\n Weight : {weight}\n Height : {height}\n HBA1C Level : {hba1clvl}\n Blood Glucose : {blood_glucose}\n Diabetes : {pred}\n")   
            return redirect(url_for('result_diabetes'))
            
        
    return render_template('diabetesform.html',form=diabetesform)

@app.route('/result')
@login_required_user
def result_diabetes():
    global phone
    global pincode
    global email
    global name
    global pred
    with app.app_context():
        user_data=Checkup.query.filter_by(name=name[0]).order_by(Checkup.form_id.desc()).first()
    name.pop()
    return render_template('result_diabetes.html', user_data=user_data, current_user=get_current_user(), phone=phone, pincode=pincode, email=email, pred=pred)
