from app import app,db, session
from flask import render_template, redirect, url_for, flash, request, jsonify
from app.forms import DiabetesForm,OtpForm,SignInForm,SignUpForm,LiverForm,KidneyForm,XrayForm,ReminderForm,UserProfileForm,FeedbackForm,ChatbotForm,DietChart,DoctorProfileForm,UserAskForm,RetailerReplyForm,AppointmentForm, MedicineForm, RegisterForm
from app.models import User, Checkup, Kidney, Liver,Message, Reminder, Doctor,FormMessage, Appointment, Shop, Medicine
from app.mails import send_email
import numpy as np
import pickle
import random
import pandas as pd
import json
import plotly
import plotly.express as px
import plotly.graph_objs as go
import plotly.io as pio
from scipy.interpolate import griddata
import time
from sklearn.cluster import KMeans
from flask_socketio import SocketIO, join_room, leave_room, send,emit
from app import socketio
from datetime import datetime
from app.chatbotFunction import getResponse
from app.format_text import format_text
from app.foodResponse import check_food_safety
from app.medicineFunction import get_medicine_information_from_image
from app.hospitalFunction import generate_hospital_map
from functools import wraps
from app.diet_chart import generate_diet_chart
from app.make_table import format_response_as_table
import pytz

model = pickle.load(open('app/static/model.pkl', 'rb'))
scaler = pickle.load(open('app/static/scaler.pkl', 'rb'))
kidney_model=pickle.load(open('app/static/Kidney_model.pkl', 'rb'))
kidney_scaler=pickle.load(open('app/static/Scaling_kidney.pkl', 'rb'))
liver_model=pickle.load(open('app/static/liver_model.pkl', 'rb'))
liver_scaler=pickle.load(open('app/static/liver_scaler.pkl', 'rb'))

def get_current_user():
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

def get_current_doctor():
    if 'doctor_id' in session:
        return Doctor.query.get(session['doctor_id'])
    return None

def get_current_shop():
    if 'shop_id' in session:
        return Shop.query.get(session['shop_id'])
    return None

