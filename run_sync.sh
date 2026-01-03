#!/bin/bash

# Configuration
SCRIPT_PATH="/root/sourcecontrol/script-garmin-badges-sync/garmin-badges-updater.py"
LOG_FILE="/var/log/garmin-badges-sync.log"
DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/1398061429822853150/2pE4MNTeCEcVXWf5D9ZN9SpofJTOYIc2yFsc6cYRngx1nMKUe_Rga2afGwJ1lZgrYNh1"

# Run the Python script
echo "----------------------------------------" >> "$LOG_FILE"
echo "Starting sync at $(date)" >> "$LOG_FILE"

# Run with system python3
/usr/bin/python3 "$SCRIPT_PATH" >> "$LOG_FILE" 2>&1
EXIT_CODE=$?

# Checks
if [ $EXIT_CODE -ne 0 ]; then
    echo "Sync FAILED at $(date) with exit code $EXIT_CODE" >> "$LOG_FILE"
    
    # Send Discord Notification
    /usr/bin/curl -H "Content-Type: application/json" \
        -d "{\"content\": \"⚠️ **Garmin Badges Sync Failed**\nExit Code: $EXIT_CODE\nCheck logs at $LOG_FILE\"}" \
        "$DISCORD_WEBHOOK_URL"
else
    echo "Sync SUCCESS at $(date)" >> "$LOG_FILE"
fi
