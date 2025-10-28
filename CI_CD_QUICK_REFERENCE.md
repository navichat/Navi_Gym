# Navi Gym CI/CD Quick Reference

## 🚀 Quick Start

```bash
# 1. Check system requirements
./setup-ci-cd.sh check

# 2. Build Docker images and run tests
./setup-ci-cd.sh all

# 3. Set up self-hosted runner
export GITHUB_TOKEN="your_github_token"

# For x64 systems
cd actions-runner && ./configure-runner.sh

# For ARM64 systems (Apple Silicon, ARM servers)
cd actions-runner-arm64 && ./configure-runner-arm64.sh
```

## 🧪 Running Tests

### Local Testing

```bash
# Quick smoke test
./scripts/run-tests.sh --suite smoke

# Run unit tests
./scripts/run-tests.sh --suite unit --verbose

# Run all tests
make test

# Test with Docker Compose
docker-compose up test-runner
```

### Test Suites Available

| Suite | Purpose | Duration | When to Use |
|-------|---------|----------|-------------|
| `smoke` | Quick validation | ~5 min | PR checks, quick validation |
| `unit` | Component testing | ~30 min | Code changes, development |
| `integration` | End-to-end testing | ~40 min | Feature completion |
| `benchmarks` | Performance testing | ~60 min | Performance validation |
| `genesis` | Physics engine tests | ~20 min | Genesis-related changes |
| `navi` | Navi Gym specific | ~15 min | Project-specific features |

## 🐳 Docker Commands

### Building Images

```bash
# Build all variants
make build-all

# Build specific variant
make build-nvidia    # NVIDIA GPU support
make build-amd       # AMD GPU support
make build           # CPU only

# ARM64 builds
docker build --platform linux/arm64 -f docker/Dockerfile -t navi-gym:arm64 .

# Multi-platform builds
docker buildx build --platform linux/amd64,linux/arm64 -t navi-gym:multi .

# Manual build
docker build -f docker/Dockerfile -t navi-gym:latest .
```

### Running Containers

```bash
# Interactive shell
make shell           # CPU container
make shell-nvidia    # NVIDIA container  
make shell-amd       # AMD container

# Run tests manually
docker run --rm -v $(pwd):/workspace/navi-gym navi-gym:latest \
  bash -c "cd /workspace/navi-gym && python -m pytest tests/"
```

## ⚙️ Self-Hosted Runner

### Setup

```bash
# In actions-runner directory
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxx"
./configure-runner.sh
```

### Management

```bash
# Check status
./monitor-runner.sh

# Service management
sudo systemctl start actions.runner.*
sudo systemctl stop actions.runner.*
sudo systemctl restart actions.runner.*

# View logs
journalctl -u actions.runner.* -f
```

## 🔄 GitHub Actions Workflows

### Triggering Workflows

1. **Automatic Triggers**:
   - Push to `main`, `develop`, `feature/*`
   - Pull requests to `main`, `develop`
   - Tags matching `v*`

2. **Manual Trigger**:
   - Go to Actions tab → Test CI/CD Pipeline → Run workflow
   - Choose test suite and options

### Workflow Outputs

- **Test Results**: Downloadable XML reports
- **Docker Images**: Built and cached images
- **Security Reports**: Vulnerability scans
- **Performance Reports**: Benchmark results

## 🛠️ Development Workflow

### Before Committing

```bash
# 1. Run local tests
./scripts/run-tests.sh --suite unit

# 2. Check Docker build
make build

# 3. Run smoke tests
./scripts/run-tests.sh --suite smoke
```

### Pull Request Process

1. **Create Feature Branch**:
   ```bash
   git checkout -b feature/your-feature
   ```

2. **Make Changes**: Implement your feature

3. **Test Locally**: Run relevant test suites

4. **Create PR**: Push and create pull request

5. **CI Validation**: Automatic smoke tests and quick validation

6. **Review Process**: Code review and approval

7. **Merge**: Triggers full test suite on main branch

### Adding New Tests

1. **Create Test File**: `tests/test_your_feature.py`

2. **Use Fixtures**: Leverage existing conftest.py fixtures

3. **Mark Tests**: Use appropriate pytest markers
   ```python
   @pytest.mark.benchmarks
   def test_performance():
       pass
   ```

4. **Update Documentation**: Add test descriptions

## 🔧 Configuration Files

### Key Files to Know

