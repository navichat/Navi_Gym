# Navi Gym CI/CD Workflows

This document describes the GitHub Actions CI/CD workflows set up for testing the Navi Gym software in Docker containers and on self-hosted runners.

## 🔧 Workflows Overview

### 1. Simple Docker Testing (`simple-docker-test.yml`)
**Purpose**: Basic Docker container testing for development
**Triggers**: Push, Pull Request, Manual dispatch
**Features**:
- Builds Docker images using existing Dockerfile
- Runs smoke tests (import tests, basic functionality)
- Runs unit tests if available
- Performance testing on manual trigger
- Security scanning with Trivy
- Comprehensive test summary

### 2. Docker Container Testing (`docker-container-test.yml`)
**Purpose**: Advanced Docker testing with multi-platform support
**Triggers**: Push (on specific paths), Pull Request, Manual dispatch
**Features**:
- Multi-platform builds (CPU/GPU variants)
- Comprehensive test suites (unit, integration, smoke)
- GPU testing on self-hosted runners
- Performance benchmarking
- Security vulnerability scanning
- Artifact collection and reporting

### 3. Self-Hosted Runner Test (`runner-test.yml`)
**Purpose**: Test and validate self-hosted runner functionality
**Triggers**: Manual dispatch
**Features**:
- System information collection
- Python environment validation
- Docker functionality testing
- GPU availability testing
- Project-specific testing
- Comprehensive system reporting

## 🐳 Docker Testing

### Container Features
- **Base Image**: PyTorch with CUDA support
- **Python Version**: 3.11
- **Dependencies**: NumPy, PyTorch, Trimesh, Genesis (if available)
- **Test Framework**: pytest with additional plugins

### Test Types

#### Smoke Tests
- Package import validation
- Basic functionality verification
- System compatibility checks

#### Unit Tests
- Runs existing pytest suite
- Handles containerized environment limitations
- Provides detailed error reporting

#### Integration Tests
- Tests inter-component functionality
- Environment-specific testing
- Timeout protection for long-running tests

#### Performance Tests
- NumPy computation benchmarks
- Import time measurements
- System resource utilization

## 🖥️ Self-Hosted Runner Setup

### Prerequisites
1. **GitHub Actions Runner**: Already installed and configured
2. **Docker**: Required for container-based testing
3. **Python 3.11+**: For native testing
4. **NVIDIA GPU** (optional): For GPU-accelerated testing

### Runner Capabilities
- **System Testing**: Hardware and OS validation
- **Docker Testing**: Container build and execution
- **GPU Testing**: CUDA availability and performance
- **Project Testing**: Custom test suite execution

## 🚀 Usage Guide

### Manual Testing
Use the workflow dispatch feature to run specific tests:

```bash
# Test basic functionality
gh workflow run runner-test.yml -f test_type=basic

# Test Docker functionality
gh workflow run runner-test.yml -f test_type=docker

# Test GPU capabilities
gh workflow run runner-test.yml -f test_type=gpu

# Run full test suite
gh workflow run runner-test.yml -f test_type=full
```

### Automated Testing
Workflows automatically trigger on:
- **Push to main/develop**: Runs smoke tests and basic validation
- **Pull Requests**: Comprehensive testing including security scans
- **Schedule**: Nightly performance benchmarks (when configured)

## 📊 Test Results and Reporting

### GitHub Step Summary
Each workflow generates a comprehensive summary including:
- Test status overview
- System information
- Performance metrics
- Error details and logs

### Artifacts
- Test results and logs
- Performance benchmark data
- Security scan reports
- Coverage reports (when available)

### Security Scanning
- **Trivy**: Container vulnerability scanning
- **Dependency scanning**: Python package security analysis
- **SARIF integration**: Results appear in GitHub Security tab

## 🔧 Configuration

### Environment Variables
```yaml
env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}
  PYTHON_VERSION: 3.11
```

### Secrets Required
- `GITHUB_TOKEN`: Automatically provided by GitHub Actions
- Additional secrets may be needed for private registries

## 🐛 Troubleshooting

### Common Issues

#### Docker Build Failures
- Check Dockerfile syntax and dependencies
- Verify base image availability
- Ensure sufficient disk space

#### Self-Hosted Runner Issues
- Verify runner is online and has capacity
- Check Docker daemon status
- Validate GPU drivers (for GPU testing)

#### Test Failures
- Review test logs in workflow summary
- Check for missing dependencies
- Verify containerized environment compatibility

### Debug Commands
```bash
# Check runner status
docker ps -a

# Verify GPU
nvidia-smi

# Test Python environment
python3 -c "import torch; print(torch.cuda.is_available())"

# Test Docker
docker run --rm hello-world
```

## 📈 Performance Optimization

### Caching Strategy
- Docker layer caching with GitHub Actions cache
- Dependency caching for faster builds
- Image registry caching for repeated use

### Resource Management
- Timeout protection for long-running tests
- Parallel test execution where possible
- Cleanup procedures to prevent resource leaks

## 🔐 Security Considerations

### Container Security
- Regular base image updates
- Vulnerability scanning in CI pipeline
- Minimal attack surface in production images

### Runner Security
- Isolated self-hosted runner environment
- Regular security updates
- Access control and monitoring

## 📝 Contributing

### Adding New Tests
1. Create test files in the `tests/` directory
2. Follow pytest conventions
3. Mark GPU-specific tests with `@pytest.mark.gpu`
4. Add containerization considerations

### Workflow Modifications
1. Test changes in feature branches
2. Use manual dispatch for validation
3. Update documentation
4. Consider backward compatibility

## 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Multi-stage Builds](https://docs.docker.com/develop/dev-best-practices/dockerfile_best-practices/)
- [Self-hosted Runners](https://docs.github.com/en/actions/hosting-your-own-runners)
- [pytest Documentation](https://docs.pytest.org/)