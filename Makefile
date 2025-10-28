# Navi Gym Docker Makefile
# Provides convenient commands for building, testing, and deploying Docker containers

.PHONY: help build build-nvidia build-amd build-all test test-unit test-integration clean push deploy-staging deploy-prod

# Default values
IMAGE_NAME ?= navi-gym
TAG ?= latest
REGISTRY ?= ghcr.io/navichat
PYTHON_VERSION ?= 3.11

# Colors for output
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m # No Color

help: ## Show this help message
	@echo "Navi Gym Docker Build System"
	@echo "============================="
	@echo ""
	@echo "Available commands:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Build default Docker image
	@echo "$(YELLOW)Building default Docker image...$(NC)"
	./scripts/build-docker.sh --name $(IMAGE_NAME) --tag $(TAG) --python-version $(PYTHON_VERSION)

build-nvidia: ## Build NVIDIA GPU Docker image
	@echo "$(YELLOW)Building NVIDIA GPU Docker image...$(NC)"
	./scripts/build-docker.sh --nvidia --name $(IMAGE_NAME) --tag $(TAG)-nvidia --python-version $(PYTHON_VERSION)

build-amd: ## Build AMD GPU Docker image
	@echo "$(YELLOW)Building AMD GPU Docker image...$(NC)"
	./scripts/build-docker.sh --amd --name $(IMAGE_NAME) --tag $(TAG)-amd --python-version $(PYTHON_VERSION)

build-multiarch: ## Build multi-architecture Docker image
	@echo "$(YELLOW)Building multi-architecture Docker image...$(NC)"
	./scripts/build-docker.sh --multiarch --name $(IMAGE_NAME) --tag $(TAG)-multiarch --python-version $(PYTHON_VERSION)

build-all: build build-nvidia build-amd ## Build all Docker images

test: ## Run all tests
	@echo "$(YELLOW)Running all tests...$(NC)"
	./scripts/run-tests.sh --image $(REGISTRY)/$(IMAGE_NAME):$(TAG) --suite all

test-unit: ## Run unit tests only
	@echo "$(YELLOW)Running unit tests...$(NC)"
	./scripts/run-tests.sh --image $(REGISTRY)/$(IMAGE_NAME):$(TAG) --suite unit --verbose

test-integration: ## Run integration tests only
	@echo "$(YELLOW)Running integration tests...$(NC)"
	./scripts/run-tests.sh --image $(REGISTRY)/$(IMAGE_NAME):$(TAG) --suite integration --verbose

test-benchmarks: ## Run benchmark tests
	@echo "$(YELLOW)Running benchmark tests...$(NC)"
	./scripts/run-tests.sh --image $(REGISTRY)/$(IMAGE_NAME):$(TAG) --suite benchmarks --timeout 3600

test-smoke: ## Run smoke tests (quick validation)
	@echo "$(YELLOW)Running smoke tests...$(NC)"
	./scripts/run-tests.sh --image $(REGISTRY)/$(IMAGE_NAME):$(TAG) --suite smoke

test-gpu: ## Test GPU functionality
	@echo "$(YELLOW)Testing GPU functionality...$(NC)"
	docker run --rm --gpus all $(REGISTRY)/$(IMAGE_NAME):$(TAG)-nvidia python -c "import torch; print('CUDA available:', torch.cuda.is_available()); print('GPU count:', torch.cuda.device_count())"

push: ## Push images to registry
	@echo "$(YELLOW)Pushing images to registry...$(NC)"
	docker push $(REGISTRY)/$(IMAGE_NAME):$(TAG)
	docker push $(REGISTRY)/$(IMAGE_NAME):$(TAG)-nvidia || true
	docker push $(REGISTRY)/$(IMAGE_NAME):$(TAG)-amd || true

clean: ## Clean up Docker images and containers
	@echo "$(YELLOW)Cleaning up Docker resources...$(NC)"
	docker system prune -f
	docker images $(IMAGE_NAME) -q | xargs -r docker rmi -f || true
	docker images $(REGISTRY)/$(IMAGE_NAME) -q | xargs -r docker rmi -f || true

clean-all: clean ## Clean up all Docker resources (including volumes)
	@echo "$(RED)Warning: This will remove ALL Docker resources!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; echo; if [[ $$REPLY =~ ^[Yy]$$ ]]; then docker system prune -a -f --volumes; fi

