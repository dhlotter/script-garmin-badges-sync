#!/usr/bin/env python3
"""
Minimal Garmin Connect authentication helper for n8n workflow.
This script handles OAuth token acquisition and management using the garth library.
"""

import garth
import json
import sys
import os
from pathlib import Path


def get_token():
    """
    Get a valid OAuth2 token for Garmin Connect.
    
    Returns:
        dict: JSON object with success status and token or error message
    """
    try:
        # Try to resume existing session
        garth_dir = Path.home() / ".garth"
        garth.resume(str(garth_dir))
        
        # Verify token is still valid by checking if we can access it
        token = garth.client.oauth2_token.token
        
        return {
            "success": True,
            "token": token,
            "message": "Resumed existing session"
        }
        
    except Exception as resume_error:
        # Session expired or doesn't exist, re-authenticate
        try:
            username = os.getenv('GARMIN_CONNECT_USERNAME')
            password = os.getenv('GARMIN_CONNECT_PASSWORD')
            
            if not username or not password:
                return {
                    "success": False,
                    "error": "Missing GARMIN_CONNECT_USERNAME or GARMIN_CONNECT_PASSWORD environment variables"
                }
            
            # Configure and login
            garth.configure()
            garth.login(username, password)
            
            # Save session for future use
            garth_dir = Path.home() / ".garth"
            garth.save(str(garth_dir))
            
            # Get the token
            token = garth.client.oauth2_token.token
            
            return {
                "success": True,
                "token": token,
                "message": "New session created"
            }
            
        except Exception as login_error:
            return {
                "success": False,
                "error": f"Authentication failed: {str(login_error)}"
            }


if __name__ == "__main__":
    result = get_token()
    print(json.dumps(result))
    
    # Exit with error code if authentication failed
    if not result.get("success"):
        sys.exit(1)
