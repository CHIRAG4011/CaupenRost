import os
import random
import string
import logging
import resend
from datetime import datetime, timedelta


def generate_otp(length=6):
    """Generate a random numeric OTP"""
    return ''.join(random.choices(string.digits, k=length))


def _is_mongo():
    """Check if MongoDB backend is active"""
    return bool(os.environ.get('MONGO_URI')) or (
        os.environ.get('DATABASE_URL') and 'mongodb' in os.environ.get('DATABASE_URL', '')
    )


def get_otp_repo():
    """Get the appropriate OTP repository based on database backend"""
    if _is_mongo():
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


def _build_html(otp, purpose):
    """Build HTML email body for the given purpose"""
    accent = '#28a745' if purpose == 'order' else '#667eea'

    if purpose == 'registration':
        title = "Verify Your Email Address"
        intro = "Welcome! Please use the following OTP to complete your registration:"
        footer = "If you didn't request this, please ignore this email."
    elif purpose == 'login':
        title = "Login Verification"
        intro = "Use the following OTP to complete your login:"
        footer = "If you didn't try to login, please secure your account immediately."
    elif purpose == 'order':
        title = "Confirm Your Order"
        intro = "Please enter the following OTP to confirm your order:"
        footer = "If you didn't place this order, please ignore this email."
    else:
        title = "Your Verification Code"
        intro = "Use the following OTP to verify your action:"
        footer = "This OTP is valid for 10 minutes."

    return f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
            <h1 style="color: white; margin: 0;">CaupenRost</h1>
        </div>
        <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
            <h2 style="color: #333;">{title}</h2>
            <p style="color: #666; font-size: 16px;">{intro}</p>
            <div style="background: {accent}; color: white; font-size: 32px; font-weight: bold; padding: 20px; text-align: center; border-radius: 10px; letter-spacing: 8px; margin: 20px 0;">
                {otp}
            </div>
            <p style="color: #666; font-size: 14px;">This OTP is valid for 10 minutes. Do not share it with anyone.</p>
            <p style="color: #999; font-size: 12px;">{footer}</p>
        </div>
    </div>
    """


def _check_email_config():
    """Log email configuration status on first use"""
    api_key = os.environ.get('RESEND_API_KEY', '').strip()
    configured = bool(api_key)
    logging.info(f"Email config check — RESEND_API_KEY configured: {configured}")
    return api_key


def send_otp_email(to_email, otp, purpose='verification'):
    """Send OTP email using Resend"""
    api_key = _check_email_config()

    if not api_key:
        logging.warning("RESEND_API_KEY not configured — OTP displayed in logs only")
        logging.info(f"=== DEV MODE === OTP for {to_email} ({purpose}): {otp}")
        return True

    subjects = {
        'registration': "Verify Your Email - CaupenRost",
        'login': "Login Verification - CaupenRost",
        'order': "Confirm Your Order - CaupenRost",
    }
    subject = subjects.get(purpose, "Your OTP - CaupenRost")

    try:
        resend.api_key = api_key
        params = {
            "from": "CaupenRost <onboarding@resend.dev>",
            "to": [to_email],
            "subject": subject,
            "html": _build_html(otp, purpose),
        }
        response = resend.Emails.send(params)
        logging.info(f"OTP email sent via Resend to {to_email} for {purpose}: {response}")
        return True
    except Exception as e:
        logging.error(f"Failed to send OTP email via Resend: {e}")
        return False


def send_and_store_otp(email, purpose='verification'):
    """Generate, store and send OTP via Resend"""
    otp = generate_otp()
    store_otp(email, otp, purpose)
    success = send_otp_email(email, otp, purpose)
    return success
