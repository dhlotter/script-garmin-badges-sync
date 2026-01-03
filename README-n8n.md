# Garmin Badges n8n Workflow Setup

## 📋 Overview
This n8n workflow replicates your Python script for syncing Garmin badges with garminbadges.com.

## 🚀 Quick Start

### Automated Setup (Recommended)

Run the setup script to install dependencies and configure authentication:

```bash
cd /Users/dhlotter/Downloads/sourcecontrol/prd/script-garmin-badges-sync
./setup-n8n.sh
```

This will:
- Install the `garth` Python library
- Help you configure environment variables
- Test Garmin authentication
- Cache your OAuth token

### Manual Setup

### 1. Import the Workflow
1. Open your n8n instance
2. Click **Workflows** → **Import from File**
3. Select `garmin-badges-n8n-workflow.json`

### 2. Configure Credentials

You'll need to set up two credential types in n8n:

#### **Garmin Connect Credentials**
- **Type**: Create a new credential type or use HTTP Basic Auth
- **Username**: Your Garmin Connect email
- **Password**: Your Garmin Connect password

#### **Garmin Badges Credentials**
- **Type**: Create a custom credential with:
  - `username`: Your GarminBadges.com username
  - `email`: Your GarminBadges.com email

### 3. Update Credential References
After importing, you'll need to:
1. Click on each node that requires credentials
2. Select the appropriate credential from the dropdown
3. Save the workflow

### Garmin Authentication (Hybrid Approach)

The workflow uses a **hybrid approach** for Garmin authentication:
- **Python script** (`garmin_auth_helper.py`) handles OAuth token acquisition
- **n8n workflow** handles all data processing and API calls
- **Tokens last ~1 year**, so authentication happens rarely

#### Setup Steps:

1. **Install Python dependencies** (one-time):
   ```bash
   pip install garth
   ```

2. **Set environment variables**:
   ```bash
   export GARMIN_CONNECT_USERNAME="your@email.com"
   export GARMIN_CONNECT_PASSWORD="yourpassword"
   ```
   
   Or create a `.env` file in the script directory:
   ```
   GARMIN_CONNECT_USERNAME=your@email.com
   GARMIN_CONNECT_PASSWORD=yourpassword
   ```

3. **Test authentication** (optional):
   ```bash
   cd /Users/dhlotter/Downloads/sourcecontrol/prd/script-garmin-badges-sync
   python3 garmin_auth_helper.py
   ```
   Should output: `{"success": true, "token": "...", "message": "..."}`

4. **Update workflow path**: 
   - Open the workflow in n8n
   - Click "Get Garmin Auth Token" node
   - Update the `cwd` parameter to match your script location

**How It Works:**
- Workflow executes `garmin_auth_helper.py` at the start
- Script returns OAuth2 token as JSON
- Token is used for all Garmin API calls
- Token is cached in `~/.garth/` for future runs
- Re-authenticates automatically if token expires

## 📅 Scheduling

The workflow is set to run **daily at 2:00 AM** (cron: `0 2 * * *`).

To change the schedule:
1. Click the **Schedule Trigger** node
2. Modify the cron expression
3. Save the workflow

## 🔧 Workflow Structure

```
Schedule Trigger (daily at 2 AM)
    ↓
Get Garmin Auth Token (Execute Python script)
    ↓
Parse Auth Token (Extract OAuth2 token)
    ↓
Get Update Key (parallel) ────────┐
    ↓                              ↓
Fetch Earned Badges                │
    ↓                              │
Transform Earned Badges ←──────────┘
    ↓
Post Earned Badges
    ↓
Split Badges (batches of 10)
    ↓
Fetch Badge Details (parallel)
    ↓
Fetch Challenge Details (optional, continues on fail)
    ↓
Merge Badge Data
    ↓
Check if All Processed
    ↓
Transform Final Badge Data
    ↓
Post Final Badge Data
```

## 🐛 Troubleshooting

### "Authentication Failed"
- Verify your Garmin Connect credentials are correct
- Consider using the hybrid Python approach for auth

### "Update Key Not Found"
- Check your GarminBadges.com credentials
- Ensure the username and email match your account

### "Badge Details 404 Errors"
- This is normal for retired badges
- The workflow continues on fail for these cases

### "Rate Limiting"
- The workflow batches requests (10 at a time)
- Adjust batch size in "Split Badges" node if needed

## 🔄 Migration from Python Script

### What's Different:
- **No local config file**: Credentials stored in n8n
- **No threading**: n8n handles parallel execution
- **No command-line args**: Configure directly in nodes
- **Built-in scheduling**: No need for external cron

### What's the Same:
- Same API endpoints
- Same data transformations
- Same badge unit mappings
- Same error handling for retired badges

## 📊 Monitoring

n8n provides built-in execution history:
1. Go to **Executions** tab
2. View success/failure status
3. Inspect node outputs for debugging

## 🔐 Security Best Practices

1. **Never hardcode credentials** in the workflow
2. Use n8n's credential system
3. Enable **workflow encryption** if available
4. Restrict access to the workflow in n8n settings

## 💡 Next Steps

1. Test the workflow manually first (click "Execute Workflow")
2. Check the execution log for any errors
3. Verify badges appear on garminbadges.com
4. Activate the workflow for automatic scheduling

## 🆘 Need Help?

If you encounter issues with Garmin authentication, I can:
1. Create a hybrid solution with minimal Python
2. Build a full OAuth2 implementation
3. Help debug specific node errors

---

**Version**: 1.0.0  
**Compatible with**: n8n v1.0+
