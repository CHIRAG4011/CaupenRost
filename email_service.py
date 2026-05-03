import os
import random
import string
import logging
import resend
from datetime import datetime, timedelta

FROM_ADDRESS = "CaupenRost <help@caupenrost.com>"


def generate_otp(length=6):
    return ''.join(random.choices(string.digits, k=length))


def _is_mongo():
    return bool(os.environ.get('MONGO_URI')) or (
        os.environ.get('DATABASE_URL') and 'mongodb' in os.environ.get('DATABASE_URL', '')
    )


def get_otp_repo():
    if _is_mongo():
        from mongo_db import MongoOTPRepo
        return MongoOTPRepo
    else:
        from db import OTPRepo
        return OTPRepo


def store_otp(email, otp, purpose='verification', expiry_minutes=10):
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


def _get_api_key():
    return os.environ.get('RESEND_API_KEY', '').strip()


def _send(subject, html, to_email):
    api_key = _get_api_key()
    if not api_key:
        logging.warning(f"RESEND_API_KEY not set — skipping email to {to_email}: {subject}")
        return False
    try:
        resend.api_key = api_key
        resp = resend.Emails.send({
            "from": FROM_ADDRESS,
            "to": [to_email],
            "subject": subject,
            "html": html,
        })
        logging.info(f"Email sent to {to_email} | subject: {subject} | id: {resp}")
        return True
    except Exception as e:
        logging.error(f"Failed to send email to {to_email}: {e}")
        return False


def _header(icon="🍞"):
    return f"""
    <tr>
      <td style="background:linear-gradient(135deg,#1a1208 0%,#2a1f0e 100%);padding:36px 40px;text-align:center;border-bottom:2px solid #d4a843;">
        <div style="font-size:36px;margin-bottom:8px;">{icon}</div>
        <h1 style="margin:0;font-family:Georgia,serif;font-size:28px;color:#d4a843;letter-spacing:3px;text-transform:uppercase;">CaupenRost</h1>
        <p style="margin:6px 0 0;color:#8b7355;font-size:12px;letter-spacing:2px;text-transform:uppercase;">Artisan Bakery</p>
      </td>
    </tr>"""


def _footer():
    return """
    <tr>
      <td style="background:#0d0b09;padding:24px 40px;text-align:center;border-top:1px solid #2a2010;">
        <p style="margin:0 0 8px;color:#6b5a3e;font-size:12px;">Questions? Contact us at <a href="mailto:help@caupenrost.com" style="color:#d4a843;text-decoration:none;">help@caupenrost.com</a></p>
        <p style="margin:0;color:#4a3a28;font-size:11px;">&copy; 2026 CaupenRost. All rights reserved.</p>
      </td>
    </tr>"""


def _wrap(rows):
    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#080605;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#080605;padding:30px 0;">
  <tr><td align="center">
    <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;border-radius:12px;overflow:hidden;border:1px solid #2a2010;">
      {rows}
    </table>
  </td></tr>
