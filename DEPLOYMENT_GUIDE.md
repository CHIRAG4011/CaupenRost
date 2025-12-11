# NIKITA RASOI & BAKES - Deployment Guide

## Overview
This comprehensive guide covers deploying the NIKITA RASOI & BAKES Flask e-commerce application both locally and on various free hosting platforms. The application uses Indian Rupee (₹) currency and includes features like product management, cart functionality, order tracking, and admin dashboard.

## 🏠 Local Development Setup

### Prerequisites
- **Python 3.11 or higher** (recommended: Python 3.11.7)
- **Git** (for cloning the repository)
- **Code Editor** (VS Code, PyCharm, or any preferred editor)
- **Web Browser** (Chrome, Firefox, Safari, or Edge)

### Method 1: Quick Start (Recommended)
```bash
# Clone the repository
git clone <your-repo-url>
cd nikita-rasoi-bakes

# Install dependencies directly (uses uv.lock for consistency)
pip install flask flask-mail werkzeug gunicorn email-validator

# Set environment variable (Windows)
set SESSION_SECRET=your-super-secret-key-change-this

# Set environment variable (macOS/Linux)
export SESSION_SECRET=your-super-secret-key-change-this

# Run the application
python main.py
```

### Method 2: Virtual Environment Setup
```bash
# Clone the repository
git clone <your-repo-url>
cd nikita-rasoi-bakes

# Create virtual environment
python -m venv bakery_env

# Activate virtual environment
# On Windows:
bakery_env\Scripts\activate
# On macOS/Linux:
source bakery_env/bin/activate

# Install dependencies
pip install flask flask-mail werkzeug gunicorn email-validator

# Run the application
python main.py
```

### Method 3: Using requirements.txt
Create a `requirements.txt` file if you need one:
```txt
Flask==3.0.0
Flask-Mail==0.9.1
Werkzeug==3.0.1
gunicorn==21.2.0
email-validator==2.1.0
```

Then install:
```bash
pip install -r requirements.txt
```

### Environment Configuration (Optional)
For email functionality, create a `.env` file in the root directory:
```env
# Required Settings
SESSION_SECRET=your-super-secret-key-here-change-this

# Email Configuration (Optional - for order confirmations)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# Development Settings
FLASK_ENV=development
DEBUG=True
```

### Running the Application
```bash
# Method 1: Direct execution (recommended for development)
python main.py

# Method 2: Using Gunicorn (production-like)
gunicorn --bind 0.0.0.0:5000 --reload main:app

# Method 3: Using Flask's built-in server
python -m flask run --host=0.0.0.0 --port=5000
```

### Accessing Your Local Application
- **Main Website:** http://localhost:5000
- **Admin Panel:** http://localhost:5000/admin
- **Products Page:** http://localhost:5000/products
- **Cart:** http://localhost:5000/cart

### Default Admin Credentials
- **Username:** admin
- **Email:** admin@nikitarasoi.com
- **Password:** admin123

### Sample Test Users
The application comes with pre-loaded sample data:
- **Customer Account:** john@example.com / password123
- **Sample Products:** Various Indian bakery items with INR pricing
- **Sample Orders:** Pre-loaded order history for testing

### Local Development Features
- **Hot Reload:** Changes to Python files automatically restart the server
- **Debug Mode:** Detailed error messages for easier development
- **In-Memory Storage:** No database setup required - data resets on restart
- **Sample Data:** Pre-loaded products, users, and orders for immediate testing

## 🌐 Free Hosting Options

### Option 1: Replit (Recommended ⭐)
**Best for:** Beginners, quick deployments, development
**Free Tier:** Generous with automatic sleep after inactivity

#### Setup on Replit:
1. **Import Repository:**
   - Go to replit.com
   - Click "Create Repl" → "Import from GitHub"
   - Enter your repository URL
   
2. **Automatic Configuration:**
   - Replit auto-detects Python projects
   - Uses `main.py` as entry point
   - Automatically installs dependencies from `pyproject.toml`