def login_required_user(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def login_required_doctor(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'doctor_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('doctorlogin'))
        return f(*args, **kwargs)
    return decorated_function

def login_required_shop(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'shop_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('shoplogin'))
        return f(*args, **kwargs)
    return decorated_function

def update_value_in_row_and_column(table, filter_column_name, filter_value, target_column_name, new_value):
    # Step 1: Search for the row where filter_column_name equals filter_value
    record = table.query.filter(getattr(table, filter_column_name) == filter_value).first()
    
    if not record:
        raise ValueError(f"No record found where '{filter_column_name}' equals '{filter_value}'.")

    # Step 2: Check if the target column exists
    if not hasattr(record, target_column_name):
        raise ValueError(f"Column '{target_column_name}' does not exist in the table.")
    
    # Step 3: Update the value in the target column
    setattr(record, target_column_name, new_value)
    
    # Commit the changes to the database
    db.session.commit()

    return f"Updated '{target_column_name}' with value '{new_value}' where '{filter_column_name}' equals '{filter_value}'."

def update_val_to_no(table, filter_column_name, filter_value, target_column_name, new_value):
    record = table.query.filter(getattr(table, filter_column_name) == filter_value).first()
    
    if not record:
        raise ValueError(f"No record found where '{filter_column_name}' equals '{filter_value}'.")

    # Step 2: Check if the target column exists
    if not hasattr(record, target_column_name):
        raise ValueError(f"Column '{target_column_name}' does not exist in the table.")
    
    # Step 3: Update the value in the target column
    setattr(record, target_column_name, new_value)
    
    # Commit the changes to the database
    db.session.commit()

    return f"Updated '{target_column_name}' with value '{new_value}' where '{filter_column_name}' equals '{filter_value}'."


valid_room_codes = {}

def generate_room_code():
    return str(random.randint(1000, 9999))


phone=0
name=[]
user=[]
form_id=[]
email=""
pincode=0
result=[]
user_details=[]
get_otp=[]
pred=0

@app.route('/home')
@app.route('/')
def home():
    return render_template('home.html')


@app.route('/api/get_response', methods=['POST', 'GET'])
def api_get_response():
    data = request.get_json()
    prompt = data.get("prompt", "")

    print(data,prompt)

    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400
     
    response = format_text(getResponse(prompt))
    print(response)
    return jsonify({"response": response})


@app.route('/api/foodResponse', methods=['POST', 'GET'])
def api_get_food_response():
    if request.method == 'POST':
        disease = request.form.get('disease', "")
        input_type = request.form.get('input_type', "")
        user_input = request.form.get('user_input', "")
        uploaded_image = request.files.get('uploaded_image')

        print(f'Disease: {disease}')
        print(f'Input Type: {input_type}')
        print(f'User Input: {user_input}')
        if uploaded_image:
            print(f'Uploaded Image: {uploaded_image.filename}')

        
        response = format_text(check_food_safety(user_input, uploaded_image, input_type, disease))
        print(response)
        return jsonify({"response": response})

    return jsonify({"error": "Invalid request method"}), 405

@app.route('/api/medresponse', methods=['POST', 'GET'])
def api_get_med_response():
    if request.method == 'POST':
        uploaded_image = request.files.get('uploaded_image')
        print(f'Uploaded Image: {uploaded_image.filename}')
        response = ""

        if uploaded_image:
            print(f'Uploaded Image: {uploaded_image.filename}')
            response = format_text(get_medicine_information_from_image(uploaded_image))
        else:
            response = "No image provided or incorrect input type."

        print(response)
        return jsonify({"response": response})

    return jsonify({"error": "Invalid request method"}), 405

     

@app.route('/api/test', methods=['GET'])
def api_test():
    return jsonify({"message": "API is working!"})


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required_user
def dashboard():
    
    doctors=Doctor.query.all()
    feedback_form = FeedbackForm()
    dietchart = DietChart()

    if dietchart.validate_on_submit():
        age = dietchart.age.data
        weight = dietchart.weight.data
        height = dietchart.height.data
        disease = dietchart.disease.data
        allergy = dietchart.allergy.data
        preference = dietchart.preference.data
        region = dietchart.region.data

        response = generate_diet_chart(age, weight, height, disease, allergy, preference, region)
        
        print(response)
        
        session['diet_chart_response'] = response

        return redirect(url_for('diet_chart_maker'))

    if feedback_form.validate_on_submit():
        reaction = request.form.get('reaction')  # Capture emoji reaction
        feedback_text = feedback_form.feedback.data  # Capture feedback text

        # Construct the email content
        email_subject = f"Feedback from {get_current_user().username}"
        email_body = f"""
        From: {get_current_user().email_address}<br/>
        Reaction: {reaction}<br/>
        Feedback: {feedback_text}
        """
        send_email("anujkaushal1068@gmail.com", email_subject, email_body)
        print("Email sent successfully!")

        return redirect(url_for('dashboard'))
   
    
    current_user = get_current_user()
    if not current_user:
        return redirect(url_for("login"))

    return render_template('dashboard.html', user_data=current_user,doctors=doctors, feedback_form=feedback_form,dietchart=dietchart)


@app.route('/diet_chart_maker')
def diet_chart_maker():
    response = session.get('diet_chart_response')
    if response:
        print(response)
        session.pop('diet_chart_response', None)

    feedback_form = FeedbackForm()
    if feedback_form.validate_on_submit():
        reaction = request.form.get('reaction')  # Capture emoji reaction
        feedback_text = feedback_form.feedback.data  # Capture feedback text

        # Construct the email content
        email_subject = f"Feedback from {get_current_user().username}"
        email_body = f"""
        From: {get_current_user().email_address}<br/>
        Reaction: {reaction}<br/>
        Feedback: {feedback_text}
        """
        send_email("anujkaushal1068@gmail.com", email_subject, email_body)
        print("Email sent successfully!")

        
        return redirect(url_for('diet_chart_maker'))
    response = format_response_as_table(response)
    return render_template('chart_diet.html', response=response, user_data=get_current_user(), feedback_form=feedback_form)


@app.route('/doctor-dashboard',methods=['GET','POST'])
@login_required_doctor
def doctor_dashboard():
    # appointments=Appointment.query.filter_by(doctor_id=get_current_doctor().id)
    # slots=[appointments.slot1,appointments.slot2,appointments.slot3,appointments.slot4,appointments.slot5,appointments.slot6,appointments.slot7,appointments.slot8,appointments.slot9,appointments.slot10,appointments.slot11,appointments.slot12,appointments.slot13,appointments.slot14,appointments.slot15,appointments.slot16,appointments.slot17,appointments.slot18,]
    # print(slots)
    feedback_form = FeedbackForm()
    if feedback_form.validate_on_submit():
        reaction = request.form.get('reaction')  # Capture emoji reaction
        feedback_text = feedback_form.feedback.data  # Capture feedback text

        # Construct the email content
        email_subject = f"Feedback from {get_current_user().username}"
        email_body = f"""
        From: {get_current_user().email_address}<br/>
        Reaction: {reaction}<br/>
        Feedback: {feedback_text}
        """
        send_email("anujkaushal1068@gmail.com", email_subject, email_body)
        print("Email sent successfully!")

        return redirect(url_for('doctor_dashboard'))
    
    current_doctor = get_current_doctor()
    if not current_doctor:
        return redirect(url_for("doctorlogin"))

    return render_template('doctor_dashboard.html', user_data=current_doctor, feedback_form=feedback_form)



@app.route('/profile',methods=['GET','POST'])
@login_required_user
def profile():

    

    feedback_form = FeedbackForm()
    if feedback_form.validate_on_submit():
        reaction = request.form.get('reaction')  # Capture emoji reaction
        feedback_text = feedback_form.feedback.data  # Capture feedback text

        # Construct the email content
        email_subject = f"Feedback from {get_current_user().username}"
        email_body = f"""
        From: {get_current_user().email_address}<br/>
        Reaction: {reaction}<br/>
        Feedback: {feedback_text}
        """
        send_email("anujkaushal1068@gmail.com", email_subject, email_body)
        print("Email sent successfully!")

        return redirect(url_for('profile'))
    

    profileset=UserProfileForm()
    user_data = User.query.filter_by(id=get_current_user().id).first()

    if profileset.validate_on_submit():
        print("I came here")
        if profileset.gender.data:
            user_data.gender = profileset.gender.data
        if profileset.age.data:
            user_data.age = profileset.age.data
        if profileset.height.data:
            user_data.height = profileset.height.data
        if profileset.weight.data:
            user_data.weight = profileset.weight.data
        if profileset.pincode.data:
            user_data.pincode = profileset.pincode.data
        if profileset.phone.data:
            user_data.phone = profileset.phone.data
        if profileset.city.data:
            user_data.city = profileset.city.data

        print(user_data.gender, user_data.age)
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))

    return render_template('profile.html', user_data=get_current_user(),user=user_data,profileset=profileset,feedback_form=feedback_form)

@app.route('/doctor-profile',methods=['GET','POST'])
@login_required_doctor
def doctor_profile():
    docform=DoctorProfileForm()
    feedback_form=FeedbackForm()
    if feedback_form.validate_on_submit():
        reaction = request.form.get('reaction')  # Capture emoji reaction
        feedback_text = feedback_form.feedback.data  # Capture feedback text

        # Construct the email content
        email_subject = f"Feedback from {get_current_user().username}"
        email_body = f"""
        From: {get_current_user().email_address}<br/>
        Reaction: {reaction}<br/>
        Feedback: {feedback_text}
        """
        send_email("anujkaushal1068@gmail.com", email_subject, email_body)
        print("Email sent successfully!")

        
        return redirect(url_for('doctor_profile'))

    user=Doctor.query.filter_by(id=get_current_doctor().id).first()
    if docform.validate_on_submit():
        print("I came here")
        if docform.gender.data:
            user.gender = docform.gender.data
        if docform.age.data:
            user.age = docform.age.data
        if docform.available.data:
            print(docform.available.data)
            if docform.available.data=="No":
                temp="slot"
                for i in range(1, 19):
                    slots=temp+str(i)
                    result=update_val_to_no(Appointment, 'doctor_id', user.id, slots, True)

            else:
                temp="slot"
                for i in range(1, 19):
                    slots=temp+str(i)
                    result=update_val_to_no(Appointment, 'doctor_id', user.id, slots, False)

            user.availability = docform.available.data
        if docform.specialization.data:
            user.specialization = docform.specialization.data
        if docform.pincode.data:
            user.pincode = docform.pincode.data
        if docform.phone.data:
            user.phone = docform.phone.data
        if docform.city.data:
            user.city = docform.city.data

        print(user.gender, user.age)
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('doctor_profile'))

    return render_template('doctor_profile.html',user=user,user_data=get_current_doctor(),docform=docform,feedback_form=feedback_form)

