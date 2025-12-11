# CaupenRost - Local Setup Guide

This guide will help you run the CaupenRost bakery application on your local machine.

---

## Prerequisites

1. **Python 3.8+** - Download from https://python.org
2. **Git** (optional) - For cloning the repository
3. **Gmail Account** with App Password for sending OTP emails

**Database:** The app automatically uses **SQLite** (no installation needed). PostgreSQL is optional for production.

---

## Step 1: Download and Extract

1. Download all project files to a folder on your computer
2. Open a terminal/command prompt in that folder

---

## Step 2: Install Python Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install flask flask-sqlalchemy flask-login flask-mail gunicorn psycopg2-binary werkzeug email-validator
```

---

## Step 3: Database Setup

### Option A: SQLite (Simpler - No Installation Required)

The app will automatically use SQLite if no PostgreSQL is configured. Just skip to Step 4.

### Option B: PostgreSQL (Recommended for Production)

1. **Install PostgreSQL** from https://postgresql.org/download/

2. **Create a database:**
   ```bash
   # Open PostgreSQL command line
   psql -U postgres
   
   # Create database and user
   CREATE DATABASE caupenrost;
   CREATE USER appuser WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE caupenrost TO appuser;
   \q
   ```

---

## Step 4: Gmail App Password Setup

To send OTP verification emails, you need a Gmail App Password:

1. Go to https://myaccount.google.com/security
2. Enable **2-Step Verification** if not already enabled
3. Go to https://myaccount.google.com/apppasswords
4. Select "Mail" and "Windows Computer" (or your device)
5. Click "Generate"
6. Copy the 16-character password (e.g., `abcd efgh ijkl mnop`)

---

## Step 5: Configure Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your settings:

```env
# Flask environment (use 'local' for SQLite)
FLASK_ENV=local

# Session Security (generate a random string)
SESSION_SECRET=your-random-secret-key-here-make-it-long

# Gmail SMTP Configuration (for OTP emails)
GMAIL_EMAIL=your-email@gmail.com
GMAIL_APP_PASSWORD=your-16-character-app-password

# Optional: PostgreSQL (only if you want to use PostgreSQL instead of SQLite)
# DATABASE_URL=postgresql://appuser:your_password@localhost:5432/caupenrost
```

**Note:** With `FLASK_ENV=local`, the app automatically uses SQLite. No database URL needed!

---

## Step 6: Load Environment Variables

### Option A: Manual Export (Linux/Mac)

```bash
export SESSION_SECRET="your-random-secret-key"
export DATABASE_URL="sqlite:///app.db"
export GMAIL_EMAIL="your-email@gmail.com"
export GMAIL_APP_PASSWORD="your-app-password"
```

### Option B: Using python-dotenv

```bash
pip install python-dotenv
```

Add this at the top of `app.py`:
```python
from dotenv import load_dotenv
load_dotenv()
```

### Option C: Windows Command Prompt

```cmd
set SESSION_SECRET=your-random-secret-key
set DATABASE_URL=sqlite:///app.db
set GMAIL_EMAIL=your-email@gmail.com
set GMAIL_APP_PASSWORD=your-app-password
```

---

## Step 7: Initialize Database

```bash
# Run the initialization script
python init_data.py
```

This creates sample products and an admin user.

---

## Step 8: Run the Application

### Development Mode:
```bash
python main.py
```

### Production Mode:
```bash
gunicorn --bind 0.0.0.0:5000 main:app
```

---

## Step 9: Access the Application

Open your browser and go to:
- **Website:** http://localhost:5000
- **Admin Panel:** http://localhost:5000/admin

### Default Admin Login:
- **Email:** opgaming565710@gmail.com
- **Password:** admin123

---

## Troubleshooting

### Email Not Sending?

1. Verify Gmail App Password is correct (16 characters, no spaces)
2. Check that 2-Step Verification is enabled on your Google account
3. Make sure "Less secure app access" is NOT what you're using (use App Passwords instead)

### Database Errors?

1. For SQLite: Delete the `instance/caupenrost.db` file and restart the app
2. For PostgreSQL: Ensure the service is running and credentials are correct

### Port Already in Use?

```bash
# Use a different port
python -c "from app import app; app.run(host='0.0.0.0', port=8080)"
```

---

## Running Offline (No Internet)

The app works offline except for:
1. **Email sending** - Requires internet to connect to Gmail SMTP
2. **Product images** - Currently use external URLs (see below to fix)

### To Make Images Work Offline:

1. Download product images and save to `static/images/products/`
2. Update product image URLs in the database or `init_data.py` to use local paths like `/static/images/products/chocolate-cake.jpg`

---

## File Structure

```
project/
├── app.py              # Flask app configuration
├── main.py             # Application entry point
├── models.py           # Database models
├── routes.py           # URL routes and views
├── email_service.py    # OTP email functionality
├── init_data.py        # Database initialization
├── templates/          # HTML templates
├── static/             # CSS, JS, images
└── .env                # Environment variables (create this)
```

---

## Quick Start Commands

```bash
# 1. Setup (one time)
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install flask flask-sqlalchemy flask-login flask-mail gunicorn werkzeug email-validator

# 2. Configure (one time)
# Create .env file with your settings

# 3. Initialize database (one time)
python init_data.py

# 4. Run (every time)
python main.py
```

---

## Support

For issues, check the logs in the terminal where you ran the application.
