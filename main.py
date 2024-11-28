from flask import Flask, render_template, url_for, redirect,flash,request,jsonify
from datetime import datetime,timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, Float, create_engine,extract
from sqlalchemy.orm import Session
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import random

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'dont_byte_me'
engine=create_engine('sqlite:///database.db')
session=Session(engine)

# Set up LangChain model and prompt template
template = """
Answer the question below.

Here is the conversation history: {context}

Question: {question}
"""
model = OllamaLLM(model="llama3")
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

# In-memory storage for conversation history
conversation_history = ""

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

def determine_menstrual_phase(days_remaining):
    if days_remaining <= 7:
        return "Early Follicular Phase","Low"
    elif days_remaining < 14:
        return "Late Follicular Phase","High"
    elif days_remaining == 14:
        return "Ovulation Phase","Very High"
    elif days_remaining <= 21:
        return "Early Luteal Phase","Moderate"
    elif days_remaining <= 31:
        return "Late Luteal Phase","Low"
    else:
        return "Menstrual Phase","Low"


@app.route('/next_cycle')
def next_cycle():
    periods = Period.query.filter_by(user_id=current_user_id).order_by(Period.period_date.asc()).all()#extracts data from Period class in ascending order of date.(latest addded at last)
    if len(periods) < 2:
        return render_template('next_cycle.html',msg_sent = False,msg = "Not enough data to predict your cycle")
    else:
        period_dates = [period.period_date for period in periods] # creates a list of period_dates from our database
        cycle_length = [(period_dates[i+1]-period_dates[i]).days for i in range(len(period_dates)-1)]
        avg_cycle_length = sum(cycle_length)/len(cycle_length)
        last_period_date = period_dates[-1]
        next_period_date = last_period_date + timedelta(days=avg_cycle_length)
        ovulation_date = next_period_date - timedelta(days=14)
        discharge_date = ovulation_date - timedelta(days=random.randint(5, 7))
        days_remaining = (next_period_date-datetime.now()).days
        if days_remaining < 0:
            return render_template('next_cycle.html',msg_sent = False,msg = "Irregular period detected. It is better to seek medical help if it lasts more than 35 days.")
        elif days_remaining > 35:
            return render_template('next_cycle.html',msg_sent = False,msg = "Invalid information entered.")
        else:
            determine_menstrual_phase(days_remaining)
            menstrual_phase,chance_of_pregnancy = determine_menstrual_phase(days_remaining)
            return render_template('next_cycle.html',next_period = next_period_date.strftime('%Y-%m-%d'),days_remaining = days_remaining,menstrual_phase = menstrual_phase, msg_sent = True,chance_of_pregnancy =chance_of_pregnancy)


@app.route('/delete/<int:period_id>', methods=["GET", "POST"])
def delete(period_id):
    # Convert the string date back to datetime obj
    period_to_delete = Period.query.filter_by(id=period_id).first()
    db.session.delete(period_to_delete)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

# API endpoint for chatbot responses
@app.route('/chat', methods=['POST'])
def chat():
    global conversation_history
    user_message = request.json.get('message', '')

    # Generate response using LangChain
    result = chain.invoke({"context": conversation_history, "question": user_message})
    bot_response = str(result)

    # Update conversation history
    conversation_history += f"\nUser: {user_message}\nAI: {bot_response}"

    return jsonify({'response': bot_response})
    
    # Simple chatbot logic (replace this with actual chatbot logic)
    if user_message.lower() == "hello":
        bot_response = "Hi there! How can I assist you today?"
    elif user_message.lower() == "bye":
        bot_response = "Goodbye! Have a great day!"
    else:
        bot_response = "I'm sorry, I don't understand that. Can you try rephrasing?"

    return jsonify({'response': bot_response})

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)