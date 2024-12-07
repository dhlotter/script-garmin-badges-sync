#!/usr/bin/env python3
import os
import subprocess
import sys
from pathlib import Path
from dotenv import load_dotenv

def run_command(command, check=True):
    """Run a shell command and return its output"""
    try:
        result = subprocess.run(command, shell=True, check=check, text=True, 
                              capture_output=True)
        print(result.stdout)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}")
        print(f"Error output: {e.stderr}")
        if check:
            sys.exit(1)
        return None

def get_env_or_exit(var_name, default=None):
    """Get environment variable or exit if not found"""
    value = os.getenv(var_name, default)
    if value is None:
        print(f"Error: {var_name} environment variable is not set")
        print("Please set it in your .env file")
        sys.exit(1)
    return value

def deploy():
    """Deploy the application from GitHub and start Docker containers"""
    # Load environment variables
    load_dotenv()
    
    # Get configuration from environment
    deploy_dir = os.path.expanduser(get_env_or_exit('DEPLOY_DIR', '~/source-control/garmin-badges-sync'))
    github_repo = get_env_or_exit('GITHUB_REPO')

    # Create deploy directory if it doesn't exist
    Path(deploy_dir).mkdir(parents=True, exist_ok=True)
    
    # Change to deploy directory
    os.chdir(deploy_dir)
    
    # Clone or pull repository
    if not Path(deploy_dir + "/.git").exists():
        print(f"Cloning repository from {github_repo}...")
        run_command(f"git clone {github_repo} .")
    else:
        print("Pulling latest changes...")
        run_command("git pull")
    
    # Check if .env file exists, create if it doesn't
    if not Path(".env").exists():
        print("Creating .env file...")
        if Path(".env.example").exists():
            run_command("cp .env.example .env")
            print("Please edit the .env file with your settings before continuing.")
            print(f"You can edit it using: nano {deploy_dir}/.env")
            sys.exit(0)
        else:
            print("Warning: No .env.example file found. You'll need to create .env manually.")
    
    # Build and start Docker containers
    print("Building and starting Docker containers...")
    run_command("docker compose down")  # Stop any existing containers
    run_command("docker compose build --no-cache")  # Build fresh
    run_command("docker compose up -d")  # Start in detached mode
    
    print("\nDeployment complete!")
    print(f"Application deployed to: {deploy_dir}")
    print("Docker containers are now running.")
    print("\nYou can check the logs using:")
    print("docker compose logs -f")

if __name__ == "__main__":
    deploy()
