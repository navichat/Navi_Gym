#!/bin/bash

# Navi Gym CI/CD Quick Setup Script
# This script helps set up the complete CI/CD environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Docker installation
check_docker() {
    if command_exists docker; then
        if docker info >/dev/null 2>&1; then
            print_success "Docker is installed and running"
            docker --version
        else
            print_error "Docker is installed but not running"
            print_status "Please start Docker service: sudo systemctl start docker"
            return 1
        fi
    else
        print_error "Docker is not installed"
        print_status "Please install Docker first: https://docs.docker.com/install/"
        return 1
    fi
}

# Function to check Docker Compose
check_docker_compose() {
    if command_exists docker-compose || docker compose version >/dev/null 2>&1; then
        print_success "Docker Compose is available"
        if command_exists docker-compose; then
            docker-compose --version
        else
            docker compose version
        fi
    else
        print_warning "Docker Compose not found, but Docker may have built-in compose"
    fi
}

# Function to check system requirements
check_system_requirements() {
    print_status "Checking system requirements..."
    
    # Check available memory
    available_mem=$(free -g | awk '/^Mem:/{print $7}')
    total_mem=$(free -g | awk '/^Mem:/{print $2}')
    print_status "Available memory: ${available_mem}GB / ${total_mem}GB"
    
    if [[ $available_mem -lt 4 ]]; then
        print_warning "Low available memory. Recommended: 8GB+ for optimal performance"
    fi
    
    # Check available disk space
    available_disk=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
    print_status "Available disk space: ${available_disk}GB"
    
    if [[ $available_disk -lt 20 ]]; then
        print_warning "Low disk space. Recommended: 50GB+ for Docker images and test artifacts"
    fi
    
    # Check for GPU
    if command_exists nvidia-smi; then
        print_success "NVIDIA GPU detected"
        nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits | head -1
    elif lspci | grep -i amd | grep -i vga >/dev/null; then
        print_success "AMD GPU detected"
    else
        print_status "No GPU detected (CPU-only mode)"
    fi
}

# Function to build Docker images
build_docker_images() {
    print_status "Building Docker images..."
    
    if [[ -f "scripts/build-docker.sh" ]]; then
        chmod +x scripts/build-docker.sh
        print_status "Using build script..."
        ./scripts/build-docker.sh --name navi-gym --tag latest
    elif [[ -f "Makefile" ]]; then
        print_status "Using Makefile..."
        make build
    elif [[ -f "docker-compose.yml" ]]; then
        print_status "Using Docker Compose..."
        if command_exists docker-compose; then
            docker-compose build navi-gym
        else
            docker compose build navi-gym
        fi
    else
        print_status "Building manually..."
        if [[ -f "docker/Dockerfile" ]]; then
            docker build -f docker/Dockerfile -t navi-gym:latest .
        else
            print_error "No Dockerfile found"
            return 1
        fi
    fi
    
    print_success "Docker images built successfully"
}

# Function to run smoke tests
run_smoke_tests() {
    print_status "Running smoke tests..."
    
    if [[ -f "scripts/run-tests.sh" ]]; then
        chmod +x scripts/run-tests.sh
        ./scripts/run-tests.sh --image navi-gym:latest --suite smoke
    else
        # Manual smoke test
        print_status "Running manual smoke test..."
        docker run --rm navi-gym:latest python -c "
import sys
print(f'Python version: {sys.version}')

# Test core imports
try:
    import numpy as np
    import torch
    import scipy
    print('✓ Core dependencies imported successfully')
except ImportError as e:
    print(f'✗ Core import failed: {e}')
    sys.exit(1)

# Test Genesis import
try:
    import genesis as gs
    print('✓ Genesis imported successfully')
except ImportError as e:
    print(f'⚠ Genesis import failed: {e}')

print('✓ Smoke test completed successfully')
"
    fi
    
    print_success "Smoke tests passed"
}

