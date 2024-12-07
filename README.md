# Garmin Badges Sync

A Docker-based application to sync Garmin badges and activities.

## Server Deployment

### 1. Clone the Repository
```bash
git clone https://github.com/dhlotter/garmin-badges-sync.git
cd garmin-badges-sync
```

### 2. Set Up Environment
Create and configure your `.env` file:
```bash
cp .env.example .env
nano .env  # or use your preferred text editor
```

### 3. Deploy with Docker
Build and start the container:
```bash
docker compose build
docker compose up -d
```

### 4. Schedule Regular Syncs
Add to crontab to run daily:
```bash
# Edit crontab
crontab -e

# Add this line to run daily at 2 AM
0 2 * * * cd /path/to/garmin-badges-sync && docker compose restart
```

## Monitoring

View logs:
```bash
docker compose logs -f
```

Check container status:
```bash
docker compose ps
```

Stop the service:
```bash
docker compose down
```

## Requirements

- Git
- Docker and Docker Compose
- Cron (for scheduling)

## Troubleshooting

1. Check container logs:
```bash
docker compose logs -f
```

2. Verify environment variables:
```bash
docker compose config
```

3. Restart the container:
```bash
docker compose restart
```

4. Full rebuild if needed:
```bash
docker compose down
docker compose build --no-cache
docker compose up -d
```

## Security Notes

- Keep your `.env` file secure and never commit it to Git
- Use appropriate file permissions for the `.env` file (600)
- Regularly update your Docker images for security patches

## License

[MIT License](LICENSE)