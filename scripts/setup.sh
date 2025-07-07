#!/bin/bash

# =======================
# Janken Core Setup Script
# =======================

set -e

echo "🚀 Janken Core Development Environment Setup"
echo "=============================================="

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check required tools
print_status "Checking required tools..."

# Check Python
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d" " -f2)
    print_success "Python $PYTHON_VERSION is installed"
else
    print_error "Python 3 is not installed. Please install Python 3.9 or later."
    exit 1
fi

# Check Flutter
if command_exists flutter; then
    FLUTTER_VERSION=$(flutter --version | head -n1 | cut -d" " -f2)
    print_success "Flutter $FLUTTER_VERSION is installed"
else
    print_error "Flutter is not installed. Please install Flutter SDK."
    exit 1
fi

# Check AWS CLI
if command_exists aws; then
    AWS_VERSION=$(aws --version 2>&1 | cut -d" " -f1 | cut -d"/" -f2)
    print_success "AWS CLI $AWS_VERSION is installed"
else
    print_warning "AWS CLI is not installed. Please install AWS CLI for server deployment."
fi

# Check SAM CLI
if command_exists sam; then
    SAM_VERSION=$(sam --version | cut -d" " -f4)
    print_success "SAM CLI $SAM_VERSION is installed"
else
    print_warning "SAM CLI is not installed. Please install SAM CLI for server development."
fi

# Check Docker
if command_exists docker; then
    DOCKER_VERSION=$(docker --version | cut -d" " -f3 | cut -d"," -f1)
    print_success "Docker $DOCKER_VERSION is installed"
else
    print_warning "Docker is not installed. Please install Docker for local development."
fi

print_status "Setting up development environment..."

# Setup Python virtual environment for server
if [ -d "server" ]; then
    print_status "Setting up Python virtual environment for server..."
    cd server
    
    if [ ! -d ".venv" ]; then
        python3 -m venv .venv
        print_success "Python virtual environment created"
    fi
    
    # Activate virtual environment
    source .venv/bin/activate || source .venv/Scripts/activate 2>/dev/null || true
    
    # Install dependencies if requirements.txt exists
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_success "Python dependencies installed"
    else
        print_warning "requirements.txt not found in server directory"
    fi
    
    cd ..
else
    print_warning "Server directory not found. Please add your SAM project to the server/ directory."
fi

# Setup Flutter dependencies for game app
if [ -d "client/game-app" ]; then
    print_status "Setting up Flutter dependencies for game app..."
    cd client/game-app
    
    if [ -f "pubspec.yaml" ]; then
        flutter pub get
        print_success "Flutter dependencies installed for game app"
    else
        print_warning "pubspec.yaml not found in client/game-app directory"
    fi
    
    cd ../..
else
    print_warning "Game app directory not found. Please add your Flutter game app to the client/game-app/ directory."
fi

# Setup Flutter dependencies for admin app
if [ -d "client/admin-app" ]; then
    print_status "Setting up Flutter dependencies for admin app..."
    cd client/admin-app
    
    if [ -f "pubspec.yaml" ]; then
        flutter pub get
        print_success "Flutter dependencies installed for admin app"
    else
        print_warning "pubspec.yaml not found in client/admin-app directory"
    fi
    
    cd ../..
else
    print_warning "Admin app directory not found. Please add your Flutter admin app to the client/admin-app/ directory."
fi

# Create environment files if they don't exist
print_status "Creating environment configuration files..."

# Server environment
if [ -d "server" ] && [ ! -f "server/.env" ]; then
    cat > server/.env << EOL
# Server Environment Variables
AWS_REGION=ap-northeast-1
DYNAMODB_TABLE_USERS=janken-users
DYNAMODB_TABLE_GAMES=janken-games
DYNAMODB_TABLE_RANKINGS=janken-rankings
DYNAMODB_TABLE_ADMIN_LOGS=janken-admin-logs
JWT_SECRET=your-jwt-secret-here
REDIS_ENDPOINT=localhost:6379
LOG_LEVEL=INFO
EOL
    print_success "Server .env file created"
fi

print_status "Validating Flutter setup..."

# Flutter doctor
if command_exists flutter; then
    flutter doctor
fi

echo ""
print_success "Setup completed! 🎉"
echo ""
echo "Next steps:"
echo "1. Add your existing projects to the respective directories:"
echo "   - Server: server/"
echo "   - Game App: client/game-app/"
echo "   - Admin App: client/admin-app/"
echo ""
echo "2. Configure AWS credentials for server deployment"
echo "3. Update environment variables in server/.env"
echo "4. Run 'flutter doctor' to verify Flutter setup"
echo ""
echo "Development commands:"
echo "- Server: cd server && sam local start-api"
echo "- Game App: cd client/game-app && flutter run"
echo "- Admin App: cd client/admin-app && flutter run -d windows"
echo ""
echo "Happy coding! 🚀" 