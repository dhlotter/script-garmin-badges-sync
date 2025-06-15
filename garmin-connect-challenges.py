#!/usr/bin/env python3

import os
import time
import logging
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from dotenv import load_dotenv
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import urllib3
import ssl
import platform
import sys
import subprocess
import tempfile
import shutil
import requests
from selenium.webdriver import ActionChains
import undetected_chromedriver as uc
from xvfbwrapper import Xvfb
import random

# Disable SSL verification warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Create an SSL context that doesn't verify certificates
ssl._create_default_https_context = ssl._create_unverified_context

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)

logger = setup_logging()

def get_system_info():
    """Get system OS and architecture information"""
    os_name = platform.system().lower()
    machine = platform.machine().lower()
    
    # Detect OS
    if os_name == 'darwin':
        system = 'mac'
    elif os_name == 'windows':
        system = 'windows'
    elif os_name == 'linux':
        system = 'linux'
    else:
        system = 'unknown'
    
    # Detect architecture
    is_arm = any(arm in machine for arm in ['arm', 'aarch'])
    is_64bit = sys.maxsize > 2**32
    
    arch = 'arm64' if is_arm and is_64bit else \
           'arm' if is_arm else \
           'x64' if is_64bit else \
           'x86'
    
    return system, arch

def get_chrome_version():
    """Get the installed Chrome/Chromium version"""
    try:
        # Try chromium-browser first (common on Linux)
        result = subprocess.run(['chromium-browser', '--version'], 
                              capture_output=True, 
                              text=True)
        if result.returncode == 0:
            version = result.stdout.strip().split()[-1].split('.')[0]
            return int(version)
    except:
        pass
    
    try:
        # Try chrome as fallback
        result = subprocess.run(['google-chrome', '--version'], 
                              capture_output=True, 
                              text=True)
        if result.returncode == 0:
            version = result.stdout.strip().split()[-1].split('.')[0]
            return int(version)
    except:
        pass
    
    # Default to latest known version if detection fails
    return 131

def download_chromedriver(system, arch):
    """Download ChromeDriver based on system and architecture"""
    try:
        chrome_version = get_chrome_version()
        if not chrome_version:
            raise Exception("Could not determine Chrome version")
            
        logger.info(f"Chrome version: {chrome_version}")
        
        # Determine the correct download URL based on system and architecture
        if system == 'mac':
            if arch == 'arm64':
                platform_path = 'mac-arm64'
            else:
                platform_path = 'mac-x64'
        elif system == 'windows':
            platform_path = 'win64' if arch in ['x64', 'arm64'] else 'win32'
        else:  # linux
            platform_path = 'linux64'
            
        download_url = f"https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/{chrome_version}.0.6778.87/{platform_path}/chromedriver-{platform_path}.zip"
        
        # Create a temporary directory
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, "chromedriver.zip")
        
        # Download the file
        logger.info(f"Downloading ChromeDriver from {download_url}")
        response = requests.get(download_url, verify=False)
        response.raise_for_status()
        
        with open(zip_path, 'wb') as f:
            f.write(response.content)
        
        # Extract the zip file
        logger.info("Extracting ChromeDriver...")
        shutil.unpack_archive(zip_path, temp_dir)
        
        # Find the chromedriver binary
        chromedriver_path = None
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                if file == 'chromedriver' or file == 'chromedriver.exe':
                    chromedriver_path = os.path.join(root, file)
                    break
            if chromedriver_path:
                break
                
        if not chromedriver_path:
            raise Exception("ChromeDriver binary not found in downloaded package")
            
        # Make it executable
        os.chmod(chromedriver_path, 0o755)
        
        return chromedriver_path
        
    except Exception as e:
        logger.error(f"Failed to download ChromeDriver: {str(e)}")
        raise

def setup_driver(headless=True):
    """Setup undetected-chromedriver with appropriate options"""
    try:
        logger.info("Setting up Chrome options...")
        options = uc.ChromeOptions()
        
        # Anti-detection options
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-blink-features')
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--start-maximized')
        options.add_argument('--enable-javascript')
        options.add_argument('--enable-cookies')
        
        # Network settings
        options.add_argument('--dns-prefetch-disable')
        options.add_argument('--no-proxy-server')
        options.add_argument('--disable-web-security')
        
        # Set realistic user agent
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        logger.info("Creating Chrome driver...")
        driver = uc.Chrome(
            options=options,
            headless=headless,
            use_subprocess=True,
            version_main=131,
            suppress_welcome=True
        )
        
        # Additional stealth settings
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Add language and plugins to make it look more realistic
        driver.execute_script("""
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
        """)
        
        # Set timeouts
        driver.set_page_load_timeout(30)  # Reduced timeout to fail faster
        driver.implicitly_wait(10)  # Reduced implicit wait
        
        logger.info("Chrome driver setup complete")
        return driver
        
    except Exception as e:
        logger.error(f"Failed to setup driver: {str(e)}")
        if isinstance(e, WebDriverException):
            logger.error(f"WebDriver error details: {e.msg}")
        raise