@app.route('/shop-sign-in', methods=['GET','POST'])
def shoplogin():
    form=SignInForm()
    if form.validate_on_submit():
        with app.app_context():
            attempted_user=Shop.query.filter_by(username=form.username.data).first()
            if attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data):
                session['shop_id']=attempted_user.id
                flash(f'You have successfully logged in as : {attempted_user.username}' , category='success')
                return redirect(url_for('shop_dashboard'))
            else:
                flash(f'Username and password do not match ! Please try again', category='error')
                flash(f'OTP does not match', category='error')

    return render_template('shop_login.html',signin=form)

@app.route('/shop-sign-up', methods=['GET','POST'])
def shop_signup():
    form=RegisterForm()
    if form.validate_on_submit():
        global user_details
        user_details.append(form.username.data)
        user_details.append(form.email_address.data)
        user_details.append(form.password.data)
        user_details.append(form.shop_name.data)
        user_details.append(form.pincode.data)
        user_details.append(form.phno.data)
        global otp
        otp=random.randint(100000, 999999)
        get_otp.append(otp)
        send_email(form.email_address.data,"Medassis Verification", f"Welcome to Medassis !!!\n Your OTP for verification is {otp}. Please enter your OTP to create an account.")
        return redirect(url_for('shop_otp'))
            
        #else:
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='error')

    return render_template('shop_signup.html',signup=form)

@app.route('/shop-otp', methods=['GET','POST'])
def shop_otp():
    otpform=OtpForm()
    if otpform.validate_on_submit():
        global user_details
        global get_otp
        print("IN OTP")
        # Access form data
        otpnum=int(str(otpform.otp1.data)+str(otpform.otp2.data)+str(otpform.otp3.data)+str(otpform.otp4.data)+str(otpform.otp5.data)+str(otpform.otp6.data))
        
        print(otpnum)
        print(get_otp)
        flash("OTP Submited!", category='success')
        if(otpnum==get_otp[0]):
            with app.app_context():
                user_data=Shop(username=user_details[0],
                                email_address=user_details[1],
                                shop_name=user_details[3],
                                pincode=user_details[4],
                                phno=user_details[5],
                                password=user_details[2])
                            
                db.session.add(user_data)
                db.session.commit()
                # login_user(user_data)
                session['shop_id']=user_data.id
                        
            user_details.pop()
            user_details.pop()
            user_details.pop()
            user_details.pop()
            user_details.pop()
            user_details.pop()
            get_otp.pop()
            return redirect(url_for('shop_dashboard'))
        flash(f"Wrong OTP entered !!! Please enter a valid OTP !!!", category='error')
    return render_template('shop_otp.html',otpform=otpform)

