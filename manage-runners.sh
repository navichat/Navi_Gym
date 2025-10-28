#!/bin/bash

# GitHub Actions Runners Management Script for Navi Gym
# This script manages both x64 and ARM64 runners with systemd integration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Runner configurations
X64_RUNNER_NAME="navi-gym-runner-$(hostname)"
ARM64_RUNNER_NAME="navi-gym-runner-arm64-$(hostname)"
X64_SERVICE="actions.runner.navichat-Navi_Gym.$X64_RUNNER_NAME.service"
ARM64_SERVICE="actions.runner.navichat-Navi_Gym.$ARM64_RUNNER_NAME.service"

# Function to check if Docker is available
check_docker() {
    if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to check service status
check_service_status() {
    local service_name=$1
    local runner_type=$2
    
    if systemctl list-units --full -all | grep -q "$service_name"; then
        local status=$(systemctl is-active "$service_name" 2>/dev/null || echo "unknown")
        local enabled=$(systemctl is-enabled "$service_name" 2>/dev/null || echo "unknown")
        
        echo -e "  ${runner_type} Runner:"
        echo -e "    Service: $service_name"
        echo -e "    Status:  $status"
        echo -e "    Enabled: $enabled"
        
        if [[ "$status" == "active" ]]; then
            echo -e "    ${GREEN}✓ Running${NC}"
        else
            echo -e "    ${RED}✗ Not running${NC}"
        fi
    else
        echo -e "  ${runner_type} Runner: ${YELLOW}Not configured${NC}"
    fi
    echo
}

# Function to create enhanced systemd override
create_enhanced_override() {
    local runner_path=$1
    local service_name=$2
    local runner_type=$3
    
    print_status "Creating enhanced systemd override for $runner_type runner..."
    
    # Create override directory
    sudo mkdir -p "/etc/systemd/system/$service_name.d"
    
    # Create enhanced override configuration
    sudo tee "/etc/systemd/system/$service_name.d/override.conf" > /dev/null << EOF
[Unit]
Description=GitHub Actions Runner (Navi Gym - $runner_type)
After=network-online.target docker.service
Wants=network-online.target docker.service
StartLimitIntervalSec=500
StartLimitBurst=5

[Service]
# Working directory
WorkingDirectory=$runner_path

# User and group
User=$USER
Group=$USER

# Pre-start checks
ExecStartPre=/bin/bash -c 'echo "Starting $runner_type runner..."'
ExecStartPre=/bin/bash -c 'until systemctl is-active network-online.target; do sleep 2; done'
ExecStartPre=/bin/bash -c 'until docker info; do echo "Waiting for Docker..."; sleep 5; done'

# Resource limits
LimitNOFILE=65536
LimitNPROC=32768
MemoryMax=12G
TasksMax=8192

# Environment variables
Environment=DOCKER_HOST=unix:///var/run/docker.sock
Environment=PYTHONPATH=/workspace/navi-gym
Environment=TI_OFFLINE_CACHE=1
Environment=HOME=$HOME
Environment=USER=$USER
Environment=RUNNER_ALLOW_RUNASROOT=1

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=read-only
ReadWritePaths=$runner_path

# Restart policy
Restart=always
RestartSec=10
TimeoutStartSec=300
TimeoutStopSec=30

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=github-runner-$runner_type

[Install]
WantedBy=multi-user.target
EOF

    print_success "Enhanced systemd override created for $runner_type runner"
}

# Function to configure a runner for systemd
setup_runner_systemd() {
    local runner_dir=$1
    local runner_type=$2
    
    if [[ ! -d "$runner_dir" ]]; then
        print_warning "$runner_type runner directory not found: $runner_dir"
        return 1
    fi
    
    print_status "Setting up systemd integration for $runner_type runner..."
    
    cd "$runner_dir"
    
    # Check if runner is configured
    if [[ ! -f ".runner" ]]; then
        print_warning "$runner_type runner not configured yet. Run configure-runner script first."
        return 1
    fi
    
    # Install systemd service
    print_status "Installing systemd service for $runner_type runner..."
    sudo ./svc.sh install || {
        print_error "Failed to install systemd service for $runner_type runner"
        return 1
    }
    
    # Get the service name
    local service_name
    if [[ "$runner_type" == "ARM64" ]]; then
        service_name="$ARM64_SERVICE"
    else
        service_name="$X64_SERVICE"
    fi
    
    # Create enhanced override
    create_enhanced_override "$(pwd)" "$service_name" "$runner_type"
    
    # Reload systemd and enable service
    sudo systemctl daemon-reload
    sudo systemctl enable "$service_name"
    
    # Start the service
    print_status "Starting $runner_type runner service..."
    sudo systemctl start "$service_name"
    
    # Verify startup
    sleep 5
    if systemctl is-active "$service_name" >/dev/null 2>&1; then
        print_success "$runner_type runner service started successfully!"
    else
        print_error "$runner_type runner service failed to start"
        print_status "Checking logs..."
        sudo journalctl -u "$service_name" --no-pager -n 20
        return 1
    fi
    
    cd - >/dev/null
}

# Function to show comprehensive status
show_status() {
    print_header "GitHub Actions Runners Status"
    
    echo "Repository: navichat/Navi_Gym"
    echo "Hostname: $(hostname)"
    echo
    
    # Check Docker
    if check_docker; then
        echo -e "Docker: ${GREEN}✓ Available${NC}"
    else
        echo -e "Docker: ${RED}✗ Not available${NC}"
    fi
    echo
    
    # Check services
    print_status "Service Status:"
    check_service_status "$X64_SERVICE" "x64"
    check_service_status "$ARM64_SERVICE" "ARM64"
    
    # System resources
    print_status "System Resources:"
    echo "  Memory: $(free -h | grep '^Mem:' | awk '{print $3 "/" $2 " (" $5 " used)"}')"
    echo "  Disk: $(df -h / | tail -1 | awk '{print $3 "/" $2 " (" $5 " used)"}')"
    echo "  Load: $(uptime | cut -d',' -f3-)"
    echo "  Architecture: $(uname -m)"
    echo
}

# Function to show logs
show_logs() {
    local runner_type=${1:-"both"}
    
    case $runner_type in
        "x64")
            print_header "x64 Runner Logs"
            sudo journalctl -u "$X64_SERVICE" --no-pager -n 30
            ;;
        "arm64")
            print_header "ARM64 Runner Logs"
            sudo journalctl -u "$ARM64_SERVICE" --no-pager -n 30
            ;;
        "both"|*)
            print_header "x64 Runner Logs"
            sudo journalctl -u "$X64_SERVICE" --no-pager -n 15
            echo
            print_header "ARM64 Runner Logs"
            sudo journalctl -u "$ARM64_SERVICE" --no-pager -n 15
            ;;
    esac
}

