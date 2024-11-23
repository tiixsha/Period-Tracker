from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, Float, create_engine
from sqlalchemy.orm import Session

app = Flask(__name__)

app.config['SECRET_KEY'] = '123456'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///data-collection.db" 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

engine = create_engine('sqlite:///data-collection.db') # creates a database engine which serves as the connection point to our database.
session = Session(engine) # provides a workspace for database interactions, handles: querying, inserting, updating, and deleting records.


db = SQLAlchemy(app) # initializing the database object(db) that connects to our Flask app

# When you create a Period object and add it to the database, SQLAlchemy uses this class to know how to store and retrieve data.

class Period(db.Model): #Period class inherits from SQLAlchemy's base class for models
    id = db.Column(db.Integer, primary_key=True)  # Auto-incrementing ID
    period_date = db.Column(db.DateTime, nullable=False) 
    def __repr__(self): # used to provide a string representation of an instance of the class (a record of the Period table).
        return f"<Period(id={self.id}, period_date={self.period_date})>"


# # In-memory storage for the user's period dates(to be stored in database later.)
# period_dates = []

@app.route('/')
def index():
    periods = Period.query.order_by(Period.period_date.desc()).all() #queries the database to get all rows from the Period table, ordered by period_date in descending order (latest dates first).
    return render_template('index.html', periods=periods)


@app.route('/delete/<int:period_id>', methods=["GET", "POST"])
def delete(period_id):
    # Convert the string date back to datetime obj
    period_to_delete = Period.query.filter_by(id=period_id).first()
    db.session.delete(period_to_delete)
    db.session.commit()
    return redirect(url_for('index'))
   

@app.route('/add', methods=['POST']) 
def add_period():
    try:
    
        date_input = request.form.get('period_date')# Retrieve and parse the date from the form
        period_date = datetime.strptime(date_input, "%Y-%m-%d")
        
        # Check if the date already exists in the database
        existing_period = Period.query.filter_by(period_date=period_date).first() # queries the database to find an existing record in the Period table that matches a specific period_date and returns the first result
        if existing_period:
            flash("This date already exists in the database.", "warning")
            return redirect(url_for('index'))

        # Create a new Period instance
        new_period = Period(period_date=period_date)

        # Add the period to the database
        db.session.add(new_period)
        db.session.commit()
        flash("Period date added successfully!", "success")
        return redirect(url_for('index'))
    except Exception as e:
        flash(f"An error occurred: {e}", "error")
        return redirect(url_for('index'))


@app.route('/blogs')
def blog():
    return render_template('blogs.html')

@app.route('/next-cycle')
def predict_next_period():
    periods = Period.query.order_by(Period.period_date.asc()).all() #extracts data from Period class in ascending order of date.(latest addded at last)
    if len(periods) < 2:
        return render_template('next_cycle.html',msg_sent = False)
    else:
        period_dates = [period.period_date for period in periods] # creates a list of period_dates from our database
        cycle_length = [(period_dates[i+1]-period_dates[i]).days for i in range(len(period_dates)-1)]
        avg_cycle_length = sum(cycle_length)/len(cycle_length)
        last_period_date = period_dates[-1]
        next_period_date = last_period_date + timedelta(days=avg_cycle_length)
        return render_template('next_cycle.html',next_period = next_period_date.strftime('%Y-%m-%d'), msg_sent = True)
    

@app.route('/insights')
def insights():
    # Pass any data needed for insights rendering
    return render_template('insights.html')



if __name__ == "__main__":
    # Wrap database operations in the app context
    with app.app_context():
        db.create_all()  # Create all tables
    app.run(debug=True)