@app.route('/shop-dashboard',methods=['GET','POST'])
@login_required_shop
def shop_dashboard():
    medicineform=MedicineForm()
    feedback_form = FeedbackForm()
    shop_data=get_current_shop()
    

    if feedback_form.validate_on_submit():
        reaction = request.form.get('reaction')  # Capture emoji reaction
        feedback_text = feedback_form.feedback.data  # Capture feedback text

        # Construct the email content
        email_subject = f"Feedback from {get_current_user().username}"
        email_body = f"""
        From: {get_current_user().email_address}<br/>
        Reaction: {reaction}<br/>
        Feedback: {feedback_text}
        """
        send_email("anujkaushal1068@gmail.com", email_subject, email_body)
        print("Email sent successfully!")

        
        return redirect(url_for('shop_dashboard'))
    if medicineform.validate_on_submit():
        
        med_data=Medicine.query.filter_by(medicine_name=medicineform.medicine_name.data, shop_name=shop_data.shop_name).first()
        if not med_data:
            print("NO")
            while app.app_context():
                new_data=Medicine(owner_name=shop_data.username,
                                email_address=shop_data.email_address,
                                phno=shop_data.phno,
                                pincode=shop_data.pincode,
                                shop_name=shop_data.shop_name,
                                qty=medicineform.qty.data,
                                medicine_name=medicineform.medicine_name.data,
                                medicine_category=medicineform.medicine_category.data,
                                price=medicineform.price.data)
                db.session.add(new_data)
                db.session.commit()
                return redirect(url_for('shop_dashboard'))

            
        else:
            if medicineform.qty.data:
                med_data.qty=med_data.qty+medicineform.qty.data
            if medicineform.price.data:
                med_data.price=medicineform.price.data

            db.session.commit()
        return redirect(url_for('shop_dashboard'))
    current_shop = get_current_shop()
    if not current_shop:
        return redirect(url_for("shoplogin"))
    results = Medicine.query.filter_by(shop_name=shop_data.shop_name).all()
    print(results)
    

    


    return render_template('shop_dashboard.html', user_data=current_shop, feedback_form=feedback_form, medicineform=medicineform, results=results, shop_data=shop_data)




@app.route('/shop-logout')
@login_required_shop
def shop_logout():
    print("Logout")
    # logout_user()
    session.pop('shop_id', None)
    return redirect(url_for('user_doc'))

@app.route('/map',methods=['GET','POST'])
@login_required_user
def usermap():
    user_data = User.query.filter_by(id=get_current_user().id).first()
    print(user_data.pincode)
    generate_hospital_map(f"{user_data.pincode}")
    feedback_form = FeedbackForm()
    if feedback_form.validate_on_submit():
        reaction = request.form.get('reaction')  # Capture emoji reaction
        feedback_text = feedback_form.feedback.data  # Capture feedback text

        # Construct the email content
        email_subject = f"Feedback from {get_current_user().username}"
        email_body = f"""
        From: {get_current_user().email_address}<br/>
        Reaction: {reaction}<br/>
        Feedback: {feedback_text}
        """
        send_email("anujkaushal1068@gmail.com", email_subject, email_body)
        print("Email sent successfully!")

        
        return redirect(url_for('usermap'))
    return render_template('map.html', pincode=user_data.pincode,user_data=get_current_user())


@app.route('/community-support',methods=['GET','POST'])
@login_required_user
def community():
    feedback_form = FeedbackForm()
    if feedback_form.validate_on_submit():
        reaction = request.form.get('reaction')  # Capture emoji reaction
        feedback_text = feedback_form.feedback.data  # Capture feedback text

        # Construct the email content
        email_subject = f"Feedback from {get_current_user().username}"
        email_body = f"""
        From: {get_current_user().email_address}<br/>
        Reaction: {reaction}<br/>
        Feedback: {feedback_text}
        """
        send_email("anujkaushal1068@gmail.com", email_subject, email_body)
        print("Email sent successfully!")

        return redirect(url_for('community'))
    return render_template('community.html',user_data=get_current_user().username, feedback_form=feedback_form)



