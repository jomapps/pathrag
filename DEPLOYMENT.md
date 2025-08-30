# PathRAG Deployment Guide

## Environment Management

This repository supports multiple deployment environments with different configurations.

## Branches

### `master` - Development Environment (Windows)
- Original development setup
- Full PathRAG implementation
- Windows-compatible configuration
- Development dependencies

### `production` - Production Environment (Ubuntu)
- Ubuntu server deployment
- Simplified API server for stability
- Production-ready configuration
- PM2 process management
- Nginx reverse proxy

## Environment Differences

### Development (Windows - master branch)
```
API Server: src/api_server.py (full PathRAG)
Port: 5000 (configurable)
Database: ArangoDB (local development)
Dependencies: Full requirements.txt
Process Management: Manual/IDE
```

### Production (Ubuntu - production branch)
```
API Server: src/api_server_simple.py (stable API)
Port: 8000
Database: ArangoDB (production instance)
Dependencies: Core dependencies only
Process Management: PM2
Reverse Proxy: Nginx
Domain: movie.ft.tc:8000
```

## Deployment Instructions

### Development Setup (Windows)
```bash
git checkout master
pip install -r requirements.txt
python src/api_server.py
```

### Production Deployment (Ubuntu)
```bash
git checkout production
source venv/bin/activate
pip install Flask Flask-CORS arango python-dotenv pydantic
pm2 start ecosystem.config.js
sudo cp pathrag-nginx.conf /etc/nginx/sites-available/pathrag
sudo ln -sf /etc/nginx/sites-available/pathrag /etc/nginx/sites-enabled/
sudo systemctl reload nginx
```

## Testing

### Development Testing
```bash
python test_magi_story.py  # Full PathRAG test
```

### Production Testing
```bash
python test_api_live.py    # API endpoint tests
```

## Synchronizing Changes

### From Development to Production
```bash
# On development machine (Windows)
git checkout master
git add .
git commit -m "Development changes"
git push origin master

# On production server (Ubuntu)
git fetch origin
git checkout production
git merge master  # Merge development changes
# Resolve any conflicts
git push origin production
pm2 restart pathrag-api
```

### From Production to Development
```bash
# On production server (Ubuntu)
git checkout production
git add .
git commit -m "Production fixes"
git push origin production

# On development machine (Windows)
git fetch origin
git checkout master
git merge production  # Merge production fixes
# Resolve any conflicts
```

## Configuration Files

### Environment Variables (.env)
- Development: FLASK_PORT=5000
- Production: FLASK_PORT=8000

### API Servers
- Development: `src/api_server.py` (full features)
- Production: `src/api_server_simple.py` (stable core)

### Process Management
- Development: Manual start
- Production: PM2 with `ecosystem.config.js`

## Monitoring

### Production Health Check
```bash
curl http://movie.ft.tc:8000/health
```

### PM2 Status
```bash
pm2 status
pm2 logs pathrag-api
```

## Backup Strategy

### Code Backup
- Both branches pushed to GitHub
- Regular commits with descriptive messages

### Database Backup
- ArangoDB backup procedures
- Environment-specific backup scripts

## Security Considerations

### Development
- Local access only
- Debug mode enabled
- Full error messages

### Production
- Public domain access
- Debug mode disabled
- Error logging to files
- Nginx security headers
- Process isolation with PM2
