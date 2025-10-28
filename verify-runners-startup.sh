#!/bin/bash

# Verify GitHub Actions Runners are running at startup
# This script checks and starts runners if they're not running

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/runner-startup.log"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log "=== GitHub Actions Runners Startup Check ==="

# Wait for Docker to be ready
log "Waiting for Docker to be available..."
timeout=300
while ! docker info >/dev/null 2>&1; do
    if [[ $timeout -le 0 ]]; then
        log "ERROR: Docker not available after 5 minutes"
        exit 1
    fi
    sleep 10
    timeout=$((timeout - 10))
done
log "Docker is available"

# Check and start user services
if systemctl --user list-unit-files github-runner-x64.service >/dev/null 2>&1; then
    if ! systemctl --user is-active github-runner-x64.service >/dev/null 2>&1; then
        log "Starting x64 runner user service..."
        systemctl --user start github-runner-x64.service
    else
        log "x64 runner is already running"
    fi
fi

if systemctl --user list-unit-files github-runner-arm64.service >/dev/null 2>&1; then
    if ! systemctl --user is-active github-runner-arm64.service >/dev/null 2>&1; then
        log "Starting ARM64 runner user service..."
        systemctl --user start github-runner-arm64.service
    else
        log "ARM64 runner is already running"
    fi
fi

# Final status check
sleep 10
log "Final status check:"
if systemctl --user list-unit-files github-runner-x64.service >/dev/null 2>&1; then
    status=$(systemctl --user is-active github-runner-x64.service 2>/dev/null || echo "unknown")
    log "x64 runner: $status"
fi

if systemctl --user list-unit-files github-runner-arm64.service >/dev/null 2>&1; then
    status=$(systemctl --user is-active github-runner-arm64.service 2>/dev/null || echo "unknown")
    log "ARM64 runner: $status"
fi

log "=== Startup check complete ==="
