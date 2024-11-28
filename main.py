from flask import Flask, render_template, url_for, redirect,flash,request
from datetime import datetime,timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, Float, create_engine,extract
from sqlalchemy.orm import Session
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'dont_byte_me'
engine=create_engine('sqlite:///database.db')
session=Session(engine)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    def __repr__(self): 
        return f"<User(user_id={self.id})>"

class Period(db.Model): 
    id = db.Column(db.Integer, primary_key=True) 
    user_id=db.Column(db.Integer,nullable=False) 
    period_date = db.Column(db.DateTime, nullable=False) 
    def __repr__(self): 
        return f"<Period(id={self.id}, period_date={self.period_date})>"

class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')


class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                global current_user_id
                current_user_id=user.id
                login_user(user)
                return redirect(url_for('index'))
            else:
                flash('Incorrect passsword or username','warning')
    
    return render_template('login.html', form=form)


@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    periods = Period.query.order_by(Period.period_date.desc()).all() 
    return render_template('index.html', periods=periods,id = current_user_id)  
 

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@ app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/add', methods=['POST']) 
def add_period():
    try:
    
        date_input = request.form.get('period_date')# Retrieve and parse the date from the form
        period_date = datetime.strptime(date_input, "%Y-%m-%d")
        period_month = period_date.month
        # Check if the date already exists in the database
        existing_period = Period.query.filter((Period.period_date == period_date) & (Period.user_id == current_user_id)).first()
         # queries the database to find an existing record in the Period table that matches a specific period_date and returns the first result
        if existing_period:
            flash("This date already exists in the database.", "warning")
            return redirect(url_for('index'))
        existing_month = Period.query.filter((extract('year', Period.period_date)== period_date.year)&((extract('month', Period.period_date) == period_date.month)) & (Period.user_id == current_user_id)).first()
        if existing_month:
            flash("You've already entered the data for this month", "warning")
            return redirect(url_for('index'))
        # Create a new Period instance
        new_period = Period(period_date=period_date,user_id=current_user_id)
        # Add the period to the database
        db.session.add(new_period)
        db.session.commit()
        flash("Period date added successfully!", "success")
        return redirect(url_for('index'))
    except Exception as e:
        flash(f"An error occurred: {e}", "error")
        return redirect(url_for('index'))

@app.route('/blog')
def blog():
    return render_template("blogs.html")

@app.route('/insights')
def insights():
    return render_template("insights.html")

@app.route('/predict_next_period')
def predict_next_period():
    return "next period"

@app.route('/delete/<int:period_id>', methods=["GET", "POST"])
def delete(period_id):
    # Convert the string date back to datetime obj
    period_to_delete = Period.query.filter_by(id=period_id).first()
    db.session.delete(period_to_delete)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)