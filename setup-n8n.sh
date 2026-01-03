#!/bin/bash

# Garmin Badges n8n Setup Script
# This script helps set up the hybrid authentication workflow

set -e

echo "🚀 Garmin Badges n8n Workflow Setup"
echo "===================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3 first."
    exit 1
fi

echo "✅ pip3 found"
echo ""

# Install garth library
echo "📦 Installing garth library..."
pip3 install garth

echo ""
echo "✅ garth library installed successfully"
echo ""

# Check for environment variables
echo "🔐 Checking environment variables..."
if [ -z "$GARMIN_CONNECT_USERNAME" ] || [ -z "$GARMIN_CONNECT_PASSWORD" ]; then
    echo "⚠️  Environment variables not set"
    echo ""
    echo "Please set the following environment variables:"
    echo "  export GARMIN_CONNECT_USERNAME=\"your@email.com\""
    echo "  export GARMIN_CONNECT_PASSWORD=\"yourpassword\""
    echo ""
    echo "Or create a .env file in this directory with:"
    echo "  GARMIN_CONNECT_USERNAME=your@email.com"
    echo "  GARMIN_CONNECT_PASSWORD=yourpassword"
    echo ""
    
    # Ask if user wants to create .env file
    read -p "Would you like to create a .env file now? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter your Garmin Connect email: " gc_email
        read -sp "Enter your Garmin Connect password: " gc_password
        echo ""
        
        cat > .env << EOF
GARMIN_CONNECT_USERNAME=$gc_email
GARMIN_CONNECT_PASSWORD=$gc_password
EOF
        
        echo "✅ .env file created"
        echo ""
        
        # Load the .env file
        export $(cat .env | xargs)
    else
        echo "⚠️  Skipping .env creation. Please set environment variables manually."
        exit 0
    fi
else
    echo "✅ Environment variables are set"
fi

echo ""

# Test authentication
echo "🔑 Testing Garmin authentication..."
if python3 garmin_auth_helper.py > /dev/null 2>&1; then
    echo "✅ Authentication successful!"
    echo ""
    echo "Token cached in ~/.garth/"
else
    echo "❌ Authentication failed. Please check your credentials."
    exit 1
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Import garmin-badges-n8n-workflow.json into n8n"
echo "2. Update the 'Get Garmin Auth Token' node's 'cwd' parameter to:"
echo "   $(pwd)"
echo "3. Configure GarminBadges.com credentials in n8n"
echo "4. Test the workflow manually"
echo "5. Activate the workflow for automatic scheduling"
echo ""
