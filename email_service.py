import os
import random
import string
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta


def generate_otp(length=6):
    """Generate a random numeric OTP"""
    return ''.join(random.choices(string.digits, k=length))


def get_otp_repo():
    """Get the appropriate OTP repository based on database backend"""
    import os
    if os.environ.get('MONGO_URI'):
        from mongo_db import MongoOTPRepo
        return MongoOTPRepo
    else:
        from db import OTPRepo
        return OTPRepo


def store_otp(email, otp, purpose='verification', expiry_minutes=10):
    """Store OTP in database"""
    OTPRepo = get_otp_repo()
    
    OTPRepo.delete_by_email_purpose(email, purpose)
    
    OTPRepo.create({
        'email': email,
        'purpose': purpose,
        'otp': otp,
        'attempts': 0,
        'expires_at': datetime.utcnow() + timedelta(minutes=expiry_minutes)
    })


def verify_otp(email, otp, purpose='verification'):
    """Verify OTP for given email and purpose"""
    OTPRepo = get_otp_repo()
    
    stored = OTPRepo.find_by_email_purpose(email, purpose)
    
    if not stored:
        return False, "No verification code found. Please request a new one."
    
    if datetime.utcnow() > stored.expires_at:
        OTPRepo.delete(stored.id)
        return False, "Verification code has expired. Please request a new one."
    
    stored.attempts += 1
    
    if stored.attempts > 5:
        OTPRepo.delete(stored.id)
        return False, "Too many attempts. Please request a new verification code."
    
    if stored.otp != otp:
        OTPRepo.update(stored.id, {'attempts': stored.attempts})
        return False, f"Invalid code. {5 - stored.attempts} attempts remaining."
    
    OTPRepo.delete(stored.id)
    return True, "Verification successful."


def send_otp_email(to_email, otp, purpose='verification'):
    """Send OTP email using Gmail SMTP"""
    try:
        mail_server = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
        mail_port = int(os.environ.get('MAIL_PORT', '587'))
        mail_username = os.environ.get('MAIL_USERNAME', '')
        mail_password = os.environ.get('MAIL_PASSWORD', '')
        mail_sender = os.environ.get('MAIL_DEFAULT_SENDER', mail_username)
        
        logging.debug(f"Mail server: {mail_server}:{mail_port}, Username configured: {bool(mail_username)}")
        
        if not mail_username or not mail_password:
            logging.warning("Mail credentials not configured - LOCAL DEV MODE: OTP displayed in logs")
            logging.info(f"=== LOCAL DEV MODE === OTP for {to_email} ({purpose}): {otp}")
            print(f"\n{'='*50}")
            print(f"LOCAL DEV MODE - Email not sent")
            print(f"OTP Code: {otp}")
            print(f"Email: {to_email}")
            print(f"Purpose: {purpose}")
            print(f"{'='*50}\n")
            return True
        
        if purpose == 'registration':
            subject = "Verify Your Email - CaupenRost"
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                    <h1 style="color: white; margin: 0;">CaupenRost</h1>
                </div>
                <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
                    <h2 style="color: #333;">Verify Your Email Address</h2>
                    <p style="color: #666; font-size: 16px;">Welcome! Please use the following OTP to complete your registration:</p>
                    <div style="background: #667eea; color: white; font-size: 32px; font-weight: bold; padding: 20px; text-align: center; border-radius: 10px; letter-spacing: 8px; margin: 20px 0;">
                        {otp}
                    </div>
                    <p style="color: #666; font-size: 14px;">This OTP is valid for 10 minutes. Do not share it with anyone.</p>
                    <p style="color: #999; font-size: 12px;">If you didn't request this, please ignore this email.</p>
                </div>
            </div>
            """
        elif purpose == 'login':
            subject = "Login Verification - CaupenRost"
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                    <h1 style="color: white; margin: 0;">CaupenRost</h1>
                </div>
                <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
                    <h2 style="color: #333;">Login Verification</h2>
                    <p style="color: #666; font-size: 16px;">Use the following OTP to complete your login:</p>
                    <div style="background: #667eea; color: white; font-size: 32px; font-weight: bold; padding: 20px; text-align: center; border-radius: 10px; letter-spacing: 8px; margin: 20px 0;">
                        {otp}
                    </div>
                    <p style="color: #666; font-size: 14px;">This OTP is valid for 10 minutes. Do not share it with anyone.</p>
                    <p style="color: #999; font-size: 12px;">If you didn't try to login, please secure your account immediately.</p>
                </div>
            </div>
            """
        elif purpose == 'order':
            subject = "Confirm Your Order - CaupenRost"
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                    <h1 style="color: white; margin: 0;">CaupenRost</h1>
                </div>
                <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
                    <h2 style="color: #333;">Confirm Your Order</h2>
                    <p style="color: #666; font-size: 16px;">Please enter the following OTP to confirm your order:</p>
                    <div style="background: #28a745; color: white; font-size: 32px; font-weight: bold; padding: 20px; text-align: center; border-radius: 10px; letter-spacing: 8px; margin: 20px 0;">
                        {otp}
                    </div>
                    <p style="color: #666; font-size: 14px;">This OTP is valid for 10 minutes. Do not share it with anyone.</p>
                    <p style="color: #999; font-size: 12px;">If you didn't place this order, please ignore this email.</p>
                </div>
            </div>
            """
        else:
            subject = "Your OTP - CaupenRost"
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                    <h1 style="color: white; margin: 0;">CaupenRost</h1>
                </div>
                <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
                    <h2 style="color: #333;">Your Verification Code</h2>
                    <p style="color: #666; font-size: 16px;">Use the following OTP to verify your action:</p>
                    <div style="background: #667eea; color: white; font-size: 32px; font-weight: bold; padding: 20px; text-align: center; border-radius: 10px; letter-spacing: 8px; margin: 20px 0;">
                        {otp}
                    </div>
                    <p style="color: #666; font-size: 14px;">This OTP is valid for 10 minutes.</p>
                </div>
            </div>
            """
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = mail_sender
        msg['To'] = to_email
        
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        try:
            logging.debug(f"Connecting to SMTP server {mail_server}:{mail_port} with TLS")
            with smtplib.SMTP(mail_server, mail_port, timeout=30) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(mail_username, mail_password)
                server.sendmail(mail_sender, to_email, msg.as_string())
            logging.info(f"OTP email sent to {to_email} for {purpose}")
            return True
        except Exception as tls_error:
            logging.warning(f"TLS connection failed: {str(tls_error)}, trying SSL on port 465")
            try:
                with smtplib.SMTP_SSL(mail_server, 465, timeout=30) as server:
                    server.login(mail_username, mail_password)
                    server.sendmail(mail_sender, to_email, msg.as_string())
                logging.info(f"OTP email sent to {to_email} for {purpose} via SSL")
                return True
            except Exception as ssl_error:
                logging.error(f"SSL connection also failed: {str(ssl_error)}")
                raise ssl_error
        
    except Exception as e:
        logging.error(f"Failed to send OTP email: {str(e)}")
        return False


def send_and_store_otp(email, purpose='verification'):
    """Generate, store and send OTP via Gmail SMTP"""
    otp = generate_otp()
    store_otp(email, otp, purpose)
    success = send_otp_email(email, otp, purpose)
    return success