def login_to_garmin(driver, email, password):
    """Log in to Garmin Connect"""
    try:
        logger.info("Attempting to log in to Garmin Connect...")
        
        # Go directly to Garmin Connect signin
        logger.info("Navigating to Garmin Connect signin...")
        try:
            driver.get("https://connect.garmin.com/signin")
            logger.info(f"Current URL: {driver.current_url}")
        except Exception as e:
            logger.error(f"Failed to load signin page: {str(e)}")
            # Try to get network status
            try:
                driver.execute_script("return navigator.onLine;")
                logger.info("Browser reports online status: true")
            except:
                logger.error("Failed to get online status")
            raise
        
        # Wait for iframe with explicit timeout handling
        logger.info("Waiting for login iframe...")
        try:
            iframe_wait = WebDriverWait(driver, 20)
            iframe = iframe_wait.until(EC.presence_of_element_located((By.ID, "gauth-widget-frame-gauth-widget")))
            logger.info("Login iframe found")
        except TimeoutException:
            logger.error("Timed out waiting for login iframe")
            # Log the page source for debugging
            logger.error(f"Page source: {driver.page_source[:500]}...")  # First 500 chars
            raise
        
        logger.info("Switching to login iframe...")
        driver.switch_to.frame(iframe)
        
        # Enter credentials slowly and naturally
        logger.info("Waiting for email field...")
        email_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "email"))
        )
        
        logger.info("Entering email...")
        email_field.clear()
        for char in email:
            email_field.send_keys(char)
            time.sleep(random.uniform(0.1, 0.3))
        
        time.sleep(random.uniform(0.5, 1.5))
        
        logger.info("Entering password...")
        password_field = driver.find_element(By.ID, "password")
        password_field.clear()
        for char in password:
            password_field.send_keys(char)
            time.sleep(random.uniform(0.1, 0.3))
        
        time.sleep(random.uniform(0.5, 1.5))
        
        logger.info("Clicking sign in button...")
        sign_in_button = driver.find_element(By.ID, "login-btn-signin")
        sign_in_button.click()
        
        logger.info("Waiting for login to complete...")
        WebDriverWait(driver, 30).until(
            lambda x: "modern/dashboard" in x.current_url
        )
        
        logger.info("Successfully logged in!")
        return True
        
    except Exception as e:
        logger.error(f"Failed to log in: {str(e)}")
        try:
            screenshot_path = "login_failure.png"
            driver.save_screenshot(screenshot_path)
            logger.info(f"Screenshot saved to {screenshot_path}")
            
            # Log additional debugging information
            logger.error(f"Current URL: {driver.current_url}")
            logger.error(f"Page source: {driver.page_source[:500]}...")  # First 500 chars
        except Exception as screenshot_error:
            logger.error(f"Failed to capture debug info: {str(screenshot_error)}")
        return False

def wait_for_challenges_page(driver):
    """Wait for the challenges page to load"""
    try:
        logger.info("Waiting for challenges page to load...")
        
        # Wait for either the challenge cards or a join button to appear
        WebDriverWait(driver, 20).until(
            EC.any_of(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'BadgeChallengeCard')]")),
                EC.presence_of_element_located((By.XPATH, "//button[text()='Join']")),
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='badge-challenge-card']"))
            )
        )
        
        # Wait a bit more for all dynamic content
        time.sleep(5)
        return True
        
    except Exception as e:
        logger.error(f"Failed to load challenges page: {str(e)}")
        return False