| File | Purpose | When to Modify |
|------|---------|----------------|
| `.github/workflows/test-ci.yml` | Main CI workflow | Adding new test jobs |
| `docker/Dockerfile` | Main Docker image | Changing dependencies |
| `docker-compose.yml` | Multi-service setup | Adding new services |
| `tests/conftest.py` | Pytest configuration | Adding test fixtures |
| `pyproject.toml` | Python/test config | Changing test settings |
| `scripts/run-tests.sh` | Test execution | Modifying test logic |
| `Makefile` | Build automation | Adding new commands |

### Environment Variables

| Variable | Purpose | Required |
|----------|---------|----------|
| `GITHUB_TOKEN` | Runner authentication | For self-hosted runner |
| `DISPLAY` | Headless display | Set automatically in CI |
| `PYTHONPATH` | Module path | Set automatically |
| `TI_ENABLE_CUDA` | GPU control | Set automatically |

## 🚨 Troubleshooting

### Common Issues

1. **Docker Build Fails**:
   ```bash
   # Clean build cache
   docker builder prune -a
   
   # Check disk space
   df -h
   
   # Manual build with no cache
   docker build --no-cache -f docker/Dockerfile -t navi-gym:test .
   ```

2. **Tests Fail in CI**:
   ```bash
   # Run same test locally
   ./scripts/run-tests.sh --suite unit --verbose
   
   # Check test in container
   docker run -it --rm navi-gym:latest bash
   cd /workspace/navi-gym && python -m pytest tests/test_specific.py -v
   ```

3. **Runner Not Appearing**:
   ```bash
   # Check runner service
   sudo systemctl status actions.runner.*
   
   # Check GitHub token permissions
   curl -H "Authorization: token $GITHUB_TOKEN" \
     https://api.github.com/repos/navichat/Navi_Gym
   
   # Reconfigure runner
   cd actions-runner && ./config.sh remove && ./configure-runner.sh
   ```

4. **Out of Memory**:
   ```bash
   # Check available memory
   free -h
   
   # Reduce parallel jobs
   ./scripts/run-tests.sh --jobs 1
   
   # Use swap file
   sudo fallocate -l 4G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

### Getting Help

1. **Check Logs**:
   - GitHub Actions: Workflow run details
   - Runner: `journalctl -u actions.runner.*`
   - Docker: `docker logs <container>`

2. **Documentation**:
   - Full docs: `CI_CD_DOCUMENTATION.md`
   - Project docs: `README.md`
   - Genesis docs: Official documentation

3. **Support Channels**:
   - GitHub Issues: Technical problems
   - Project maintainers: Architecture questions

## 📊 Monitoring

### Key Metrics

- **Build Success Rate**: Target >95%
- **Test Execution Time**: Monitor for regressions
- **Runner Availability**: Target >99% uptime
- **Resource Usage**: CPU, memory, disk trends

### Monitoring Commands

```bash
# Runner status
./monitor-runner.sh

# Docker resource usage
docker stats

# System resources
htop
df -h
free -h

# Test history
ls -la test-results/
```

## 🎯 Best Practices

### Test Writing

- ✅ Write focused, independent tests
- ✅ Use descriptive test names
- ✅ Implement proper cleanup
- ✅ Use appropriate fixtures
- ❌ Don't create test dependencies
- ❌ Don't test implementation details

### Docker Images

- ✅ Use multi-stage builds
- ✅ Implement proper caching
- ✅ Set resource limits
- ✅ Use specific base image tags
- ❌ Don't include development tools in production
- ❌ Don't run as root unnecessarily

### CI/CD Pipeline

- ✅ Fail fast on critical errors
- ✅ Use parallel execution
- ✅ Cache appropriately
- ✅ Provide clear feedback
- ❌ Don't run expensive tests on every PR
- ❌ Don't ignore flaky tests

## 📝 Quick Commands Cheat Sheet

```bash
# Setup and validation
./setup-ci-cd.sh all
./setup-ci-cd.sh check

# Testing
make test
make test-unit
make quick-test
./scripts/run-tests.sh --suite smoke

# Docker
make build
make build-all
make shell
docker-compose up test-runner

# Runner management
./actions-runner/configure-runner.sh
./actions-runner/monitor-runner.sh
sudo systemctl restart actions.runner.*

# Cleanup
make clean
docker system prune -f
```

---

*For detailed information, see [CI_CD_DOCUMENTATION.md](CI_CD_DOCUMENTATION.md)*