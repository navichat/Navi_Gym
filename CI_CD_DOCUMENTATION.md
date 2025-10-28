# Navi Gym CI/CD Documentation

## Overview

This document describes the Continuous Integration and Continuous Deployment (CI/CD) setup for the Navi Gym project, which uses GitHub Actions workflows to run tests in Docker containers.

## Architecture

### 1. GitHub Actions Workflows

#### Primary Test Workflow (`test-ci.yml`)
- **Trigger**: Push to main/develop, Pull Requests, Manual dispatch
- **Purpose**: Comprehensive testing in Docker containers
- **Features**:
  - Change detection to optimize test execution
  - Multi-variant Docker builds (CPU, NVIDIA GPU)
  - Parallel test execution
  - Security scanning
  - Test result aggregation

#### Legacy Docker CI Workflow (`docker-ci.yml`)
- **Purpose**: Docker image building and basic validation
- **Features**: Multi-architecture builds, security scanning

#### ARM64 CI Workflow (`arm64-ci.yml`)
- **Trigger**: Commits with `[arm64]` tag, manual dispatch
- **Purpose**: Native ARM64 testing and optimization
- **Features**:
  - ARM64-native Docker builds
  - Performance benchmarking
  - Architecture-specific optimizations
  - ARM64 vs x64 performance comparison

### 2. Self-Hosted Runner Setup

The project supports self-hosted GitHub Actions runners for:
- Access to local GPU resources
- Faster build times with local caching
- Custom hardware configurations
- Cost optimization for compute-intensive workloads
- **ARM64 architecture support** for Apple Silicon and ARM-based servers

#### Runner Variants Available

1. **x64 Runner** (`actions-runner/`):
   - Standard x86_64 architecture
   - NVIDIA GPU support
   - Compatible with most cloud providers

2. **ARM64 Runner** (`actions-runner-arm64/`):
   - Native ARM64/aarch64 support
   - Optimized for Apple Silicon and ARM servers
   - Reduced emulation overhead
   - ARM64-specific performance optimizations

## Test Suites

### Available Test Suites

1. **Smoke Tests** (`smoke`)
   - Quick validation of basic functionality
   - Import tests for core dependencies
   - Runtime: ~5 minutes
   - Triggered: On all PRs and pushes

2. **Unit Tests** (`unit`)
   - Individual component testing
   - Uses pytest framework
   - Runtime: ~30 minutes
   - Triggered: When Python files change

3. **Integration Tests** (`integration`)
   - End-to-end functionality testing
   - Scene creation and physics simulation
   - Runtime: ~40 minutes
   - Triggered: On main branch pushes

4. **Benchmark Tests** (`benchmarks`)
   - Performance validation
   - GPU acceleration testing
   - Runtime: ~60 minutes
   - Triggered: Manual or main branch pushes

5. **Genesis Tests** (`genesis`)
   - Specific to Genesis physics engine
   - Scene creation and simulation tests
   - Runtime: ~20 minutes

6. **Navi Tests** (`navi`)
   - Navi Gym specific functionality
   - Custom workspace validation
   - Runtime: ~15 minutes

## Docker Configuration

### Base Images

1. **CPU Image** (`docker/Dockerfile`)
   - PyTorch 2.5.1 with CUDA 12.1
   - Genesis physics engine
   - Complete Python environment
   - Size: ~8GB

2. **NVIDIA GPU Image** (same Dockerfile with GPU support)
   - CUDA runtime enabled
   - GPU acceleration for testing
   - Additional GPU libraries

3. **AMD GPU Image** (`docker/Dockerfile.amdgpu`)
   - ROCm support for AMD GPUs
   - Specialized for AMD hardware

### Test Environment Configuration

```yaml
environment:
  DISPLAY: :99                    # Headless display
  PYOPENGL_PLATFORM: osmesa      # Software rendering
  TI_ENABLE_CUDA: 0              # Disable CUDA for CI
  TI_ENABLE_OPENGL: 0            # Disable OpenGL for CI
  TI_ENABLE_VULKAN: 0            # Disable Vulkan for CI
  PYTHONPATH: /workspace/navi-gym # Project root
```

## Usage

### Running Tests Locally

Using the provided test script:

```bash
# Run all tests
./scripts/run-tests.sh --image navi-gym:latest --suite all

# Run unit tests with verbose output
./scripts/run-tests.sh --image navi-gym:latest --suite unit --verbose

# Run integration tests with custom timeout
./scripts/run-tests.sh --image navi-gym:latest --suite integration --timeout 3600

# Run smoke tests quickly
./scripts/run-tests.sh --image navi-gym:latest --suite smoke
```

Using Make commands:

```bash
# Build and test
make build test

# Quick smoke test
make quick-test

# Full CI pipeline
make ci-test

# Test specific components
make test-unit
make test-integration
make test-benchmarks
```

Using Docker Compose:

```bash
# Run test service
docker-compose up test-runner

# Run with specific test suite
docker-compose run test-runner pytest tests/ -m "not benchmarks"
```

### Setting Up Self-Hosted Runner

1. **Prerequisites**:
   - Linux machine with Docker installed
   - GitHub token with repo and workflow permissions
   - Sufficient disk space (>50GB recommended)
   - Adequate RAM (>8GB recommended)

2. **Installation**:
   ```bash
   # Already completed in your workspace
   cd actions-runner
   
   # Set your GitHub token
   export GITHUB_TOKEN="your_github_token_here"
   
   # Configure and start the runner
   ./configure-runner.sh
   ```

3. **Monitoring**:
   ```bash
   # Check runner status
   ./monitor-runner.sh
   
   # View runner logs
   journalctl -u actions.runner.* -f
   
   # Restart runner service
   sudo systemctl restart actions.runner.*
   ```

