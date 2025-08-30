#!/bin/bash

# PathRAG with ArangoDB - One-Click Deployment Script
# This script provides automated deployment for PathRAG with ArangoDB integration
# Compatible with Ubuntu 20.04+ and similar Linux distributions

set -e  # Exit on any error

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_FILE="/tmp/pathrag_deploy.log"
DEPLOY_USER="pathrag"
DEPLOY_HOME="/home/$DEPLOY_USER"
APP_DIR="$DEPLOY_HOME/pathrag"
SERVICE_NAME="pathrag"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✓${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ✗${NC} $1" | tee -a "$LOG_FILE"
}

# Error handling
error_exit() {
    log_error "$1"
    log_error "Deployment failed. Check log file: $LOG_FILE"
    exit 1
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        error_exit "This script must be run as root (use sudo)"
    fi
}

# Check system requirements
check_system() {
    log "Checking system requirements..."
    
    # Check OS
    if [[ ! -f /etc/os-release ]]; then
        error_exit "Cannot determine OS version"
    fi
    
    source /etc/os-release
    if [[ "$ID" != "ubuntu" ]] && [[ "$ID" != "debian" ]]; then
        log_warning "This script is optimized for Ubuntu/Debian. Proceeding anyway..."
    fi
    
    # Check architecture
    ARCH=$(uname -m)
    if [[ "$ARCH" != "x86_64" ]] && [[ "$ARCH" != "amd64" ]]; then
        log_warning "Architecture $ARCH may not be fully supported"
    fi
    
    log_success "System check completed"
}

# Update system packages
update_system() {
    log "Updating system packages..."
    
    export DEBIAN_FRONTEND=noninteractive
    apt-get update -y || error_exit "Failed to update package list"
    apt-get upgrade -y || error_exit "Failed to upgrade packages"
    
    log_success "System packages updated"
}

# Install system dependencies
install_dependencies() {
    log "Installing system dependencies..."
    
    # Essential packages
    PACKAGES=(
        "curl"
        "wget"
        "git"
        "build-essential"
        "software-properties-common"
        "apt-transport-https"
        "ca-certificates"
        "gnupg"
        "lsb-release"
        "python3"
        "python3-pip"
        "python3-venv"
        "python3-dev"
        "nginx"
        "supervisor"
        "htop"
        "unzip"
        "jq"
    )
    
    for package in "${PACKAGES[@]}"; do
        log "Installing $package..."
        apt-get install -y "$package" || error_exit "Failed to install $package"
    done
    
    log_success "System dependencies installed"
}

# Install ArangoDB
install_arangodb() {
    log "Installing ArangoDB..."
    
    # Add ArangoDB repository key
    curl -fsSL https://download.arangodb.com/arangodb39/DEBIAN/Release.key | gpg --dearmor -o /usr/share/keyrings/arangodb.gpg
    
    # Add ArangoDB repository
    echo "deb [signed-by=/usr/share/keyrings/arangodb.gpg] https://download.arangodb.com/arangodb39/DEBIAN/ $(lsb_release -cs) main" > /etc/apt/sources.list.d/arangodb.list
    
    # Update package list
    apt-get update -y || error_exit "Failed to update package list after adding ArangoDB repository"
    
    # Install ArangoDB
    echo 'arangodb3 arangodb3/password password pathrag123' | debconf-set-selections
    echo 'arangodb3 arangodb3/password_again password pathrag123' | debconf-set-selections
    
    apt-get install -y arangodb3 || error_exit "Failed to install ArangoDB"
    
    # Start and enable ArangoDB
    systemctl start arangodb3 || error_exit "Failed to start ArangoDB"
    systemctl enable arangodb3 || error_exit "Failed to enable ArangoDB"
    
    # Wait for ArangoDB to be ready
    log "Waiting for ArangoDB to be ready..."
    for i in {1..30}; do
        if curl -s http://localhost:8529/_api/version > /dev/null 2>&1; then
            break
        fi
        sleep 2
    done
    
    log_success "ArangoDB installed and started"
}

# Create deployment user
create_user() {
    log "Creating deployment user..."
    
    if id "$DEPLOY_USER" &>/dev/null; then
        log_warning "User $DEPLOY_USER already exists"
    else
        useradd -m -s /bin/bash "$DEPLOY_USER" || error_exit "Failed to create user $DEPLOY_USER"
        log_success "User $DEPLOY_USER created"
    fi
    
    # Create application directory
    mkdir -p "$APP_DIR" || error_exit "Failed to create application directory"
    chown -R "$DEPLOY_USER:$DEPLOY_USER" "$DEPLOY_HOME" || error_exit "Failed to set ownership"
    
    log_success "Deployment user configured"
}

