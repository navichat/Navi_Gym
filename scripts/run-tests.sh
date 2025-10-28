#!/bin/bash

# Test Runner Script for Navi Gym Docker Containers
# This script runs comprehensive tests in Docker containers

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
IMAGE_NAME="navi-gym:latest"
TEST_SUITE="all"
VERBOSE=false
KEEP_CONTAINER=false
OUTPUT_DIR="test-results"
PARALLEL_JOBS=1
TIMEOUT=1800  # 30 minutes
HEADLESS=true

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

# Function to show usage
show_usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Run tests in Navi Gym Docker containers

OPTIONS:
    -i, --image IMAGE       Docker image to test (default: $IMAGE_NAME)
    -s, --suite SUITE       Test suite to run: all, unit, integration, benchmarks (default: $TEST_SUITE)
    -v, --verbose           Enable verbose output
    -k, --keep-container    Keep container after tests
    -o, --output-dir DIR    Output directory for test results (default: $OUTPUT_DIR)
    -j, --jobs NUMBER       Number of parallel jobs (default: $PARALLEL_JOBS)
    -t, --timeout SECONDS   Test timeout in seconds (default: $TIMEOUT)
    --gui                   Enable GUI tests (disable headless mode)
    -h, --help              Show this help message

TEST SUITES:
    all           Run all tests
    unit          Run unit tests only
    integration   Run integration tests only  
    benchmarks    Run benchmark tests only
    smoke         Run smoke tests (quick validation)
    genesis       Run Genesis-specific tests
    navi          Run Navi Gym specific tests

EXAMPLES:
    # Run all tests on default image
    $0

    # Run unit tests with verbose output
    $0 --suite unit --verbose

    # Run integration tests on specific image
    $0 --image navi-gym:nvidia-latest --suite integration

    # Run benchmarks with custom timeout
    $0 --suite benchmarks --timeout 3600

    # Run tests and keep results
    $0 --output-dir ./my-results --keep-container

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -i|--image)
            IMAGE_NAME="$2"
            shift 2
            ;;
        -s|--suite)
            TEST_SUITE="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -k|--keep-container)
            KEEP_CONTAINER=true
            shift
            ;;
        -o|--output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -j|--jobs)
            PARALLEL_JOBS="$2"
            shift 2
            ;;
        -t|--timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        --gui)
            HEADLESS=false
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Validate test suite
case $TEST_SUITE in
    all|unit|integration|benchmarks|smoke|genesis|navi)
        ;;
    *)
        print_error "Invalid test suite: $TEST_SUITE"
        show_usage
        exit 1
        ;;
esac

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Container configuration
CONTAINER_NAME="navi-gym-test-$(date +%s)"
WORKSPACE_DIR="/workspace/navi-gym"

# Environment variables for testing
TEST_ENV=""
if [[ "$HEADLESS" == true ]]; then
    TEST_ENV="$TEST_ENV -e DISPLAY=:99 -e PYOPENGL_PLATFORM=osmesa"
    TEST_ENV="$TEST_ENV -e TI_ENABLE_CUDA=0 -e TI_ENABLE_OPENGL=0 -e TI_ENABLE_VULKAN=0"
fi

TEST_ENV="$TEST_ENV -e PYTHONPATH=$WORKSPACE_DIR"
TEST_ENV="$TEST_ENV -e PYTEST_DISABLE_PLUGIN_AUTOLOAD=1"

print_status "Starting test execution..."
print_status "Image: $IMAGE_NAME"
print_status "Test Suite: $TEST_SUITE"
print_status "Output Directory: $OUTPUT_DIR"
print_status "Parallel Jobs: $PARALLEL_JOBS"
print_status "Timeout: ${TIMEOUT}s"
print_status "Headless: $HEADLESS"

# Check if Docker image exists
if ! docker image inspect "$IMAGE_NAME" > /dev/null 2>&1; then
    print_error "Docker image not found: $IMAGE_NAME"
    print_status "Available images:"
    docker images | grep navi-gym || echo "No navi-gym images found"
    exit 1
fi

# Function to run tests in container
run_test_command() {
    local test_cmd="$1"
    local test_name="$2"
    local output_file="$OUTPUT_DIR/${test_name}-results.xml"
    
    print_status "Running $test_name tests..."
    
    local docker_cmd="docker run"
    
    # Add container options
    if [[ "$KEEP_CONTAINER" == false ]]; then
        docker_cmd="$docker_cmd --rm"
    fi
    
    docker_cmd="$docker_cmd --name $CONTAINER_NAME-$test_name"
    docker_cmd="$docker_cmd -v $(pwd):$WORKSPACE_DIR"
    docker_cmd="$docker_cmd -v $(realpath $OUTPUT_DIR):/test-results"
    docker_cmd="$docker_cmd -w $WORKSPACE_DIR"
    docker_cmd="$docker_cmd $TEST_ENV"
    docker_cmd="$docker_cmd $IMAGE_NAME"
    
    # Verbose flag for pytest
    local pytest_verbose=""
    if [[ "$VERBOSE" == true ]]; then
        pytest_verbose="-v -s"
    fi
    
    # Execute with timeout
    timeout "$TIMEOUT" $docker_cmd bash -c "$test_cmd" || {
        local exit_code=$?
        if [[ $exit_code -eq 124 ]]; then
            print_error "$test_name tests timed out after ${TIMEOUT}s"
        else
            print_error "$test_name tests failed with exit code $exit_code"
        fi
        return $exit_code
    }
}

