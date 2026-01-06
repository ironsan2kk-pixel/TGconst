#!/bin/bash

# ============================================
# Telegram Bot Constructor - Installation Script
# ============================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="telegram-bot-constructor"
PROJECT_DIR=$(dirname $(dirname $(realpath $0)))
VENV_DIR="$PROJECT_DIR/venv"
DATA_DIR="$PROJECT_DIR/data"
LOG_DIR="/var/log/supervisor"

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  Telegram Bot Constructor - Installation  ${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Function to print status
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_warning "This script should be run as root for full installation"
        print_warning "Some steps may require manual sudo execution"
    fi
}

# Check Python version
check_python() {
    echo -e "\n${BLUE}[1/8] Checking Python...${NC}"
    
    if command -v python3.11 &> /dev/null; then
        PYTHON_CMD="python3.11"
    elif command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        if [[ $(echo "$PYTHON_VERSION >= 3.10" | bc -l) -eq 1 ]]; then
            PYTHON_CMD="python3"
        else
            print_error "Python 3.10+ required. Found: $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "Python 3 not found. Please install Python 3.10+"
        exit 1
    fi
    
    print_status "Python found: $($PYTHON_CMD --version)"
}

# Check Node.js
check_nodejs() {
    echo -e "\n${BLUE}[2/8] Checking Node.js...${NC}"
    
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node -v)
        print_status "Node.js found: $NODE_VERSION"
    else
        print_warning "Node.js not found. Install it for frontend development."
        print_warning "Run: curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - && sudo apt install -y nodejs"
    fi
}

# Create virtual environment
create_venv() {
    echo -e "\n${BLUE}[3/8] Creating virtual environment...${NC}"
    
    if [[ -d "$VENV_DIR" ]]; then
        print_warning "Virtual environment already exists"
    else
        $PYTHON_CMD -m venv "$VENV_DIR"
        print_status "Virtual environment created at $VENV_DIR"
    fi
    
    # Activate venv
    source "$VENV_DIR/bin/activate"
    print_status "Virtual environment activated"
}

# Install Python dependencies
install_python_deps() {
    echo -e "\n${BLUE}[4/8] Installing Python dependencies...${NC}"
    
    source "$VENV_DIR/bin/activate"
    pip install --upgrade pip
    pip install -r "$PROJECT_DIR/requirements.txt"
    
    print_status "Python dependencies installed"
}

# Install Node.js dependencies (frontend)
install_nodejs_deps() {
    echo -e "\n${BLUE}[5/8] Installing Node.js dependencies (frontend)...${NC}"
    
    if command -v npm &> /dev/null; then
        cd "$PROJECT_DIR/frontend"
        npm install
        print_status "Node.js dependencies installed"
        cd "$PROJECT_DIR"
    else
        print_warning "npm not found, skipping frontend dependencies"
    fi
}

# Create directories
create_directories() {
    echo -e "\n${BLUE}[6/8] Creating directories...${NC}"
    
    mkdir -p "$DATA_DIR"
    mkdir -p "$DATA_DIR/bots"
    mkdir -p "$LOG_DIR" 2>/dev/null || print_warning "Could not create $LOG_DIR (need sudo)"
    
    print_status "Directories created"
}

# Setup environment file
setup_env() {
    echo -e "\n${BLUE}[7/8] Setting up environment...${NC}"
    
    if [[ ! -f "$PROJECT_DIR/.env" ]]; then
        cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
        
        # Generate random secrets
        SECRET_KEY=$(openssl rand -hex 32)
        JWT_SECRET=$(openssl rand -hex 32)
        
        # Update .env with generated secrets
        sed -i "s/your-super-secret-key-change-this/$SECRET_KEY/" "$PROJECT_DIR/.env"
        sed -i "s/your-jwt-secret/$JWT_SECRET/" "$PROJECT_DIR/.env"
        
        print_status ".env file created with generated secrets"
        print_warning "Please edit .env file with your settings!"
    else
        print_warning ".env file already exists"
    fi
}

# Create admin user
create_admin() {
    echo -e "\n${BLUE}[8/8] Creating admin user...${NC}"
    
    source "$VENV_DIR/bin/activate"
    
    if [[ -f "$DATA_DIR/main.db" ]]; then
        print_warning "Database already exists. Skipping admin creation."
        print_warning "To create new admin, run: python scripts/create_admin.py"
    else
        cd "$PROJECT_DIR"
        python scripts/create_admin.py
        print_status "Admin user created"
    fi
}

# Print final instructions
print_instructions() {
    echo ""
    echo -e "${BLUE}============================================${NC}"
    echo -e "${GREEN}  Installation completed!${NC}"
    echo -e "${BLUE}============================================${NC}"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo ""
    echo "1. Edit configuration file:"
    echo "   nano $PROJECT_DIR/.env"
    echo ""
    echo "2. Configure Pyrogram session (for userbot):"
    echo "   source $VENV_DIR/bin/activate"
    echo "   python scripts/generate_session.py"
    echo ""
    echo "3. Start the backend:"
    echo "   source $VENV_DIR/bin/activate"
    echo "   python backend/run.py"
    echo ""
    echo "4. Start the userbot (in another terminal):"
    echo "   source $VENV_DIR/bin/activate"
    echo "   python userbot/run.py"
    echo ""
    echo "5. Start frontend (development):"
    echo "   cd frontend && npm run dev"
    echo ""
    echo "6. For production, configure supervisor:"
    echo "   sudo cp scripts/supervisor/*.conf /etc/supervisor/conf.d/"
    echo "   sudo supervisorctl reread"
    echo "   sudo supervisorctl update"
    echo ""
    echo -e "${YELLOW}API will be available at:${NC} http://localhost:8000"
    echo -e "${YELLOW}Frontend (dev) at:${NC} http://localhost:3000"
    echo ""
}

# Main execution
main() {
    check_root
    check_python
    check_nodejs
    create_venv
    install_python_deps
    install_nodejs_deps
    create_directories
    setup_env
    create_admin
    print_instructions
}

# Run main function
main