@socketio.on('send_message')
def handle_send_message(data):
    print(f"Received message: {data}")
    try:
        timestamp_utc = datetime.fromisoformat(data.get('timestamp').replace('Z', '+00:00'))

        local_tz = pytz.timezone('Asia/Kolkata')
        timestamp_local = timestamp_utc.astimezone(local_tz)
        print(f"Timestamp in local time: {timestamp_local}")

        message = Message(content=data['message'], author=get_current_user(), timestamp=timestamp_local)
        db.session.add(message)
        db.session.commit()
        print("Message saved to database")

    except Exception as e:
        print(f"Error saving message: {e}")
        db.session.rollback()
    else:
        emit('receive_message', {
            'username': get_current_user().username,
            'message': data['message'],
            'timestamp': timestamp_local.isoformat()
        }, broadcast=True)

@app.route('/load_messages')
@login_required_user
def load_messages():
    print("Loading messages...")
    messages = Message.query.order_by(Message.timestamp).all()
    messages_data = [{
        'content': message.content,
        'username': message.author.username,
        'timestamp': message.timestamp.isoformat()
    } for message in messages]
    print(f"Loaded messages: {messages_data}")
    return jsonify({'messages': messages_data})


@app.route('/med-shop', methods=['GET', 'POST'])
def med_shop():
    
    feedback_form = FeedbackForm()
    if feedback_form.validate_on_submit():
        reaction = request.form.get('reaction')  # Capture emoji reaction
        feedback_text = feedback_form.feedback.data  # Capture feedback text

        # Construct the email content
        email_subject = f"Feedback from {get_current_user().username}"
        email_body = f"""
        From: {get_current_user().email_address}<br/>
        Reaction: {reaction}<br/>
        Feedback: {feedback_text}
        """
        send_email("anujkaushal1068@gmail.com", email_subject, email_body)
        print("Email sent successfully!")

        return redirect(url_for('med_shop'))


    return render_template(
        'medicine-platform.html',
        user_data=get_current_user(),
        feedback_form=feedback_form
    )
    
@app.route('/medicine-details')
def medicine_details():
    feedback_form=FeedbackForm()
    if feedback_form.validate_on_submit():
        reaction = request.form.get('reaction')  # Capture emoji reaction
        feedback_text = feedback_form.feedback.data  # Capture feedback text

        # Construct the email content
        email_subject = f"Feedback from {get_current_user().username}"
        email_body = f"""
        From: {get_current_user().email_address}<br/>
        Reaction: {reaction}<br/>
        Feedback: {feedback_text}
        """
        send_email("anujkaushal1068@gmail.com", email_subject, email_body)
        print("Email sent successfully!")

        return redirect(url_for('medicine_details'))
    return render_template('medicine-details.html',user_data=get_current_user(),feedback_form=feedback_form)
    

 



@app.route('/doc_or_user')
def user_doc():
    return render_template('user_or_doctor.html')



@app.route('/appointment/<int:doctor_id>', methods=['GET', 'POST'])
def appointment(doctor_id):
    appointmentform = AppointmentForm()
    appointmentform.doctorId.data = doctor_id

    appointment = Appointment.query.filter_by(doctor_id=doctor_id).first()

    # Define the time slot choices with both label update and disabling logic
    appointmentform.time_slot.choices = [
        ('slot1', '10:00-10:30am') if not appointment or not appointment.slot1 else ('slot1', '10:00-10:30am (Booked)'),
        ('slot2', '10:30-11:00am') if not appointment or not appointment.slot2 else ('slot2', '10:30-11:00am (Booked)'),
        ('slot3', '11:00-11:30am') if not appointment or not appointment.slot3 else ('slot3', '11:00-11:30am (Booked)'),
        ('slot4', '11:30-12:00pm') if not appointment or not appointment.slot4 else ('slot4', '11:30-12:00pm (Booked)'),
        ('slot5', '12:00-12:30pm') if not appointment or not appointment.slot5 else ('slot5', '12:00-12:30pm (Booked)'),
        ('slot6', '12:30-1:00pm') if not appointment or not appointment.slot6 else ('slot6', '12:30-1:00pm (Booked)'),
        ('slot7', '4:00-4:30pm') if not appointment or not appointment.slot7 else ('slot7', '4:00-4:30pm (Booked)'),
        ('slot8', '4:30-5:00pm') if not appointment or not appointment.slot8 else ('slot8', '4:30-5:00pm (Booked)'),
        ('slot9', '5:00-5:30pm') if not appointment or not appointment.slot9 else ('slot9', '5:00-5:30pm (Booked)'),
        ('slot10', '5:30-6:00pm') if not appointment or not appointment.slot10 else ('slot10', '5:30-6:00pm (Booked)'),
        ('slot11', '6:00-6:30pm') if not appointment or not appointment.slot11 else ('slot11', '6:00-6:30pm (Booked)'),
        ('slot12', '6:30-7:00pm') if not appointment or not appointment.slot12 else ('slot12', '6:30-7:00pm (Booked)'),
        ('slot13', '7:00-7:30pm') if not appointment or not appointment.slot13 else ('slot13', '7:00-7:30pm (Booked)'),
        ('slot14', '7:30-8:00pm') if not appointment or not appointment.slot14 else ('slot14', '7:30-8:00pm (Booked)'),
        ('slot15', '8:00-8:30pm') if not appointment or not appointment.slot15 else ('slot15', '8:00-8:30pm (Booked)'),
        ('slot16', '8:30-9:00pm') if not appointment or not appointment.slot16 else ('slot16', '8:30-9:00pm (Booked)'),
        ('slot17', '9:00-9:30pm') if not appointment or not appointment.slot17 else ('slot17', '9:00-9:30pm (Booked)'),
        ('slot18', '9:30-10:00pm') if not appointment or not appointment.slot18 else ('slot18', '9:30-10:00pm (Booked)')
    ]
    # patient_id=User.query.filter_by(userid=get_current_user().id)
    doctor = Doctor.query.filter_by(id=doctor_id).first()
    doctor_mail=doctor.email_address
    if appointmentform.validate_on_submit():
        timeslot = appointmentform.time_slot.data
        date = appointmentform.date.data
        doctorId = appointmentform.doctorId.data
        with app.app_context():
            try:
                result=update_value_in_row_and_column(Appointment, 'doctor_id', doctorId, timeslot, True)
                print(result)
                # Process the form data (e.g., save to the database)
                print("Form Submitted:", timeslot, date, doctorId)
                print(doctor_mail)
                send_email(doctor_mail, "Appointment Fixed", "")

                return redirect(url_for('create_room', doctor_email=doctor_mail))

            except ValueError as e:
                print(e)

    doctor = Doctor.query.filter_by(id=doctor_id).first()

    if doctor is None:
        return "Doctor not found", 404

    feedback_form = FeedbackForm()
    if feedback_form.validate_on_submit():
        reaction = request.form.get('reaction')  # Capture emoji reaction
        feedback_text = feedback_form.feedback.data  # Capture feedback text

        # Construct the email content
        email_subject = f"Feedback from {get_current_user().username}"
        email_body = f"""
        From: {get_current_user().email_address}<br/>
        Reaction: {reaction}<br/>
        Feedback: {feedback_text}
        """
        send_email("anujkaushal1068@gmail.com", email_subject, email_body)
        print("Email sent successfully!")

        return redirect(url_for('appointment', doctor_id=doctor.id))

    return render_template(
        'appointment.html',
        user_data=get_current_user(),
        appointmentform=appointmentform,
        feedback_form=feedback_form,
        doctor=doctor
    )