</table>
</body></html>"""


def _otp_html(otp, title, intro, footer_note, accent='#d4a843', icon='🔑'):
    body = f"""
    <tr>
      <td style="background:#0d0b09;padding:40px;">
        <h2 style="margin:0 0 12px;font-family:Georgia,serif;color:#e8d5a3;font-size:22px;">{title}</h2>
        <p style="margin:0 0 28px;color:#8b7355;font-size:15px;line-height:1.6;">{intro}</p>
        <div style="background:#1a1208;border:1px solid {accent};border-radius:10px;padding:28px;text-align:center;margin:0 0 28px;">
          <p style="margin:0 0 8px;color:#6b5a3e;font-size:11px;letter-spacing:2px;text-transform:uppercase;">Your Verification Code</p>
          <div style="font-size:40px;font-weight:bold;letter-spacing:14px;color:{accent};font-family:monospace;">{otp}</div>
          <p style="margin:10px 0 0;color:#6b5a3e;font-size:12px;">Valid for 10 minutes &bull; Do not share</p>
        </div>
        <p style="margin:0;color:#6b5a3e;font-size:13px;line-height:1.6;">{footer_note}</p>
      </td>
    </tr>"""
    return _wrap(_header(icon) + body + _footer())


def send_otp_email(to_email, otp, purpose='verification'):
    subjects = {
        'registration': "Verify Your Email — CaupenRost",
        'login': "Your Login Code — CaupenRost",
        'order': "Confirm Your Order — CaupenRost",
    }
    subject = subjects.get(purpose, "Your Verification Code — CaupenRost")

    if purpose == 'registration':
        title = "Verify Your Email"
        intro = "Welcome to CaupenRost! Please use the code below to complete your registration."
        note = "If you didn't create an account with us, you can safely ignore this email."
        accent = '#d4a843'
        icon = '✉️'
    elif purpose == 'login':
        title = "Login Verification"
        intro = "Use the code below to complete your login to CaupenRost."
        note = "If you didn't try to log in, please secure your account immediately."
        accent = '#c49a2e'
        icon = '🔐'
    elif purpose == 'order':
        title = "Confirm Your Order"
        intro = "You're almost there! Enter the code below to confirm and place your order."
        note = "If you didn't initiate this order, please contact us at help@caupenrost.com."
        accent = '#28a745'
        icon = '🛒'
    else:
        title = "Your Verification Code"
        intro = "Use the code below to verify your action."
        note = "This code is valid for 10 minutes."
        accent = '#d4a843'
        icon = '🔑'

    if not _get_api_key():
        logging.warning("RESEND_API_KEY not configured — OTP displayed in logs only")
        logging.info(f"=== DEV MODE === OTP for {to_email} ({purpose}): {otp}")
        return True

    html = _otp_html(otp, title, intro, note, accent, icon)
    return _send(subject, html, to_email)


def send_and_store_otp(email, purpose='verification'):
    otp = generate_otp()
    store_otp(email, otp, purpose)
    return send_otp_email(email, otp, purpose)


def send_welcome_email(to_email, username):
    subject = "Welcome to CaupenRost — Your Artisan Bakery!"
    body = f"""
    <tr>
      <td style="background:#0d0b09;padding:40px;">
        <h2 style="margin:0 0 12px;font-family:Georgia,serif;color:#d4a843;font-size:24px;">Welcome, {username}!</h2>
        <p style="margin:0 0 20px;color:#8b7355;font-size:15px;line-height:1.6;">
          Your account has been successfully created. We're thrilled to have you as part of the CaupenRost family.
        </p>
        <div style="background:#1a1208;border-left:3px solid #d4a843;padding:20px 24px;border-radius:0 8px 8px 0;margin:0 0 28px;">
          <p style="margin:0 0 8px;color:#e8d5a3;font-size:14px;font-weight:bold;">What you can do now:</p>
          <ul style="margin:0;padding-left:18px;color:#8b7355;font-size:14px;line-height:1.8;">
            <li>Browse our artisan collection</li>
            <li>Add items to your cart &amp; place orders</li>
            <li>Track your orders in real time</li>
            <li>Reach out via our support centre</li>
          </ul>
        </div>
        <p style="margin:0;color:#6b5a3e;font-size:13px;">Need help? Write to us at <a href="mailto:help@caupenrost.com" style="color:#d4a843;text-decoration:none;">help@caupenrost.com</a></p>
      </td>
    </tr>"""
    html = _wrap(_header('🎉') + body + _footer())
    return _send(subject, html, to_email)


def send_welcome_back_email(to_email, username):
    subject = "Welcome Back to CaupenRost!"
    body = f"""
    <tr>
      <td style="background:#0d0b09;padding:40px;">
        <h2 style="margin:0 0 12px;font-family:Georgia,serif;color:#d4a843;font-size:24px;">Welcome back, {username}!</h2>
        <p style="margin:0 0 20px;color:#8b7355;font-size:15px;line-height:1.6;">
          You have successfully logged in to CaupenRost. Enjoy browsing our fresh artisan bakes.
        </p>
        <p style="margin:0;color:#6b5a3e;font-size:13px;">
          Didn't log in? Contact us immediately at <a href="mailto:help@caupenrost.com" style="color:#d4a843;text-decoration:none;">help@caupenrost.com</a>
        </p>
      </td>
    </tr>"""
    html = _wrap(_header('👋') + body + _footer())
    return _send(subject, html, to_email)


def send_order_confirmation_email(to_email, order):
    order_id = str(order.id)
    subject = f"Order Confirmed — #{order_id} | CaupenRost"

    items_rows = ""
    try:
        for item in (order.items or []):
            name = item.get('name', item.get('product_id', 'Item'))
            qty = item.get('quantity', 1)
            price = item.get('price', 0)
            items_rows += f"""
            <tr>
              <td style="padding:10px 0;color:#8b7355;font-size:14px;border-bottom:1px solid #1a1208;">{name}</td>
              <td style="padding:10px 0;color:#8b7355;font-size:14px;border-bottom:1px solid #1a1208;text-align:center;">{qty}</td>
              <td style="padding:10px 0;color:#e8d5a3;font-size:14px;border-bottom:1px solid #1a1208;text-align:right;">&#8377;{price * qty:.2f}</td>
            </tr>"""
    except Exception:
        pass

    payment_label = {
        'cash_on_delivery': 'Cash on Delivery',
        'qr_payment': 'UPI / QR Payment',
    }.get(getattr(order, 'payment_method', ''), getattr(order, 'payment_method', 'N/A'))

    body = f"""
    <tr>
      <td style="background:#0d0b09;padding:40px;">
        <div style="background:#1a1208;border:1px solid #2a2010;border-radius:8px;padding:16px 20px;margin:0 0 28px;text-align:center;">
          <p style="margin:0 0 4px;color:#6b5a3e;font-size:11px;letter-spacing:2px;text-transform:uppercase;">Order ID</p>
          <p style="margin:0;color:#d4a843;font-size:22px;font-weight:bold;font-family:monospace;">#{order_id}</p>
        </div>
        <h2 style="margin:0 0 12px;font-family:Georgia,serif;color:#e8d5a3;font-size:22px;">Your order is confirmed!</h2>
        <p style="margin:0 0 24px;color:#8b7355;font-size:15px;line-height:1.6;">
          Thank you for choosing CaupenRost. We're preparing your artisan bakes with care.
        </p>
        {'<table width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 20px;"><tr><th style="text-align:left;color:#6b5a3e;font-size:11px;letter-spacing:1px;text-transform:uppercase;padding-bottom:8px;">Item</th><th style="text-align:center;color:#6b5a3e;font-size:11px;letter-spacing:1px;text-transform:uppercase;padding-bottom:8px;">Qty</th><th style="text-align:right;color:#6b5a3e;font-size:11px;letter-spacing:1px;text-transform:uppercase;padding-bottom:8px;">Amount</th></tr>' + items_rows + '</table>' if items_rows else ''}
        <table width="100%" cellpadding="0" cellspacing="0" style="background:#1a1208;border-radius:8px;padding:0;margin:0 0 24px;">
          <tr>
            <td style="padding:12px 16px;color:#6b5a3e;font-size:13px;border-bottom:1px solid #2a2010;">Payment Method</td>
            <td style="padding:12px 16px;color:#e8d5a3;font-size:13px;border-bottom:1px solid #2a2010;text-align:right;">{payment_label}</td>
          </tr>
          <tr>
            <td style="padding:12px 16px;color:#6b5a3e;font-size:13px;border-bottom:1px solid #2a2010;">Delivery Address</td>
            <td style="padding:12px 16px;color:#e8d5a3;font-size:13px;border-bottom:1px solid #2a2010;text-align:right;">{getattr(order, 'shipping_address', 'N/A')}</td>
          </tr>
          <tr>
            <td style="padding:14px 16px;color:#d4a843;font-size:14px;font-weight:bold;">Order Total</td>
            <td style="padding:14px 16px;color:#d4a843;font-size:18px;font-weight:bold;text-align:right;">&#8377;{getattr(order, 'total', 0):.2f}</td>
          </tr>
        </table>
        <p style="margin:0;color:#6b5a3e;font-size:13px;line-height:1.6;">
          Track your order status in your <a href="#" style="color:#d4a843;text-decoration:none;">account dashboard</a>.<br>
          Questions? <a href="mailto:help@caupenrost.com" style="color:#d4a843;text-decoration:none;">help@caupenrost.com</a>
        </p>
      </td>
    </tr>"""
    html = _wrap(_header('✅') + body + _footer())
    return _send(subject, html, to_email)


def send_order_status_email(to_email, username, order):
    order_id = str(order.id)
    status = getattr(order, 'status', 'updated')

    status_info = {
        'pending':                  ('⏳', '#f59e0b', 'Order Received',            'We have received your order and it\'s in the queue.'),
        'confirmed':                ('✅', '#10b981', 'Order Confirmed',            'Your order has been confirmed and is being prepared.'),
        'processing':               ('👨‍🍳', '#6366f1', 'Being Prepared',           'Our bakers are crafting your order with love.'),
        'out_for_delivery':         ('🚚', '#3b82f6', 'Out for Delivery',          'Your order is on its way to you!'),
        'delivered':                ('🎉', '#d4a843', 'Order Delivered',           'Your order has been delivered. Enjoy your bakes!'),
        'cancelled':                ('❌', '#ef4444', 'Order Cancelled',           'Your order has been cancelled. Contact us if this was unexpected.'),
        'payment_pending':          ('💳', '#f59e0b', 'Awaiting Payment',          'Please complete your payment to proceed.'),
        'payment_proof_submitted':  ('📎', '#8b5cf6', 'Payment Proof Received',   'We\'ve received your payment proof and are verifying it.'),
        'refunded':                 ('💰', '#10b981', 'Order Refunded',            'Your refund has been processed. Please allow a few business days.'),
    }

    icon, accent, label, desc = status_info.get(status, ('📦', '#d4a843', status.replace('_', ' ').title(), 'Your order status has been updated.'))

    subject = f"Order Update: {label} — #{order_id} | CaupenRost"

    body = f"""
    <tr>
      <td style="background:#0d0b09;padding:40px;">
        <div style="background:#1a1208;border:1px solid #2a2010;border-radius:8px;padding:16px 20px;margin:0 0 28px;text-align:center;">
          <p style="margin:0 0 4px;color:#6b5a3e;font-size:11px;letter-spacing:2px;text-transform:uppercase;">Order ID</p>
          <p style="margin:0;color:#d4a843;font-size:22px;font-weight:bold;font-family:monospace;">#{order_id}</p>
        </div>
        <div style="text-align:center;margin:0 0 24px;">
          <div style="display:inline-block;background:{accent}20;border:1px solid {accent};border-radius:20px;padding:8px 20px;">
            <span style="color:{accent};font-size:14px;font-weight:bold;">{icon} {label}</span>
          </div>
        </div>
        <h2 style="margin:0 0 12px;font-family:Georgia,serif;color:#e8d5a3;font-size:20px;">Hi {username}, your order has been updated.</h2>
        <p style="margin:0 0 24px;color:#8b7355;font-size:15px;line-height:1.6;">{desc}</p>
        <table width="100%" cellpadding="0" cellspacing="0" style="background:#1a1208;border-radius:8px;margin:0 0 24px;">
          <tr>
            <td style="padding:12px 16px;color:#6b5a3e;font-size:13px;border-bottom:1px solid #2a2010;">Order Total</td>
            <td style="padding:12px 16px;color:#e8d5a3;font-size:13px;border-bottom:1px solid #2a2010;text-align:right;">&#8377;{getattr(order, 'total', 0):.2f}</td>
          </tr>
          <tr>
            <td style="padding:12px 16px;color:#6b5a3e;font-size:13px;">Delivery Address</td>
            <td style="padding:12px 16px;color:#e8d5a3;font-size:13px;text-align:right;">{getattr(order, 'shipping_address', 'N/A')}</td>
          </tr>
        </table>
        <p style="margin:0;color:#6b5a3e;font-size:13px;line-height:1.6;">
          View full details in your <a href="#" style="color:#d4a843;text-decoration:none;">order dashboard</a>.<br>
          Need help? <a href="mailto:help@caupenrost.com" style="color:#d4a843;text-decoration:none;">help@caupenrost.com</a>
        </p>
      </td>
    </tr>"""
    html = _wrap(_header(icon) + body + _footer())
    return _send(subject, html, to_email)


def log_startup_config():
    api_key = _get_api_key()
    if api_key:
        logging.info("Email startup: RESEND_API_KEY configured: True — Resend email sending is active")
    else:
        logging.warning("Email startup: RESEND_API_KEY configured: False — OTP codes will be logged only")
