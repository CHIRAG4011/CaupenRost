import random
import string
import logging
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
    """Get the stored OTP for display (local OTP system)"""
    init_otp_store()
    key = f"{email}_{purpose}"
    if key in data_store['otp_codes']:
        return data_store['otp_codes'][key]['otp']
    return None


def send_and_store_otp(email, purpose='verification'):
    """Generate and store OTP locally (no email sending)"""
    otp = generate_otp()
    store_otp(email, otp, purpose)
    logging.info(f"OTP generated for {email} ({purpose}): {otp}")
    return True, otp