shell: ## Open shell in Docker container
	docker run -it --rm -v $(PWD):/workspace/navi-gym $(REGISTRY)/$(IMAGE_NAME):$(TAG) bash

shell-nvidia: ## Open shell in NVIDIA Docker container
	docker run -it --rm --gpus all -v $(PWD):/workspace/navi-gym $(REGISTRY)/$(IMAGE_NAME):$(TAG)-nvidia bash

shell-amd: ## Open shell in AMD Docker container
	docker run -it --rm --device=/dev/kfd --device=/dev/dri -v $(PWD):/workspace/navi-gym $(REGISTRY)/$(IMAGE_NAME):$(TAG)-amd bash

dev-setup: ## Set up development environment
	@echo "$(YELLOW)Setting up development environment...$(NC)"
	@if [ ! -d "venv" ]; then python3 -m venv venv; fi
	@./venv/bin/pip install -r requirements.txt
	@./venv/bin/pip install -r requirements-minimal.txt
	@echo "$(GREEN)Development environment ready. Activate with: source venv/bin/activate$(NC)"

lint: ## Run linting on Docker files
	@echo "$(YELLOW)Linting Docker files...$(NC)"
	@command -v hadolint >/dev/null 2>&1 || { echo "$(RED)hadolint not found. Install with: brew install hadolint$(NC)"; exit 1; }
	hadolint docker/Dockerfile
	hadolint docker/Dockerfile.amdgpu

security-scan: ## Run security scan on images
	@echo "$(YELLOW)Running security scan...$(NC)"
	@command -v trivy >/dev/null 2>&1 || { echo "$(RED)trivy not found. Install with: brew install trivy$(NC)"; exit 1; }
	trivy image $(REGISTRY)/$(IMAGE_NAME):$(TAG)

# Development shortcuts
dev: dev-setup ## Alias for dev-setup

quick-test: build test-smoke ## Quick build and smoke test

ci-test: build-all test ## Full CI test suite

# Release commands
release-prepare: ## Prepare for release
	@echo "$(YELLOW)Preparing release...$(NC)"
	@echo "Current version: $$(git describe --tags --abbrev=0 2>/dev/null || echo 'No tags found')"
	@read -p "Enter new version (e.g., v1.2.3): " version; \
	if [ -n "$$version" ]; then \
		echo "$(GREEN)Preparing release $$version$(NC)"; \
		git tag -a "$$version" -m "Release $$version"; \
		echo "$(GREEN)Tag created. Push with: git push origin $$version$(NC)"; \
	fi

release-build: ## Build release images
	@echo "$(YELLOW)Building release images...$(NC)"
	$(MAKE) build-all TAG=latest
	$(MAKE) push TAG=latest

# Docker Compose shortcuts (if docker-compose.yml exists)
up: ## Start services with docker-compose
	@if [ -f docker-compose.yml ]; then \
		docker-compose up -d; \
	else \
		echo "$(RED)docker-compose.yml not found$(NC)"; \
	fi

down: ## Stop services with docker-compose
	@if [ -f docker-compose.yml ]; then \
		docker-compose down; \
	else \
		echo "$(RED)docker-compose.yml not found$(NC)"; \
	fi

logs: ## View service logs
	@if [ -f docker-compose.yml ]; then \
		docker-compose logs -f; \
	else \
		echo "$(RED)docker-compose.yml not found$(NC)"; \
	fi

# Status and info commands
status: ## Show Docker system status
	@echo "$(GREEN)Docker System Status$(NC)"
	@echo "==================="
	@docker system df
	@echo ""
	@echo "$(GREEN)Running Containers$(NC)"
	@echo "=================="
	@docker ps
	@echo ""
	@echo "$(GREEN)Available Images$(NC)"
	@echo "================"
	@docker images | grep -E "(navi-gym|$(IMAGE_NAME))" || echo "No Navi Gym images found"

info: ## Show build information
	@echo "$(GREEN)Build Configuration$(NC)"
	@echo "==================="
	@echo "Image Name: $(IMAGE_NAME)"
	@echo "Tag: $(TAG)"
	@echo "Registry: $(REGISTRY)"
	@echo "Python Version: $(PYTHON_VERSION)"
	@echo "Git Commit: $$(git rev-parse --short HEAD 2>/dev/null || echo 'Unknown')"
	@echo "Git Branch: $$(git branch --show-current 2>/dev/null || echo 'Unknown')"