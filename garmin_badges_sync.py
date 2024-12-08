#!/usr/bin/env python3

version="1.4.0"

"""
Source: https://garminbadges.com/upload/garminbadges-updater.py
A script to sync Garmin badges with garminbadges.com
"""

import garth
import requests
import sys
import json
import os
import logging
from threading import Thread
import threading
from pathlib import Path
import webbrowser
from dotenv import load_dotenv
from pythonjsonlogger import jsonlogger
import datetime
import time

# Global variables
userId = 0
updateKey = ""
pythonVersion = ""
debugMode = False
logger = None

def setup_logging():
    """Configure JSON logging"""
    global logger
    logger = logging.getLogger('garmin_badges_sync')
    logHandler = logging.StreamHandler()
    
    # Create custom JSON formatter
    class CustomJsonFormatter(jsonlogger.JsonFormatter):
        def add_fields(self, log_record, record, message_dict):
            super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
            log_record['timestamp'] = datetime.datetime.now().isoformat()
            log_record['level'] = record.levelname
            log_record['type'] = 'log'  # To distinguish from result JSON

    formatter = CustomJsonFormatter('%(timestamp)s %(level)s %(name)s %(message)s')
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
    
    # Set log level based on debug mode
    logger.setLevel(logging.DEBUG if debugMode else logging.INFO)

def main():
    result = {
        "success": False,
        "message": "",
        "data": {},
        "error": None,
        "type": "result"  # To distinguish from log JSON
    }

    try:
        setup_logging()
        logger.info("Starting Garmin badges sync", extra={"version": version})
        
        handleArguments(sys.argv)
        logger.debug("Command line arguments processed", extra={"args": sys.argv})

        configFileName = getConfigFileNameAndMakeSureFolderExists()
        logger.debug("Config directory initialized", extra={"config_file": configFileName})

        loginToGarminBadgesAndConnect(configFileName)
        logger.info("Successfully logged in to Garmin Connect")

        fetchUserInfoFromGarminBadgesToGlobalVariables(configFileName)
        logger.info("Retrieved user info", extra={"user_id": userId})

        doVersionCheck(pythonVersion, version)
        logger.debug("Version check passed", extra={"current_version": version, "required_version": pythonVersion})

        # Fetch earned Json from Garmin
        logger.info("Fetching earned badges from Garmin")
        garminEarnedJson = garth.connectapi("/badge-service/badge/earned")
        logger.debug("Retrieved earned badges", extra={"badge_count": len(garminEarnedJson) if isinstance(garminEarnedJson, list) else 1})

        # Create Garmin Badges Json
        strippedGarminEarnedJson = createGarminBadgesJson(garminEarnedJson, updateKey)

        # POST stripped Json to Garmin Badges
        logger.info("Posting earned badges to Garmin Badges")
        badgesToFetch = postJsonToGarminbadges(strippedGarminEarnedJson, "https://garminbadges.com/api/index.php/user/earned")

        # Fetch badges from Garmin
        logger.info("Fetching detailed badge information")
        garminBadgeJsonArray = fetchBadgesFromGarmin(badgesToFetch.json())
        logger.debug("Retrieved badge details", extra={"badges_processed": len(garminBadgeJsonArray)})

        # Create final Garmin Badges Json
        garminBadgeJson = createGarminBadgesJson(garminBadgeJsonArray, updateKey)

        # POST the new badge json to Garmin Badges
        logger.info("Posting final badge data to Garmin Badges")
        gbBadgeResponse = postJsonToGarminbadges(garminBadgeJson, "https://garminbadges.com/api/index.php/user/challenges")

        result["success"] = True
        result["message"] = "Successfully synced Garmin badges"
        result["data"] = {
            "badges_synced": len(garminBadgeJsonArray),
            "user_id": userId,
            "response": gbBadgeResponse.json() if gbBadgeResponse else None
        }
        logger.info("Sync completed successfully", extra={"badges_synced": len(garminBadgeJsonArray)})

    except Exception as e:
        logger.error(f"Sync failed: {str(e)}", exc_info=True, extra={
            "error_type": type(e).__name__,
            "error_details": str(e)
        })
        result["success"] = False
        result["message"] = f"Failed to sync Garmin badges: {str(e)}"
        result["error"] = {
            "type": type(e).__name__,
            "message": str(e)
        }

    # Print result as JSON (separate from logs)
    print(json.dumps(result, indent=2))
    
    # Exit with appropriate status code
    sys.exit(0 if result["success"] else 1)

