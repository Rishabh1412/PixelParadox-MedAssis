from app import app,db, session
from flask import render_template, redirect, url_for, flash, request, jsonify
from app.forms import OtpForm,SignInForm,SignUpForm,UserProfileForm
from app.models import User
import random
from functools import wraps

user_details=[]


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
        
        print("IN OTP")
        # Access form data
        otpnum=int(str(otpform.otp1.data)+str(otpform.otp2.data)+str(otpform.otp3.data)+str(otpform.otp4.data)+str(otpform.otp5.data)+str(otpform.otp6.data))
        
        print(otpnum)
        
        
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
            
            return redirect(url_for('dashboard'))
        flash(f"Wrong OTP entered !!! Please enter a valid OTP !!!", category='error')
    return render_template('otp.html',otpform=otpform)

@app.route('/logout')
@login_required_user
def logout():
    print("Logout")
    session.pop('user_id', None)
    return redirect(url_for('home'))
