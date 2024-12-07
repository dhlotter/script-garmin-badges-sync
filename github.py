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
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}")
        print(f"Error output: {e.stderr}")
        if check:
            sys.exit(1)
        return None

def deploy(commit_msg=None):
    """Deploy the application to the remote server"""
    # Load environment variables
    load_dotenv()
    
    # Get GitHub repo from .env
    github_repo = os.getenv('GITHUB_REPO')
    if not github_repo:
        print("Error: GITHUB_REPO not set in .env file")
        sys.exit(1)

    # Initialize git if needed
    if not Path('.git').exists():
        print("Initializing git repository...")
        run_command('git init')
        run_command(f'git remote add origin {github_repo}')
    
    # Add all files
    print("Adding files to git...")
    run_command('git add .')
    
    # Get commit message from argument or prompt
    if not commit_msg:
        commit_msg = input("Enter commit message: ").strip()
        if not commit_msg:
            print("Error: Commit message cannot be empty")
            sys.exit(1)
    
    # Commit changes
    print(f"Committing with message: {commit_msg}")
    run_command(f'git commit -m "{commit_msg}"')
    
    # Push to GitHub
    print("Pushing to GitHub...")
    run_command('git push -u origin main')
    
    print("\nDeployment complete!")
    print("Your code has been pushed to GitHub successfully.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Use the entire rest of the command line as the commit message
        commit_message = ' '.join(sys.argv[1:])
        deploy(commit_message)
    else:
        deploy()