def getConfigFileNameAndMakeSureFolderExists():
    configDir = os.path.join(os.path.expanduser('~'), "data", ".garminbadges")
    configFileName = os.path.join(configDir, "config.json")
    Path(configDir).mkdir(parents=True, exist_ok=True)
    return configFileName

def handleArguments(arguments):
    global debugMode

    if "--version" in sys.argv:
        printVersion()
        sys.exit(0)
    if "--help" in sys.argv:
        printHelp()
        sys.exit(0)
    if "--V" in sys.argv:
        debugMode = True


def loginToGarminBadgesAndConnect(configFileName):
    try:
        # Load environment variables
        load_dotenv()
        
        # Get credentials from environment variables
        gb_username = os.getenv('GARMIN_BADGES_USERNAME')
        gb_email = os.getenv('GARMIN_BADGES_EMAIL')
        gc_email = os.getenv('GARMIN_CONNECT_USERNAME')
        gc_password = os.getenv('GARMIN_CONNECT_PASSWORD')

        if not all([gb_username, gb_email, gc_email, gc_password]):
            raise ValueError("Missing required environment variables. Please check your .env file.")

        # Check if config file exists and session is valid
        try:
            f = open(configFileName, "r")
            if "--clear" in sys.argv:
                raise Exception("Clear flag detected")
            garth.resume(os.path.join(os.path.expanduser('~'), "data", ".garth"))
            garth.client.username
        except Exception as e:
            if(debugMode):
                logger.debug("Session is expired or an error occurred. Logging in again...")

            # Save Garmin Badges credentials
            config = {"gbUsername": gb_username, "gbEmail": gb_email}
            with open(configFileName, 'w') as f:
                json.dump(config, f)

            # Login to Garmin Connect with exponential backoff retry
            max_retries = 5
            base_delay = 3  # seconds
            
            for attempt in range(max_retries):
                try:
                    delay = base_delay * (2 ** attempt)  # Exponential backoff
                    logger.info(f"Attempting to login to Garmin Connect (attempt {attempt + 1}/{max_retries})")
                    
                    # Clear any existing session
                    garth.client.clear()
                    
                    # Attempt login
                    garth.login(gc_email, gc_password)
                    
                    # Test the connection by making a simple API call
                    test_response = garth.connectapi("/userprofile-service/userprofile")
                    if test_response:
                        logger.info("Successfully connected to Garmin Connect")
                        garth.save(os.path.join(os.path.expanduser('~'), "data", ".garth"))
                        break
                    else:
                        raise Exception("Failed to verify connection")
                        
                except Exception as e:
                    error_msg = str(e)
                    if attempt == max_retries - 1:  # Last attempt
                        raise Exception(f"Failed to login to Garmin Connect after {max_retries} attempts: {error_msg}")
                    
                    logger.warning(f"Login attempt {attempt + 1} failed: {error_msg}")
                    logger.info(f"Waiting {delay} seconds before next attempt...")
                    time.sleep(delay)

    except Exception as e:
        logger.error(f"Error during login process: {str(e)}")
        sys.exit(1)

def fetchUserInfoFromGarminBadgesToGlobalVariables(configFileName):
    global pythonVersion, updateKey, userId

    with open(configFileName, 'r') as f:
        config = json.load(f)

    # Get update key and user id from garminbadges.com
    updateKeyJson = {
        "username": config["gbUsername"],
        "email": config["gbEmail"]
    }
    response = postJsonToGarminbadges(updateKeyJson, "https://garminbadges.com/api/index.php/user/updatekey")
    userId = response.json()["id"]
    updateKey = response.json()["update_key"]
    pythonVersion = response.json()["python_script_version"]

