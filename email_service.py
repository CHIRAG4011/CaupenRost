import os
import random
import string
import logging
import resend
from datetime import datetime, timedelta

FROM_ADDRESS = "CaupenRost <help@caupenrost.shop>"


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
    try:
        OTPRepo = get_otp_repo()
        OTPRepo.delete_by_email_purpose(email, purpose)
        OTPRepo.create({
            'email': email,
            'purpose': purpose,
            'otp': otp,
            'attempts': 0,
            'expires_at': datetime.utcnow() + timedelta(minutes=expiry_minutes)
        })
    except Exception as e:
        logging.error(f"Failed to store OTP for {email}: {e}")
        raise


def verify_otp(email, otp, purpose='verification'):
    OTPRepo = get_otp_repo()
    stored = OTPRepo.find_by_email_purpose(email, purpose)

    if not stored:
        return False, "No verification code found. Please request a new one."

    now = datetime.utcnow()
    expires = stored.expires_at
    if expires is not None:
        if getattr(expires, 'tzinfo', None) is not None:
            from datetime import timezone
            now = datetime.now(timezone.utc)
        if now > expires:
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


# ── Shared layout primitives ─────────────────────────────────────────────────

def _wrap(inner_html):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="x-apple-disable-message-reformatting">
  <title>CaupenRost</title>
</head>
<body style="margin:0;padding:0;background-color:#06040302;font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;">
  <!--[if mso]><table width="100%"><tr><td><![endif]-->
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
         style="background:linear-gradient(180deg,#0a0703 0%,#06040302 100%);min-height:100vh;padding:40px 16px;">
    <tr>
      <td align="center" valign="top">
        <!-- Outer glow wrapper -->
        <table role="presentation" width="620" cellpadding="0" cellspacing="0"
               style="max-width:620px;width:100%;">
          {inner_html}
        </table>
      </td>
    </tr>
  </table>
  <!--[if mso]></td></tr></table><![endif]-->