3. **Set Environment Variables:**
   - Click "Secrets" tab (lock icon)
   - Add: `SESSION_SECRET` = Generate strong 32-character key
   - Optional: Add email configuration variables

4. **Deploy:**
   - Click "Run" button
   - Access via provided `.replit.app` URL
   - Upgrade to "Always On" for $7/month to prevent sleeping

#### Advantages:
- ✅ Zero configuration required
- ✅ Automatic HTTPS and custom domains
- ✅ Built-in code editor and terminal
- ✅ Instant deployments
- ✅ Great for testing and small projects

#### Limitations:
- Apps sleep after 1 hour of inactivity (free tier)
- Limited CPU and memory on free tier

### Option 2: Railway 🚂
**Best for:** Production-ready deployments, API services
**Free Tier:** $5 credit monthly (very generous)

#### Setup on Railway:
1. **Connect Repository:**
   - Visit railway.app
   - Sign up with GitHub
   - Click "New Project" → "Deploy from GitHub repo"

2. **Automatic Deployment:**
   - Railway auto-detects Python apps
   - Uses `Procfile` or auto-generates start command

3. **Environment Variables:**
   ```
   SESSION_SECRET=your-secret-key-32-chars
   PORT=$PORT
   ```

4. **Custom Start Command:**
   ```bash
   gunicorn --bind 0.0.0.0:$PORT main:app
   ```

#### Advantages:
- ✅ Automatic deployments on git push
- ✅ Custom domains and HTTPS
- ✅ Database add-ons available
- ✅ No sleep limitations
- ✅ Professional infrastructure

#### Limitations:
- Free credit expires monthly
- Requires credit card for verification

### Option 3: Render 🎨
**Best for:** Static sites, web services, databases
**Free Tier:** 750 hours/month (good for always-on apps)

#### Setup on Render:
1. **Create Web Service:**
   - Go to render.com
   - Connect GitHub repository
   - Choose "Web Service"

2. **Configuration:**
   - **Name:** nikita-rasoi-bakes
   - **Environment:** Python 3
   - **Build Command:** `pip install flask flask-mail werkzeug gunicorn email-validator`
   - **Start Command:** `gunicorn --bind 0.0.0.0:$PORT main:app`

3. **Environment Variables:**
   - Add `SESSION_SECRET` in dashboard
   - Optional: Email configuration

#### Advantages:
- ✅ No credit card required
- ✅ 750 free hours monthly
- ✅ Automatic SSL certificates
- ✅ Built-in monitoring
- ✅ PostgreSQL databases available

#### Limitations:
- Slower cold starts
- Limited bandwidth on free tier

### Option 4: Fly.io ✈️
**Best for:** Global deployments, Docker containers
**Free Tier:** Good allowances with credit card verification

#### Setup on Fly.io:
1. **Install Fly CLI:**
   ```bash
   # Install flyctl
   curl -L https://fly.io/install.sh | sh
   ```

2. **Initialize App:**
   ```bash
   fly auth login
   fly launch
   ```

3. **Configuration (fly.toml):**
   ```toml
   app = "nikita-rasoi-bakes"
   
   [env]
     PORT = "8080"
   
   [[services]]
     http_checks = []
     internal_port = 8080
     processes = ["app"]
     protocol = "tcp"
   ```

#### Advantages:
- ✅ Global edge deployments
- ✅ Docker-based (flexible)
- ✅ Great performance
- ✅ Volume storage available

#### Limitations:
- More complex setup
- Requires Docker knowledge for advanced use

### Option 5: Vercel + Serverless 🔺
**Best for:** Serverless deployments, global CDN
**Free Tier:** Generous for hobby projects

#### Setup on Vercel:
1. **Install Vercel CLI:**
   ```bash
   npm i -g vercel
   ```

2. **Create vercel.json:**
   ```json
   {
     "builds": [
       {
         "src": "main.py",
         "use": "@vercel/python"
       }
     ],
     "routes": [
       {
         "src": "/(.*)",
         "dest": "main.py"
       }
     ]
   }
   ```