@app.route('/sign-in', methods=['GET','POST'])
def login():
    form=SignInForm()
    if form.validate_on_submit():
        with app.app_context():
            attempted_user=User.query.filter_by(username=form.username.data).first()
            if attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data):
                # login_user(attempted_user)
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


@app.route('/doctor-sign-in', methods=['GET', 'POST'])
def doctorlogin():
    form = SignInForm()
    if form.validate_on_submit():
        with app.app_context():
            attempted_user = Doctor.query.filter_by(username=form.username.data).first()
            try:
                if attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data):
                    session['doctor_id'] = attempted_user.id
                    flash(f'You have successfully logged in as: {attempted_user.username}', category='success')
                    return redirect(url_for('doctor_dashboard'))
                else:
                    flash('Username and password do not match! Please try again.', category='error')
            except Exception as e:
                flash(f'An error occurred: {str(e)}', category='error')
                flash('OTP does not match', category='error')

    return render_template('doctor_login.html', signin=form)



@app.route('/doctor-sign-up', methods=['GET','POST'])
def doctor_signup():
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
        return redirect(url_for('doctor_otp'))
            
        #else:
           # flash(f"Wrong OTP eneted !!! Please enter it correctly", category='error')
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='error')

    return render_template('doctor_signup.html',signup=form)

@app.route('/logout')
@login_required_user
def logout():
    print("Logout")
    # logout_user()
    session.pop('user_id', None)
    return redirect(url_for('user_doc'))

@app.route('/doctor-logout')
@login_required_doctor
def doctor_logout():
    print("Logout")
    # logout_user()
    session.pop('doctor_id', None)
    return redirect(url_for('user_doc'))

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
        flash("OTP Submited!", category='success')
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

@app.route('/doctor-otp', methods=['GET','POST'])
def doctor_otp():
    otpform=OtpForm()
    if otpform.validate_on_submit():
        global user_details
        global get_otp
        print("IN OTP")
        # Access form data
        otpnum=int(str(otpform.otp1.data)+str(otpform.otp2.data)+str(otpform.otp3.data)+str(otpform.otp4.data)+str(otpform.otp5.data)+str(otpform.otp6.data))
        
        print(otpnum)
        print(get_otp)
        flash("OTP Submited!", category='success')
        if(otpnum==get_otp[0]):
            with app.app_context():
                user_data=Doctor(username=user_details[0],
                                email_address=user_details[1],
                                password=user_details[2])
                            
                db.session.add(user_data)
                db.session.commit()
                # login_user(user_data)
                session['doctor_id']=user_data.id
            
            with app.app_context():
                    appointment=Appointment(doctor_id=get_current_doctor().id)
                    db.session.add(appointment)
                    db.session.commit()
            
            user_details.pop()
            user_details.pop()
            user_details.pop()
            get_otp.pop()
            return redirect(url_for('doctor_dashboard'))
        flash(f"Wrong OTP entered !!! Please enter a valid OTP !!!", category='error')
    return render_template('doctor_otp.html',otpform=otpform)