</body>
</html>"""


def _header(title="CaupenRost", subtitle="Artisan Bakery", accent="#e07832"):
    return f"""
  <!-- ═══ HEADER ═══ -->
  <tr>
    <td style="border-radius:16px 16px 0 0;overflow:hidden;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0">

        <!-- Top accent stripe -->
        <tr>
          <td style="background:linear-gradient(90deg,{accent} 0%,#c9661f 50%,{accent} 100%);height:4px;font-size:0;line-height:0;">&nbsp;</td>
        </tr>

        <!-- Main header bg -->
        <tr>
          <td style="background:linear-gradient(160deg,#150e05 0%,#1f1408 40%,#0f0906 100%);padding:48px 48px 40px;text-align:center;">

            <!-- Decorative top line -->
            <table role="presentation" align="center" cellpadding="0" cellspacing="0" style="margin:0 auto 28px;">
              <tr>
                <td style="width:40px;height:1px;background:linear-gradient(90deg,transparent,{accent});font-size:0;">&nbsp;</td>
                <td style="padding:0 12px;color:{accent};font-size:18px;">✦</td>
                <td style="width:40px;height:1px;background:linear-gradient(90deg,{accent},transparent);font-size:0;">&nbsp;</td>
              </tr>
            </table>

            <!-- Bakery icon badge -->
            <div style="display:inline-block;background:linear-gradient(135deg,{accent}22 0%,{accent}11 100%);border:1px solid {accent}44;border-radius:50%;width:72px;height:72px;line-height:72px;font-size:34px;margin:0 auto 20px;">
              🥐
            </div>

            <!-- Brand name -->
            <h1 style="margin:0 0 6px;font-family:Georgia,'Times New Roman',serif;font-size:36px;font-weight:700;color:{accent};letter-spacing:6px;text-transform:uppercase;line-height:1.1;">
              CaupenRost
            </h1>

            <!-- Tagline -->
            <p style="margin:0 0 20px;color:#c8a87a;font-size:11px;letter-spacing:4px;text-transform:uppercase;">
              {subtitle}
            </p>

            <!-- Decorative divider -->
            <table role="presentation" align="center" cellpadding="0" cellspacing="0" style="margin:0 auto;">
              <tr>
                <td style="width:60px;height:1px;background:linear-gradient(90deg,transparent,{accent}66);font-size:0;">&nbsp;</td>
                <td style="padding:0 10px;color:{accent}88;font-size:12px;">❧</td>
                <td style="width:60px;height:1px;background:linear-gradient(90deg,{accent}66,transparent);font-size:0;">&nbsp;</td>
              </tr>
            </table>

          </td>
        </tr>
      </table>
    </td>
  </tr>"""


def _footer():
    return """
  <!-- ═══ FOOTER ═══ -->
  <tr>
    <td style="border-radius:0 0 16px 16px;overflow:hidden;">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0">

        <!-- Divider -->
        <tr>
          <td style="background:linear-gradient(90deg,transparent,#e0783244,transparent);height:1px;font-size:0;">&nbsp;</td>
        </tr>

        <!-- Footer body -->
        <tr>
          <td style="background:linear-gradient(180deg,#0f0906 0%,#080604 100%);padding:32px 48px 28px;text-align:center;">

            <!-- Social / links row -->
            <table role="presentation" align="center" cellpadding="0" cellspacing="0" style="margin:0 auto 20px;">
              <tr>
                <td style="padding:0 8px;">
                  <a href="mailto:help@caupenrost.shop"
                     style="display:inline-block;background:#1a1208;border:1px solid #3a2810;border-radius:6px;padding:8px 16px;
                            color:#e07832;font-size:12px;text-decoration:none;letter-spacing:0.5px;">
                    ✉&nbsp; Email Us
                  </a>
                </td>
                <td style="padding:0 8px;">
                  <a href="#"
                     style="display:inline-block;background:#1a1208;border:1px solid #3a2810;border-radius:6px;padding:8px 16px;
                            color:#e07832;font-size:12px;text-decoration:none;letter-spacing:0.5px;">
                    🛍&nbsp; Shop Now
                  </a>
                </td>
                <td style="padding:0 8px;">
                  <a href="#"
                     style="display:inline-block;background:#1a1208;border:1px solid #3a2810;border-radius:6px;padding:8px 16px;
                            color:#e07832;font-size:12px;text-decoration:none;letter-spacing:0.5px;">
                    💬&nbsp; Support
                  </a>
                </td>
              </tr>
            </table>

            <!-- Info text -->
            <p style="margin:0 0 8px;color:#7a5c38;font-size:12px;line-height:1.7;">
              Questions? We're always here —
              <a href="mailto:help@caupenrost.shop" style="color:#e07832;text-decoration:none;">help@caupenrost.shop</a>
            </p>
            <p style="margin:0 0 16px;color:#7a5c38;font-size:11px;">
              +91 7016377439 &nbsp;·&nbsp; hello@caupenrost.com
            </p>

            <!-- Bottom stripe -->
            <table role="presentation" align="center" cellpadding="0" cellspacing="0" style="margin:0 auto 16px;width:80%;">
              <tr>
                <td style="height:1px;background:linear-gradient(90deg,transparent,#3a281066,transparent);font-size:0;">&nbsp;</td>
              </tr>
            </table>

            <p style="margin:0;color:#4a3820;font-size:11px;letter-spacing:0.5px;">
              &copy; 2026 CaupenRost &nbsp;·&nbsp; Made with love in India &nbsp;·&nbsp; All rights reserved.
            </p>

          </td>
        </tr>

        <!-- Bottom accent stripe -->
        <tr>
          <td style="background:linear-gradient(90deg,#e07832 0%,#c9661f 50%,#e07832 100%);height:3px;font-size:0;">&nbsp;</td>
        </tr>

      </table>
    </td>
  </tr>"""


def _card_open(bg="#0f0906"):
    return f'<tr><td style="background:{bg};padding:0;">'


def _card_close():
    return '</td></tr>'


# ── OTP / Verification emails ────────────────────────────────────────────────

def _build_otp_email(otp, purpose_config):
    title      = purpose_config['title']
    greeting   = purpose_config['greeting']
    body_text  = purpose_config['body']
    note       = purpose_config['note']
    accent     = purpose_config['accent']
    cta_label  = purpose_config['cta_label']
    urgency    = purpose_config.get('urgency', 'This code is valid for 10 minutes only.')

    digits = list(otp)
    digit_cells = "".join(
        f'<td style="width:48px;height:60px;background:#1a1208;border:2px solid {accent};'
        f'border-radius:10px;text-align:center;vertical-align:middle;'
        f'font-size:30px;font-weight:900;color:{accent};font-family:monospace;'
        f'letter-spacing:0;padding:0;margin:0 4px;box-shadow:0 0 12px {accent}33;">'
        f'{d}</td><td style="width:6px;">&nbsp;</td>'
        for d in digits
    )

    body = f"""
  <!-- ═══ BODY ═══ -->
  <tr>
    <td style="background:linear-gradient(180deg,#0f0906 0%,#0a0603 100%);padding:0 48px 48px;">

      <!-- Greeting -->
      <h2 style="margin:40px 0 8px;font-family:Georgia,serif;font-size:26px;color:#f0e0c8;font-weight:700;line-height:1.2;">
        {title}
      </h2>
      <p style="margin:0 0 8px;font-size:15px;color:#c8a87a;font-weight:500;">{greeting}</p>

      <!-- Divider -->
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:20px 0;">
        <tr>
          <td style="height:1px;background:linear-gradient(90deg,{accent}88,transparent);font-size:0;">&nbsp;</td>
        </tr>
      </table>

      <!-- Body text -->
      <p style="margin:0 0 32px;font-size:16px;color:#a08060;line-height:1.8;">
        {body_text}
      </p>

      <!-- CTA label -->
      <p style="margin:0 0 14px;font-size:11px;color:#7a5c38;letter-spacing:3px;text-transform:uppercase;text-align:center;">
        — &nbsp; {cta_label} &nbsp; —
      </p>

      <!-- OTP Code Block -->
      <table role="presentation" align="center" cellpadding="0" cellspacing="0"
             style="margin:0 auto 12px;background:linear-gradient(135deg,#1f1408,#160e06);
                    border:1px solid {accent}55;border-radius:16px;padding:28px 32px;">
        <tr>
          <td align="center" style="padding:0;">
            <table role="presentation" cellpadding="0" cellspacing="0" style="margin:0 auto;">
              <tr>
                {digit_cells}
              </tr>
            </table>
          </td>
        </tr>
      </table>

      <!-- Urgency note -->
      <p style="margin:0 0 32px;text-align:center;font-size:12px;color:#6b5040;letter-spacing:0.5px;">
        ⏱ &nbsp; {urgency}
      </p>

      <!-- Security banner -->
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
             style="background:#1a0e06;border-left:3px solid {accent};border-radius:0 10px 10px 0;margin:0 0 32px;">
        <tr>
          <td style="padding:16px 20px;">
            <p style="margin:0 0 4px;font-size:13px;font-weight:700;color:#e07832;">🔒&nbsp; Security Notice</p>
            <p style="margin:0;font-size:13px;color:#7a5c38;line-height:1.7;">{note}</p>
          </td>
        </tr>
      </table>

      <!-- Closing note -->
      <p style="margin:0;font-size:13px;color:#5a4030;line-height:1.7;text-align:center;">
        With warm regards &nbsp;·&nbsp;
        <span style="color:#e07832;">The CaupenRost Team</span>
      </p>

    </td>
  </tr>"""
    return _wrap(_header(subtitle="Your Verification Code", accent=accent) + body + _footer())


def send_otp_email(to_email, otp, purpose='verification'):
    configs = {
        'registration': {
            'subject':   "🎉 Verify Your Email — CaupenRost Awaits You!",
            'title':     "Almost there — verify your email!",
            'greeting':  "You're one step away from joining the CaupenRost family.",
            'body':      "Thank you for signing up at CaupenRost! To complete your registration and unlock your full account, please use the secure verification code below. Enter it on the verification page and you'll be exploring our freshly baked artisan collection in moments.",
            'note':      "If you did not create a CaupenRost account, please disregard this email — no action is required on your part.",
            'accent':    "#e07832",
            'cta_label': "Your One-Time Registration Code",
            'urgency':   "Valid for 10 minutes · Do not share this code with anyone.",
        },
        'login': {
            'subject':   "🔐 Your Login Code — CaupenRost",
            'title':     "Secure login verification",
            'greeting':  "Welcome back! Let's make sure it's really you.",
            'body':      "A login attempt was made to your CaupenRost account. Use the secure one-time code below to complete your sign-in. Once entered, you'll be back to browsing our artisan bakes in no time.",
            'note':      "If you did not attempt to log in, please ignore this email and consider securing your account by contacting us immediately at help@caupenrost.shop.",
            'accent':    "#c9661f",
            'cta_label': "Your One-Time Login Code",
            'urgency':   "Expires in 10 minutes · Never share your code.",
        },
        'order': {
            'subject':   "🛒 Confirm Your Order — CaupenRost",
            'title':     "Confirm your order",
            'greeting':  "Your delicious selection is almost on its way!",
            'body':      "You've added some wonderful items to your basket at CaupenRost! To finalise and place your order, please enter the one-time confirmation code below. Your freshly baked goods will be on their way as soon as you do!",
            'note':      "If you did not initiate this order, please contact us immediately at help@caupenrost.shop so we can help.",
            'accent':    "#22c55e",
            'cta_label': "Your Order Confirmation Code",
            'urgency':   "Valid for 10 minutes · Your cart is saved.",
        },
    }

    cfg = configs.get(purpose, {
        'subject':   "🔑 Your Verification Code — CaupenRost",
        'title':     "Verification required",
        'greeting':  "Please verify your identity to continue.",
        'body':      "Use the secure one-time code below to complete the requested action on your CaupenRost account.",
        'note':      "If you did not request this code, please ignore this email.",
        'accent':    "#e07832",
        'cta_label': "Your Verification Code",
        'urgency':   "Valid for 10 minutes · Do not share this code.",
    })

    if not _get_api_key():
        logging.warning("RESEND_API_KEY not configured — OTP displayed in logs only")
        logging.info(f"=== DEV MODE === OTP for {to_email} ({purpose}): {otp}")
        return True

    html = _build_otp_email(otp, cfg)
    return _send(cfg['subject'], html, to_email)


def send_and_store_otp(email, purpose='verification'):
    try:
        otp = generate_otp()
        store_otp(email, otp, purpose)
        return send_otp_email(email, otp, purpose)
    except Exception as e:
        logging.error(f"send_and_store_otp failed for {email} ({purpose}): {e}")
        return False


# ── Welcome email ────────────────────────────────────────────────────────────

def send_welcome_email(to_email, username):
    subject = "🎉 Welcome to CaupenRost — Your Artisan Bakery Journey Begins!"

    perks = [
        ("🥖", "Artisan Collection",   "Browse hundreds of handcrafted breads, cakes, pastries and seasonal specials — all baked fresh every day."),
        ("🚀", "Express Delivery",     "Order before noon and get your bakes delivered the same day. Free delivery on orders above ₹500."),
        ("📦", "Real-Time Tracking",   "Know exactly where your order is at every step — from oven to doorstep."),
        ("💬", "Dedicated Support",    "Our support team is on standby. Reach us any time at help@caupenrost.shop — we respond fast."),
    ]

    perk_rows = ""
    for icon, perk_title, perk_desc in perks:
        perk_rows += f"""
        <tr>
          <td valign="top" style="padding:16px 20px;border-bottom:1px solid #1f1408;">
            <table role="presentation" cellpadding="0" cellspacing="0" width="100%">
              <tr>
                <td valign="top" style="width:44px;padding-right:14px;">
                  <div style="background:linear-gradient(135deg,#e0783222,#e0783211);border:1px solid #e0783244;
                              border-radius:10px;width:40px;height:40px;text-align:center;line-height:40px;font-size:20px;">
                    {icon}
                  </div>
                </td>
                <td valign="top">
                  <p style="margin:0 0 3px;font-size:14px;font-weight:700;color:#f0dcc0;">{perk_title}</p>
                  <p style="margin:0;font-size:13px;color:#7a5c38;line-height:1.6;">{perk_desc}</p>
                </td>
              </tr>
            </table>
          </td>
        </tr>"""

    body = f"""
  <tr>
    <td style="background:linear-gradient(180deg,#0f0906 0%,#0a0603 100%);padding:0 48px 48px;">

      <!-- Hero greeting -->
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
             style="background:linear-gradient(135deg,#1f1408,#160e06);border:1px solid #e0783244;
                    border-radius:16px;margin:36px 0 32px;overflow:hidden;">
        <tr>
          <td style="padding:36px 32px;text-align:center;">
            <div style="font-size:52px;margin:0 0 12px;">🎊</div>
            <h2 style="margin:0 0 10px;font-family:Georgia,serif;font-size:30px;color:#e07832;font-weight:700;line-height:1.2;">
              Welcome, {username}!
            </h2>
            <p style="margin:0;font-size:16px;color:#c8a87a;line-height:1.7;">
              Your account is ready. You're now part of the<br>
              <strong style="color:#e07832;">CaupenRost</strong> family — and we couldn't be more delighted.
            </p>
          </td>
        </tr>
      </table>

      <!-- Body copy -->
      <p style="margin:0 0 28px;font-size:16px;color:#a08060;line-height:1.9;">
        Every loaf, every cake, every pastry at CaupenRost is crafted with premium local ingredients,
        time-honoured recipes, and a whole lot of love. We bake fresh every single day so that what
        arrives at your door is as good as if you'd picked it straight from our oven.
      </p>

      <!-- Perks table -->
      <p style="margin:0 0 14px;font-size:11px;color:#7a5c38;letter-spacing:3px;text-transform:uppercase;">
        — &nbsp; What's waiting for you &nbsp; —
      </p>
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
             style="background:#0f0906;border:1px solid #2a1a0a;border-radius:12px;overflow:hidden;margin:0 0 32px;">
        {perk_rows}
      </table>

      <!-- CTA button -->
      <table role="presentation" align="center" cellpadding="0" cellspacing="0" style="margin:0 auto 32px;">
        <tr>
          <td style="border-radius:50px;background:linear-gradient(135deg,#e07832,#c9661f);
                     box-shadow:0 4px 20px #e0783244;">
            <a href="#" style="display:inline-block;padding:16px 48px;font-size:15px;font-weight:700;
                                color:#fff;text-decoration:none;letter-spacing:1px;border-radius:50px;">
              🛍&nbsp; Start Shopping Now
            </a>
          </td>
        </tr>
      </table>

      <!-- Closing -->
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
             style="background:#1a0e06;border-left:3px solid #e07832;border-radius:0 10px 10px 0;">
        <tr>
          <td style="padding:18px 22px;">
            <p style="margin:0 0 4px;font-size:14px;font-weight:700;color:#f0dcc0;">A personal note from us 🍰</p>
            <p style="margin:0;font-size:13px;color:#7a5c38;line-height:1.7;">
              We started CaupenRost with a simple dream — to bring the joy of freshly baked goods
              to every home. We're so glad you've chosen to be a part of that journey.
              Bake on!
            </p>
          </td>
        </tr>
      </table>

    </td>
  </tr>"""

    html = _wrap(_header(subtitle="Welcome to the Family", accent="#e07832") + body + _footer())
    return _send(subject, html, to_email)


# ── Welcome-back email ───────────────────────────────────────────────────────

def send_welcome_back_email(to_email, username):
    subject = "👋 You're Back — Welcome to CaupenRost Again!"

    body = f"""
  <tr>
    <td style="background:linear-gradient(180deg,#0f0906 0%,#0a0603 100%);padding:0 48px 48px;">

      <!-- Hero -->
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
             style="background:linear-gradient(135deg,#1f1408,#160e06);border:1px solid #c9661f44;
                    border-radius:16px;margin:36px 0 28px;overflow:hidden;">
        <tr>
          <td style="padding:36px 32px;text-align:center;">
            <div style="font-size:48px;margin:0 0 12px;">👋</div>
            <h2 style="margin:0 0 10px;font-family:Georgia,serif;font-size:28px;color:#e07832;font-weight:700;">
              Welcome back, {username}!
            </h2>
            <p style="margin:0;font-size:15px;color:#c8a87a;line-height:1.7;">
              We've missed you. Your favourite artisan bakes are<br>
              still here — fresh out of the oven, just for you.
            </p>
          </td>
        </tr>
      </table>

      <!-- Body -->
      <p style="margin:0 0 28px;font-size:16px;color:#a08060;line-height:1.9;">
        You've just signed in successfully to CaupenRost. Whether you're back for
        your favourite sourdough, planning a celebration cake, or simply craving something
        special — we're ready to bake it for you. Explore what's new today!
      </p>

      <!-- Quick actions -->
      <p style="margin:0 0 14px;font-size:11px;color:#7a5c38;letter-spacing:3px;text-transform:uppercase;">
        — &nbsp; Pick up right where you left off &nbsp; —
      </p>
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 32px;">
        <tr>
          <td style="width:50%;padding-right:8px;">
            <a href="#" style="display:block;text-decoration:none;text-align:center;
                                background:#1a1208;border:1px solid #3a2810;border-radius:12px;padding:20px 12px;">
              <div style="font-size:28px;margin:0 0 8px;">🛍</div>
              <p style="margin:0 0 4px;font-size:13px;font-weight:700;color:#f0dcc0;">Browse Products</p>
              <p style="margin:0;font-size:12px;color:#7a5c38;">Fresh bakes await</p>
            </a>
          </td>
          <td style="width:50%;padding-left:8px;">
            <a href="#" style="display:block;text-decoration:none;text-align:center;
                                background:#1a1208;border:1px solid #3a2810;border-radius:12px;padding:20px 12px;">
              <div style="font-size:28px;margin:0 0 8px;">📦</div>
              <p style="margin:0 0 4px;font-size:13px;font-weight:700;color:#f0dcc0;">My Orders</p>
              <p style="margin:0;font-size:12px;color:#7a5c38;">Track your orders</p>
            </a>
          </td>
        </tr>
      </table>

      <!-- CTA -->
      <table role="presentation" align="center" cellpadding="0" cellspacing="0" style="margin:0 auto 32px;">
        <tr>
          <td style="border-radius:50px;background:linear-gradient(135deg,#e07832,#c9661f);
                     box-shadow:0 4px 20px #e0783244;">
            <a href="#" style="display:inline-block;padding:15px 44px;font-size:15px;font-weight:700;
                                color:#fff;text-decoration:none;letter-spacing:1px;border-radius:50px;">
              🥐&nbsp; Explore Today's Bakes
            </a>
          </td>
        </tr>
      </table>

      <!-- Security note -->
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
             style="background:#1a0e06;border-left:3px solid #c9661f;border-radius:0 10px 10px 0;">
        <tr>
          <td style="padding:16px 20px;">
            <p style="margin:0 0 3px;font-size:13px;font-weight:700;color:#e07832;">🔒&nbsp; Wasn't you?</p>
            <p style="margin:0;font-size:13px;color:#7a5c38;line-height:1.7;">
              If you did not sign in to CaupenRost, please contact us immediately at
              <a href="mailto:help@caupenrost.shop" style="color:#e07832;text-decoration:none;">help@caupenrost.shop</a>
              so we can secure your account right away.
            </p>
          </td>
        </tr>
      </table>

    </td>
  </tr>"""

    html = _wrap(_header(subtitle="Good to See You Again", accent="#c9661f") + body + _footer())
    return _send(subject, html, to_email)


# ── Order confirmation email ─────────────────────────────────────────────────

def send_order_confirmation_email(to_email, order):
    order_id = str(order.id)
    subject = f"✅ Order Confirmed — #{order_id} | CaupenRost"

    items_rows = ""
    order_subtotal = 0
    try:
        for item in (order.items or []):
            name     = item.get('name', item.get('product_id', 'Bakery Item'))
            qty      = item.get('quantity', 1)
            price    = item.get('price', 0)
            subtotal = price * qty
            order_subtotal += subtotal
            items_rows += f"""
            <tr>
              <td style="padding:14px 16px;border-bottom:1px solid #1f1408;">
                <p style="margin:0 0 2px;font-size:14px;color:#f0dcc0;font-weight:500;">{name}</p>
                <p style="margin:0;font-size:12px;color:#5a4030;">Qty: {qty} &nbsp;·&nbsp; ₹{price:.0f} each</p>
              </td>
              <td style="padding:14px 16px;border-bottom:1px solid #1f1408;text-align:right;
                          font-size:15px;font-weight:700;color:#e07832;vertical-align:middle;">
                ₹{subtotal:.2f}
              </td>
            </tr>"""
    except Exception:
        pass

    payment_label = {
        'cash_on_delivery': '💵 Cash on Delivery',
        'qr_payment':       '📱 UPI / QR Payment',
    }.get(getattr(order, 'payment_method', ''), getattr(order, 'payment_method', 'N/A'))

    total_display = getattr(order, 'total', order_subtotal)
    address = getattr(order, 'shipping_address', 'N/A')

    items_section = ""
    if items_rows:
        items_section = f"""
      <!-- Order items -->
      <p style="margin:0 0 12px;font-size:11px;color:#7a5c38;letter-spacing:3px;text-transform:uppercase;">
        — &nbsp; Your order &nbsp; —
      </p>
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
             style="background:#0f0906;border:1px solid #2a1a0a;border-radius:12px;overflow:hidden;margin:0 0 24px;">
        <tr>
          <td style="padding:12px 16px;background:#1a1208;border-bottom:1px solid #2a1a0a;">
            <span style="font-size:11px;font-weight:700;color:#7a5c38;letter-spacing:1px;text-transform:uppercase;">Item</span>
          </td>
          <td style="padding:12px 16px;background:#1a1208;border-bottom:1px solid #2a1a0a;text-align:right;">
            <span style="font-size:11px;font-weight:700;color:#7a5c38;letter-spacing:1px;text-transform:uppercase;">Total</span>
          </td>
        </tr>
        {items_rows}
        <tr>
          <td style="padding:16px;background:#1a1208;">
            <span style="font-size:15px;font-weight:700;color:#f0dcc0;">Order Total</span>
          </td>
          <td style="padding:16px;background:#1a1208;text-align:right;">
            <span style="font-size:20px;font-weight:900;color:#e07832;">₹{total_display:.2f}</span>
          </td>
        </tr>
      </table>"""

    body = f"""
  <tr>
    <td style="background:linear-gradient(180deg,#0f0906 0%,#0a0603 100%);padding:0 48px 48px;">

      <!-- Confirmation hero -->
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
             style="background:linear-gradient(135deg,#0d1f0e,#091508);border:1px solid #22c55e44;
                    border-radius:16px;margin:36px 0 28px;overflow:hidden;">
        <tr>
          <td style="padding:32px;text-align:center;">
            <div style="display:inline-block;background:#22c55e22;border:2px solid #22c55e66;
                        border-radius:50%;width:64px;height:64px;line-height:64px;font-size:30px;margin:0 0 16px;">
              ✅
            </div>
            <h2 style="margin:0 0 8px;font-family:Georgia,serif;font-size:26px;color:#4ade80;font-weight:700;">
              Order Confirmed!
            </h2>
            <p style="margin:0 0 16px;font-size:14px;color:#86efac;line-height:1.6;">
              Your delicious selection is confirmed and our bakers are already at work.
            </p>
            <!-- Order ID pill -->
            <div style="display:inline-block;background:#1a2e1a;border:1px solid #22c55e55;
                        border-radius:50px;padding:8px 24px;">
              <span style="font-size:11px;color:#6b9a6b;letter-spacing:2px;text-transform:uppercase;">Order ID</span>
              &nbsp;
              <span style="font-size:18px;font-weight:900;color:#4ade80;font-family:monospace;">#{order_id}</span>
            </div>
          </td>
        </tr>
      </table>

      <!-- Intro -->
      <p style="margin:0 0 28px;font-size:16px;color:#a08060;line-height:1.9;">
        Thank you for choosing CaupenRost! We've received your order and our artisan bakers are
        preparing everything with the care and quality you deserve. You'll receive another update
        as soon as your order is on its way.
      </p>

      {items_section}

      <!-- Order details -->
      <p style="margin:0 0 12px;font-size:11px;color:#7a5c38;letter-spacing:3px;text-transform:uppercase;">
        — &nbsp; Order details &nbsp; —
      </p>
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
             style="background:#0f0906;border:1px solid #2a1a0a;border-radius:12px;overflow:hidden;margin:0 0 32px;">
        <tr>
          <td style="padding:14px 16px;border-bottom:1px solid #1f1408;color:#7a5c38;font-size:13px;">
            💳&nbsp; Payment Method
          </td>
          <td style="padding:14px 16px;border-bottom:1px solid #1f1408;text-align:right;color:#f0dcc0;font-size:13px;font-weight:600;">
            {payment_label}
          </td>
        </tr>
        <tr>
          <td style="padding:14px 16px;border-bottom:1px solid #1f1408;color:#7a5c38;font-size:13px;vertical-align:top;">
            📍&nbsp; Delivery Address
          </td>
          <td style="padding:14px 16px;border-bottom:1px solid #1f1408;text-align:right;color:#f0dcc0;font-size:13px;">
            {address}
          </td>
        </tr>
        <tr>
          <td style="padding:14px 16px;color:#7a5c38;font-size:13px;">📅&nbsp; Estimated Delivery</td>
          <td style="padding:14px 16px;text-align:right;color:#f0dcc0;font-size:13px;font-weight:600;">Within 24–48 hours</td>
        </tr>
      </table>

      <!-- CTA -->
      <table role="presentation" align="center" cellpadding="0" cellspacing="0" style="margin:0 auto 32px;">
        <tr>
          <td style="border-radius:50px;background:linear-gradient(135deg,#22c55e,#16a34a);
                     box-shadow:0 4px 20px #22c55e33;">
            <a href="#" style="display:inline-block;padding:15px 44px;font-size:15px;font-weight:700;
                                color:#fff;text-decoration:none;letter-spacing:1px;border-radius:50px;">
              📦&nbsp; Track Your Order
            </a>
          </td>
        </tr>
      </table>

      <!-- Closing note -->
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
             style="background:#1a0e06;border-left:3px solid #22c55e;border-radius:0 10px 10px 0;">
        <tr>
          <td style="padding:18px 22px;">
            <p style="margin:0 0 4px;font-size:14px;font-weight:700;color:#4ade80;">
              🥐&nbsp; Baked with love, delivered with care
            </p>
            <p style="margin:0;font-size:13px;color:#7a5c38;line-height:1.7;">
              Every item is freshly prepared on the day of dispatch. Questions about your order?
              Reach us at <a href="mailto:help@caupenrost.shop" style="color:#22c55e;text-decoration:none;">help@caupenrost.shop</a>
              — we're happy to help.
            </p>
          </td>
        </tr>
      </table>

    </td>
  </tr>"""

    html = _wrap(_header(subtitle="Order Confirmed", accent="#22c55e") + body + _footer())
    return _send(subject, html, to_email)


# ── Order status update email ────────────────────────────────────────────────

def send_order_status_email(to_email, username, order):
    order_id = str(order.id)
    status   = getattr(order, 'status', 'updated')

    status_info = {
        'pending': {
            'icon': '⏳', 'accent': '#f59e0b', 'label': 'Order Received',
            'headline': 'We\'ve got your order!',
            'desc': 'Your order has landed in our system and is now in the queue. Our bakers will begin preparing it shortly. Sit tight — something delicious is on its way!',
            'tip': 'No action needed from you. We\'ll send you another update as soon as your order moves to the next stage.',
        },
        'confirmed': {
            'icon': '✅', 'accent': '#10b981', 'label': 'Order Confirmed',
            'headline': 'Your order is confirmed!',
            'desc': 'Great news — your order has been officially confirmed and has entered our production schedule. Our artisan bakers are gearing up to craft your selection with care.',
            'tip': 'We typically start preparation within the next 1–2 hours. You\'ll receive a notification when baking begins.',
        },
        'processing': {
            'icon': '👨‍🍳', 'accent': '#8b5cf6', 'label': 'Being Prepared',
            'headline': 'Our bakers are hard at work!',
            'desc': 'Your order is now actively being prepared in our kitchen. From hand-kneading the dough to carefully decorating each item, our team is pouring their craft into your order right now.',
            'tip': 'This is where the magic happens! Your bakes are being made fresh, just for you.',
        },
        'out_for_delivery': {
            'icon': '🚚', 'accent': '#3b82f6', 'label': 'Out for Delivery',
            'headline': 'Your order is on its way!',
            'desc': 'The wait is almost over — your freshly baked order has left our kitchen and is heading to your doorstep. Please ensure someone is available to receive it.',
            'tip': 'Keep your phone handy — our delivery partner may call ahead of arrival.',
        },
        'delivered': {
            'icon': '🎉', 'accent': '#e07832', 'label': 'Order Delivered',
            'headline': 'Delivered — enjoy every bite!',
            'desc': 'Your CaupenRost order has been delivered successfully. We hope your artisan bakes are everything you imagined — warm, fresh, and absolutely delicious. Bon appétit!',
            'tip': 'Loved it? We\'d be thrilled if you left a review. It means the world to our baking team!',
        },
        'cancelled': {
            'icon': '❌', 'accent': '#ef4444', 'label': 'Order Cancelled',
            'headline': 'Your order has been cancelled.',
            'desc': 'We\'re sorry to let you know that this order has been cancelled. If you didn\'t request this cancellation or have any questions, please reach out to us right away.',
            'tip': 'If you were charged for this order, a full refund will be processed within 3–5 business days.',
        },
        'payment_pending': {
            'icon': '💳', 'accent': '#f59e0b', 'label': 'Awaiting Payment',
            'headline': 'Payment required to proceed.',
            'desc': 'Your order is reserved, but we\'re waiting for your payment to confirm it. Please complete your payment at the earliest to avoid losing your spot in the queue.',
            'tip': 'Orders with pending payment are held for up to 2 hours before being automatically cancelled.',
        },
        'payment_proof_submitted': {
            'icon': '📎', 'accent': '#8b5cf6', 'label': 'Payment Proof Received',
            'headline': 'We\'ve received your payment proof!',
            'desc': 'Thank you for submitting your UPI / QR payment proof. Our team is currently verifying the transaction. This usually takes less than 30 minutes during business hours.',
            'tip': 'Once your payment is verified, your order will move into production automatically.',
        },
        'refunded': {
            'icon': '💰', 'accent': '#10b981', 'label': 'Order Refunded',
            'headline': 'Your refund has been processed.',
            'desc': 'We\'ve processed a refund for your cancelled order. The amount will reflect in your original payment method within 3–7 business days depending on your bank.',
            'tip': 'If you have any concerns about the refund timeline, please don\'t hesitate to contact our support team.',
        },
    }

    info = status_info.get(status, {
        'icon': '📦', 'accent': '#e07832', 'label': status.replace('_', ' ').title(),
        'headline': 'Your order status has been updated.',
        'desc': 'There\'s a new update on your CaupenRost order. Log in to your account dashboard for full details.',
        'tip': 'Contact us at help@caupenrost.shop if you have any questions.',
    })

    icon    = info['icon']
    accent  = info['accent']
    label   = info['label']
    headline = info['headline']
    desc    = info['desc']
    tip     = info['tip']

    subject = f"{icon} Order Update: {label} — #{order_id} | CaupenRost"

    total   = getattr(order, 'total', 0)
    address = getattr(order, 'shipping_address', 'N/A')

    body = f"""
  <tr>
    <td style="background:linear-gradient(180deg,#0f0906 0%,#0a0603 100%);padding:0 48px 48px;">

      <!-- Status hero -->
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
             style="background:linear-gradient(135deg,#150e05,#0f0904);border:1px solid {accent}44;
                    border-radius:16px;margin:36px 0 28px;overflow:hidden;">
        <tr>
          <!-- Side accent bar -->
          <td style="width:5px;background:linear-gradient(180deg,{accent},{accent}88);font-size:0;">&nbsp;</td>
          <td style="padding:28px 28px 28px 24px;">
            <!-- Status badge -->
            <div style="display:inline-block;background:{accent}1a;border:1px solid {accent}55;
                        border-radius:50px;padding:6px 18px;margin:0 0 14px;">
              <span style="font-size:13px;font-weight:700;color:{accent};">{icon}&nbsp; {label}</span>
            </div>
            <h2 style="margin:0 0 10px;font-family:Georgia,serif;font-size:24px;color:#f0dcc0;font-weight:700;line-height:1.3;">
              {headline}
            </h2>
            <!-- Order ID -->
            <p style="margin:0;font-size:12px;color:#7a5c38;">
              Order <span style="color:{accent};font-family:monospace;font-size:14px;font-weight:700;">#{order_id}</span>
              &nbsp;·&nbsp; Hi, <strong style="color:#c8a87a;">{username}</strong>
            </p>
          </td>
        </tr>
      </table>

      <!-- Description -->
      <p style="margin:0 0 28px;font-size:16px;color:#a08060;line-height:1.9;">
        {desc}
      </p>

      <!-- Order summary -->
      <p style="margin:0 0 12px;font-size:11px;color:#7a5c38;letter-spacing:3px;text-transform:uppercase;">
        — &nbsp; Order summary &nbsp; —
      </p>
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
             style="background:#0f0906;border:1px solid #2a1a0a;border-radius:12px;overflow:hidden;margin:0 0 24px;">
        <tr>
          <td style="padding:14px 16px;border-bottom:1px solid #1f1408;color:#7a5c38;font-size:13px;">
            🏷️&nbsp; Order ID
          </td>
          <td style="padding:14px 16px;border-bottom:1px solid #1f1408;text-align:right;
                      color:{accent};font-family:monospace;font-size:15px;font-weight:700;">
            #{order_id}
          </td>
        </tr>
        <tr>
          <td style="padding:14px 16px;border-bottom:1px solid #1f1408;color:#7a5c38;font-size:13px;">
            📊&nbsp; Status
          </td>
          <td style="padding:14px 16px;border-bottom:1px solid #1f1408;text-align:right;">
            <span style="background:{accent}1a;border:1px solid {accent}44;border-radius:20px;
                         padding:4px 12px;font-size:12px;font-weight:700;color:{accent};">
              {label}
            </span>
          </td>
        </tr>
        <tr>
          <td style="padding:14px 16px;border-bottom:1px solid #1f1408;color:#7a5c38;font-size:13px;">
            📍&nbsp; Delivery Address
          </td>
          <td style="padding:14px 16px;border-bottom:1px solid #1f1408;text-align:right;color:#f0dcc0;font-size:13px;">
            {address}
          </td>
        </tr>
        <tr>
          <td style="padding:16px 16px;color:#7a5c38;font-size:13px;">
            💰&nbsp; Order Total
          </td>
          <td style="padding:16px 16px;text-align:right;color:#e07832;font-size:20px;font-weight:900;">
            ₹{total:.2f}
          </td>
        </tr>
      </table>

      <!-- Tip box -->
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0"
             style="background:#1a0e06;border-left:3px solid {accent};border-radius:0 10px 10px 0;margin:0 0 32px;">
        <tr>
          <td style="padding:16px 20px;">
            <p style="margin:0 0 4px;font-size:13px;font-weight:700;color:{accent};">
              💡&nbsp; Good to know
            </p>
            <p style="margin:0;font-size:13px;color:#7a5c38;line-height:1.7;">{tip}</p>
          </td>
        </tr>
      </table>

      <!-- CTA -->
      <table role="presentation" align="center" cellpadding="0" cellspacing="0" style="margin:0 auto 32px;">
        <tr>
          <td style="border-radius:50px;background:linear-gradient(135deg,{accent},{accent}cc);
                     box-shadow:0 4px 20px {accent}33;">
            <a href="#" style="display:inline-block;padding:15px 44px;font-size:15px;font-weight:700;
                                color:#fff;text-decoration:none;letter-spacing:1px;border-radius:50px;">
              📦&nbsp; View Order Details
            </a>
          </td>
        </tr>
      </table>

      <!-- Help line -->
      <p style="margin:0;font-size:13px;color:#5a4030;line-height:1.7;text-align:center;">
        Need help with your order? We're always here —
        <a href="mailto:help@caupenrost.shop" style="color:{accent};text-decoration:none;">help@caupenrost.shop</a>
      </p>

    </td>
  </tr>"""

    html = _wrap(_header(subtitle=f"Order Update · {label}", accent=accent) + body + _footer())
    return _send(subject, html, to_email)


def log_startup_config():
    api_key = _get_api_key()
    if api_key:
        logging.info("Email startup: RESEND_API_KEY configured: True — Resend email sending is active")
    else:
        logging.warning("Email startup: RESEND_API_KEY configured: False — OTP codes will be logged only")
