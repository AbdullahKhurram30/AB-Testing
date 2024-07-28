from flask import render_template, request, redirect, url_for
# flask_login is used to manage the user sessions
from flask_login import UserMixin, login_user, login_required, logout_user, current_user
# flask_wtf is used to create the forms
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import input_required, ValidationError
import random

try:
    from app import app, db, login_manager, bcrypt
except ImportError:
    from __init__ import app, db, login_manager, bcrypt

@app.before_first_request
def create_tables():
    '''
    This function is used to create the tables in the database
    '''
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    '''
    This function is used to load the user from the database
    '''
    return User.query.get(int(user_id))

# I will use classes to store various attributes and keep track of the objects created to manage various users

# make a class for users
class User(db.Model, UserMixin):
    '''
    This class is used to create the user objects

    Attributes:
        id: the id of the user
        username: the username of the user
        password: the password of the user
        page_type: the version of the page that the user is viewing
        visits: the number of times the user has visited the page
        total_donation: the total amount of donations made by the user

    Methods:
        __repr__: returns the string representation of the object
    '''
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    page_type = db.Column(db.Integer, nullable=False)
    visits = db.Column(db.Integer, nullable=False)
    total_donation = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"User('{self.username}')" # this is the string representation of the object
    
# make a class for tasks
class Donation(db.Model):
    '''
    This class is used to create the Donation objects

    Attributes:
        id: the id of the donation
        user_id: the id of the user who created the task
        amount: the amount of the donation made

    Methods:
        __repr__: returns the string representation of the object
    '''
    __tablename__ = 'Donations'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Donation('{self.id}', '{self.user_id}')"
    
# make a class for the registration form
class RegistrationForm(FlaskForm):
    '''
    This class is used to create the registration form

    Attributes:
        username: the username of the user
        password: the password of the user
        submit: the submit button

    Methods:
        validate_username: validates the username
    '''
    username = StringField('Username', validators=[input_required()])
    password = PasswordField('Password', validators=[input_required()])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        '''
        This function is used to validate the username
        '''
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')
        
# make a class for the login form
class LoginForm(FlaskForm):
    '''
    This class is used to create the login form

    Attributes:
        username: the username of the user
        password: the password of the user
        submit: the submit button
    '''
    username = StringField('Username', validators=[input_required()])
    password = PasswordField('Password', validators=[input_required()])
    submit = SubmitField('Login')

@app.route('/')
def home():
    '''
    This function is used to render the home page which is the same as the login page
    '''
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    '''
    This function is used to render the login page
    '''
    # create the login form
    form = LoginForm()
    # check if the form is valid
    if form.validate_on_submit():
        # get the user from the database
        user = User.query.filter_by(username=form.username.data).first()
        # check if the user exists
        if user:
            # check if the password is correct
            if bcrypt.check_password_hash(user.password, form.password.data):
                # login the user
                login_user(user)
                # redirect to the dashboard
                return redirect(url_for('dashboard'))
        # if the user does not exist or the password is incorrect
        else:
            error = 'Invalid username or password. Please try again.'
            return render_template('login.html', form=form, error=error)
    # if the form is not valid
    else:
        return render_template('login.html', form=form)
    
@app.route('/register', methods=['GET', 'POST'])
def register():
    '''
    This function is used to render the registration page
    '''
    # create the registration form
    form = RegistrationForm()
    # check if the form is valid
    if form.validate_on_submit():
        # hash the password
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        # create the user object
        user = User(username=form.username.data, password=hashed_password, page_type=random.randint(0, 1), visits=0, total_donation=0)
        # add the user to the database
        db.session.add(user)
        db.session.commit()
        # redirect to the login page
        return redirect(url_for('dashboard'))
    else:
        error = 'Username already exists.'
        return render_template('register.html', form=form, error=error)
    
@app.route('/dashboard')
@login_required
def dashboard():
    '''
    This function is used to render the dashboard page
    '''
    # get the page_type of the user that is logged in
    page_type = current_user.page_type
    # increment the number of visits of the user
    current_user.visits += 1
    db.session.commit()

    if page_type == 0:
        return render_template('index1.html')
    else:
        return render_template('index2.html')

@app.route('/donate', methods=['GET', 'POST'])
@login_required
def donate():
    '''
    This function is used to keep track of the donations that are made    
    '''
    if request.method == 'POST':
        # Retrieve and validate the donation amount
        amount = request.form.get('amount')
        print(f"Donation amount received: {amount}")  # Debugging print
        
        if amount:
            try:
                amount = int(amount)
                print(f"Parsed donation amount: {amount}")  # Debugging print
                # create the donation object
                donation = Donation(user_id=current_user.id, amount=amount)
                # add the donation to the database
                db.session.add(donation)
                db.session.commit()
                # update the total_donation of the user
                current_user.total_donation += amount
                db.session.commit()
                # redirect to the thank you page
                return redirect(url_for('thankyou'))
            except ValueError:
                # Handle the case where amount is not a valid integer
                error = 'Invalid donation amount. Please enter a valid number.'
                return url_for('dashboard', error=error)
        else:
            error = 'Donation amount cannot be empty.'
            return url_for('dashboard', error=error)
        
    else:
        return redirect(url_for('dashboard'))
    
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    '''
    This function is used to logout the user
    '''
    logout_user()
    return redirect(url_for('login'))

@app.route('/thankyou')
@login_required
def thankyou():
    '''
    This function is used to render the thank you page after a successful donation
    '''
    return render_template('thankyou.html')