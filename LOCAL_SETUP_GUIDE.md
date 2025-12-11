# CaupenRost Bakery - Local Deployment Guide

This comprehensive guide will help you run the CaupenRost bakery application on your local machine with MongoDB.

---

## Prerequisites

Before starting, ensure you have:

1. **Python 3.8+** - Download from https://python.org
2. **Git** (optional) - For version control
3. **MongoDB** - Either local installation or MongoDB Atlas (cloud)
4. **Gmail Account** with App Password for sending OTP emails

---

## Step 1: Download the Project

### Option A: Clone from Git
```bash
git clone <your-repository-url>
cd caupenrost
```

### Option B: Download ZIP
1. Download all project files to a folder
2. Extract and open a terminal in that folder

---

## Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate
```

---

## Step 3: Install Python Dependencies

```bash
pip install flask flask-pymongo flask-login flask-mail gunicorn werkzeug email-validator pymongo python-dotenv requests razorpay
```

Or use the requirements file:
```bash
pip install -r requirements.txt
```

### Create requirements.txt (if needed):
```
flask>=2.0
flask-pymongo>=2.3
flask-login>=0.6
flask-mail>=0.9
gunicorn>=21.0
werkzeug>=2.0
email-validator>=2.0
pymongo>=4.0
python-dotenv>=1.0
requests>=2.28
razorpay>=1.3
```

---

## Step 4: MongoDB Setup

### Option A: MongoDB Atlas (Cloud - Recommended for Beginners)

1. **Create a free MongoDB Atlas account:**
   - Go to https://www.mongodb.com/atlas
   - Click "Try Free" and create an account

2. **Create a new cluster:**
   - Choose the FREE tier (M0 Sandbox)
   - Select a region close to you
   - Click "Create Cluster"

3. **Create a database user:**
   - Go to "Database Access" in the left menu
   - Click "Add New Database User"
   - Choose "Password" authentication
   - Enter a username and password (save these!)
   - Set privileges to "Read and write to any database"
   - Click "Add User"

4. **Allow network access:**
   - Go to "Network Access" in the left menu
   - Click "Add IP Address"
   - Click "Allow Access from Anywhere" (for development)
   - Click "Confirm"

5. **Get your connection string:**
   - Go to "Database" and click "Connect"
   - Choose "Connect your application"
   - Select "Python" and version "3.6 or later"
   - Copy the connection string (looks like):
     ```
     mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/
     ```
   - Replace `<password>` with your actual password
   - Add your database name at the end:
     ```
     mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/caupenrost
     ```

### Option B: Local MongoDB Installation

1. **Install MongoDB Community Edition:**
   
   **Windows:**
   - Download from https://www.mongodb.com/try/download/community
   - Run the installer
   - Choose "Complete" installation
   - Install MongoDB as a Windows Service
   
   **Mac:**
   ```bash
   brew tap mongodb/brew
   brew install mongodb-community
   brew services start mongodb-community
   ```
   
   **Linux (Ubuntu/Debian):**
   ```bash
   wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -
   echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
   sudo apt-get update
   sudo apt-get install -y mongodb-org
   sudo systemctl start mongod
   sudo systemctl enable mongod
   ```

2. **Verify MongoDB is running:**
   ```bash
   mongosh
   # You should see the MongoDB shell
   # Type 'exit' to quit
   ```

3. **Your connection string for local MongoDB:**
   ```
   mongodb://localhost:27017/caupenrost
   ```

---

## Step 5: Gmail App Password Setup

To send OTP verification emails:

1. Go to https://myaccount.google.com/security
2. Enable **2-Step Verification** if not already enabled
3. Go to https://myaccount.google.com/apppasswords
4. Select "Mail" and your device type
5. Click "Generate"
6. Copy the 16-character password (format: `abcd efgh ijkl mnop`)

---

## Step 6: Create Environment File

Create a file named `.env` in your project root:

```env
# MongoDB Connection
# For MongoDB Atlas (cloud):
MONGO_URI=mongodb+srv://your-username:your-password@cluster0.xxxxx.mongodb.net/caupenrost

# For Local MongoDB:
# MONGO_URI=mongodb://localhost:27017/caupenrost

# Flask Session Secret (generate a random string)
SESSION_SECRET=your-super-secret-random-key-here-make-it-long-and-random

