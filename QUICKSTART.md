# Garmin Badges n8n - Quick Reference

## 📁 Files Overview

| File | Purpose |
|------|---------|
| `garmin-badges-n8n-workflow.json` | n8n workflow (import this) |
| `garmin_auth_helper.py` | OAuth authentication script |
| `setup-n8n.sh` | Automated setup script |
| `README-n8n.md` | Full documentation |
| `garmin-badges-updater.py` | Original Python script (for reference) |

## ⚡ Quick Setup (3 Steps)

### 1. Run Setup Script
```bash
cd /Users/dhlotter/Downloads/sourcecontrol/prd/script-garmin-badges-sync
./setup-n8n.sh
```

### 2. Import Workflow
- Open n8n → Workflows → Import from File
- Select `garmin-badges-n8n-workflow.json`
- Update "Get Garmin Auth Token" node's `cwd` to your script directory

### 3. Configure Credentials
In n8n, create credentials for:
- **GarminBadges.com**: username + email

## 🔑 Environment Variables

Required in your shell or `.env` file:
```bash
GARMIN_CONNECT_USERNAME=your@email.com
GARMIN_CONNECT_PASSWORD=yourpassword
```

## 🧪 Testing

### Test Authentication Only
```bash
python3 garmin_auth_helper.py
```
Expected output:
```json
{"success": true, "token": "...", "message": "..."}
```

### Test Full Workflow
1. Open workflow in n8n
2. Click "Execute Workflow"
3. Check execution log for errors
4. Verify badges on garminbadges.com

## 📅 Scheduling

Default: Daily at 2:00 AM (cron: `0 2 * * *`)

To change:
1. Click "Schedule Trigger" node
2. Modify cron expression
3. Save workflow

## 🔧 Troubleshooting

### "Authentication failed"
- Check environment variables are set
- Verify Garmin credentials are correct
- Try running `python3 garmin_auth_helper.py` manually

### "Command not found: python3"
- Install Python 3.10+
- Or update workflow to use `python` instead of `python3`

### "Module not found: garth"
```bash
pip3 install garth
```

### "Token expired"
- Delete `~/.garth/` directory
- Run workflow again (will re-authenticate)

## 🎯 Workflow Nodes

| Node | Purpose |
|------|---------|
| Schedule Trigger | Runs daily at 2 AM |
| Get Garmin Auth Token | Executes Python script |
| Parse Auth Token | Extracts OAuth2 token |
| Get Update Key | Gets GarminBadges.com API key |
| Fetch Earned Badges | Gets badges from Garmin |
| Transform Earned Badges | Formats data |
| Post Earned Badges | Sends to GarminBadges.com |
| Split Badges | Processes in batches of 10 |
| Fetch Badge Details | Gets detailed info |
| Fetch Challenge Details | Gets challenge data (optional) |
| Merge Badge Data | Combines details |
| Check if All Processed | Loop control |
| Transform Final Badge Data | Final formatting |
| Post Final Badge Data | Final submission |

## 💡 Tips

- **Token lasts ~1 year**: You won't need to re-authenticate often
- **Parallel processing**: Badges are fetched 10 at a time for speed
- **Error handling**: Retired badges (404s) are handled gracefully
- **Execution history**: Check n8n's execution log for debugging

## 📚 More Info

See [README-n8n.md](file:///Users/dhlotter/Downloads/sourcecontrol/prd/script-garmin-badges-sync/README-n8n.md) for full documentation.