### Manual Workflow Dispatch

You can trigger workflows manually from GitHub:

1. Go to **Actions** tab in your repository
2. Select **Test CI/CD Pipeline**
3. Click **Run workflow**
4. Choose options:
   - **Test suite**: Select which tests to run
   - **Skip cache**: Force fresh Docker builds

## Configuration Files

### GitHub Actions Workflows

- `.github/workflows/test-ci.yml` - Main testing workflow
- `.github/workflows/docker-ci.yml` - Docker build workflow
- `.github/workflows/deploy.yml` - Deployment workflow
- `.github/workflows/production.yml` - Production pipeline

### Test Configuration

- `tests/conftest.py` - Pytest configuration and fixtures
- `pyproject.toml` - Python project configuration with test settings
- `pytest.ini` - Additional pytest settings (if needed)

### Docker Configuration

- `docker/Dockerfile` - Main Docker image
- `docker/Dockerfile.amdgpu` - AMD GPU specific image
- `docker-compose.yml` - Multi-service Docker configuration

### Build Scripts

- `scripts/run-tests.sh` - Test execution script
- `scripts/build-docker.sh` - Docker build script
- `Makefile` - Build automation

## Best Practices

### 1. Test Organization

- Keep tests focused and independent
- Use appropriate test markers (`@pytest.mark.benchmarks`)
- Implement proper test fixtures for common setup
- Use parameterized tests for multiple scenarios

### 2. Docker Best Practices

- Use multi-stage builds to reduce image size
- Implement proper caching strategies
- Set resource limits for containers
- Use headless configurations for CI environments

### 3. CI/CD Optimization

- Use change detection to skip unnecessary work
- Implement parallel test execution where possible
- Cache Docker layers and test artifacts
- Set appropriate timeouts for different test types

### 4. Monitoring and Debugging

- Use structured logging in tests
- Implement health checks for services
- Monitor resource usage during tests
- Preserve test artifacts for debugging

## Troubleshooting

### Common Issues

1. **Docker Build Failures**
   ```bash
   # Check Docker status
   docker info
   
   # Clean build cache
   docker builder prune -a
   
   # Check disk space
   df -h
   ```

2. **Test Failures**
   ```bash
   # Run tests locally with more verbose output
   ./scripts/run-tests.sh --suite unit --verbose
   
   # Check container logs
   docker logs <container_name>
   
   # Debug interactive container
   docker run -it --rm navi-gym:latest bash
   ```

3. **Self-Hosted Runner Issues**
   ```bash
   # Check runner service status
   sudo systemctl status actions.runner.*
   
   # Restart runner
   sudo systemctl restart actions.runner.*
   
   # Check runner logs
   journalctl -u actions.runner.* --since "1 hour ago"
   ```

4. **GPU Access Issues**
   ```bash
   # Test NVIDIA GPU access
   docker run --rm --gpus all nvidia/cuda:12.1-runtime-ubuntu20.04 nvidia-smi
   
   # Test AMD GPU access
   docker run --rm --device=/dev/kfd --device=/dev/dri rocm/pytorch:latest rocm-smi
   ```

### Performance Optimization

1. **Runner Performance**
   - Ensure adequate RAM and storage
   - Use SSD storage for Docker workspace
   - Configure swap if needed
   - Monitor CPU and memory usage

2. **Test Performance**
   - Use pytest-xdist for parallel execution
   - Implement test caching where appropriate
   - Skip expensive tests in PR validation
   - Use appropriate test fixtures

3. **Docker Performance**
   - Implement effective layer caching
   - Use Docker BuildKit for improved builds
   - Clean up unused images regularly
   - Configure Docker daemon for optimal performance

## Security Considerations

### 1. Runner Security

- Run runner service with minimal privileges
- Regularly update runner software
- Monitor runner activity and logs
- Implement network restrictions if needed

### 2. Container Security

- Use trusted base images
- Implement security scanning with Trivy
- Keep dependencies updated
- Follow container security best practices

### 3. Secret Management

- Use GitHub Secrets for sensitive data
- Never commit tokens or credentials
- Rotate secrets regularly
- Implement least-privilege access

## Monitoring and Metrics

### Key Metrics to Monitor

1. **Test Success Rate**: Percentage of passing tests
2. **Build Duration**: Time taken for CI/CD pipelines
3. **Resource Usage**: CPU, memory, and disk usage
4. **Runner Availability**: Uptime of self-hosted runners
5. **Security Scan Results**: Vulnerability counts and severity

### Monitoring Tools

- GitHub Actions dashboard for workflow status
- SystemD logs for runner monitoring
- Docker stats for container resource usage
- Custom monitoring script (`monitor-runner.sh`)

## Future Improvements

### Planned Enhancements

1. **Advanced Caching**
   - Implement test result caching
   - Optimize Docker layer caching
   - Add dependency caching

2. **Enhanced Reporting**
   - Test coverage reporting
   - Performance benchmarking
   - Visual test reports

3. **Additional Test Types**
   - End-to-end simulation tests
   - Multi-GPU distributed tests
   - Long-running stability tests

4. **Deployment Automation**
   - Automated releases
   - Environment promotion
   - Rollback capabilities

### Contributing to CI/CD

When contributing to the CI/CD system:

1. Test changes in feature branches
2. Update documentation for new features
3. Consider backward compatibility
4. Add appropriate test coverage
5. Follow existing patterns and conventions

## Support

For CI/CD related issues:

1. Check existing GitHub Issues
2. Review workflow run logs
3. Consult this documentation
4. Create detailed issue reports with:
   - Workflow run links
   - Error messages
   - System information
   - Steps to reproduce

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Documentation](https://docs.docker.com/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Genesis Physics Engine Documentation](https://genesis-world.readthedocs.io/)