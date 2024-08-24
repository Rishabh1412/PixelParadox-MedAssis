from app import app,db, session
from flask import render_template, redirect, url_for, flash, request, jsonify
from app.forms import OtpForm, SignInForm, SignUpForm, UserProfileForm, DiabetesForm, KidneyForm
from app.models import User, Checkup, Kidney
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
from scipy.interpolate import griddata
import time
from sklearn.cluster import KMeans

model = pickle.load(open('./app/static/model.pkl', 'rb'))
scaler = pickle.load(open('./app/static/scaler.pkl', 'rb'))
kidney_model=pickle.load(open('app/static/Kidney_model.pkl', 'rb'))
kidney_scaler=pickle.load(open('app/static/Scaling_kidney.pkl', 'rb'))

user_details=[]
get_otp=[]
phone=0
pincode=0
email=""
pred=0
name=[]
user=[]


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

@app.route('/kidney-form', methods=['GET','POST'])
@login_required_user
def kidney():
    kidneyform=KidneyForm()
    if kidneyform.validate_on_submit():
        name = kidneyform.username.data
        gender = kidneyform.gender.data
        height = kidneyform.height.data
        weight = kidneyform.weight.data
        smoke_alco = kidneyform.smoke_alco.data
        age = kidneyform.age.data
        physical_activity = kidneyform.physical_activity.data
        kidney_diet_score = kidneyform.kidney_diet_score.data
        fhkd = kidneyform.fhkd.data
        fhh = kidneyform.fhh.data
        fhd = kidneyform.fhd.data
        urinary_tract = kidneyform.urinary_tract.data
        systolic_bp = kidneyform.systoyic_bp.data
        diastolic_bp = kidneyform.diastotic_bp.data
        fasting_blood_sugar = kidneyform.fasting_blood_sugar.data
        hba1clvl = kidneyform.hba1clvl.data
        serum_creative = kidneyform.serum_creative.data
        bunlvl = kidneyform.bunlvl.data
        gfr = kidneyform.gfr.data
        protein_in_urine = kidneyform.protein_in_urine.data
        serum_electrolyes_sodium = kidneyform.serum_electrolyes_sodium.data
        serum_electrolyes_potassium = kidneyform.serum_electrolyes_potassium.data
        haemoglobin_lvl = kidneyform.haemoglobin_lvl.data
        cholestrol_lvl = kidneyform.cholestrol_lvl.data
        diuretics = kidneyform.diuretics.data
        edema = kidneyform.edema.data
        muscle = kidneyform.muscle.data
        itching = kidneyform.itching.data

        global user
        user.append(name)
        weight=float(weight)
        height=float(height)
        fasting_blood_sugar=float(fasting_blood_sugar)
        if gender=="Male":
            gender_val=1
        else:
            gender_val=0
        if physical_activity>=2:
            phy_val=1
        else:
            phy_val=0
        if smoke_alco=="Smoking" or smoke_alco=="Alcohol":
            smok_val=1
        elif smoke_alco=="Both":
            smok_val=2
        elif smoke_alco=="None":
            smok_val=0

        if kidney_diet_score>=5:
            kidney_val=1
        else:
            kidney_val=0

        if urinary_tract=="Yes":
            urinary_val=1
        else:
            urinary_val=0

        genetics_val=0
        genetics=[fhkd, fhh, fhd]
        for i in genetics:
            if i=="Yes":
                genetics_val+=1

        if serum_electrolyes_sodium>=139:
            serum_sodium_val=1
        else:
            serum_sodium_val=0

        if serum_electrolyes_potassium>=4.05:
            serum_potassium_val=1
        else:
            serum_potassium_val=0
        
        if diuretics=="Yes":
            diuretics_val=1
        else:
            diuretics_val=0
        
        if edema=="Yes":
            edema_val=1
        else:
            edema_val=0
        
        if muscle=="low":
            muscle_low=1
            muscle_moderate=0
        elif muscle=="moderate":
            muscle_low=0
            muscle_moderate=1
        else:
            muscle_low=0
            muscle_moderate=0

        if itching=="low":
            itching_low=1
            itching_moderate=0
        elif itching=="moderate":
            itching_low=0
            itching_moderate=1
        else:
            itching_low=0
            itching_moderate=0

        if age<=30:
            age_mid=0
            age_sen=0
        elif age>30 and age<=60:
            age_mid=1
            age_sen=0
        else:
            age_mid=0
            age_sen=1

        bmi=weight/(height*height)
        if bmi>=34.05:
            obesity=1
            overwgt=0
            underwgt=0
        elif bmi<34.05 and bmi>=27.65:
            obesity=0
            overwgt=1
            underwgt=0
        elif bmi<27.65 and bmi>=12:
            obesity=0
            overwgt=0
            underwgt=0
        else:
            obesity=0
            overwgt=0
            underwgt=1
        

        query = np.array([gender_val, phy_val, smok_val, kidney_val, urinary_val, systolic_bp, diastolic_bp, fasting_blood_sugar, hba1clvl, serum_creative, bunlvl, gfr, protein_in_urine, genetics_val, serum_sodium_val, serum_potassium_val, haemoglobin_lvl, cholestrol_lvl, diuretics_val, edema_val, muscle_low, muscle_moderate, itching_low, itching_moderate, age_mid, age_sen, obesity, overwgt, underwgt])
        query = query.reshape(1,29)
        input_trf=kidney_scaler.transform(query)
        kidney_per=kidney_model.predict(input_trf)
        global pred
        pred=kidney_per
        print(pred)


        with app.app_context():
            checkup_data=Kidney(
                            name=name,
                            age=age,
                            gender=gender,
                            height=height,
                            weight=weight,
                            smok_alc=smoke_alco,
                            physical_act=physical_activity,
                            kidney_diet=kidney_diet_score,
                            fhkd=fhkd,
                            fhh=fhh,
                            fhd=fhd,
                            urinary=urinary_tract,
                            systolic_bp=systolic_bp,
                            diastolic_bp=diastolic_bp,
                            blood_sugar=fasting_blood_sugar,
                            hba1c=hba1clvl,
                            serum=serum_creative,
                            bun_lvl=bunlvl,
                            gfr=gfr,
                            protein_urine=protein_in_urine,
                            sodium_electrolyte=serum_electrolyes_sodium,
                            potassium_electrolyte=serum_electrolyes_potassium,
                            hemoglobin=haemoglobin_lvl,
                            cholesterol=cholestrol_lvl,
                            diuretics=diuretics,
                            edema=edema,
                            muscle_cramps=muscle,
                            itching=itching,
                            kidney_per=pred,
                            )
            
            db.session.add(checkup_data)
            db.session.commit()

        email_message = f"""
            <html>
            <body>
                <h2>Diabetes Risk Assessment Report</h2>
                <p><strong>Name:</strong> {name}</p>
                <p><strong>Gender:</strong> {gender}</p>
                <p><strong>Age:</strong> {age}</p>
                <p><strong>Height:</strong> {height} m</p>
                <p><strong>HBA1C Level:</strong> {hba1clvl}</p>
                <p><strong>Diabetes Risk:</strong> {pred[0][0]*100} %</p>
            </body>
            </html>
            """
        
        send_email(get_current_user().email_address,"Medassis Report", email_message)
        return redirect(url_for('result_kidney'))
            
                
        

    return render_template('kidney.html',kidneyform=kidneyform)

