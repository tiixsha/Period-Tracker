# another_file.py
from main import db, Emaildb
from app import app

 MY_EMAIL = "tishamdr123@gmail.com"
MY_PASSWORD = "najy zwnk njhy cnbl"

def get_all_emails():
    with app.app_context():  # Ensure the context is set
        emails = Emaildb.query.all()
        for email in emails:
            
                if days_remaining==14:
                    content = "🌸 Ovulation Day Alert! 🌸: Today is a key day in your cycle—it's your ovulation day! This means your chances of conception are at their highest. Take care of yourself and make the most of it!"
                elif days_remaining == 3 | days_remaining == 2 | days_remaining == 1:
                    content = f"🗓️ Period Reminder! 🗓️: Just a heads-up, your period is only {{days_remaining}} days away. Now's a great time to prepare and ensure you have everything you need. Take care and be kind to yourself!"
                elif days_remaining == 0:
                    content = "🌹 Period Day Alert! 🌹: Today marks the start of your period. Remember to take extra care of yourself during this time. To help ease period pain, try incorporating foods like dark leafy greens, which are rich in iron and help replenish lost nutrients. Bananas are great for cramps and bloating due to their high potassium content. Nuts and seeds are packed with magnesium, which can help reduce muscle cramps. Berries are full of antioxidants and vitamins, helping to reduce inflammation. Chamomile tea is known for its soothing effects and can help relax your muscles and ease cramps. Take it easy and nurture your body today!"
                else:
                    content = f"🗓️ Period Countdown Alert! 🗓️ Just a friendly reminder, there are only {days_remaining} days remaining until your period. Now's a perfect time to get prepared and ensure you have everything you need. Take it easy and be kind to yourself!"
                
                with smtplib.SMTP("smtp.gmail.com",port = 587) as connection:
                    connection.starttls()
                    connection.login(MY_EMAIL, MY_PASSWORD)
                    connection.sendmail(
                        from_addr=MY_EMAIL,
                        to_addrs=user_mail,
                        msg=f"Subject:FlowSync\n\n{content}".encode('utf-8')
                        )
def get_email_by_user_id(user_id):
    with app.app_context():  # Ensure the context is set
        email = Email.query.filter_by(user_id=user_id).first()
        if email:
            print(f"User ID: {email.user_id}, Email: {email.user_email}, Next Period: {email.next_period}")
        else:
            print("No email found for this user_id")

# Example function calls
get_all_emails()
get_email_by_user_id(1)
