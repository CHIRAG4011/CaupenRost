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


def store_otp(email, otp, purpose='verification', expiry_minutes=10):
    """Store OTP in database"""
    from app import db
    from models import OTPCode
    
    OTPCode.query.filter_by(email=email, purpose=purpose).delete()
    
    otp_code = OTPCode(
        email=email,
        purpose=purpose,
        otp=otp,
        attempts=0,
        expires_at=datetime.utcnow() + timedelta(minutes=expiry_minutes)
    )
    db.session.add(otp_code)
    db.session.commit()


def verify_otp(email, otp, purpose='verification'):
    """Verify OTP for given email and purpose"""
    from app import db
    from models import OTPCode
    
    stored = OTPCode.query.filter_by(email=email, purpose=purpose).first()
    
    if not stored:
        return False, "No verification code found. Please request a new one."
    
    if datetime.utcnow() > stored.expires_at:
        db.session.delete(stored)
        db.session.commit()
        return False, "Verification code has expired. Please request a new one."
    
    stored.attempts += 1
    
    if stored.attempts > 5:
        db.session.delete(stored)
        db.session.commit()
        return False, "Too many attempts. Please request a new verification code."
    
    if stored.otp != otp:
        db.session.commit()
        return False, f"Invalid code. {5 - stored.attempts} attempts remaining."
    
    db.session.delete(stored)
    db.session.commit()
    return True, "Verification successful."


def send_otp_email(to_email, otp, purpose='verification'):
    """Send OTP email using Gmail SMTP"""
    try:
        gmail_user = os.environ.get('GMAIL_EMAIL')
        gmail_password = os.environ.get('GMAIL_APP_PASSWORD')
        
        logging.debug(f"Gmail user configured: {bool(gmail_user)}, Password configured: {bool(gmail_password)}")
        
        if not gmail_user or not gmail_password:
            logging.error(f"Gmail credentials not configured - GMAIL_EMAIL: {bool(gmail_user)}, GMAIL_APP_PASSWORD: {bool(gmail_password)}")
            return False
        
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
        msg['From'] = gmail_user
        msg['To'] = to_email
        
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        # Try TLS connection first (port 587), then fall back to SSL (port 465)
        try:
            logging.debug("Attempting Gmail SMTP with TLS on port 587")
            with smtplib.SMTP('smtp.gmail.com', 587, timeout=30) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(gmail_user, gmail_password)
                server.sendmail(gmail_user, to_email, msg.as_string())
            logging.info(f"OTP email sent to {to_email} for {purpose} via TLS")
            return True
        except Exception as tls_error:
            logging.warning(f"TLS connection failed: {str(tls_error)}, trying SSL")
            try:
                with smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=30) as server:
                    server.login(gmail_user, gmail_password)
                    server.sendmail(gmail_user, to_email, msg.as_string())
                logging.info(f"OTP email sent to {to_email} for {purpose} via SSL")
                return True
            except Exception as ssl_error:
                logging.error(f"SSL connection also failed: {str(ssl_error)}")
                raise ssl_error
        
    except Exception as e:
        logging.error(f"Failed to send OTP email: {str(e)}")
        return False


def send_and_store_otp(email, purpose='verification'):
    """Generate, store and send OTP via Gmail"""
    otp = generate_otp()
    store_otp(email, otp, purpose)
    success = send_otp_email(email, otp, purpose)
    return success