@app.route('/result-kidney')
@login_required_user
def result_kidney():
    global pred
    with app.app_context():
        user_data=Kidney.query.filter_by(name=user[0]).order_by(Kidney.form_id.desc()).first()
    user.pop()
    return render_template('result_kidney.html', user_data=user_data, current_user=get_current_user(), pred=pred)

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

@app.route('/kidneyplot')
def index7():
    pio.templates.default = "plotly"
    df = pd.read_csv('app/static/kidneyData.csv')
    df_scatter = df.sample(n=250, random_state=42)

    fig_scatter = px.scatter_3d(df_scatter, x='SystolicBP', y='DiastolicBP', z='FastingBloodSugar', color='AgeGroup',title="3D Scatter Plot of Systolic BP, Diastolic BP, and Blood Sugar Level")
    fig_scatter.update_layout(height=500)

    fig_hist = px.histogram(df, x='AgeGroup', color='Gender', barmode='group',title="Histogram of Age Group by Gender")
    fig_hist.update_layout(width=500, height=500)

    x = df['SystolicBP']
    y = df['DiastolicBP']
    z = df['FastingBloodSugar']

    xi = np.linspace(x.min(), x.max(), 100)
    yi = np.linspace(y.min(), y.max(), 100)
    xi, yi = np.meshgrid(xi, yi)

    zi = griddata((x, y), z, (xi, yi), method='linear')

    fig_surface = go.Figure(data=[go.Surface(z=zi, x=xi, y=yi)])
    fig_surface.update_layout(title='Surface Plot of Systolic BP, Diastolic BP, and Blood Sugar Level',scene=dict(xaxis_title='Systolic BP',yaxis_title='Diastolic BP',zaxis_title='Blood Sugar Level'),width=700, height=700)

    fig_heatmap = px.density_heatmap(df, x='ProteinInUrine', y='SerumCreatinine',color_continuous_scale='Viridis',title='Heatmap of Protein in Urine vs Serum Creatinine Levels')
    fig_heatmap.update_layout(width=700, height=700)

    x_mesh = df['SystolicBP']
    y_mesh = df['DiastolicBP']
    z_mesh = df['HbA1c']

    xi_mesh = np.linspace(x_mesh.min(), x_mesh.max(), 100)
    yi_mesh = np.linspace(y_mesh.min(), y_mesh.max(), 100)
    xi_mesh, yi_mesh = np.meshgrid(xi_mesh, yi_mesh)

    zi_mesh = griddata((x_mesh, y_mesh), z_mesh, (xi_mesh, yi_mesh), method='linear')

    fig_mesh = go.Figure(data=[go.Surface(z=zi_mesh, x=xi_mesh, y=yi_mesh)])
    fig_mesh.update_layout(title='Mesh Plot of HbA1c, Systolic BP, and Diastolic BP',
                           scene=dict(xaxis_title='Systolic BP',yaxis_title='Diastolic BP',zaxis_title='HbA1c'),width=700, height=700)

    fig_live = px.scatter(df, x='CholesterolTotal', y='SerumCreatinine',
                         title='Live Graph of Cholesterol Levels vs Serum Creatinine Levels')
    fig_live.update_layout(width=700, height=700)

    # pie charts
    df_high_systolic = df[df['SystolicBP'] > 120]
    pie_systolic = px.pie(df_high_systolic, names='Diagnosis', title='Percentage of People with Systolic BP Above 120',
                         color='Diagnosis',color_discrete_map={0: 'blue', 1: 'red'})
    pie_systolic.update_layout(width=600, height=400)

    df_high_diastolic = df[df['DiastolicBP'] > 80]
    pie_diastolic = px.pie(df_high_diastolic, names='Diagnosis', title='Percentage of People with Diastolic BP Above 80',
                          color='Diagnosis',color_discrete_map={0: 'blue', 1: 'red'})
    pie_diastolic.update_layout(width=600, height=400)

    df_high_hba1c = df[(df['HbA1c'] > 5.7) & (df['Diagnosis'] == 1)]
    pie_hba1c = px.pie(df_high_hba1c, names='Diagnosis', title='Percentage of People with High HbA1c and Diagnosis = Positive',
                       color='Diagnosis',color_discrete_map={1: 'red'})
    pie_hba1c.update_layout(width=600, height=400)

    df_high_cholesterol = df[(df['CholesterolTotal'] > 150) & (df['Diagnosis'] == 1)]
    pie_cholesterol = px.pie(df_high_cholesterol, names='Diagnosis', title='Percentage of People with High Cholesterol and Diagnosis = Positive',
                             color='Diagnosis',color_discrete_map={1: 'red'})
    pie_cholesterol.update_layout(width=600, height=400)

    df_gender_diagnosis = df[df['Diagnosis'] == 1]
    pie_gender = px.pie(df_gender_diagnosis, names='Gender', title='Percentage of People with Diagnosis = Positive by Gender',
                        color='Gender',color_discrete_map={0: 'blue', 1: 'red'})
    pie_gender.update_layout(width=600, height=400)

    plot_scatter_html = pio.to_html(fig_scatter, full_html=False)

    plot_hist_html = pio.to_html(fig_hist, full_html=False)

    plot_surface_html = pio.to_html(fig_surface, full_html=False)

    plot_heatmap_html = pio.to_html(fig_heatmap, full_html=False)

    plot_mesh_html = pio.to_html(fig_mesh, full_html=False)

    plot_live_html = pio.to_html(fig_live, full_html=False)
    plot_pie_systolic_html = pio.to_html(pie_systolic, full_html=False)
    plot_pie_diastolic_html = pio.to_html(pie_diastolic, full_html=False)
    plot_pie_cholesterol_html = pio.to_html(pie_cholesterol, full_html=False)

    plot_pie_hba1c_html = pio.to_html(pie_hba1c, full_html=False)
    plot_pie_gender_html = pio.to_html(pie_gender, full_html=False)

    return render_template('index0.html', 
                           plot_scatter_html=plot_scatter_html, 
                           plot_hist_html=plot_hist_html,
                           plot_surface_html=plot_surface_html,
                           plot_heatmap_html=plot_heatmap_html,
                           plot_mesh_html=plot_mesh_html,
                           plot_live_html=plot_live_html,
                           plot_pie_systolic_html=plot_pie_systolic_html,
                           plot_pie_diastolic_html=plot_pie_diastolic_html,
                           plot_pie_cholesterol_html=plot_pie_cholesterol_html,
                           plot_pie_hba1c_html=plot_pie_hba1c_html,
                           plot_pie_gender_html=plot_pie_gender_html)