# Function to set up self-hosted runner
setup_runner() {
    print_status "Setting up GitHub Actions self-hosted runner..."
    
    if [[ ! -d "actions-runner" ]]; then
        print_error "Actions runner directory not found"
        print_status "Please run the GitHub Actions runner setup first"
        return 1
    fi
    
    cd actions-runner
    
    if [[ ! -f "configure-runner.sh" ]]; then
        print_error "Runner configuration script not found"
        return 1
    fi
    
    if [[ -z "$GITHUB_TOKEN" ]]; then
        print_error "GITHUB_TOKEN environment variable is required"
        print_status "Please set your GitHub token:"
        print_status "export GITHUB_TOKEN=\"your_github_token_here\""
        return 1
    fi
    
    chmod +x configure-runner.sh
    ./configure-runner.sh
    
    cd ..
    print_success "Self-hosted runner configured"
}

# Function to validate CI/CD setup
validate_setup() {
    print_status "Validating CI/CD setup..."
    
    # Check workflow files
    if [[ -f ".github/workflows/test-ci.yml" ]]; then
        print_success "Test CI workflow found"
    else
        print_warning "Test CI workflow not found"
    fi
    
    if [[ -f ".github/workflows/docker-ci.yml" ]]; then
        print_success "Docker CI workflow found"
    else
        print_warning "Docker CI workflow not found"
    fi
    
    # Check test configuration
    if [[ -f "tests/conftest.py" ]]; then
        print_success "Pytest configuration found"
    else
        print_warning "Pytest configuration not found"
    fi
    
    # Check Docker configuration
    if [[ -f "docker-compose.yml" ]]; then
        print_success "Docker Compose configuration found"
    else
        print_warning "Docker Compose configuration not found"
    fi
    
    # Check scripts
    if [[ -f "scripts/run-tests.sh" ]]; then
        print_success "Test runner script found"
    else
        print_warning "Test runner script not found"
    fi
    
    if [[ -f "Makefile" ]]; then
        print_success "Makefile found"
    else
        print_warning "Makefile not found"
    fi
    
    print_success "Setup validation completed"
}

# Function to display usage help
show_help() {
    cat << EOF
Navi Gym CI/CD Quick Setup Script

Usage: $0 [COMMAND]

Commands:
    check       Check system requirements and dependencies
    build       Build Docker images for testing
    test        Run smoke tests to validate setup
    runner      Set up GitHub Actions self-hosted runner
    validate    Validate CI/CD configuration
    all         Run all setup steps (default)
    help        Show this help message

Environment Variables:
    GITHUB_TOKEN    Required for setting up self-hosted runner

Examples:
    # Full setup
    $0 all

    # Check requirements only
    $0 check

    # Build and test
    $0 build
    $0 test

    # Set up runner (requires GITHUB_TOKEN)
    export GITHUB_TOKEN="your_token_here"
    $0 runner

    # Validate configuration
    $0 validate

EOF
}

# Main execution
main() {
    local command="${1:-all}"
    
    print_status "Navi Gym CI/CD Quick Setup"
    print_status "============================="
    
    case "$command" in
        "check")
            check_docker
            check_docker_compose
            check_system_requirements
            ;;
        "build")
            check_docker || exit 1
            build_docker_images
            ;;
        "test")
            run_smoke_tests
            ;;
        "runner")
            setup_runner
            ;;
        "validate")
            validate_setup
            ;;
        "all")
            print_status "Running complete setup..."
            check_docker || exit 1
            check_docker_compose
            check_system_requirements
            build_docker_images
            run_smoke_tests
            validate_setup
            
            print_success "Complete setup finished!"
            print_status ""
            print_status "Next steps:"
            print_status "1. Set up self-hosted runner: export GITHUB_TOKEN=<token> && $0 runner"
            print_status "2. Run full tests: make test"
            print_status "3. Check CI/CD documentation: CI_CD_DOCUMENTATION.md"
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            print_error "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"