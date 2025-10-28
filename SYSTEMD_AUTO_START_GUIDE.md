# GitHub Actions Runners Systemd Auto-Start Guide

This guide explains how to configure the GitHub Actions runners to start automatically with systemd on your aarch64 system.

## Overview

Your system now has comprehensive systemd integration for GitHub Actions runners with multiple layers of reliability:

### 🔧 Available Scripts

1. **`./configure-runner.sh`** - Configure x64 runner with systemd integration
2. **`./configure-runner-arm64.sh`** - Configure ARM64 runner with systemd integration  
3. **`./manage-runners.sh`** - Comprehensive runner management
4. **`./setup-auto-start.sh`** - Multi-layer auto-start configuration

## 🚀 Quick Setup

### Step 1: Configure Runners
```bash
# Set your GitHub token
export GITHUB_TOKEN="your_github_token_here"

# Configure x64 runner (if needed)
cd actions-runner
./configure-runner.sh
cd ..

# Configure ARM64 runner (recommended for your aarch64 system)
cd actions-runner-arm64
./configure-runner-arm64.sh
cd ..
```

### Step 2: Setup Auto-Start
```bash
# Configure comprehensive auto-start
./setup-auto-start.sh setup
```

### Step 3: Verify Setup
```bash
# Check runner status
./manage-runners.sh status

# View logs
./manage-runners.sh logs
```

## 🔄 Systemd Integration Features

### Built-in Systemd Configuration

Both runner configuration scripts automatically:

- ✅ **Install systemd service** using `./svc.sh install`
- ✅ **Create enhanced override** with resource limits and dependencies
- ✅ **Enable auto-start** with `systemctl enable`
- ✅ **Configure restart policy** (always restart with 5-10 second delay)
- ✅ **Set resource limits** (8-12GB memory, file/process limits)
- ✅ **Wait for Docker** availability before starting
- ✅ **Set environment variables** for optimal performance

### Enhanced Override Configuration

Located at: `/etc/systemd/system/actions.runner.navichat-Navi_Gym.*.service.d/override.conf`

Features:
- **Network dependency**: Waits for network-online.target
- **Docker dependency**: Waits for Docker service
- **Resource limits**: Memory, tasks, file descriptors
- **Security**: NoNewPrivileges, PrivateTmp, ProtectSystem
- **Logging**: Structured journal logging
- **Restart policy**: Always restart with exponential backoff

## 🎯 Auto-Start Methods

The setup provides multiple layers of auto-start reliability:

### 1. System Systemd Services (Primary)
```bash
# Service names (auto-generated based on hostname)
sudo systemctl status actions.runner.navichat-Navi_Gym.navi-gym-runner-spark-b271.service
sudo systemctl status actions.runner.navichat-Navi_Gym.navi-gym-runner-arm64-spark-b271.service
```

### 2. User Systemd Services (Alternative)
```bash
# User services for additional reliability
systemctl --user status github-runner-x64.service
systemctl --user status github-runner-arm64.service
```

### 3. Desktop Autostart (GUI Sessions)
- Location: `~/.config/autostart/github-runners.desktop`
- Runs verification script on desktop login

### 4. Cron Job Monitoring (Backup)
- Checks runners every 5 minutes
- Automatically restarts if stopped

## 📊 Management Commands

### Basic Operations
```bash
# Show comprehensive status
./manage-runners.sh status

# Start/stop/restart runners
./manage-runners.sh start [x64|arm64|both]
./manage-runners.sh stop [x64|arm64|both]
./manage-runners.sh restart [x64|arm64|both]

# View logs
./manage-runners.sh logs [x64|arm64|both]
```

### System Service Management
```bash
# System services (if configured)
sudo systemctl start actions.runner.navichat-Navi_Gym.navi-gym-runner-arm64-$(hostname).service
sudo systemctl stop actions.runner.navichat-Navi_Gym.navi-gym-runner-arm64-$(hostname).service
sudo systemctl restart actions.runner.navichat-Navi_Gym.navi-gym-runner-arm64-$(hostname).service

# Check service status
sudo systemctl status actions.runner.navichat-Navi_Gym.navi-gym-runner-arm64-$(hostname).service

# View service logs
sudo journalctl -u actions.runner.navichat-Navi_Gym.navi-gym-runner-arm64-$(hostname).service -f
```

### User Service Management
```bash
# User services
systemctl --user start github-runner-arm64.service
systemctl --user stop github-runner-arm64.service
systemctl --user restart github-runner-arm64.service

# View user service logs
journalctl --user -u github-runner-arm64.service -f
```

## 🔍 Monitoring & Troubleshooting

### Status Verification
```bash
# Complete system status
./manage-runners.sh status

# Startup verification
./verify-runners-startup.sh

# Check auto-start configuration
./setup-auto-start.sh check
```

### Log Locations
```bash
# Startup logs
tail -f runner-startup.log

# System service logs
sudo journalctl -u actions.runner.navichat-Navi_Gym.navi-gym-runner-arm64-$(hostname).service -f

# User service logs
journalctl --user -u github-runner-arm64.service -f

# Runner application logs
tail -f actions-runner-arm64/_diag/Runner_*.log
```

### Common Issues

1. **Docker not available**
   ```bash
   # Check Docker status
   systemctl status docker
   
   # Add user to docker group
   sudo usermod -aG docker $USER
   # Logout and login again
   ```

2. **Service fails to start**
   ```bash
   # Check detailed logs
   sudo journalctl -u actions.runner.navichat-Navi_Gym.navi-gym-runner-arm64-$(hostname).service --no-pager -n 50
   
   # Verify runner configuration
   cd actions-runner-arm64 && ls -la .runner .credentials*
   ```

3. **Runner not appearing in GitHub**
   ```bash
   # Check network connectivity
   curl -I https://api.github.com
   
   # Verify token permissions
   # Token needs 'repo' and 'workflow' scopes
   ```

## 🎯 Recommended Configuration

For your aarch64 system, we recommend:

1. **Primary**: ARM64 runner for native performance
2. **Optional**: x64 runner for compatibility (if needed)
3. **Auto-start**: Multi-layer approach for maximum reliability

### ARM64 Optimized Setup
```bash
# Configure ARM64 runner with auto-start
export GITHUB_TOKEN="your_token"
cd actions-runner-arm64
./configure-runner-arm64.sh
cd ..
./setup-auto-start.sh setup
```

## 🔐 Security Features

- **User isolation**: Runs as regular user, not root
- **Resource limits**: Memory and process limits
- **Security constraints**: NoNewPrivileges, PrivateTmp
- **Docker socket**: Secure access to Docker daemon
- **Credential protection**: Runner credentials excluded from git

## 📈 Performance Optimization

- **Native ARM64**: Optimal performance on your aarch64 system
- **Resource limits**: Prevents resource exhaustion
- **Restart policy**: Automatic recovery from failures
- **Docker integration**: Pre-built containers for fast CI/CD
- **Monitoring**: Comprehensive logging and status checking

## 🔄 Boot Sequence

1. **System boot** → Network available
2. **Docker starts** → Docker daemon ready
3. **Runner services start** → Wait for Docker
4. **Desktop login** (if GUI) → Autostart verification
5. **Cron monitoring** → Continuous health checks

Your GitHub Actions runners will now start automatically and reliably on every system boot!