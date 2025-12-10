import os
import random
import string
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

from data_store import data_store


def init_otp_store():
    """Initialize OTP storage in data_store"""
    if 'otp_codes' not in data_store:
        data_store['otp_codes'] = {}


def generate_otp(length=6):
    """Generate a random numeric OTP"""
    return ''.join(random.choices(string.digits, k=length))


def store_otp(email, otp, purpose='verification', expiry_minutes=10):
    """Store OTP in server-side data_store for cross-worker persistence"""
    init_otp_store()
    key = f"{email}_{purpose}"
    data_store['otp_codes'][key] = {
        'otp': otp,
        'created_at': datetime.now(),
        'expires_at': datetime.now() + timedelta(minutes=expiry_minutes),
        'attempts': 0
    }


def verify_otp(email, otp, purpose='verification'):
    """Verify OTP for given email and purpose using server-side storage"""
    init_otp_store()
    key = f"{email}_{purpose}"
    
    if key not in data_store['otp_codes']:
        return False, "No verification code found. Please request a new one."
    
    stored = data_store['otp_codes'][key]
    
    if datetime.now() > stored['expires_at']:
        del data_store['otp_codes'][key]
        return False, "Verification code has expired. Please request a new one."
    
    stored['attempts'] += 1
    
    if stored['attempts'] > 5:
        del data_store['otp_codes'][key]
        return False, "Too many attempts. Please request a new verification code."
    
    if stored['otp'] != otp:
        return False, f"Invalid code. {5 - stored['attempts']} attempts remaining."
    
    del data_store['otp_codes'][key]
    return True, "Verification successful."


def get_stored_otp(email, purpose='verification'):
    """Get the stored OTP for display (fallback)"""
    init_otp_store()
    key = f"{email}_{purpose}"
    if key in data_store['otp_codes']:
        return data_store['otp_codes'][key]['otp']
    return None


def send_otp_email(to_email, otp, purpose='verification'):
    """Send OTP email using Gmail SMTP"""
    try:
        gmail_user = os.environ.get('GMAIL_EMAIL')
        gmail_password = os.environ.get('GMAIL_APP_PASSWORD')
        
        if not gmail_user or not gmail_password:
            logging.error("Gmail credentials not configured")
            return False
        
        if purpose == 'registration':
            subject = "Verify Your Email - NIKITA RASOI & BAKES"
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                    <h1 style="color: white; margin: 0;">NIKITA RASOI & BAKES</h1>
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
            subject = "Login Verification - NIKITA RASOI & BAKES"
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                    <h1 style="color: white; margin: 0;">NIKITA RASOI & BAKES</h1>
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
            subject = "Confirm Your Order - NIKITA RASOI & BAKES"
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                    <h1 style="color: white; margin: 0;">NIKITA RASOI & BAKES</h1>
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
            subject = "Your OTP - NIKITA RASOI & BAKES"
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                    <h1 style="color: white; margin: 0;">NIKITA RASOI & BAKES</h1>
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
        msg['From'] = gmail_user
        msg['To'] = to_email
        
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(gmail_user, gmail_password)
            server.sendmail(gmail_user, to_email, msg.as_string())
        
        logging.info(f"OTP email sent to {to_email} for {purpose}")
        return True
        
    except Exception as e:
        logging.error(f"Failed to send OTP email: {str(e)}")
        return False


def send_and_store_otp(email, purpose='verification'):
    """Generate, store and send OTP via Gmail"""
    otp = generate_otp()
    store_otp(email, otp, purpose)
    success = send_otp_email(email, otp, purpose)
    return success