def doVersionCheck(latestVersion, currentVersion):
    if (latestVersion == currentVersion):
        return
    else:
        latestVersionArray = [int(num) for num in latestVersion.split('.')]
        currentVersionArray = [int(num) for num in currentVersion.split('.')]

        # Ignore patch version
        latestVersionArray.pop()
        currentVersionArray.pop()

        for latestVersionValue, currentVersionValue in zip(latestVersionArray, currentVersionArray):
            if latestVersionValue > currentVersionValue:
                logger.error("Script is outdated and will not run. Get the latest version (v.{}) at https://garminbadges.com/upload/garminbadges-updater.py".format(latestVersion))
                sys.exit()

def fetchOneBadgeFromGarmin(badgeNo, badgeUuid, badgeJson):
    try:
        garminBadgeResponse = garth.connectapi("/badge-service/badge/detail/v2/" + str(badgeNo))
        if badgeUuid:
            garminBadgeResponseUuid = garth.connectapi("/badgechallenge-service/badgeChallenge/" + badgeUuid)
            garminBadgeResponse["joinDateLocal"] = garminBadgeResponseUuid["joinDateLocal"]
        badgeJson.append(garminBadgeResponse)
    except Exception as e:
        if not garminBadgeResponse:
            badgeJson.append("")
        else:
            badgeJson.append(garminBadgeResponse)
        logger.error(f"Error fetching badge {badgeNo}: {str(e)}")

def fetchBadgesFromGarmin(badgesToFetch):
    NO_OF_THREADS_BEFORE_START = threading.active_count()
    badgeJson = []
    threads = []
    threadIndex = 0
    runningThreads = 0
    
    maxNumberOfRunningThreads = 10

    # Create all threads
    for badge in badgesToFetch:
        process = Thread(target=fetchOneBadgeFromGarmin, args=[badge["badgeNo"], badge["badgeUuid"], badgeJson])
        threads.append(process)

    # Limit the number of started threads to not exceed the thread pool
    while len(badgeJson) < len(threads):
        if(threadIndex < len(threads) and threading.active_count() - NO_OF_THREADS_BEFORE_START < maxNumberOfRunningThreads):
            threads[threadIndex].start()
            threadIndex += 1
    return badgeJson


def postJsonToGarminbadges(json, url):
    headers = {'Content-type': 'application/json'}
    return requests.post(url, headers=headers, json=json)

def createGarminBadgesJson(json, updateKey):
    newJson = []
    joinDateLocal = None;

    unitArray = {
        1: "mi_km",
        2: "ft_m",
        3: "activities",
        4: "days",
        5: "steps",
        6: "mi",
        7: "seconds"
    }

    for badge in json:
        if not badge:
            continue
        badgeUnit = ""
        try:
            badgeUnit = unitArray[badge["badgeUnitId"]]
        except KeyError as e:
            badgeUnit = ""

        if "joinDateLocal" in badge:
            joinDateLocal = badge["joinDateLocal"]
            
        newBadge = {
            "badgeId": badge["badgeId"],
            "badgeName": badge["badgeName"],
            "count": badge["badgeEarnedNumber"],
            "earned_date": badge["badgeEarnedDate"],
            "badgeProgressValue": badge["badgeProgressValue"],
            "badgeTargetValue": badge["badgeTargetValue"],
            "badgeUnit": badgeUnit,
            "userJoined": True if badge["userJoined"] else False,
            "joinDateLocal": joinDateLocal,
            "createdBy": "Python script v." + version
        }
        newJson.append(newBadge);

    newJson = {
        "update_key": updateKey,
        "badges": newJson
    }

    return newJson


def openWebPages(arguments):
    global userId
    if "--open-badges" in sys.argv:
        webbrowser.open_new_tab("https://garminbadges.com/index.php?userId=" + str(userId))
    if "--open-challenges" in sys.argv:
        webbrowser.open_new_tab("https://garminbadges.com/challenges.php?userId=" + str(userId))

def printVersion():
    print("Garminbadges Updater v." + version)

def printHelp():
    print("Usage: garminbadges-updater.py [options]\n")
    print("Options and arguments:")
    print("   --clear           : Enter user credentials again.")
    print("   --help            : This information about options and arguments.")
    print("   --open-badges     : Open badge page after update.")
    print("   --open-challenges : Open challenge page after update.")
    print("   --version         : Print version of the script.")
    print("   --V               : Verbose/debug mode.")


if __name__ == "__main__":
    main()