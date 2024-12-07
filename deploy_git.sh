#!/bin/bash

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check if required environment variables are set
if [ -z "$DEPLOY_USER" ] || [ -z "$DEPLOY_PASSWORD" ] || [ -z "$DEPLOY_DIR" ] || [ -z "$DEPLOY_SERVER" ]; then
    echo "Error: DEPLOY_USER, DEPLOY_PASSWORD, DEPLOY_DIR, and DEPLOY_SERVER must be set in .env file"
    exit 1
fi

SERVER_HOST="${1:-$DEPLOY_SERVER}"
SERVER="${DEPLOY_USER}@${SERVER_HOST}"
REMOTE_DIR="${DEPLOY_DIR}"
GITHUB_REPO="https://github.com/dhlotter/garmin_badges_sync.git"

echo "Deploying to:"
echo "  Server: $SERVER"
echo "  Directory: $REMOTE_DIR"
echo

# Test SSH connection and setup git repo if needed
echo "Setting up repository..."
sshpass -p "$DEPLOY_PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER "
    if [ ! -d $REMOTE_DIR ]; then
        # Clone the repository if it doesn't exist
        git clone $GITHUB_REPO $REMOTE_DIR
    else
        # Pull latest changes if it exists
        cd $REMOTE_DIR
        git pull origin main
    fi
"

# Deploy on server
echo "Deploying..."
sshpass -p "$DEPLOY_PASSWORD" ssh $SERVER "
    cd $REMOTE_DIR

    # Copy example env if needed
    if [ ! -f .env ]; then
        cp .env.example .env
    fi

    # Build and start containers
    docker compose pull
    docker compose up -d --build
"

echo
echo "Deployment complete!"
echo "You can edit the .env file on the remote server using:"
echo "sshpass -p \"$DEPLOY_PASSWORD\" ssh $SERVER 'nano $REMOTE_DIR/.env'"
