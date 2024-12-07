# Garmin Badges Sync

## Overview
This script synchronizes badges from Garmin Connect to Garmin Badges, providing an automated way to track and update your earned achievements.

## Features
- Authenticate with Garmin Connect
- Retrieve earned badges
- Upload badges to Garmin Badges
- Robust error handling and retry mechanisms
- Multiple authentication strategies

## Prerequisites
- Python 3.8+
- Garmin Connect account
- Garmin Badges account

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/garmin-badges-sync.git
cd garmin-badges-sync
```

### 2. Create a Virtual Environment (Optional but Recommended)
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## Configuration

### Environment Variables
Create a `.env` file in the project root with the following variables:
```
GARMIN_CONNECT_USERNAME=your_garmin_connect_email
GARMIN_CONNECT_PASSWORD=your_garmin_connect_password
GARMIN_BADGES_USERNAME=your_garmin_badges_username
GARMIN_BADGES_EMAIL=your_garmin_badges_email
```

## Usage

### Running the Script
```bash
python sync.py
```

### Command Line Arguments
- `--V`: Enable verbose/debug mode
- `--garmin`: Open Garmin Connect badges page
- `--garminbadges`: Open Garmin Badges website

## Troubleshooting
- Check `garmin_sync.log` for detailed error logs
- Ensure your Garmin Connect credentials are correct
- Verify network connectivity
- Be aware of Garmin's rate limiting policies

## Security Notes
- Never commit your `.env` file to version control
- Use strong, unique passwords
- Consider using environment-specific configurations

## Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License
Distributed under the MIT License. See `LICENSE` for more information.

## Contact
Your Name - your.email@example.com

Project Link: [https://github.com/yourusername/garmin-badges-sync](https://github.com/yourusername/garmin-badges-sync)



# Things on the ToDo list
1. create working script to sync garmin connect reliably to garmin badges
2. action 
3. action 
4. action

## links 
- https://connect.garmin.com/modern/badges
- https://garminbadges.com/