# Function to control services
control_service() {
    local action=$1
    local runner_type=${2:-"both"}
    
    case $runner_type in
        "x64")
            print_status "${action^}ing x64 runner..."
            sudo systemctl "$action" "$X64_SERVICE"
            ;;
        "arm64")
            print_status "${action^}ing ARM64 runner..."
            sudo systemctl "$action" "$ARM64_SERVICE"
            ;;
        "both"|*)
            print_status "${action^}ing both runners..."
            sudo systemctl "$action" "$X64_SERVICE" "$ARM64_SERVICE"
            ;;
    esac
    
    sleep 2
    show_status
}

# Function to setup both runners
setup_both_runners() {
    print_header "Setting up systemd for both runners"
    
    # Check for GitHub token
    if [[ -z "$GITHUB_TOKEN" ]]; then
        print_error "GITHUB_TOKEN environment variable is required"
        print_status "Please set your GitHub token:"
        print_status "export GITHUB_TOKEN=\"your_github_token_here\""
        exit 1
    fi
    
    print_status "Setting up x64 runner..."
    if setup_runner_systemd "./actions-runner" "x64"; then
        print_success "x64 runner systemd setup complete"
    else
        print_error "x64 runner systemd setup failed"
    fi
    
    echo
    print_status "Setting up ARM64 runner..."
    if setup_runner_systemd "./actions-runner-arm64" "ARM64"; then
        print_success "ARM64 runner systemd setup complete"
    else
        print_error "ARM64 runner systemd setup failed"
    fi
    
    echo
    print_header "Setup Complete"
    show_status
}

