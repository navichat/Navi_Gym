#!/bin/bash

# GitHub Actions Runners Auto-Start Script
# This script ensures runners are configured to start automatically on boot

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${CYAN}================================${NC}"
    echo -e "${CYAN} $1${NC}"
    echo -e "${CYAN}================================${NC}"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    print_error "This script should not be run as root"
    print_status "Run as your regular user account"
    exit 1
fi

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNNER_USER=$(whoami)
X64_RUNNER_PATH="$SCRIPT_DIR/actions-runner"
ARM64_RUNNER_PATH="$SCRIPT_DIR/actions-runner-arm64"

print_header "GitHub Actions Runners Auto-Start Setup"

# Function to check if Docker is in user's groups
check_docker_access() {
    if groups $RUNNER_USER | grep -q '\bdocker\b'; then
        print_success "User $RUNNER_USER is in docker group"
        return 0
    else
        print_warning "User $RUNNER_USER is not in docker group"
        print_status "Adding user to docker group..."
        sudo usermod -aG docker $RUNNER_USER
        print_warning "You may need to logout and login again for group changes to take effect"
        return 1
    fi
}

# Function to ensure systemd lingering is enabled
enable_systemd_lingering() {
    print_status "Enabling systemd lingering for user $RUNNER_USER..."
    sudo loginctl enable-linger $RUNNER_USER
    print_success "Systemd lingering enabled - user services will start at boot"
}

# Function to create systemd user services
create_user_services() {
    print_status "Creating user systemd services..."
    
    # Create user systemd directory
    mkdir -p ~/.config/systemd/user
    
    # Create x64 user service
    if [[ -d "$X64_RUNNER_PATH" ]]; then
        print_status "Creating x64 runner user service..."
        cat > ~/.config/systemd/user/github-runner-x64.service << EOF
[Unit]
Description=GitHub Actions Runner (x64)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=$X64_RUNNER_PATH
ExecStartPre=/bin/bash -c 'until systemctl --user is-active network-online.target; do sleep 5; done'
ExecStartPre=/bin/bash -c 'until docker info; do echo "Waiting for Docker..."; sleep 10; done'
ExecStart=$X64_RUNNER_PATH/run.sh
Restart=always
RestartSec=15
TimeoutStartSec=300

# Environment
Environment=DOCKER_HOST=unix:///var/run/docker.sock
Environment=HOME=$HOME
Environment=USER=$RUNNER_USER
Environment=PYTHONPATH=/workspace/navi-gym

# Resource limits
MemoryMax=8G
TasksMax=4096

# Logging
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
EOF
    fi
    
    # Create ARM64 user service
    if [[ -d "$ARM64_RUNNER_PATH" ]]; then
        print_status "Creating ARM64 runner user service..."
        cat > ~/.config/systemd/user/github-runner-arm64.service << EOF
[Unit]
Description=GitHub Actions Runner (ARM64)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=$ARM64_RUNNER_PATH
ExecStartPre=/bin/bash -c 'until systemctl --user is-active network-online.target; do sleep 5; done'
ExecStartPre=/bin/bash -c 'until docker info; do echo "Waiting for Docker..."; sleep 10; done'
ExecStart=$ARM64_RUNNER_PATH/run.sh
Restart=always
RestartSec=15
TimeoutStartSec=300

# Environment
Environment=DOCKER_HOST=unix:///var/run/docker.sock
Environment=HOME=$HOME
Environment=USER=$RUNNER_USER
Environment=PYTHONPATH=/workspace/navi-gym

# Resource limits
MemoryMax=8G
TasksMax=4096

# Logging
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
EOF
    fi
    
    # Reload user daemon
    systemctl --user daemon-reload
    
    # Enable services to start automatically
    if [[ -d "$X64_RUNNER_PATH" && -f "$X64_RUNNER_PATH/.runner" ]]; then
        systemctl --user enable github-runner-x64.service
        print_success "x64 runner user service enabled"
    fi
    
    if [[ -d "$ARM64_RUNNER_PATH" && -f "$ARM64_RUNNER_PATH/.runner" ]]; then
        systemctl --user enable github-runner-arm64.service
        print_success "ARM64 runner user service enabled"
    fi
}

# Function to create startup script
create_startup_script() {
    print_status "Creating startup verification script..."
    
    cat > "$SCRIPT_DIR/verify-runners-startup.sh" << 'EOF'
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
EOF

    chmod +x "$SCRIPT_DIR/verify-runners-startup.sh"
    print_success "Startup verification script created"
}

