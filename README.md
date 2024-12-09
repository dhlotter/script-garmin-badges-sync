# Garmin Badges Sync

A collection of Python scripts to sync Garmin badges and manage Garmin Connect challenges.

## Scripts Overview

### 1. garmin-badges-updater.py
The main script that syncs your Garmin Connect to Garmin Badges. It:
- Fetches all earned badges from your Garmin Connect account
- Processes both regular and challenge badges
- Handles retired badges gracefully
- Updates your profile on garminbadges.com
- Provides detailed logging of the sync process

### 2. garmin-connect-challenges.py
A utility script to manage Garmin Connect challenges. It can:
- List available challenges
- Join challenges automatically
- Filter challenges by type and date
- Show challenge details and requirements

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/dhlotter/garmin-badges-sync.git
cd garmin-badges-sync
```

### 2. Set Up Python Environment
```bash
# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

### 3. Configure Cloudflare Certificate (if using Cloudflare WARP)
```bash
# Install certifi
pip install certifi

# Download Cloudflare root certificate
wget https://developers.cloudflare.com/cloudflare-one/static/documentation/connections/Cloudflare_CA.pem

# Append to CA store
cat Cloudflare_CA.pem >> $(python -m certifi)

# Set environment variables
export CERT_PATH=$(python -m certifi)
export SSL_CERT_FILE=${CERT_PATH}
export REQUESTS_CA_BUNDLE=${CERT_PATH}
```

### 4. Set Up Environment Variables
Create a `.env` file in the project root:
```bash
GARMIN_BADGES_USERNAME=your_garminbadges_username
GARMIN_BADGES_EMAIL=your_garminbadges_email
GARMIN_CONNECT_USERNAME=your_garmin_connect_email
GARMIN_CONNECT_PASSWORD=your_garmin_connect_password
```

## Running the Scripts

### Manual Execution
```bash
# Sync badges
python garmin-badges-updater.py

# Additional options:
python garmin-badges-updater.py --help  # Show all options
python garmin-badges-updater.py --V     # Run in verbose mode
```

### Automated Scheduling

#### Using Cron (Linux/macOS)
Add to crontab to run daily:
```bash
# Edit crontab
crontab -e

# Add this line to run daily at 2 AM (adjust paths as needed)
0 2 * * * cd /path/to/garmin-badges-sync && source venv/bin/activate && python garmin-badges-updater.py >> sync.log 2>&1
```

#### Using Task Scheduler (Windows)
1. Open Task Scheduler
2. Create a new Basic Task
3. Set the trigger (e.g., daily at 2 AM)
4. Action: Start a program
5. Program/script: `path\to\venv\Scripts\python.exe`
6. Arguments: `path\to\garmin-badges-updater.py`
7. Start in: `path\to\garmin-badges-sync`

## Monitoring and Troubleshooting

### Logging
The script uses Python's logging module and outputs:
- INFO level: Normal operation updates
- WARNING level: Non-critical issues
- ERROR level: Critical problems
- DEBUG level: Detailed information (with --V flag)

### Common Issues
1. SSL/Certificate errors:
   - Verify Cloudflare certificate setup
   - Check SSL environment variables

2. Authentication failures:
   - Verify environment variables are set correctly
   - Check Garmin Connect credentials

3. API errors:
   - Check internet connectivity
   - Verify API endpoints are accessible

## Security Notes

- Keep your `.env` file secure and never commit it to Git
- Use appropriate file permissions for the `.env` file (600)
- Store credentials securely when setting up automated runs
- Regularly update your Python packages for security patches

## License

[MIT License](LICENSE)