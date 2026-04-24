#!/usr/bin/env bash

# This script adds cap/watchdog.py to the user's crontab to run every 5 minutes.
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WATCHDOG_SCRIPT="${PROJECT_DIR}/cap/watchdog.py"
LOG_FILE="${PROJECT_DIR}/watchdog.log"

CRON_JOB="*/5 * * * * /usr/bin/env python3 ${WATCHDOG_SCRIPT} >> ${LOG_FILE} 2>&1"

# Check if the cron job already exists
if crontab -l 2>/dev/null | grep -q "${WATCHDOG_SCRIPT}"; then
    echo "Watchdog cron job already exists."
else
    # Append the new cron job
    (crontab -l 2>/dev/null; echo "${CRON_JOB}") | crontab -
    echo "Successfully added watchdog cron job."
fi

# Make the python script executable
chmod +x "${WATCHDOG_SCRIPT}"