3. **Deploy:**
   ```bash
   vercel --prod
   ```

#### Advantages:
- ✅ Global CDN
- ✅ Instant scaling
- ✅ Zero configuration
- ✅ Analytics included

#### Limitations:
- Serverless limitations (stateless)
- 10-second execution limit

### Option 6: PythonAnywhere 🐍
**Best for:** Python-specific hosting, learning
**Free Tier:** Always-on web apps with limitations

#### Setup on PythonAnywhere:
1. **Create Free Account:**
   - Sign up at pythonanywhere.com
   - Upload your code files

2. **Web App Configuration:**
   - Create new web app
   - Choose Python 3.11
   - Set source code directory
   - Configure WSGI file

3. **WSGI Configuration:**
   ```python
   import sys
   path = '/home/yourusername/nikita-rasoi-bakes'
   if path not in sys.path:
       sys.path.append(path)
   
   from main import app as application
   ```

#### Advantages:
- ✅ Python-focused platform
- ✅ Always-on free tier
- ✅ SSH access available
- ✅ Good for learning

#### Limitations:
- Limited CPU seconds on free tier
- No custom domains on free tier

### Quick Comparison Table

| Platform | Free Tier | Always-On | Custom Domain | Database | Difficulty |
|----------|-----------|-----------|---------------|----------|------------|
| Replit | ✅ Good | 💰 Paid | ✅ Yes | ✅ Yes | 🟢 Easy |
| Railway | ✅ $5/month | ✅ Yes | ✅ Yes | ✅ Yes | 🟡 Medium |
| Render | ✅ 750hrs | ✅ Yes | ✅ Yes | ✅ Yes | 🟡 Medium |
| Fly.io | ✅ Good | ✅ Yes | ✅ Yes | ✅ Yes | 🔴 Hard |
| Vercel | ✅ Good | ✅ Yes | ✅ Yes | ⚠️ Limited | 🟡 Medium |
| PythonAnywhere | ✅ Limited | ✅ Yes | 💰 Paid | ⚠️ MySQL | 🟡 Medium |

## 🔧 Deployment Configuration Files

### Required Files for External Hosting

#### Create `requirements.txt`:
```txt
Flask==3.0.0
Flask-Mail==0.9.1
Werkzeug==3.0.1
gunicorn==21.2.0
email-validator==2.1.0
```

#### Create `Procfile` (for Railway, Heroku):
```
web: gunicorn --bind 0.0.0.0:$PORT main:app
```

#### Create `runtime.txt` (for Python version specification):
```
python-3.11.7
```

#### Create `.env.example` (for environment variable reference):
```env
# Copy this file to .env and fill in your values
SESSION_SECRET=change-this-to-a-random-32-character-string

# Email Configuration (Optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# Development Settings
FLASK_ENV=development
DEBUG=True
```

#### Create `app.json` (for platform compatibility):
```json
{
  "name": "NIKITA RASOI & BAKES",
  "description": "A Flask e-commerce application for an Indian bakery",
  "keywords": ["flask", "ecommerce", "bakery", "python"],
  "website": "https://github.com/yourusername/nikita-rasoi-bakes",
  "repository": "https://github.com/yourusername/nikita-rasoi-bakes",
  "env": {
    "SESSION_SECRET": {
      "description": "A secret key for session management",
      "generator": "secret"
    }
  },
  "formation": {
    "web": {
      "quantity": 1,
      "size": "free"
    }
  }
}
```

### Docker Configuration (Advanced)

#### Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]
```

#### Create `.dockerignore`:
```
__pycache__/
*.pyc
*.pyo
*.pyd
.env
.git
.gitignore
README.md
.DS_Store
.vscode/
venv/
bakery_env/
```

## 🔒 Production Considerations

### Security Settings
For production deployments, ensure:

1. **Strong Session Secret:**
   ```python
   # Generate a secure secret key
   import secrets
   SESSION_SECRET = secrets.token_urlsafe(32)
   # Example: "KmH8vR2_jP9x4LqWnZt3BcVy1FdGhJkMlN6OsQrTuA8"
   ```

2. **Environment Variables:**
   ```env
   FLASK_ENV=production
   DEBUG=False
   SESSION_SECRET=your-secure-32-character-key
   ```

3. **Security Headers (add to Flask app):**
   ```python
   @app.after_request
   def security_headers(response):
       response.headers['X-Content-Type-Options'] = 'nosniff'
       response.headers['X-Frame-Options'] = 'DENY'
       response.headers['X-XSS-Protection'] = '1; mode=block'
       return response
   ```

4. **HTTPS Only:** All hosting platforms provide HTTPS automatically

### Database Considerations
**Current Setup:** In-memory storage (suitable for):
- ✅ Development and testing
- ✅ Small-scale applications
- ✅ Demos and prototypes
- ✅ Educational projects

**For Production with Persistent Data:**
- **SQLite:** File-based, simple, good for small apps
- **PostgreSQL:** Recommended for production (available on most platforms)
- **MySQL/MariaDB:** Alternative relational database
- **MongoDB:** NoSQL option for flexible schemas

### Email Configuration for Production
**This project uses Gmail SMTP for sending emails.**

**Gmail SMTP Setup:**
1. Enable 2-Step Verification on your Google account
2. Generate an App Password at https://myaccount.google.com/apppasswords
3. Configure the following environment variables:

```env
GMAIL_EMAIL=your-email@gmail.com
GMAIL_APP_PASSWORD=your-16-char-app-password
```

**Notes:**
- Gmail allows 500 emails/day for regular accounts
- App Passwords are required (regular passwords won't work)
- The 16-character password looks like: `abcd efgh ijkl mnop`

### Performance Optimization

1. **Static File Serving:**
   ```python
   # Enable compression (add to Flask app)
   from flask_compress import Compress
   Compress(app)
   ```
   - Use CDN for static assets (Cloudflare, AWS CloudFront)
   - Enable gzip compression

2. **Caching Strategy:**
   ```python
   # Session storage with Redis (for multiple servers)
   import redis
   from flask_session import Session
   
   app.config['SESSION_TYPE'] = 'redis'
   app.config['SESSION_REDIS'] = redis.from_url('redis://localhost:6379')
   Session(app)
   ```

3. **Database Optimization:**
   - Implement connection pooling
   - Add database indexes for frequently queried fields
   - Use database caching for product catalogs

4. **Application Monitoring:**
   - Add logging for production debugging
   - Monitor response times and error rates
   - Set up alerts for downtime

### Scaling Considerations

**Horizontal Scaling (Multiple Servers):**
- Use external session storage (Redis)
- Implement load balancing
- Use external database

**Vertical Scaling (More Resources):**
- Upgrade hosting plan
- Optimize database queries
- Implement caching layers

## Monitoring and Maintenance

### Application Monitoring
- Monitor application logs
- Set up error tracking (Sentry, Rollbar)
- Monitor resource usage

### Backup Strategy
- Regular data backups (when using persistent storage)
- Code repository backups
- Configuration backups

### Updates and Maintenance
- Regular dependency updates
- Security patches
- Monitor for vulnerabilities

## 🛠️ Troubleshooting Guide

### Local Development Issues

#### Python/Flask Issues
1. **"Module not found" Error:**
   ```bash
   # Ensure you're in the right directory
   cd nikita-rasoi-bakes
   
   # Check if virtual environment is activated
   which python  # Should show your virtual environment path
   
   # Reinstall dependencies
   pip install flask flask-mail werkzeug gunicorn email-validator
   ```

2. **Port Already in Use:**
   ```bash
   # Find and kill process using port 5000
   lsof -ti:5000 | xargs kill -9
   
   # Or use a different port
   python main.py --port=8000
   ```

3. **Session Secret Missing:**
   ```bash
   # Set environment variable
   export SESSION_SECRET="your-32-character-secret-key"
   
   # Or create .env file with SESSION_SECRET
   ```

4. **Static Files Not Loading:**
   - Verify file paths in templates
   - Check static folder structure
   - Clear browser cache

#### Email Configuration Issues
1. **Gmail SMTP Not Working:**
   - Enable 2-Factor Authentication
   - Generate App Password (not your regular password)
   - Use app password in MAIL_PASSWORD

2. **Connection Timeout:**
   ```env
   # Try alternative Gmail settings
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=465
   MAIL_USE_SSL=True
   ```

### Deployment Issues

#### General Deployment Problems
1. **Application Won't Start:**
   ```bash
   # Check logs for specific errors
   # Most platforms provide build/deployment logs
   
   # Common fixes:
   # - Verify main.py exists and has app object
   # - Check if all dependencies are in requirements.txt
   # - Ensure Python version compatibility
   ```

2. **Environment Variables Not Set:**
   ```bash
   # Verify environment variables are set on platform
   # Check platform-specific documentation for setting env vars
   ```

3. **Build Failures:**
   ```bash
   # Common causes:
   # - Missing requirements.txt
   # - Incompatible Python version
   # - Syntax errors in code
   ```

#### Platform-Specific Issues

#### Replit Issues:
- **App Not Accessible:** Use 0.0.0.0 as host, not localhost
- **Environment Variables:** Set in Secrets panel, not .env file
- **Build Errors:** Check Console tab for detailed error messages
- **App Sleeping:** Upgrade to Always On or use UptimeRobot for periodic pings

#### Railway Issues:
- **Build Timeout:** Optimize build process, remove unnecessary dependencies
- **Port Issues:** Ensure app listens on $PORT environment variable
- **Memory Limits:** Monitor usage, optimize for free tier limits
- **Credit Exhausted:** Upgrade plan or optimize resource usage

#### Render Issues:
- **Cold Starts:** Free tier has longer startup times
- **Build Commands:** Ensure build command installs all dependencies
- **Environment Variables:** Set in Render dashboard, not in code
- **Health Checks:** Ensure app responds to health check requests

#### Vercel Issues:
- **Serverless Limitations:** App must be stateless for Vercel
- **Request Timeout:** 10-second limit on free tier
- **File Size Limits:** Large uploads may fail
- **Memory Storage:** In-memory data won't persist between requests

### Performance Issues

#### Slow Loading Times
1. **Optimize Images:**
   - Use compressed images
   - Implement lazy loading
   - Consider image CDN

2. **Database Optimization:**
   - Add indexes for frequently queried fields
   - Limit query results
   - Implement pagination

3. **Caching:**
   ```python
   # Add simple caching
   from functools import lru_cache
   
   @lru_cache(maxsize=128)
   def get_popular_products():
       # Cached function
       pass
   ```

#### Memory Issues
1. **Memory Leaks:**
   - Monitor memory usage
   - Clear unused variables
   - Optimize data structures

2. **Free Tier Limits:**
   - Implement efficient data structures
   - Use streaming for large responses
   - Optimize session storage

### Common Error Messages and Solutions

#### "Application Error" (Generic)
```bash
# Check application logs for specific error
# Common causes:
# 1. Missing environment variables
# 2. Code syntax errors
# 3. Import errors
# 4. Port binding issues
```

#### "No module named 'flask'"
```bash
# Dependencies not installed properly
pip install -r requirements.txt