@app.route('/meeting')
def meeting():
    room_id = request.args.get("roomID")
    if not room_id:
        room_id = generate_room_code()
    print(f"Room ID: {room_id}")
    if get_current_doctor():
        user_data=get_current_doctor().username
    else:
        user_data=get_current_user().username
    return render_template("meeting.html", user_data=user_data)


@app.route('/join', methods=['GET', 'POST'])
def join():
    if request.method == "POST":
        room_id = request.form.get("roomID")
        if room_id in valid_room_codes:
            return redirect(f"/meeting?roomID={room_id}")
        else:
            flash("Invalid room code. Please try again.")
            return redirect('/join')
    return render_template('join.html')


@app.route('/create_room', methods=['GET'])
def create_room():
    doctor_email = request.args.get('doctor_email') 
    room_id = generate_room_code()
    valid_room_codes[room_id] = True
    send_email(doctor_email,"Join code for the appointment.",f"The joining code is {room_id}.")
    print(f"Generated Room Code: {room_id}")
    return redirect('/dashboard')


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
    return render_template('result_diabetes.html', user_data=user_data, current_user=get_current_user, phone=phone, pincode=pincode, email=email, pred=pred)




@app.route('/liver-form', methods=['GET','POST'])
def liver():
    liverform=LiverForm()
    if liverform.validate_on_submit():
        name = liverform.name.data
        age = liverform.age.data
        gender = liverform.gender.data
        global phone
        global pincode
        global user
        user.append(name)
        address = liverform.address.data
        pincode = liverform.pincode.data
        total_protein = liverform.total_protein.data
        albumin = liverform.albumin.data
        ag_ratio = liverform.ag_ratio.data
        total_bilirubin = liverform.total_bilirubin.data
        direct_bilirubin = liverform.direct_bilirubin.data
        alkaline_phosphate = liverform.alkaline_phosphate.data
        sgpt = liverform.sgpt.data
        sgot = liverform.sgot.data
        height = liverform.height.data
        weight = liverform.weight.data
        phone = liverform.phone.data
        total_protein=float(total_protein)
        albumin=float(albumin)
        ag_ratio=float(ag_ratio)
        height=float(height)
        weight=float(weight)

        if gender=="Male":
            gender_val=1
        else:
            gender_val=0
    
        if total_bilirubin>=5.3:
            tb_low=0
            tb_medium=0
            tb_veryhigh=1
        elif total_bilirubin<5.3 and total_bilirubin>=2.6:
            tb_low=0
            tb_medium=0
            tb_veryhigh=0
        elif total_bilirubin<2.6 and total_bilirubin>=0.8:
            tb_low=0
            tb_medium=1
            tb_veryhigh=0
        else:
            tb_low=1
            tb_medium=0
            tb_veryhigh=0

        if direct_bilirubin>=2.95:
            db_low=0
            db_medium=0
            db_veryhigh=1
        elif direct_bilirubin<2.95 and direct_bilirubin>=1.3:
            db_low=0
            db_medium=0
            db_veryhigh=0
        elif direct_bilirubin<1.3 and direct_bilirubin>=0.2:
            db_low=0
            db_medium=1
            db_veryhigh=0
        else:
            db_low=1
            db_medium=0
            db_veryhigh=0
        
        if alkaline_phosphate>=481:
            alkphos_low=0
            alkphos_medium=0
            alkphos_veryhigh=1
        elif alkaline_phosphate<481 and alkaline_phosphate>=298:
            alkphos_low=0
            alkphos_medium=0
            alkphos_veryhigh=0
        elif alkaline_phosphate<298 and alkaline_phosphate>=176:
            alkphos_low=0
            alkphos_medium=1
            alkphos_veryhigh=0
        else:
            alkphos_low=1
            alkphos_medium=0
            alkphos_veryhigh=0

        if sgpt>=115.5:
            sgpt_low=0
            sgpt_medium=0
            sgpt_veryigh=1
        elif sgpt<115.5 and sgpt>=66:
            sgpt_low=0
            sgpt_medium=0
            sgpt_veryigh=0
        elif sgpt<66 and sgpt>=23:
            sgpt_low=0
            sgpt_medium=1
            sgpt_veryigh=0
        else:
            sgpt_low=1
            sgpt_medium=0
            sgpt_veryigh=0

        if sgot>=179.395:
            sgot_low=0
            sgot_medium=0
            sgot_veryigh=1
        elif sgot<179.395 and sgot>=86.75:
            sgot_low=0
            sgot_medium=0
            sgot_veryigh=0
        elif sgot<86.75 and sgot>=25:
            sgot_low=0
            sgot_medium=1
            sgot_veryigh=0
        else:
            sgot_low=1
            sgot_medium=0
            sgot_veryigh=0

        if total_protein>=9.3:
            total_protein=9.3
        elif total_protein<=3.7:
            total_protein=3.7
        

        query=np.array([age, gender_val,total_protein, albumin, ag_ratio, tb_low, tb_medium, tb_veryhigh, db_low, db_medium, db_veryhigh, alkphos_low, alkphos_medium, alkphos_veryhigh, sgpt_low, sgpt_medium, sgpt_veryigh, sgot_low, sgot_medium, sgot_veryigh])
        query = query.reshape(1,20)
        input_trf=liver_scaler.transform(query)
        liver_per=liver_model.predict(input_trf)
        print(liver_per[0][0])

        with app.app_context():
                checkup_data=Liver(name=name,
                                   age=age,
                                   gender=gender,
                                   total_protein=total_protein,
                                   albumin=albumin,
                                   ag_ratio=ag_ratio,
                                   total_bilirubin=total_bilirubin,
                                   direct_bilirubin=direct_bilirubin,
                                   alkaline_phosphate=alkaline_phosphate,
                                   sgpt=sgpt,
                                   sgot=sgot,
                                   height=height,
                                   weight=weight,
                                   liver_per=liver_per
                )
                db.session.add(checkup_data)
                db.session.commit()

        send_email(get_current_user().email_address,"Medassis Report", f'''
                   Name : {name}
                   Gender : {gender}
                   Age : {age}
                   Weight : {weight}
                   Height : {height}
                   Your Chances of Liver Cirhhosis is {liver_per[0][0]*100} %
                   '''
        )
        return redirect(url_for('result_liver'))
        

    
    return render_template('liver.html',liverform=liverform)