# Function to create desktop autostart entry
create_autostart_entry() {
    print_status "Creating desktop autostart entry..."
    
    # Create autostart directory
    mkdir -p ~/.config/autostart
    
    # Create autostart desktop file
    cat > ~/.config/autostart/github-runners.desktop << EOF
[Desktop Entry]
Type=Application
Name=GitHub Actions Runners
Comment=Start GitHub Actions Runners for Navi Gym
Exec=$SCRIPT_DIR/verify-runners-startup.sh
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
StartupNotify=false
EOF

    print_success "Desktop autostart entry created"
}

# Function to create cron job as backup
create_cron_backup() {
    print_status "Creating cron job as backup startup method..."
    
    # Add cron job to check runners every 5 minutes
    (crontab -l 2>/dev/null; echo "*/5 * * * * $SCRIPT_DIR/verify-runners-startup.sh >/dev/null 2>&1") | crontab -
    
    print_success "Cron job created for runner monitoring"
}

# Function to check system prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check if runners are configured
    local configured_runners=0
    
    if [[ -f "$X64_RUNNER_PATH/.runner" ]]; then
        print_success "x64 runner is configured"
        configured_runners=$((configured_runners + 1))
    else
        print_warning "x64 runner is not configured"
    fi
    
    if [[ -f "$ARM64_RUNNER_PATH/.runner" ]]; then
        print_success "ARM64 runner is configured"
        configured_runners=$((configured_runners + 1))
    else
        print_warning "ARM64 runner is not configured"
    fi
    
    if [[ $configured_runners -eq 0 ]]; then
        print_error "No runners are configured!"
        print_status "Please run the configure-runner scripts first:"
        print_status "  cd $X64_RUNNER_PATH && ./configure-runner.sh"
        print_status "  cd $ARM64_RUNNER_PATH && ./configure-runner-arm64.sh"
        exit 1
    fi
    
    # Check Docker access
    check_docker_access
    
    # Check systemd version
    local systemd_version=$(systemctl --version | head -1 | awk '{print $2}')
    print_status "Systemd version: $systemd_version"
    
    print_success "Prerequisites check completed"
}

# Function to show final status
show_final_status() {
    print_header "Auto-Start Configuration Complete"
    
    echo "The following auto-start methods have been configured:"
    echo
    echo "1. Systemd User Services:"
    if systemctl --user list-unit-files github-runner-x64.service >/dev/null 2>&1; then
        echo "   ✓ x64 runner: systemctl --user status github-runner-x64.service"
    fi
    if systemctl --user list-unit-files github-runner-arm64.service >/dev/null 2>&1; then
        echo "   ✓ ARM64 runner: systemctl --user status github-runner-arm64.service"
    fi
    echo
    
    echo "2. Desktop Autostart:"
    echo "   ✓ ~/.config/autostart/github-runners.desktop"
    echo
    
    echo "3. Cron Job Monitoring:"
    echo "   ✓ Checks runners every 5 minutes"
    echo
    
    echo "4. Management Commands:"
    echo "   ✓ ./manage-runners.sh status    # Check runner status"
    echo "   ✓ ./manage-runners.sh start     # Start runners manually"
    echo "   ✓ ./manage-runners.sh logs      # View runner logs"
    echo
    
    echo "Logs:"
    echo "   ✓ Runner startup: $SCRIPT_DIR/runner-startup.log"
    echo "   ✓ Service logs: journalctl --user -u github-runner-x64.service"
    echo "   ✓ Service logs: journalctl --user -u github-runner-arm64.service"
    echo
    
    print_success "Runners will now start automatically on system boot!"
    print_warning "Note: You may need to logout and login again for all changes to take effect"
}

# Main setup function
main() {
    case "${1:-setup}" in
        "setup")
            check_prerequisites
            enable_systemd_lingering
            create_user_services
            create_startup_script
            create_autostart_entry
            create_cron_backup
            show_final_status
            ;;
        "check")
            check_prerequisites
            ;;
        "verify")
            "$SCRIPT_DIR/verify-runners-startup.sh"
            ;;
        "help"|"-h"|"--help")
            cat << EOF
GitHub Actions Runners Auto-Start Setup

Usage: $0 [COMMAND]

Commands:
  setup                  Complete auto-start setup (default)
  check                  Check prerequisites only
  verify                 Run startup verification
  help                   Show this help

This script will:
1. Enable systemd lingering for the current user
2. Create user systemd services for both runners
3. Set up desktop autostart
4. Create cron job backup
5. Configure automatic startup verification

EOF
            ;;
        *)
            print_error "Unknown command: $1"
            print_status "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"