# Function to create systemd user service (alternative approach)
create_user_service() {
    local runner_type=${1:-"both"}
    
    print_header "Creating user systemd services"
    
    # Create user systemd directory
    mkdir -p ~/.config/systemd/user
    
    if [[ "$runner_type" == "x64" || "$runner_type" == "both" ]]; then
        print_status "Creating x64 user service..."
        cat > ~/.config/systemd/user/github-runner-x64.service << EOF
[Unit]
Description=GitHub Actions Runner (x64)
After=network-online.target docker.service
Wants=network-online.target

[Service]
Type=simple
User=%i
WorkingDirectory=/home/barberb/Navi_Gym/actions-runner
ExecStart=/home/barberb/Navi_Gym/actions-runner/run.sh
Restart=always
RestartSec=10
Environment=DOCKER_HOST=unix:///var/run/docker.sock

[Install]
WantedBy=default.target
EOF
    fi
    
    if [[ "$runner_type" == "arm64" || "$runner_type" == "both" ]]; then
        print_status "Creating ARM64 user service..."
        cat > ~/.config/systemd/user/github-runner-arm64.service << EOF
[Unit]
Description=GitHub Actions Runner (ARM64)
After=network-online.target docker.service
Wants=network-online.target

[Service]
Type=simple
User=%i
WorkingDirectory=/home/barberb/Navi_Gym/actions-runner-arm64
ExecStart=/home/barberb/Navi_Gym/actions-runner-arm64/run.sh
Restart=always
RestartSec=10
Environment=DOCKER_HOST=unix:///var/run/docker.sock

[Install]
WantedBy=default.target
EOF
    fi
    
    # Reload user daemon
    systemctl --user daemon-reload
    
    # Enable services
    if [[ "$runner_type" == "x64" || "$runner_type" == "both" ]]; then
        systemctl --user enable github-runner-x64.service
    fi
    if [[ "$runner_type" == "arm64" || "$runner_type" == "both" ]]; then
        systemctl --user enable github-runner-arm64.service
    fi
    
    print_success "User services created and enabled"
    print_status "To start: systemctl --user start github-runner-x64.service"
    print_status "To start: systemctl --user start github-runner-arm64.service"
}

# Main function
main() {
    case "${1:-status}" in
        "status"|"st")
            show_status
            ;;
        "logs"|"log")
            show_logs "$2"
            ;;
        "start")
            control_service "start" "$2"
            ;;
        "stop")
            control_service "stop" "$2"
            ;;
        "restart")
            control_service "restart" "$2"
            ;;
        "setup")
            setup_both_runners
            ;;
        "user-service")
            create_user_service "$2"
            ;;
        "help"|"-h"|"--help")
            cat << EOF
GitHub Actions Runners Management Script

Usage: $0 [COMMAND] [RUNNER_TYPE]

Commands:
  status, st              Show runners status (default)
  logs, log              Show runners logs
  start                  Start runners
  stop                   Stop runners
  restart                Restart runners
  setup                  Setup systemd for both runners
  user-service           Create user systemd services
  help                   Show this help

Runner Types (optional):
  x64                    Target x64 runner only
  arm64                  Target ARM64 runner only
  both                   Target both runners (default)

Examples:
  $0 status              # Show status of both runners
  $0 logs arm64          # Show ARM64 runner logs
  $0 restart x64         # Restart only x64 runner
  $0 setup               # Setup systemd for both runners

Environment:
  GITHUB_TOKEN           Required for setup command

EOF
            ;;
        *)
            print_error "Unknown command: $1"
            print_status "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"