@app.route('/result-liver')
@login_required_user
def result_liver():
    global phone
    global pincode
    global user
    with app.app_context():
        user_data=Liver.query.filter_by(name=user[0]).order_by(Liver.form_id.desc()).first()
    user.pop()
    return render_template('result_liver.html', user_data=user_data, current_user=get_current_user, phone=phone, pincode=pincode)




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
        
        send_email(get_current_user().email_address,"Medassis Report", f'''
                   Name : {name}
                   Gender : {gender}
                   Age : {age}
                   Weight : {weight}
                   Height : {height}
                   Your Chances of Kidney Disease is {kidney_per[0][0]*100} %
                   '''
        )
        return redirect(url_for('result_kidney'))
            
                
        

    return render_template('kidney.html',kidneyform=kidneyform)

@app.route('/result-kidney')
@login_required_user
def result_kidney():
    global pred
    with app.app_context():
        user_data=Kidney.query.filter_by(name=user[0]).order_by(Kidney.form_id.desc()).first()
    user.pop()
    return render_template('result_kidney.html', user_data=user_data, current_user=get_current_user, pred=pred)

@app.route('/x-ray-form',methods=['POST','GET'])
def x_ray():
    xrayform=XrayForm()
    if xrayform.validate_on_submit():
        username = xrayform.username.data
        gender = xrayform.gender.data
        age = xrayform.age.data
        height = xrayform.height.data
        weight = xrayform.weight.data
        x_ray_file = xrayform.x_ray.data
        

    return render_template('xray.html',xrayform=xrayform)

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

@app.route('/news',methods=['GET','POST'])
def news():
    feedback_form = FeedbackForm()

    if feedback_form.validate_on_submit():
        reaction = request.form.get('reaction')  # Capture emoji reaction
        feedback_text = feedback_form.feedback.data  # Capture feedback text

        # Construct the email content
        email_subject = f"Feedback from {get_current_user().username}"
        email_body = f"""
        From: {get_current_user().email_address}<br/>
        Reaction: {reaction}<br/>
        Feedback: {feedback_text}
        """
        send_email("anujkaushal1068@gmail.com", email_subject, email_body)
        print("Email sent successfully!")

        return redirect(url_for('news'))

    return render_template('news.html', user_data=get_current_user(),feedback_form=feedback_form)


@app.route('/reminder', methods=['GET','POST'])
def reminder():
    
    reminderform=ReminderForm()
    feedback_form = FeedbackForm()

    if feedback_form.validate_on_submit():
        reaction = request.form.get('reaction')  # Capture emoji reaction
        feedback_text = feedback_form.feedback.data  # Capture feedback text

        # Construct the email content
        email_subject = f"Feedback from {get_current_user().username}"
        email_body = f"""
        From: {get_current_user().email_address}<br/>
        Reaction: {reaction}<br/>
        Feedback: {feedback_text}
        """
        send_email("anujkaushal1068@gmail.com", email_subject, email_body)
        print("Email sent successfully!")

        return redirect(url_for('reminder'))
    
    if reminderform.validate_on_submit():
        with app.app_context():
            email=Reminder(
                email_address=get_current_user().email_address,
                medicine=reminderform.medicine.data,
                reminder_time=reminderform.reminder_time.data
            )
            
            db.session.add(email)
            db.session.commit()
            flash(f'Email scheduled successfully !!!', category='success')
            return redirect(url_for('dashboard'))
    else:
        print(reminderform.errors)
    return render_template('reminder.html',reminderform=reminderform , user_data=get_current_user() , feedback_form = feedback_form)

