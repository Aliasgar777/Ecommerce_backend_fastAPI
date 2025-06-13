import smtplib
from email.message import EmailMessage
from app.core.logger import logger

def send_reset_email(email: str, token: str):
    reset_link = f"http://127.0.0.1:8000/token={token}"
    msg = EmailMessage()
    msg['Subject'] = "Reset Your Password"
    msg['From'] = "aliasgarsaify61@gmail.com"
    msg['To'] = email
    msg.set_content(f"Click the link to reset your password: {reset_link}")
    logger.info(f"email sent for reset password to {email}")
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.login("aliasgarsaify61@gmail.com", "oazjcqbljgfyobwk")
        smtp.send_message(msg)