# Install Python dependencies
install_python_deps() {
    log "Installing Python dependencies..."
    
    # Upgrade pip
    python3 -m pip install --upgrade pip || error_exit "Failed to upgrade pip"
    
    # Install global Python packages
    pip3 install virtualenv || error_exit "Failed to install virtualenv"
    
    log_success "Python dependencies installed"
}

# Deploy application
deploy_application() {
    log "Deploying PathRAG application..."
    
    # Copy application files
    cp -r "$PROJECT_ROOT"/* "$APP_DIR/" || error_exit "Failed to copy application files"
    
    # Set ownership
    chown -R "$DEPLOY_USER:$DEPLOY_USER" "$APP_DIR" || error_exit "Failed to set ownership"
    
    # Create Python virtual environment
    sudo -u "$DEPLOY_USER" python3 -m venv "$APP_DIR/venv" || error_exit "Failed to create virtual environment"
    
    # Install Python requirements
    sudo -u "$DEPLOY_USER" "$APP_DIR/venv/bin/pip" install --upgrade pip || error_exit "Failed to upgrade pip in venv"
    
    if [[ -f "$APP_DIR/requirements.txt" ]]; then
        sudo -u "$DEPLOY_USER" "$APP_DIR/venv/bin/pip" install -r "$APP_DIR/requirements.txt" || error_exit "Failed to install Python requirements"
    else
        log_warning "requirements.txt not found, installing basic dependencies"
        sudo -u "$DEPLOY_USER" "$APP_DIR/venv/bin/pip" install flask python-dotenv pyarango || error_exit "Failed to install basic dependencies"
    fi
    
    log_success "Application deployed"
}

# Configure environment
configure_environment() {
    log "Configuring environment..."
    
    # Copy example.env to .env if it doesn't exist
    if [[ ! -f "$APP_DIR/.env" ]] && [[ -f "$APP_DIR/example.env" ]]; then
        cp "$APP_DIR/example.env" "$APP_DIR/.env" || error_exit "Failed to copy environment file"
        chown "$DEPLOY_USER:$DEPLOY_USER" "$APP_DIR/.env" || error_exit "Failed to set ownership of .env"
        log_success "Environment file created from example.env"
    else
        log_warning ".env file already exists or example.env not found"
    fi
    
    # Create logs directory
    mkdir -p "$APP_DIR/logs" || error_exit "Failed to create logs directory"
    chown -R "$DEPLOY_USER:$DEPLOY_USER" "$APP_DIR/logs" || error_exit "Failed to set ownership of logs directory"
    
    # Create data directory
    mkdir -p "$APP_DIR/pathrag_data" || error_exit "Failed to create data directory"
    chown -R "$DEPLOY_USER:$DEPLOY_USER" "$APP_DIR/pathrag_data" || error_exit "Failed to set ownership of data directory"
    
    log_success "Environment configured"
}

# Create systemd service
create_service() {
    log "Creating systemd service..."
    
    cat > "/etc/systemd/system/$SERVICE_NAME.service" << EOF
[Unit]
Description=PathRAG API Service with ArangoDB
After=network.target arangodb3.service
Requires=arangodb3.service

[Service]
Type=simple
User=$DEPLOY_USER
Group=$DEPLOY_USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
ExecStart=$APP_DIR/venv/bin/python -m scripts.api_server
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=$SERVICE_NAME

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$APP_DIR

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload systemd and enable service
    systemctl daemon-reload || error_exit "Failed to reload systemd"
    systemctl enable "$SERVICE_NAME" || error_exit "Failed to enable service"
    
    log_success "Systemd service created"
}

# Configure nginx
configure_nginx() {
    log "Configuring Nginx..."
    
    cat > "/etc/nginx/sites-available/$SERVICE_NAME" << EOF
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    location /health {
        proxy_pass http://127.0.0.1:5000/health;
        access_log off;
    }
}
EOF
    
    # Enable site
    ln -sf "/etc/nginx/sites-available/$SERVICE_NAME" "/etc/nginx/sites-enabled/$SERVICE_NAME" || error_exit "Failed to enable nginx site"
    
    # Remove default site
    rm -f /etc/nginx/sites-enabled/default
    
    # Test nginx configuration
    nginx -t || error_exit "Nginx configuration test failed"
    
    # Restart nginx
    systemctl restart nginx || error_exit "Failed to restart nginx"
    systemctl enable nginx || error_exit "Failed to enable nginx"
    
    log_success "Nginx configured"
}

# Start services
start_services() {
    log "Starting services..."
    
    # Start PathRAG service
    systemctl start "$SERVICE_NAME" || error_exit "Failed to start PathRAG service"
    
    # Wait for service to be ready
    log "Waiting for PathRAG service to be ready..."
    for i in {1..30}; do
        if curl -s http://localhost:5000/health > /dev/null 2>&1; then
            break
        fi
        sleep 2
    done
    
    log_success "Services started"
}

# Run health checks
run_health_checks() {
    log "Running health checks..."
    
    # Check ArangoDB
    if curl -s http://localhost:8529/_api/version > /dev/null 2>&1; then
        log_success "ArangoDB is healthy"
    else
        log_error "ArangoDB health check failed"
    fi
    
    # Check PathRAG service
    if curl -s http://localhost:5000/health > /dev/null 2>&1; then
        log_success "PathRAG service is healthy"
    else
        log_error "PathRAG service health check failed"
    fi
    
    # Check Nginx
    if curl -s http://localhost/ > /dev/null 2>&1; then
        log_success "Nginx is healthy"
    else
        log_error "Nginx health check failed"
    fi
}

# Display deployment summary
show_summary() {
    log "\n" + "="*60
    log_success "PathRAG Deployment Completed Successfully!"
    log "\n" + "="*60
    
    echo -e "\n${GREEN}🎉 Deployment Summary:${NC}"
    echo -e "${BLUE}├─${NC} Application Directory: $APP_DIR"
    echo -e "${BLUE}├─${NC} Service Name: $SERVICE_NAME"
    echo -e "${BLUE}├─${NC} Service User: $DEPLOY_USER"
    echo -e "${BLUE}├─${NC} ArangoDB: http://localhost:8529"
    echo -e "${BLUE}├─${NC} PathRAG API: http://localhost:5000"
    echo -e "${BLUE}└─${NC} Web Interface: http://localhost/"
    
    echo -e "\n${GREEN}🔧 Service Management:${NC}"
    echo -e "${BLUE}├─${NC} Start service: sudo systemctl start $SERVICE_NAME"
    echo -e "${BLUE}├─${NC} Stop service: sudo systemctl stop $SERVICE_NAME"
    echo -e "${BLUE}├─${NC} Restart service: sudo systemctl restart $SERVICE_NAME"
    echo -e "${BLUE}├─${NC} Check status: sudo systemctl status $SERVICE_NAME"
    echo -e "${BLUE}└─${NC} View logs: sudo journalctl -u $SERVICE_NAME -f"
    
    echo -e "\n${GREEN}📁 Important Files:${NC}"
    echo -e "${BLUE}├─${NC} Environment: $APP_DIR/.env"
    echo -e "${BLUE}├─${NC} Logs: $APP_DIR/logs/"
    echo -e "${BLUE}├─${NC} Data: $APP_DIR/pathrag_data/"
    echo -e "${BLUE}└─${NC} Service: /etc/systemd/system/$SERVICE_NAME.service"
    
    echo -e "\n${GREEN}🔑 Default Credentials:${NC}"
    echo -e "${BLUE}├─${NC} ArangoDB: root / pathrag123"
    echo -e "${BLUE}└─${NC} Update credentials in: $APP_DIR/.env"
    
    echo -e "\n${YELLOW}⚠️  Next Steps:${NC}"
    echo -e "${BLUE}1.${NC} Update $APP_DIR/.env with your API keys"
    echo -e "${BLUE}2.${NC} Restart the service: sudo systemctl restart $SERVICE_NAME"
    echo -e "${BLUE}3.${NC} Test the API: curl http://localhost:5000/health"
    echo -e "${BLUE}4.${NC} Check the logs: sudo journalctl -u $SERVICE_NAME -f"
    
    echo -e "\n${GREEN}📖 Documentation:${NC}"
    echo -e "${BLUE}└─${NC} README: $APP_DIR/README.md"
    
    log "\n" + "="*60
}

# Main deployment function
main() {
    log "Starting PathRAG with ArangoDB deployment..."
    log "Log file: $LOG_FILE"
    
    check_root
    check_system
    update_system
    install_dependencies
    install_arangodb
    create_user
    install_python_deps
    deploy_application
    configure_environment
    create_service
    configure_nginx
    start_services
    run_health_checks
    show_summary
    
    log_success "Deployment completed successfully!"
}

# Handle script arguments
case "${1:-}" in
    "--help" | "-h")
        echo "PathRAG with ArangoDB Deployment Script"
        echo "Usage: $0 [options]"
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --version, -v  Show version information"
        echo "  --check        Run health checks only"
        echo "  --status       Show service status"
        exit 0
        ;;
    "--version" | "-v")
        echo "PathRAG Deployment Script v1.0.0"
        exit 0
        ;;
    "--check")
        run_health_checks
        exit 0
        ;;
    "--status")
        systemctl status "$SERVICE_NAME" || true
        systemctl status arangodb3 || true
        systemctl status nginx || true
        exit 0
        ;;
    "")
        main
        ;;
    *)
        echo "Unknown option: $1"
        echo "Use --help for usage information"
        exit 1
        ;;
esac