def join_challenges(driver):
    """Join all available challenges"""
    try:
        print("\n=== Navigating to Challenges Page ===")
        driver.get("https://connect.garmin.com/modern/challenge")
        
        if not wait_for_challenges_page(driver):
            logger.error("Could not load challenges page")
            return
        
        # Wait a bit more for dynamic content
        time.sleep(5)
        
        # Find all Join buttons
        join_buttons = driver.find_elements(By.XPATH, "//button[text()='Join']")
        total_challenges = len(join_buttons)
        
        if total_challenges == 0:
            print("\n✨ No new challenges found to join!")
            return
            
        print(f"\n=== Found {total_challenges} Challenge{'s' if total_challenges > 1 else ''} to Join ===")
        
        challenges_joined = 0
        for button in join_buttons:
            try:
                # Get the challenge name from the card using a more robust selector
                try:
                    # Find the parent card element
                    challenge_card = button.find_element(By.XPATH, "./ancestor::div[contains(@class, 'BadgeChallengeCard')]")
                    
                    # Try multiple selectors for the name
                    name_selectors = [
                        ".//div[contains(@class, 'badgeName')]",  # Generic class name
                        ".//div[contains(@class, 'BadgeChallengeCard') and contains(@class, 'badgeName')]",  # More specific
                        ".//div[contains(@class, 'title')]",  # Fallback to generic title
                        ".//div[contains(@class, 'name')]",  # Another fallback
                    ]
                    
                    challenge_name = None
                    for selector in name_selectors:
                        try:
                            name_elem = challenge_card.find_element(By.XPATH, selector)
                            challenge_name = name_elem.text
                            if challenge_name:
                                break
                        except:
                            continue
                    
                    if not challenge_name:
                        challenge_name = "Unknown Challenge"
                        
                except Exception as e:
                    logger.debug(f"Could not get challenge details: {str(e)}")
                    challenge_name = "Unknown Challenge"
                
                print(f"\n🎯 Joining challenge ({challenges_joined + 1}/{total_challenges}): {challenge_name}")
                
                # Scroll the button into view with offset to avoid header overlap
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                time.sleep(1)  # Wait for any animations
                
                # Try multiple click methods
                try:
                    # Try JavaScript click first
                    driver.execute_script("arguments[0].click();", button)
                except:
                    try:
                        # Try regular click
                        button.click()
                    except:
                        # Try moving to element first
                        actions = ActionChains(driver)
                        actions.move_to_element(button).click().perform()
                
                challenges_joined += 1
                print(f"✅ Successfully joined: {challenge_name}")
                time.sleep(2)  # Wait between joins
                
            except Exception as e:
                print(f"❌ Failed to join: {challenge_name}")
                logger.error(f"Error details: {str(e)}")
                # Try to scroll past this button and continue
                driver.execute_script("window.scrollBy(0, 100);")
                continue
        
        print(f"\n=== Summary ===")
        print(f"✨ Successfully joined {challenges_joined} out of {total_challenges} challenge{'s' if total_challenges > 1 else ''}")
        if challenges_joined < total_challenges:
            print(f"⚠️  Failed to join {total_challenges - challenges_joined} challenge{'s' if (total_challenges - challenges_joined) > 1 else ''}")
        
        return challenges_joined
        
    except Exception as e:
        logger.error(f"Error in join_challenges: {str(e)}")
        return 0

def main():
    """Main function"""
    display = None
    try:
        print("\n=== Starting Garmin Challenge Joiner ===")
        
        # Load environment variables
        load_dotenv()
        email = os.getenv("GARMIN_CONNECT_USERNAME")
        password = os.getenv("GARMIN_CONNECT_PASSWORD")
        
        if not email or not password:
            print("❌ Missing Garmin Connect credentials in .env file")
            return
        
        print("🔄 Starting virtual display...")
        display = Xvfb(width=1920, height=1080, colordepth=24)
        display.start()
        
        print("🔄 Initializing browser...")
        driver = setup_driver(headless=False)  # Use non-headless mode with Xvfb
        
        try:
            print("\n=== Logging in to Garmin Connect ===")
            if not login_to_garmin(driver, email, password):
                print("❌ Failed to log in to Garmin Connect")
                return
            
            print("\n=== Joining Available Challenges ===")
            if join_challenges(driver):
                print("✅ Successfully processed all challenges")
            else:
                print("❌ Failed to process challenges")
            
        except Exception as e:
            logger.error(f"Error during execution: {str(e)}")
            raise
        finally:
            logger.info("Cleaning up resources...")
            try:
                driver.quit()
            except Exception as e:
                logger.error(f"Error while closing driver: {str(e)}")
    
    except Exception as e:
        print(f"\n❌ Script failed: {str(e)}")
        if 'driver' in locals():
            try:
                driver.quit()
            except:
                pass
    finally:
        if display:
            display.stop()

if __name__ == "__main__":
    main()