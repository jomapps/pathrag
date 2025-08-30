# PathRAG Environment Synchronization Guide

This guide ensures both Ubuntu production and Windows development environments stay synchronized and working properly.

## Environment Overview

### 🖥️ Windows Development Environment (master branch)
- **Purpose**: Full PathRAG development and testing
- **Branch**: `master`
- **API Server**: `src/api_server.py` (full PathRAG implementation)
- **Port**: 5000 (default)
- **Database**: ArangoDB (local development instance)
- **Dependencies**: Full requirements.txt + PathRAG library
- **Process Management**: Manual start via IDE or command line

### 🐧 Ubuntu Production Environment (production branch)
- **Purpose**: Stable API server for production use
- **Branch**: `production`
- **API Server**: `src/api_server_simple.py` (simplified stable API)
- **Port**: 8000
- **Database**: ArangoDB (production instance at movie.ft.tc:8529)
- **Dependencies**: Core dependencies only (Flask, ArangoDB, etc.)
- **Process Management**: PM2 with ecosystem.config.js
- **Reverse Proxy**: Nginx (movie.ft.tc:8000)

## 🔄 Synchronization Workflow

### 1. Development to Production (Recommended Flow)

#### On Windows Development Machine:
```bash
# 1. Ensure you're on master branch
git checkout master
git status

# 2. Test your changes locally
python src/api_server.py
# Test at http://localhost:5000

# 3. Commit and push changes
git add .
git commit -m "Development: [describe your changes]"
git push origin master
```

#### On Ubuntu Production Server:
```bash
# 1. Switch to production branch
git checkout production

# 2. Fetch latest changes
git fetch origin

# 3. Merge development changes (be careful with conflicts)
git merge origin/master

# 4. Resolve any conflicts if they occur
# Edit conflicted files manually
# git add <resolved-files>
# git commit -m "Merge: Resolve conflicts from master"

# 5. Test the changes
python verify_environments.py

# 6. Restart services if tests pass
pm2 restart pathrag-api

# 7. Verify production is working
curl http://movie.ft.tc:8000/health

# 8. Push production branch
git push origin production
```

### 2. Production Hotfixes to Development

#### On Ubuntu Production Server:
```bash
# 1. Make hotfix on production branch
git checkout production

# 2. Make necessary changes
# Edit files as needed

# 3. Test changes
python verify_environments.py

# 4. Commit and push
git add .
git commit -m "Hotfix: [describe the fix]"
git push origin production

# 5. Restart services
pm2 restart pathrag-api
```

#### On Windows Development Machine:
```bash
# 1. Fetch and merge hotfix
git checkout master
git fetch origin
git merge origin/production

# 2. Test merged changes
python src/api_server.py

# 3. Push updated master
git push origin master
```

## 🧪 Testing and Verification

### Automated Verification
Run the verification script on both environments:

```bash
# On both Windows and Ubuntu
python verify_environments.py
```

### Manual Testing

#### Ubuntu Production:
```bash
# 1. Check PM2 status
pm2 status

# 2. Check logs
pm2 logs pathrag-api

# 3. Test API endpoints
curl http://localhost:8000/health
curl http://movie.ft.tc:8000/health

# 4. Run live API tests
python test_api_live.py

# 5. Check Nginx status
sudo systemctl status nginx
nginx -t
```

#### Windows Development:
```bash
# 1. Start API server
python src/api_server.py

# 2. Test endpoints
# Visit http://localhost:5000/health in browser

# 3. Run full PathRAG tests
python test_magi_story.py  # If available
```

## ⚠️ Important Considerations

### File Differences Between Environments

**Files that should be different:**
- `.env` (different database hosts, ports, API keys)
- `ecosystem.config.js` (production only)
- `pathrag-nginx.conf` (production only)
- `start_pathrag.sh` (production only)

**Files that should be synchronized:**
- All source code in `src/`
- `requirements.txt`
- `README.md`
- Documentation files
- Test files

### Conflict Resolution

When merging between branches, common conflicts occur in:

1. **Environment files** (`.env`):
   - Keep environment-specific values
   - Don't merge database credentials

2. **API server files**:
   - Production uses `api_server_simple.py`
   - Development uses `api_server.py`
   - Both should be maintained separately

3. **Configuration files**:
   - PM2 config is production-only
   - Nginx config is production-only

### Branch Protection Rules

1. **Never force push** to either branch
2. **Always test** before merging
3. **Use descriptive commit messages**
4. **Tag releases** for important milestones

## 🚨 Emergency Procedures

### Production Server Issues

1. **Check PM2 status**: `pm2 status`
2. **Restart services**: `pm2 restart pathrag-api`
3. **Check logs**: `pm2 logs pathrag-api`
4. **Rollback if needed**: `git reset --hard HEAD~1`

### Development Environment Issues

1. **Check Python environment**: `python --version`
2. **Reinstall dependencies**: `pip install -r requirements.txt`
3. **Reset to last working commit**: `git reset --hard origin/master`

### Database Issues

1. **Check ArangoDB status**: 
   - Production: `curl http://movie.ft.tc:8529/_api/version`
   - Development: `curl http://localhost:8529/_api/version`

2. **Restart ArangoDB**:
   - Ubuntu: `sudo systemctl restart arangodb3`
   - Windows: Restart ArangoDB service

## 📋 Maintenance Checklist

### Daily
- [ ] Check PM2 status on production
- [ ] Monitor logs for errors
- [ ] Verify API health endpoints

### Weekly
- [ ] Run `verify_environments.py` on both systems
- [ ] Check for security updates
- [ ] Review and clean up logs

### Monthly
- [ ] Update dependencies (test in development first)
- [ ] Backup ArangoDB databases
- [ ] Review and update documentation

## 🔧 Useful Commands

### Git Commands
```bash
# Check branch status
git branch -a

# See differences between branches
git diff master..production

# Check commit history
git log --oneline --graph --all

# Sync with remote
git fetch --all
```

### PM2 Commands
```bash
# Status and management
pm2 status
pm2 restart pathrag-api
pm2 stop pathrag-api
pm2 logs pathrag-api
pm2 monit

# Save configuration
pm2 save
pm2 startup
```

### Nginx Commands
```bash
# Test configuration
nginx -t

# Reload configuration
sudo systemctl reload nginx

# Check status
sudo systemctl status nginx

# View logs
sudo tail -f /var/log/nginx/pathrag_access.log
sudo tail -f /var/log/nginx/pathrag_error.log
```

## 📞 Support

If you encounter issues:

1. **Check this guide first**
2. **Run verification script**: `python verify_environments.py`
3. **Check logs** for specific error messages
4. **Document the issue** with steps to reproduce
5. **Test fixes in development** before applying to production

Remember: **Always test in development before deploying to production!**
