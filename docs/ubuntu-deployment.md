# PathRAG Ubuntu Production Deployment Guide

This guide provides step-by-step instructions for deploying PathRAG with ArangoDB on Ubuntu production servers with nginx and PM2.

## 📋 Prerequisites

- Ubuntu 18.04+ server with sudo access
- nginx installed and running
- PM2 process manager installed
- Python 3.8+ installed
- Git installed
- Domain name or IP address configured

## 🚀 Deployment Steps

### 1. Create Application Directory

```bash
# Create the main application directory
sudo mkdir -p /opt/pathrag
sudo chown $USER:$USER /opt/pathrag
cd /opt/pathrag
```

### 2. Set Up GitHub Deploy Key

#### Generate SSH Key Pair
```bash
# Generate a new SSH key specifically for this repository
ssh-keygen -t ed25519 -C "pathrag-deploy-key" -f ~/.ssh/pathrag_deploy_key

# When prompted:
# - Enter file: (press Enter to use default or specify custom path)
# - Enter passphrase: (leave empty for automated deployment)
```

#### Display and Copy Public Key
```bash
# Copy this output to add to GitHub
cat ~/.ssh/pathrag_deploy_key.pub
```

#### Configure SSH for GitHub
```bash
# Create/edit SSH config
nano ~/.ssh/config

# Add this configuration:
Host github.com-pathrag
    HostName github.com
    User git
    IdentityFile ~/.ssh/pathrag_deploy_key
    IdentitiesOnly yes
```

#### Set Proper Permissions
```bash
chmod 600 ~/.ssh/pathrag_deploy_key
chmod 644 ~/.ssh/pathrag_deploy_key.pub
chmod 600 ~/.ssh/config
```

#### Test SSH Connection
```bash
# Test the connection (should show successful authentication)
ssh -T git@github.com-pathrag
```

### 3. GitHub Repository Configuration

1. Go to your GitHub repository
2. Navigate to **Settings** → **Deploy keys**
3. Click **Add deploy key**
4. Paste the public key content from step 2
5. Give it a title like "Ubuntu Production Server"
6. ✅ Check **Allow write access** (if you need to push from server)
7. Click **Add key**

### 4. Clone Repository

```bash
# Clone using the SSH config alias
git clone git@github.com-pathrag:yourusername/pathrag.git
cd pathrag

# Or if already cloned with HTTPS, change remote:
# git remote set-url origin git@github.com-pathrag:yourusername/pathrag.git
```

### 5. Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 6. Configure Environment Variables

```bash
# Copy example environment file
cp example.env .env

# Edit with your actual credentials
nano .env
```

**Required configurations in `.env`:**
```bash
# ArangoDB Configuration
ARANGODB_HOST=localhost
ARANGODB_PORT=8529
ARANGODB_USERNAME=root
ARANGODB_PASSWORD=your_secure_password
ARANGODB_DATABASE=pathrag

# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini

# PathRAG Configuration
PATHRAG_HOST=0.0.0.0
PATHRAG_PORT=8000
PATHRAG_DEBUG=false
```

### 7. Install and Configure ArangoDB

```bash
# Add ArangoDB repository
curl -OL https://download.arangodb.com/arangodb310/DEBIAN/Release.key
sudo apt-key add - < Release.key
echo 'deb https://download.arangodb.com/arangodb310/DEBIAN/ /' | sudo tee /etc/apt/sources.list.d/arangodb.list

# Install ArangoDB
sudo apt update
sudo apt install arangodb3

# Start and enable ArangoDB
sudo systemctl start arangodb3
sudo systemctl enable arangodb3

# Create database and user (run these in ArangoDB shell)
arangosh --server.endpoint http+tcp://127.0.0.1:8529
```

In ArangoDB shell:
```javascript
// Create database
db._createDatabase("pathrag");

// Use the database
db._useDatabase("pathrag");

// Create collections will be handled by the application
```

### 8. Configure PM2

```bash
# Start the application with PM2
pm2 start src/api_server.py --name "pathrag-api" --interpreter python3

# Save PM2 configuration
pm2 save

# Set up PM2 to start on boot
pm2 startup
# Follow the instructions provided by the startup command
```

### 9. Configure Nginx

```bash
# Copy the nginx configuration
sudo cp deploy/nginx.conf /etc/nginx/sites-available/pathrag

# Edit the configuration for your domain
sudo nano /etc/nginx/sites-available/pathrag

# Enable the site
sudo ln -s /etc/nginx/sites-available/pathrag /etc/nginx/sites-enabled/

# Test nginx configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

### 10. Set Up SSL (Optional but Recommended)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com

# Test automatic renewal
sudo certbot renew --dry-run
```

### 11. Create Log Directories

```bash
# Create log directories
sudo mkdir -p /var/log/pathrag
sudo chown $USER:$USER /var/log/pathrag

# Create backup directory
sudo mkdir -p /opt/pathrag/backups
sudo chown $USER:$USER /opt/pathrag/backups
```

### 12. Test the Deployment

```bash
# Check PM2 status
pm2 status

# Check application logs
pm2 logs pathrag-api

# Test API endpoint
curl http://localhost:8000/health

# Test through nginx
curl http://your-domain.com/health
```

## 🔄 Deployment Updates

To update the application:

```bash
cd /opt/pathrag/pathrag

# Pull latest changes
git pull origin master

# Activate virtual environment
source venv/bin/activate

# Update dependencies if needed
pip install -r requirements.txt

# Restart the application
pm2 restart pathrag-api

# Check status
pm2 status
```

## 🔧 Maintenance Commands

### Backup Database
```bash
# Create database backup
arangodump --server.endpoint http+tcp://127.0.0.1:8529 --output-directory "/opt/pathrag/backups/$(date +%Y%m%d_%H%M%S)"
```

### Monitor Logs
```bash
# View PM2 logs
pm2 logs pathrag-api

# View nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# View ArangoDB logs
sudo journalctl -u arangodb3 -f
```

### System Health Check
```bash
# Check all services
sudo systemctl status nginx
sudo systemctl status arangodb3
pm2 status

# Check disk space
df -h

# Check memory usage
free -h
```

## 🚨 Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 8000 and 8529 are available
2. **Permission issues**: Check file ownership and permissions
3. **Database connection**: Verify ArangoDB is running and credentials are correct
4. **API key issues**: Ensure OpenAI API key is valid and has sufficient credits

### Useful Commands
```bash
# Check port usage
sudo netstat -tlnp | grep :8000
sudo netstat -tlnp | grep :8529

# Check process status
ps aux | grep python
ps aux | grep arangodb

# Restart services
pm2 restart pathrag-api
sudo systemctl restart nginx
sudo systemctl restart arangodb3
```

## 🔒 Security Considerations

1. **Firewall**: Configure UFW to allow only necessary ports
2. **SSL**: Always use HTTPS in production
3. **Database**: Secure ArangoDB with strong passwords
4. **Environment**: Never commit `.env` files to version control
5. **Updates**: Keep system and dependencies updated
6. **Backups**: Regular database and application backups

## 📞 Support

For issues and questions:
- Check the logs first
- Review the troubleshooting section
- Consult the main documentation in the `docs/` directory
- Check GitHub issues for known problems

---

**Note**: Replace `yourusername/pathrag` with your actual GitHub username and repository name throughout this guide.