@app.route('/live-data')
def live_data():
    df = pd.read_csv('app/static/kidneyData.csv')
    df_live = df.sample(n=250, random_state=int(time.time()))
    fig_live = px.scatter(df_live, x='CholesterolTotal', y='SerumCreatinine',title='Live Graph of Cholesterol Levels vs Serum Creatinine Levels')
    fig_live.update_layout(width=700, height=700)
    return pio.to_html(fig_live, full_html=False)

@app.route('/LiverPlot')
def index8():
    pio.templates.default = "plotly"
    df=pd.read_csv('app/static/Indian Liver Patient Dataset (ILPD).csv')
    df_disease = df[df['Selector'] == 2].head(250)  

    scatter_fig = px.scatter_3d(df_disease, x='Age', y='TB', z='DB',
                                color='Gender', title='3D Scatter Plot of Age, TB, and DB (Disease Cases Only)',labels={'TB': 'Total Bilirubin', 'DB': 'Direct Bilirubin'},color_discrete_map={'Male': 'blue', 'Female': 'red'})  
    
    scatter_fig.update_layout(scene=dict(xaxis_title='Age',yaxis_title='Total Bilirubin (TB)',zaxis_title='Direct Bilirubin (DB)'),height=800) 

    histogram_fig = px.histogram(df[df['Selector'] == 2], x='Age', color='Gender', 
                                 title='Histogram of Age Groups for People with Disease',labels={'Age': 'Age Groups'},color_discrete_map={'Male': 'blue', 'Female': 'red'},nbins=10)  

    histogram_fig.update_layout(width=600)  

    surface_df = df_disease[['Age', 'Alkphos', 'A/G Ratio']].dropna()

    x = np.linspace(surface_df['Age'].min(), surface_df['Age'].max(), 50)
    y = np.linspace(surface_df['Alkphos'].min(), surface_df['Alkphos'].max(), 50)
    x, y = np.meshgrid(x, y)
    z = np.empty(x.shape)
    
    for i in range(len(x)):
        for j in range(len(y)):
            z[i, j] = np.interp(x[i, j], surface_df['Age'], surface_df['A/G Ratio'])

    surface_fig = go.Figure(data=[go.Surface(z=z, x=x, y=y)])
    surface_fig.update_layout(title='Surface Plot of A/G Ratio, Alkphos, and Age',scene=dict(xaxis_title='Age',yaxis_title='Alkphos',zaxis_title='A/G Ratio'),height=700)  
    heatmap_fig = px.density_heatmap(df_disease, x='Age', y='Sgpt', z='Sgot',title='Heatmap of Age, SGPT, and SGOT',
                                     labels={'Sgpt': 'SGPT (ALT)', 'Sgot': 'SGOT (AST)'},color_continuous_scale='Viridis')

    
    heatmap_fig.update_layout(width=600)  

    
    ag_ratio_pie = df_disease['A/G Ratio'] > 2.5
    ag_ratio_fig = px.pie(df_disease, names=ag_ratio_pie, title='People with A/G Ratio > 2.5',labels={'A/G Ratio': 'A/G Ratio > 2.5'},color_discrete_map={True: 'green', False: 'red'})

    gender_pie_fig = px.pie(df_disease, names='Gender', title='Percent of Males and Females with Disease',labels={'Gender': 'Gender'},color_discrete_map={'Male': 'blue', 'Female': 'red'})

    age_groups = pd.cut(df_disease['Age'], bins=[0, 18, 60, df_disease['Age'].max()], labels=['Below 18', '18-60', 'Above 60'])
    age_group_fig = px.pie(df_disease, names=age_groups, title='Percent of People with Disease by Age Group',labels={'Age': 'Age Group'},color_discrete_map={'Below 18': 'orange', '18-60': 'yellow', 'Above 60': 'purple'})

    tb_pie = df_disease['TB'] > 0.9
    tb_fig = px.pie(df_disease, names=tb_pie, title='People with TB > 0.9',labels={'TB': 'TB > 0.9'},color_discrete_map={True: 'blue', False: 'gray'})

    db_pie = df_disease['DB'] > 0.7
    db_fig = px.pie(df_disease, names=db_pie, title='People with DB > 0.7',labels={'DB': 'DB > 0.7'},color_discrete_map={True: 'cyan', False: 'gray'})

    kmeans = KMeans(n_clusters=3, random_state=0).fit(df_disease[['Age', 'TB', 'DB']])
    df_disease['Cluster'] = kmeans.labels_

    cluster_fig = px.scatter_3d(df_disease, x='Age', y='TB', z='DB',color='Cluster',  title='3D Scatter Plot of Clusters (Age, TB, DB)',labels={'TB': 'Total Bilirubin', 'DB': 'Direct Bilirubin'},
                                color_continuous_scale='Viridis') 

    cluster_fig.update_layout(scene=dict(xaxis_title='Age',yaxis_title='Total Bilirubin (TB)',zaxis_title='Direct Bilirubin (DB)'),height=800)  

    scatter_graphJSON = pio.to_json(scatter_fig)
    histogram_graphJSON = pio.to_json(histogram_fig)
    surface_graphJSON = pio.to_json(surface_fig)
    heatmap_graphJSON = pio.to_json(heatmap_fig)
    ag_ratio_graphJSON = pio.to_json(ag_ratio_fig)
    gender_pie_graphJSON = pio.to_json(gender_pie_fig)
    age_group_graphJSON = pio.to_json(age_group_fig)
    tb_graphJSON = pio.to_json(tb_fig)
    db_graphJSON = pio.to_json(db_fig)
    cluster_graphJSON = pio.to_json(cluster_fig)

    return render_template('index.html', 
                           scatter_graphJSON=scatter_graphJSON,
                           histogram_graphJSON=histogram_graphJSON,
                           surface_graphJSON=surface_graphJSON,
                           heatmap_graphJSON=heatmap_graphJSON,
                           ag_ratio_graphJSON=ag_ratio_graphJSON,
                           gender_pie_graphJSON=gender_pie_graphJSON,
                           age_group_graphJSON=age_group_graphJSON,
                           tb_graphJSON=tb_graphJSON,
                           db_graphJSON=db_graphJSON,
                           cluster_graphJSON=cluster_graphJSON)

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