# Or install individually
pip install flask flask-mail werkzeug gunicorn email-validator
```

#### "Address already in use"
```bash
# Port 5000 is occupied
# Kill the process or use different port
kill -9 $(lsof -ti:5000)
python main.py --port=8080
```

#### "Internal Server Error"
```bash
# Enable debug mode to see detailed errors
export FLASK_ENV=development
export DEBUG=True
python main.py
```

### Testing Your Deployment

#### Functionality Checklist
- [ ] Home page loads correctly
- [ ] Product pages display with INR pricing
- [ ] Cart functionality works (add/remove items)
- [ ] User registration and login
- [ ] Order placement with address validation
- [ ] Admin panel access (admin@nikitarasoi.com / admin123)
- [ ] Email functionality (if configured)
- [ ] Responsive design on mobile/tablet

#### Performance Testing
```bash
# Test response times
curl -w "@curl-format.txt" -o /dev/null -s "https://your-app-url.com"

# Monitor memory usage (local)
ps aux | grep python
```

### Getting Help

#### Debugging Steps
1. **Check Logs:** Platform-specific log viewing
2. **Test Locally:** Ensure it works on your machine first
3. **Verify Environment:** Check all environment variables
4. **Check Dependencies:** Ensure all packages are installed
5. **Test Incrementally:** Deploy minimal version first

#### Resources for Help
- **Platform Documentation:** Each hosting platform has comprehensive docs
- **Flask Documentation:** https://flask.palletsprojects.com/
- **Stack Overflow:** Search for specific error messages
- **GitHub Issues:** Check if others have similar problems
- **Community Forums:** Platform-specific communities

#### Creating Support Tickets
When asking for help, include:
- Exact error message
- Platform being used
- Steps to reproduce
- Code snippets (relevant parts only)
- Environment details (Python version, etc.)

## 📚 Additional Resources

### Official Documentation
- **Flask:** https://flask.palletsprojects.com/
- **Python:** https://docs.python.org/3/
- **Replit:** https://docs.replit.com/
- **Railway:** https://docs.railway.app/
- **Render:** https://render.com/docs
- **Vercel:** https://vercel.com/docs

### Learning Resources
- **Flask Tutorial:** https://flask.palletsprojects.com/tutorial/
- **Python Deployment:** https://realpython.com/python-web-applications/
- **Web Development Best Practices:** https://web.dev/

### Community Support
- **Flask Discord:** Official Flask community
- **Reddit:** r/flask, r/Python, r/webdev
- **Stack Overflow:** Tag questions with 'flask', 'python', 'deployment'
- **GitHub Discussions:** Platform-specific repositories

### Useful Tools
- **SSL Testing:** https://www.ssllabs.com/ssltest/
- **Performance Testing:** https://gtmetrix.com/
- **Uptime Monitoring:** https://uptimerobot.com/ (free)
- **Error Tracking:** https://sentry.io/ (free tier available)

## 📞 Support and Maintenance

### Regular Maintenance Tasks
- **Weekly:** Check application logs and performance
- **Monthly:** Update dependencies and security patches
- **Quarterly:** Review hosting costs and optimization opportunities
- **Annually:** Security audit and backup strategy review

### Monitoring Setup
```python
# Basic logging setup (add to main.py)
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### Backup Strategy
- **Code:** Always use Git version control
- **Data:** Regular exports if using persistent storage
- **Configuration:** Document all environment variables
- **Database:** Automated backups for production databases

---

## 🎯 Quick Start Summary

### For Beginners (Replit - Recommended)
1. Go to replit.com and import your GitHub repository
2. Click "Run" - Replit handles everything automatically
3. Set SESSION_SECRET in Secrets panel
4. Access your app via the provided .replit.app URL

### For Developers (Railway)
1. Connect GitHub repository to railway.app
2. Add SESSION_SECRET environment variable
3. Deploy automatically on git push
4. Get custom domain and HTTPS

### For Local Testing
1. `git clone <your-repo>`
2. `pip install flask flask-mail werkzeug gunicorn email-validator`
3. `export SESSION_SECRET="your-secret-key"`
4. `python main.py`
5. Open http://localhost:5000

---

**🚀 Ready to Deploy?**
This application is production-ready for small to medium-scale deployments. The in-memory storage makes it perfect for demos, prototypes, and small businesses. For larger scale applications, consider implementing a persistent database solution.

**📧 Need Help?**
If you encounter issues not covered in this guide, check the platform-specific documentation or reach out to their support teams. Most hosting platforms have excellent documentation and responsive support communities.

**🔄 Keep Updated:**
Web technologies evolve rapidly. Check for updates to Python, Flask, and your hosting platform regularly to ensure security and performance.