from app import app,db, session
from flask import render_template, redirect, url_for, flash, request, jsonify
from app.forms import OtpForm, SignInForm, SignUpForm, UserProfileForm, DiabetesForm
from app.models import User, Checkup
import random
import pickle
from app.mails import send_email
from functools import wraps
import numpy as np
import pandas as pd
import plotly.io as pio
import plotly.express as px
import json
import plotly
import plotly.graph_objs as go

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
    diabetesform = DiabetesForm()
    if diabetesform.validate_on_submit():
        username = diabetesform.username.data
        global name
        name.append(username)
        gender = diabetesform.gender.data
        age = diabetesform.age.data
        address = diabetesform.address.data
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
        elif (height) > 3:
            flash("Invalid Height Input.", category='error')
        elif (blood_glucose) > 700:
            flash("Invalid blood glucose level", category='error')
        else:
            flash("Form Submitted!", category='success')
            if hypertension == "Yes":
                hypertension_int = 1
            else:
                hypertension_int = 0

            if previousHeartDisease == "Yes":
                heart_disease = 1
            else:
                heart_disease = 0

            if gender == "Male":
                gender_int = 1
            else:
                gender_int = 0

            if smoking_History == "Other":
                smk_curr = 0
                smk_ever = 0
                smk_former = 0
                smk_never = 0
                smk_nt_curr = 0

            elif smoking_History == "Current":
                smk_curr = 1
                smk_ever = 0
                smk_former = 0
                smk_never = 0
                smk_nt_curr = 0

            elif smoking_History == "Ever":
                smk_curr = 0
                smk_ever = 1
                smk_former = 0
                smk_never = 0
                smk_nt_curr = 0

            elif smoking_History == "Former":
                smk_curr = 0
                smk_ever = 0
                smk_former = 1
                smk_never = 0
                smk_nt_curr = 0

            elif smoking_History == "Never":
                smk_curr = 0
                smk_ever = 0
                smk_former = 0
                smk_never = 1
                smk_nt_curr = 0

            else:
                smk_curr = 0
                smk_ever = 0
                smk_former = 0
                smk_never = 0
                smk_nt_curr = 1

            bmi = weight / (height * height)
            if bmi > 34:
                wgt_over = 1
                wgt_under = 0

            elif bmi < 14:
                wgt_over = 0
                wgt_under = 1

            else:
                wgt_over = 0
                wgt_under = 0

            if hba1clvl == "Below 3":
                hba1c_4 = 0
                hba1c_5 = 0
                hba1c_6 = 0
                hba1c_7 = 0
                hba1c_8 = 0
                hba1c_9 = 0

            elif hba1clvl == "3-4":
                hba1c_4 = 1
                hba1c_5 = 0
                hba1c_6 = 0
                hba1c_7 = 0
                hba1c_8 = 0
                hba1c_9 = 0

            elif hba1clvl == "4-5":
                hba1c_4 = 0
                hba1c_5 = 1
                hba1c_6 = 0
                hba1c_7 = 0
                hba1c_8 = 0
                hba1c_9 = 0

            elif hba1clvl == "5-6":
                hba1c_4 = 0
                hba1c_5 = 0
                hba1c_6 = 1
                hba1c_7 = 0
                hba1c_8 = 0
                hba1c_9 = 0

            elif hba1clvl == "6-7":
                hba1c_4 = 0
                hba1c_5 = 0
                hba1c_6 = 0
                hba1c_7 = 1
                hba1c_8 = 0
                hba1c_9 = 0

            elif hba1clvl == "7-8":
                hba1c_4 = 0
                hba1c_5 = 0
                hba1c_6 = 0
                hba1c_7 = 0
                hba1c_8 = 1
                hba1c_9 = 0

            else:
                hba1c_4 = 0
                hba1c_5 = 0
                hba1c_6 = 0
                hba1c_7 = 0
                hba1c_8 = 0
                hba1c_9 = 1

            query = np.array([age, hypertension_int, heart_disease, blood_glucose, gender_int, smk_curr, smk_ever, smk_former, smk_never, smk_nt_curr, wgt_over, wgt_under, hba1c_4, hba1c_5, hba1c_6, hba1c_7, hba1c_8, hba1c_9])
            query = query.reshape(1, 18)
            input_trf = scaler.transform(query)
            prediction = model.predict(input_trf)
            global pred
            pred = prediction

            print(pred)

            with app.app_context():
                checkup_data = Checkup(age=age,
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

            # Format the email content
            if prediction[0] == 0:
                result_message = "Your chances of diabetes are low."
            else:
                result_message = "Your chances of diabetes are high."

            email_message = f"""
            <html>
            <body>
                <h2>Diabetes Risk Assessment Report</h2>
                <p><strong>Name:</strong> {username}</p>
                <p><strong>Gender:</strong> {gender}</p>
                <p><strong>Age:</strong> {age}</p>
                <p><strong>Hypertension:</strong> {hypertension}</p>
                <p><strong>Previous Heart Disease:</strong> {previousHeartDisease}</p>
                <p><strong>Weight:</strong> {weight} kg</p>
                <p><strong>Height:</strong> {height} m</p>
                <p><strong>HBA1C Level:</strong> {hba1clvl}</p>
                <p><strong>Blood Glucose:</strong> {blood_glucose} mg/dL</p>
                <p><strong>Diabetes Risk:</strong> {result_message}</p>
            </body>
            </html>
            """

            send_email(email, "Medassis Report", email_message)
            return redirect(url_for('result_diabetes'))
    return render_template("diabetesform.html",form=diabetesform)

@app.route('/diabetesPlot')
def index():
    pio.templates.default = "plotly"
    df = pd.read_csv('app/static/diabetes_prediction_dataset.csv')

    diabetes_data = df[df['diabetes'] == 1]
    diabetes_sample = diabetes_data.sample(n=200, random_state=42)
    colors = diabetes_sample['smoking_history'].apply(lambda x: 'green' if x == 'never' else 'red')
    bubble_fig = px.scatter_3d(
        diabetes_sample, x='age', y='HbA1c_level', z='blood_glucose_level',
        color=colors, size='blood_glucose_level', opacity=0.6,
        color_discrete_map={'green': 'green', 'red': 'red'}
    )
    bubble_fig.update_layout(
        title='3D Bubble Plot of Blood Glucose Levels by Age and HbA1c Level with Smoking History for Diabetic Patients',
        scene=dict(
            xaxis_title='Age',
            yaxis_title='HbA1c Level',
            zaxis_title='Blood Glucose Level'
        ),
        legend_title='Smoking History',
        width=1000,
        height=800
    )
    bubble_graphJSON = json.dumps(bubble_fig, cls=plotly.utils.PlotlyJSONEncoder)

    # Generate Histogram
    age_bins = np.arange(0, diabetes_data['age'].max() + 5, 5)
    histogram_fig = px.histogram(diabetes_data, x='age', color='gender', 
                                 title='Histogram of Age by Gender for Diabetic Patients',
                                 labels={'age': 'Age Groups', 'count': 'Frequency of Diabetes'},
                                 nbins=len(age_bins))
    histogram_fig.update_layout(
        bargap=0.1,
        bargroupgap=0.2,
        width=800,
        height=600
    )
    histogram_graphJSON = json.dumps(histogram_fig, cls=plotly.utils.PlotlyJSONEncoder)

    # Generate 3D Scatter Plot
    diabetes_data_sample = df[df['diabetes'] == 1].sample(n=250, random_state=42)
    non_diabetes_data_sample = df[df['diabetes'] == 0].sample(n=250, random_state=42)
    combined_data = pd.concat([diabetes_data_sample, non_diabetes_data_sample])
    scatter_fig = px.scatter_3d(
        combined_data, x='age', y='bmi', z='HbA1c_level',
        color=np.where(combined_data['diabetes'] == 1, 'Diabetes', 'Non-Diabetes'),
        symbol=np.where(combined_data['diabetes'] == 1, 'Diabetes', 'Non-Diabetes'),
        opacity=0.7,
        size_max=20,
        labels={'age': 'Age', 'bmi': 'BMI', 'HbA1c_level': 'HbA1c Level'},
        title='Scatter Plot of Age vs BMI vs HbA1c Level with Diabetes Status'
    )
    scatter_fig.update_traces(marker=dict(color='red'), selector=dict(type='scatter3d', name='Diabetes'))
    scatter_fig.update_traces(marker=dict(color='blue'), selector=dict(type='scatter3d', name='Non-Diabetes'))
    scatter_fig.update_layout(
        scene=dict(xaxis_title='Age', yaxis_title='BMI', zaxis_title='HbA1c Level'),
        height=800
    )
    scatter_graphJSON = json.dumps(scatter_fig, cls=plotly.utils.PlotlyJSONEncoder)

    # Generate 3D Mesh Plot
    diabetes_data = df[df['diabetes'] == 1].head(1000)
    bmi = diabetes_data['bmi']
    age = diabetes_data['age']
    hbA1c = diabetes_data['HbA1c_level']
    mesh_fig = go.Figure(data=[go.Mesh3d(x=bmi, y=age, z=hbA1c, opacity=0.5)])
    mesh_fig.update_layout(
        title='3D Mesh Plot of BMI, Age, and HbA1c Level for People with Diabetes',
        scene=dict(
            xaxis_title='BMI',
            yaxis_title='Age',
            zaxis_title='HbA1c Level'
        ),
        width=1200,
        height=800
    )
    mesh_graphJSON = json.dumps(mesh_fig, cls=plotly.utils.PlotlyJSONEncoder)

    # Generate Pie Charts
    diabetes_counts = {
        'Smoking History': diabetes_data['smoking_history'].value_counts(),
        'Heart Disease': diabetes_data['heart_disease'].value_counts()
    }
    non_diabetes_counts = {
        'Smoking History': df[df['diabetes'] == 0]['smoking_history'].value_counts(),
        'Heart Disease': df[df['diabetes'] == 0]['heart_disease'].value_counts()
    }

    pie_fig_diabetes_smoking = go.Figure(data=[go.Pie(
        labels=diabetes_counts['Smoking History'].index, 
        values=diabetes_counts['Smoking History'].values,
        name='Smoking History - Diabetes'
    )])
    pie_fig_diabetes_heart = go.Figure(data=[go.Pie(
        labels=diabetes_counts['Heart Disease'].index, 
        values=diabetes_counts['Heart Disease'].values,
        name='Heart Disease - Diabetes'
    )])
    pie_fig_non_diabetes_smoking = go.Figure(data=[go.Pie(
        labels=non_diabetes_counts['Smoking History'].index, 
        values=non_diabetes_counts['Smoking History'].values,
        name='Smoking History - Non-Diabetes'
    )])
    pie_fig_non_diabetes_heart = go.Figure(data=[go.Pie(
        labels=non_diabetes_counts['Heart Disease'].index, 
        values=non_diabetes_counts['Heart Disease'].values,
        name='Heart Disease - Non-Diabetes'
    )])

    pie_graphJSON_diabetes_smoking = json.dumps(pie_fig_diabetes_smoking, cls=plotly.utils.PlotlyJSONEncoder)
    pie_graphJSON_diabetes_heart = json.dumps(pie_fig_diabetes_heart, cls=plotly.utils.PlotlyJSONEncoder)
    pie_graphJSON_non_diabetes_smoking = json.dumps(pie_fig_non_diabetes_smoking, cls=plotly.utils.PlotlyJSONEncoder)
    pie_graphJSON_non_diabetes_heart = json.dumps(pie_fig_non_diabetes_heart, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('index13.html', 
                           bubble_plot=bubble_graphJSON,
                           histogram_plot=histogram_graphJSON,
                           scatter_plot=scatter_graphJSON,
                           mesh_plot=mesh_graphJSON,
                           pie_diabetes_smoking=pie_graphJSON_diabetes_smoking,
                           pie_diabetes_heart=pie_graphJSON_diabetes_heart,
                           pie_non_diabetes_smoking=pie_graphJSON_non_diabetes_smoking,
                           pie_non_diabetes_heart=pie_graphJSON_non_diabetes_heart)



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
