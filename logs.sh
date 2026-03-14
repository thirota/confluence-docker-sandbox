#!/usr/bin/env bash
docker compose exec confluence tail -f /var/atlassian/application-data/confluence/logs/atlassian-confluence.log
