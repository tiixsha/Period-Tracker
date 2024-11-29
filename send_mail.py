# another_file.py
from main import db, Emaildb
from app import app
import smtplib
import os
from dotenv import load_dotenv

load_dotenv()

MY_EMAIL = "tishamdr123@gmail.com"
MY_PASSWORD = os.environ.get("PASSWORD")

def get_all_emails():
    with app.app_context():  
        emails = Emaildb.query.all()
        for email in emails:
                days_remaining = email.next_period
                user_mail = email.user_email
                if days_remaining==14:
                    content = "🌸 Ovulation Day Alert! 🌸: Today is a key day in your cycle—it's your ovulation day! This means your chances of conception are at their highest. Take care of yourself and make the most of it!"
                elif days_remaining == 3 | days_remaining == 2 | days_remaining == 1:
                    content = f"🗓️ Period Reminder! 🗓️: Just a heads-up, your period is only {{days_remaining}} days away. Now's a great time to prepare and ensure you have everything you need. Take care and be kind to yourself!"
                elif days_remaining == 0:
                    content = "🌹 Period Day Alert! 🌹: Today marks the start of your period. Remember to take extra care of yourself during this time. To help ease period pain, try incorporating foods like dark leafy greens, which are rich in iron and help replenish lost nutrients. Bananas are great for cramps and bloating due to their high potassium content. Nuts and seeds are packed with magnesium, which can help reduce muscle cramps. Berries are full of antioxidants and vitamins, helping to reduce inflammation. Chamomile tea is known for its soothing effects and can help relax your muscles and ease cramps. Take it easy and nurture your body today!"
                else:
                     content = ""
                if content:
                     with smtplib.SMTP("smtp.gmail.com",port = 587) as connection:
                        connection.starttls()
                        connection.login(MY_EMAIL, MY_PASSWORD)
                        connection.sendmail(
                            from_addr=MY_EMAIL,
                            to_addrs=user_mail,
                            msg=f"Subject:FlowSync\n\n{content}".encode('utf-8')
                            )
                
get_all_emails()