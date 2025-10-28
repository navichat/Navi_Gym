#!/bin/bash

# Docker Build Script for Navi Gym
# This script builds Docker images for different configurations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
IMAGE_NAME="navi-gym"
TAG="latest"
DOCKERFILE="docker/Dockerfile"
PLATFORM="linux/amd64"
PUSH=false
REGISTRY="ghcr.io"
PYTHON_VERSION="3.11"
BUILD_ARGS=""
CACHE_FROM=""
CACHE_TO=""

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

Build Docker images for Navi Gym

OPTIONS:
    -n, --name NAME         Image name (default: $IMAGE_NAME)
    -t, --tag TAG           Image tag (default: $TAG)
    -d, --dockerfile PATH   Dockerfile path (default: $DOCKERFILE)
    -p, --platform PLATFORM Target platform (default: $PLATFORM)
    --push                  Push image to registry
    -r, --registry URL      Registry URL (default: $REGISTRY)
    --python-version VER    Python version (default: $PYTHON_VERSION)
    --nvidia                Use NVIDIA GPU Dockerfile
    --amd                   Use AMD GPU Dockerfile
    --multiarch             Build for multiple architectures
    --cache-from SOURCE     Cache source for Docker buildx
    --cache-to DEST         Cache destination for Docker buildx
    -h, --help              Show this help message

EXAMPLES:
    # Build basic image
    $0

    # Build NVIDIA GPU image
    $0 --nvidia --tag nvidia-latest

    # Build AMD GPU image
    $0 --amd --tag amd-latest

    # Build and push multi-architecture image
    $0 --multiarch --push --tag multi-latest

    # Build with custom registry and tag
    $0 --registry docker.io/myuser --tag v1.0.0 --push

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -n|--name)
            IMAGE_NAME="$2"
            shift 2
            ;;
        -t|--tag)
            TAG="$2"
            shift 2
            ;;
        -d|--dockerfile)
            DOCKERFILE="$2"
            shift 2
            ;;
        -p|--platform)
            PLATFORM="$2"
            shift 2
            ;;
        --push)
            PUSH=true
            shift
            ;;
        -r|--registry)
            REGISTRY="$2"
            shift 2
            ;;
        --python-version)
            PYTHON_VERSION="$2"
            shift 2
            ;;
        --nvidia)
            DOCKERFILE="docker/Dockerfile"
            TAG="${TAG}-nvidia"
            shift
            ;;
        --amd)
            DOCKERFILE="docker/Dockerfile.amdgpu"
            TAG="${TAG}-amd"
            shift
            ;;
        --multiarch)
            PLATFORM="linux/amd64,linux/arm64"
            TAG="${TAG}-multiarch"
            shift
            ;;
        --cache-from)
            CACHE_FROM="$2"
            shift 2
            ;;
        --cache-to)
            CACHE_TO="$2"
            shift 2
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

# Construct full image name
FULL_IMAGE_NAME="${REGISTRY}/${IMAGE_NAME}:${TAG}"

# Build arguments
BUILD_ARGS="--build-arg PYTHON_VERSION=${PYTHON_VERSION}"

# Add cache arguments if specified
if [[ -n "$CACHE_FROM" ]]; then
    BUILD_ARGS="$BUILD_ARGS --cache-from $CACHE_FROM"
fi

if [[ -n "$CACHE_TO" ]]; then
    BUILD_ARGS="$BUILD_ARGS --cache-to $CACHE_TO"
fi

print_status "Starting Docker build process..."
print_status "Image: $FULL_IMAGE_NAME"
print_status "Dockerfile: $DOCKERFILE"
print_status "Platform: $PLATFORM"
print_status "Python Version: $PYTHON_VERSION"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running or not accessible"
    exit 1
fi

# Check if Dockerfile exists
if [[ ! -f "$DOCKERFILE" ]]; then
    print_error "Dockerfile not found: $DOCKERFILE"
    exit 1
fi

# Create buildx builder if needed for multi-arch builds
if [[ "$PLATFORM" == *","* ]]; then
    print_status "Setting up Docker Buildx for multi-architecture build..."
    docker buildx create --name navi-gym-builder --use --driver docker-container --driver-opt network=host 2>/dev/null || true
    docker buildx inspect --bootstrap
fi

# Build the image
print_status "Building Docker image..."

if [[ "$PLATFORM" == *","* ]]; then
    # Multi-architecture build
    BUILD_CMD="docker buildx build"
    if [[ "$PUSH" == true ]]; then
        BUILD_CMD="$BUILD_CMD --push"
    else
        BUILD_CMD="$BUILD_CMD --load"
        print_warning "Multi-arch builds cannot be loaded locally. Use --push to push to registry."
    fi
else
    # Single architecture build
    BUILD_CMD="docker build"
fi

# Execute build command
eval "$BUILD_CMD \
    --file $DOCKERFILE \
    --platform $PLATFORM \
    --tag $FULL_IMAGE_NAME \
    $BUILD_ARGS \
    ."

if [[ $? -eq 0 ]]; then
    print_success "Docker image built successfully: $FULL_IMAGE_NAME"
else
    print_error "Docker build failed"
    exit 1
fi

# Push image if requested (for single arch builds)
if [[ "$PUSH" == true && "$PLATFORM" != *","* ]]; then
    print_status "Pushing image to registry..."
    docker push "$FULL_IMAGE_NAME"
    if [[ $? -eq 0 ]]; then
        print_success "Image pushed successfully: $FULL_IMAGE_NAME"
    else
        print_error "Failed to push image"
        exit 1
    fi
fi

# Test basic functionality
print_status "Testing basic image functionality..."
if [[ "$PLATFORM" != *","* ]]; then
    docker run --rm "$FULL_IMAGE_NAME" python -c "
import sys
print('Python version:', sys.version)
try:
    import numpy as np
    print('✓ NumPy available')
    import torch
    print('✓ PyTorch available')
    print('✓ Basic functionality test passed')
except ImportError as e:
    print('✗ Import test failed:', e)
    sys.exit(1)
"
    if [[ $? -eq 0 ]]; then
        print_success "Basic functionality test passed"
    else
        print_warning "Basic functionality test failed, but image was built"
    fi
else
    print_warning "Skipping functionality test for multi-arch build"
fi

print_success "Build process completed!"
print_status "Image: $FULL_IMAGE_NAME"
print_status "Run with: docker run --rm -it $FULL_IMAGE_NAME"