# Gmail SMTP Configuration (for OTP emails)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-16-character-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# Optional: Razorpay Payment Gateway
# RAZORPAY_KEY_ID=your-razorpay-key
# RAZORPAY_KEY_SECRET=your-razorpay-secret
```

**Important:** Never commit the `.env` file to version control!

Add to `.gitignore`:
```
.env
venv/
__pycache__/
*.pyc
```

---

## Step 7: Initialize the Database

The application will automatically create sample data on first run, including:
- Admin user
- Product categories
- Sample products

Default admin credentials:
- **Email:** opgaming565710@gmail.com
- **Password:** admin123

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

Open your browser and navigate to:

| Page | URL |
|------|-----|
| Home | http://localhost:5000 |
| Shop | http://localhost:5000/products |
| Cart | http://localhost:5000/cart |
| Login | http://localhost:5000/login |
| Admin Panel | http://localhost:5000/admin |

---

## Project Structure

```
caupenrost/
├── app.py                 # Flask app configuration & MongoDB connection
├── main.py                # Application entry point
├── routes.py              # URL routes and views
├── db.py                  # Database repository classes
├── mongodb_models.py      # MongoDB model classes
├── data_store.py          # Data initialization & utilities
├── email_service.py       # OTP email functionality
├── utils.py               # Helper utilities
├── config.py              # Configuration settings
├── templates/             # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── products.html
│   ├── cart.html
│   ├── admin/
│   └── ...
├── static/                # CSS, JS, images
│   ├── css/
│   ├── js/
│   └── images/
├── .env                   # Environment variables (create this)
├── requirements.txt       # Python dependencies
└── LOCAL_SETUP_GUIDE.md   # This guide
```

---

## Environment Variables Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `MONGO_URI` | Yes | MongoDB connection string | `mongodb+srv://user:pass@cluster.mongodb.net/caupenrost` |
| `SESSION_SECRET` | Yes | Flask session encryption key | Any random string (32+ characters) |
| `MAIL_SERVER` | No | SMTP server | `smtp.gmail.com` |
| `MAIL_PORT` | No | SMTP port | `587` |
| `MAIL_USERNAME` | No | Email address | `you@gmail.com` |
| `MAIL_PASSWORD` | No | Gmail App Password | `abcd efgh ijkl mnop` |
| `MAIL_DEFAULT_SENDER` | No | From address | `you@gmail.com` |

---

## Troubleshooting

### MongoDB Connection Failed

**Error:** `InvalidURI: Invalid URI scheme`
- Ensure your MONGO_URI starts with `mongodb://` or `mongodb+srv://`
- Check for typos in the connection string

**Error:** `ServerSelectionTimeoutError`
- For Atlas: Check that your IP is whitelisted in Network Access
- For local: Ensure MongoDB service is running
  ```bash
  # Windows
  net start MongoDB
  
  # Mac
  brew services start mongodb-community
  
  # Linux
  sudo systemctl start mongod
  ```

### Email Not Sending

1. Verify Gmail App Password is correct (16 characters, no spaces when entered)
2. Check that 2-Step Verification is enabled
3. Ensure you're using App Passwords, not your regular Gmail password

### Port Already in Use

```bash
# Find process using port 5000
# Windows:
netstat -ano | findstr :5000

# Mac/Linux:
lsof -i :5000

# Kill the process or use a different port:
gunicorn --bind 0.0.0.0:8080 main:app
```

### Module Not Found Errors

```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

---

## Quick Start Summary

```bash
# 1. Clone/download project
cd caupenrost

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Mac/Linux
# or: venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install flask flask-pymongo flask-login flask-mail gunicorn werkzeug email-validator pymongo python-dotenv

# 4. Create .env file with your MongoDB URI and settings
# (see Step 6 above)

# 5. Run the application
python main.py

# 6. Open http://localhost:5000 in your browser
```

---

## Deploying to Production

For production deployment, consider:

1. **Use a process manager** like Supervisor or systemd
2. **Set up a reverse proxy** with Nginx or Apache
3. **Enable HTTPS** with Let's Encrypt
4. **Use MongoDB Atlas** for reliable database hosting
5. **Set strong secrets** and never expose them

Example Nginx configuration:
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Support

If you encounter issues:
1. Check the terminal logs for error messages
2. Verify your `.env` file has all required variables
3. Ensure MongoDB is running and accessible
4. Test your MongoDB connection string using MongoDB Compass (free GUI tool)

For MongoDB Compass:
1. Download from https://www.mongodb.com/products/compass
2. Paste your connection string to test connectivity
