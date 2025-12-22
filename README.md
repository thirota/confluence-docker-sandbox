# Confluence Docker Sandbox

A lightweight and reproducible sandbox environment for running Atlassian Confluence Data Center with Docker Compose.  
Useful for testing, plugin development, data generation, and verification before Cloud migration.

---

## Features

- Confluence Data Center (official Docker image): https://hub.docker.com/r/atlassian/confluence
- PostgreSQL: https://hub.docker.com/_/postgres
- Persistent Docker volumes
- Utility scripts:
  - run.sh — Start Confluence + PostgreSQL
  - open.sh — Open Confluence in browser
  - stop.sh — Stop running containers
  - reset.sh — Remove volumes (dangerous)
  - backup.sh — Backup Confluence & PostgreSQL volumes
  - restore.sh — Restore from latest backups

---

## Repository Structure

confluence-docker-sandbox/  
├── docker-compose.yml       # Confluence + PostgreSQL environment  
├── run.sh                   # Start services  
├── open.sh                  # Open Confluence in browser  
├── stop.sh                  # Stop services  
├── reset.sh                 # Reset volumes (dangerous)  
├── backup.sh                # Backup volumes  
├── restore.sh               # Restore volumes  
└── README.md                # This file

---

## Requirements

- Docker  
- Docker Compose plugin  
- macOS/Linux (WSL2 should work, not fully tested)

---

## Usage

### Start Confluence
```
./run.sh
```

### Check Confluence log
```
docker exec -it confluence-docker-sandbox-confluence-1 bash
tail -f /var/atlassian/application-data/confluence/logs/atlassian-confluence.log
```

### Access Confluence
Once the container is running, execute:
```
./open.sh
```
You should see the Confluence setup wizard or your restored instance.

You can get a license for testing here:

https://developer.atlassian.com/platform/marketplace/timebomb-licenses-for-testing-server-apps/

### Stop Confluence
```
./stop.sh
```

### Reset all volumes (dangerous)
```
./reset.sh
```

### Backup volumes
```
./backup.sh
```

### Restore from the latest backups
```
./restore.sh
```

---

## Notes

- Volumes are persistent unless removed with `reset.sh`.
- Backups are stored as tar.gz files in the repository directory.
- Restore script automatically finds the latest backup.

---

## Reference Links

- Confluence Release Notes: https://confluence.atlassian.com/doc/confluence-release-notes-327.html
- Atlassian End of Support Policy: https://confluence.atlassian.com/support/atlassian-end-of-support-policy-201851003.html

---

## Acknowledgements

This repository was originally forked from:  
https://github.com/collabsoft-net/example-confluence-app-with-docker-compose  
Thanks to the original authors for providing a helpful baseline.
