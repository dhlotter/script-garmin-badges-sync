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
import datetime
import time
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Global variables
userId = 0
updateKey = ""
pythonVersion = ""
debugMode = False
logger = None

# Load environment variables
load_dotenv()

def setup_logging():
    """Configure logging with simple format"""
    global logger
    logger = logging.getLogger('garmin_badges_sync')
    logHandler = logging.StreamHandler()
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
    logger.setLevel(logging.DEBUG if debugMode else logging.INFO)

def main():
    try:
        # Set up logging
        setup_logging()
        logger.info("Starting Garmin badges sync")

        handleArguments(sys.argv)
        if(debugMode):
            logger.info("Garmin Badges Updater v." + version)
            logger.info("Verbose/debug mode enabled")
            logger.info("Script started with command: " + ' '.join(sys.argv))

        configFileName = getConfigFileNameAndMakeSureFolderExists()
        loginToGarminBadgesAndConnect(configFileName)
        fetchUserInfoFromGarminBadgesToGlobalVariables(configFileName)
        doVersionCheck(pythonVersion, version)

        # Fetch earned badges from Garmin
        logger.info("Fetching earned badges from Garmin")
        garminEarnedJson = garth.connectapi("/badge-service/badge/earned")
        logger.info(f"Found {len(garminEarnedJson)} earned badges")

        # Process badge data
        logger.info("Processing badge data")
        strippedGarminEarnedJson = createGarminBadgesJson(garminEarnedJson, updateKey)

        # Post to Garmin Badges
        logger.info("Posting earned badges to Garmin Badges")
        badgesToFetch = postJsonToGarminbadges(strippedGarminEarnedJson, "https://garminbadges.com/api/index.php/user/earned")

        # Fetch detailed badge information
        logger.info("Fetching detailed badge information")
        garminBadgeJsonArray = fetchBadgesFromGarmin(badgesToFetch.json())
        logger.info(f"Retrieved details for {len(garminBadgeJsonArray)} badges")

        # Process badge details
        logger.info("Processing badge details")
        garminBadgeJson = createGarminBadgesJson(garminBadgeJsonArray, updateKey)

        # Post final data
        logger.info("Posting final badge data to Garmin Badges")
        gbBadgeResponse = postJsonToGarminbadges(garminBadgeJson, "https://garminbadges.com/api/index.php/user/challenges")
        logger.info("Successfully synced badges with Garmin Badges")

        # Open web pages
        openWebPages(sys.argv)

        if(debugMode):
            logger.info("Script ended.")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        sys.exit(1)

def getConfigFileNameAndMakeSureFolderExists():
    configDir = os.path.expanduser('~') + "/.garminbadges/"
    configFileName = configDir + "config.json"
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
        # Check if config file exists
        f = open(configFileName, "r")
                
        if "--clear" in sys.argv:
            raise Exception
            
        garth.resume("~/.garth")
        garth.client.username
        
    except Exception as e:
        if(debugMode):
            logger.info("Session expired or an error occurred. Attempting to log in with environment variables")
            
        # Get credentials from environment variables
        gb_username = os.getenv('GARMIN_BADGES_USERNAME')
        gb_email = os.getenv('GARMIN_BADGES_EMAIL')
        gc_email = os.getenv('GARMIN_CONNECT_USERNAME')
        gc_password = os.getenv('GARMIN_CONNECT_PASSWORD')
        
        # Validate all required credentials are present
        if not all([gb_username, gb_email, gc_email, gc_password]):
            logger.error("Error: Missing required environment variables. Please ensure your .env file contains:")
            logger.error("GARMIN_BADGES_USERNAME")
            logger.error("GARMIN_BADGES_EMAIL")
            logger.error("GARMIN_CONNECT_USERNAME")
            logger.error("GARMIN_CONNECT_PASSWORD")
            sys.exit(1)

        # Save Garmin Badges config
        config = {"gbUsername": gb_username, "gbEmail": gb_email}
        with open(configFileName, 'w') as f:
            json.dump(config, f)
            logger.info("Saved Garmin Badges configuration")

        # Configure Garth session and login
        garth.configure()
        logger.info("Logging in to Garmin Connect...")
        garth.login(gc_email, gc_password)
        garth.save("~/.garth")
        logger.info("Successfully logged in to Garmin Connect")

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
    logger.info(f"Retrieved user info (user ID: {userId})")

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
                logger.error(f"Script is outdated and will not run. Get the latest version (v.{latestVersion}) at https://garminbadges.com/upload/garminbadges-updater.py")
                sys.exit(1)

def fetchOneBadgeFromGarmin(badgeNo, badgeUuid, badgeJson):
    try:
        # First try to get the basic badge details
        garminBadgeResponse = garth.connectapi("/badge-service/badge/detail/v2/" + str(badgeNo))
        
        # If we have a UUID, try to get challenge details, but don't fail if 404
        if badgeUuid:
            try:
                garminBadgeResponseUuid = garth.connectapi("/badgechallenge-service/badgeChallenge/" + badgeUuid)
                garminBadgeResponse["joinDateLocal"] = garminBadgeResponseUuid["joinDateLocal"]
            except Exception as e:
                if "404" in str(e):
                    # This is likely a retired challenge badge, just log it and continue
                    logger.debug(f"Badge {badgeNo} appears to be retired (404 on challenge details)")
                    garminBadgeResponse["joinDateLocal"] = None
                else:
                    # For other errors, log them but continue
                    logger.warning(f"Non-404 error fetching challenge details for badge {badgeNo}: {str(e)}")
                    garminBadgeResponse["joinDateLocal"] = None
        
        badgeJson.append(garminBadgeResponse)
        return True
        
    except Exception as e:
        if "404" in str(e):
            logger.debug(f"Badge {badgeNo} not found (404)")
        else:
            logger.error(f"Error fetching badge {badgeNo}: {str(e)}")
        
        # Add an empty response to maintain array indexing
        badgeJson.append("")
        return False

def fetchBadgesFromGarmin(badgesToFetch):
    NO_OF_THREADS_BEFORE_START = threading.active_count()
    badgeJson = []
    threads = []
    threadIndex = 0
    maxNumberOfRunningThreads = 10

    # Create all threads
    for badge in badgesToFetch:
        process = Thread(target=fetchOneBadgeFromGarmin, args=[badge["badgeNo"], badge["badgeUuid"], badgeJson])
        threads.append(process)

    # Limit the number of started threads
    while len(badgeJson) < len(threads):
        if(threadIndex < len(threads) and threading.active_count() - NO_OF_THREADS_BEFORE_START < maxNumberOfRunningThreads):
            threads[threadIndex].start()
            threadIndex += 1
    return badgeJson

def postJsonToGarminbadges(json, url):
    headers = {'Content-type': 'application/json'}
    return requests.post(url, headers=headers, json=json, verify=True)

def createGarminBadgesJson(json, updateKey):
    newJson = []
    joinDateLocal = None

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
        except KeyError:
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
        newJson.append(newBadge)

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
    logger.info("Garmin Badges Updater v." + version)

def printHelp():
    logger.info("Usage: garminbadges-updater.py [options]\n")
    logger.info("Options and arguments:")
    logger.info("   --clear           : Enter user credentials again.")
    logger.info("   --help            : This information about options and arguments.")
    logger.info("   --open-badges     : Open badge page after update.")
    logger.info("   --open-challenges : Open challenge page after update.")
    logger.info("   --version         : Print version of the script.")
    logger.info("   --V               : Verbose/debug mode.")

if __name__ == "__main__":
    main()