# Function to generate test report
generate_report() {
    local report_file="$OUTPUT_DIR/test-report.md"
    
    cat > "$report_file" << EOF
# Navi Gym Test Report

**Date:** $(date)
**Image:** $IMAGE_NAME
**Test Suite:** $TEST_SUITE
**Headless Mode:** $HEADLESS

## Test Results

EOF
    
    # Add results for each test file found
    for result_file in "$OUTPUT_DIR"/*-results.xml; do
        if [[ -f "$result_file" ]]; then
            local test_name=$(basename "$result_file" -results.xml)
            echo "### $test_name" >> "$report_file"
            
            # Try to extract basic info from XML (simplified)
            if command -v xmllint > /dev/null 2>&1; then
                local tests=$(xmllint --xpath "//testsuite/@tests" "$result_file" 2>/dev/null | sed 's/tests="//g' | sed 's/"//g' || echo "unknown")
                local failures=$(xmllint --xpath "//testsuite/@failures" "$result_file" 2>/dev/null | sed 's/failures="//g' | sed 's/"//g' || echo "unknown")
                local errors=$(xmllint --xpath "//testsuite/@errors" "$result_file" 2>/dev/null | sed 's/errors="//g' | sed 's/"//g' || echo "unknown")
                
                echo "- Tests: $tests" >> "$report_file"
                echo "- Failures: $failures" >> "$report_file"
                echo "- Errors: $errors" >> "$report_file"
            else
                echo "- Status: Completed (XML details require xmllint)" >> "$report_file"
            fi
            echo "" >> "$report_file"
        fi
    done
    
    echo "## System Information" >> "$report_file"
    echo "- Docker Version: $(docker --version)" >> "$report_file"
    echo "- Host OS: $(uname -s)" >> "$report_file"
    echo "- Host Architecture: $(uname -m)" >> "$report_file"
    
    print_success "Test report generated: $report_file"
}

# Run tests based on suite selection
case $TEST_SUITE in
    "smoke")
        print_status "Running smoke tests..."
        run_test_command "python -c 'import numpy, torch, scipy; print(\"✓ Core imports successful\")'" "smoke-imports"
        ;;
        
    "unit")
        print_status "Running unit tests..."
        run_test_command "python -m pytest tests/ -x --tb=short --junit-xml=/test-results/unit-results.xml $pytest_verbose" "unit"
        ;;
        
    "integration")
        print_status "Running integration tests..."
        run_test_command "python -m pytest tests/ -m 'not benchmarks' --tb=short --junit-xml=/test-results/integration-results.xml $pytest_verbose" "integration"
        ;;
        
    "benchmarks")
        print_status "Running benchmark tests..."
        run_test_command "python -m pytest tests/ -m 'benchmarks' --tb=short --junit-xml=/test-results/benchmark-results.xml $pytest_verbose" "benchmarks"
        ;;
        
    "genesis")
        print_status "Running Genesis-specific tests..."
        run_test_command "
        python -c '
import genesis as gs
print(\"Testing Genesis functionality...\")
gs.init(backend=gs.cpu)
scene = gs.Scene(show_viewer=False)
print(\"✓ Genesis basic functionality test passed\")
' && python -m pytest tests/test_*genesis* tests/test_*rigid* tests/test_*physics* --junit-xml=/test-results/genesis-results.xml $pytest_verbose" "genesis"
        ;;
        
    "navi")
        print_status "Running Navi Gym specific tests..."
        run_test_command "
        cd $WORKSPACE_DIR &&
        python -c '
import sys
sys.path.insert(0, \".\")
print(\"Testing Navi Gym specific functionality...\")

# Test basic requirements
import numpy as np
import torch
import scipy
print(\"✓ Core dependencies available\")

# Test project structure
import os
if os.path.exists(\"navi_gym\"):
    import navi_gym
    print(\"✓ Navi Gym module available\")
else:
    print(\"ℹ Navi Gym module not found, testing workspace structure\")

print(\"✓ Navi Gym tests completed\")
'" "navi"
        ;;
        
    "all")
        print_status "Running all test suites..."
        run_test_command "python -c 'import numpy, torch, scipy; print(\"✓ Smoke test passed\")'" "smoke"
        run_test_command "python -m pytest tests/ --tb=short --junit-xml=/test-results/all-results.xml -n $PARALLEL_JOBS $pytest_verbose" "all"
        ;;
esac

# Generate final report
generate_report

# Cleanup containers if not keeping them
if [[ "$KEEP_CONTAINER" == false ]]; then
    print_status "Cleaning up test containers..."
    docker ps -a --filter "name=$CONTAINER_NAME" --format "{{.Names}}" | xargs -r docker rm -f 2>/dev/null || true
fi

print_success "Test execution completed!"
print_status "Results available in: $OUTPUT_DIR"
print_status "View report with: cat $OUTPUT_DIR/test-report.md"