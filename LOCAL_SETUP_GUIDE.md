# CaupenRost Bakery - Local Development Guide

This guide helps you run the CaupenRost bakery application on your local machine. The application supports both **SQLite/PostgreSQL** and **MongoDB** backends.

---

## Quick Start (SQLite - Simplest)

For the fastest setup, use SQLite (default):

```bash
# 1. Clone/download project
cd caupenrost

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Mac/Linux
# or: venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install flask flask-sqlalchemy flask-login flask-mail gunicorn werkzeug email-validator psycopg2-binary python-dotenv requests

# 4. Create .env file (optional for SQLite)
echo "SESSION_SECRET=your-random-secret-key-here" > .env

# 5. Initialize database with sample data
python init_data.py

# 6. Run the application
python main.py

# 7. Open http://localhost:5000 in your browser
```

**Default Admin Login:** admin / admin123

---

## Database Backend Options

| Backend | Best For | Setup Complexity |
|---------|----------|------------------|
| **SQLite** | Local development, testing | Simplest (no setup) |
| **PostgreSQL** | Production-like environment | Medium |
| **MongoDB** | Document-based workflows | Medium |

---

## Option 1: SQLite Setup (Default)

SQLite requires no additional setup. The database file is created automatically at `instance/app.db`.

### Environment Variables (Optional)
```env
SESSION_SECRET=your-random-secret-key
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-gmail-app-password
```

---

## Option 2: PostgreSQL Setup

### Install PostgreSQL

**Mac:**
```bash
brew install postgresql
brew services start postgresql
createdb caupenrost
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo -u postgres createdb caupenrost
sudo -u postgres psql -c "CREATE USER myuser WITH PASSWORD 'mypassword';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE caupenrost TO myuser;"
```

**Windows:**
- Download from https://www.postgresql.org/download/windows/
- Use pgAdmin to create a database called `caupenrost`

### Environment Variables
```env
DATABASE_URL=postgresql://myuser:mypassword@localhost:5432/caupenrost
SESSION_SECRET=your-random-secret-key
```

Or use individual variables:
```env
PGHOST=localhost
PGPORT=5432
PGUSER=myuser
PGPASSWORD=mypassword
PGDATABASE=caupenrost
```

---

## Option 3: MongoDB Setup

### Install MongoDB Locally

**Mac:**
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

**Linux (Ubuntu):**
```bash
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org
sudo systemctl start mongod
```

**Windows:**
- Download from https://www.mongodb.com/try/download/community
- Run the installer and start MongoDB service

### MongoDB Atlas (Cloud)

1. Create free account at https://www.mongodb.com/atlas
2. Create a cluster (free M0 tier)
3. Create database user and whitelist your IP
4. Get connection string

### Environment Variables
```env
MONGO_URI=mongodb://localhost:27017/caupenrost
# Or for Atlas:
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/caupenrost
SESSION_SECRET=your-random-secret-key
```

---

## Email Configuration (OTP Verification)

The app uses email for OTP verification. To enable:

1. Go to https://myaccount.google.com/security
2. Enable 2-Step Verification
3. Go to https://myaccount.google.com/apppasswords
4. Generate an App Password for "Mail"

```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-16-char-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
```

---

## Initialize Database

### Seed Sample Data
```bash
python init_data.py
```

### Reset and Reseed (WARNING: Deletes all data)
```bash
python init_data.py --reset
```

### Force MongoDB Mode
```bash
python init_data.py --mongo
```

---

## Running the Application

### Development Mode
```bash
python main.py
```

### Production Mode
```bash
gunicorn --bind 0.0.0.0:5000 --reload main:app
```

---

## Application URLs

| Page | URL |
|------|-----|
| Home | http://localhost:5000 |
| Products | http://localhost:5000/products |
| Categories | http://localhost:5000/categories |
| Cart | http://localhost:5000/cart |
| Login | http://localhost:5000/login |
| Admin Dashboard | http://localhost:5000/admin |

---

## Project Structure

```
caupenrost/
├── app.py                 # Flask app configuration
├── main.py                # Application entry point
├── routes.py              # URL routes and views
├── db.py                  # SQLAlchemy repository classes
├── mongo_db.py            # MongoDB repository classes
├── models.py              # SQLAlchemy models
├── mongodb_models.py      # MongoDB model classes
├── data_store.py          # Data initialization utilities
├── init_data.py           # Database seeding script
├── email_service.py       # OTP email functionality
├── utils.py               # Helper utilities
├── config.py              # Configuration settings
├── templates/             # HTML templates
│   ├── base.html
│   ├── admin/             # Admin panel templates
│   ├── auth/              # Login/register templates
│   └── user/              # User profile templates
├── static/                # CSS, JS, images
├── instance/              # SQLite database (auto-created)
└── .env                   # Environment variables (create this)
```

---

## Troubleshooting

### Database Connection Issues

**SQLite:** Ensure `instance/` directory is writable.

**PostgreSQL:**
```bash
# Check if running
pg_isready

# Test connection
psql -U myuser -d caupenrost -h localhost
```

**MongoDB:**
```bash
# Check if running
mongosh --eval "db.runCommand('ping')"
```

### Email Not Sending

1. Verify Gmail App Password is correct
2. Check 2-Step Verification is enabled
3. Use App Passwords, not regular Gmail password
4. Check firewall allows outbound SMTP (port 587)

### Port Already in Use

```bash
# Find process using port 5000
lsof -i :5000  # Mac/Linux
netstat -ano | findstr :5000  # Windows

# Use different port
gunicorn --bind 0.0.0.0:8080 main:app
```

### Module Not Found

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

---

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `SESSION_SECRET` | Yes | Flask session encryption key |
| `DATABASE_URL` | No | PostgreSQL connection string |
| `MONGO_URI` | No | MongoDB connection string (enables MongoDB mode) |
| `MAIL_USERNAME` | No | Gmail address for sending OTPs |
| `MAIL_PASSWORD` | No | Gmail App Password |

---

## Default Credentials

After running `python init_data.py`:

| User | Password | Role |
|------|----------|------|
| admin | admin123 | Administrator |
| john_doe | Password1! | Regular User |
| sarah_baker | Password1! | Regular User |
