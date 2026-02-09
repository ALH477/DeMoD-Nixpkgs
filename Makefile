.PHONY: help run dev install clean test format check

help: ## Show this help message
	@echo '╔══════════════════════════════════════════════════════════════╗'
	@echo '║  DeMoD Nixpkgs - Beautiful Package Management for Nix       ║'
	@echo '║  Copyright (c) 2026 DeMoD LLC                                ║'
	@echo '╚══════════════════════════════════════════════════════════════╝'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

run: ## Run the TUI application using Nix
	nix run

dev: ## Enter development shell
	nix develop

install: ## Install to user profile
	nix profile install .

build: ## Build the package
	nix build

clean: ## Clean build artifacts
	rm -rf result result-*
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

test: ## Run tests (placeholder)
	@echo "No tests configured yet"

format: ## Format Python code
	nix develop -c python -m black demod_nixpkgs.py

check: ## Check flake
	nix flake check

update: ## Update flake inputs
	nix flake update

repl: ## Enter Nix REPL
	nix repl

show: ## Show flake info
	nix flake show

standalone: ## Run without Nix (requires Python deps installed)
	python3 demod_nixpkgs.py

deps: ## Install Python dependencies (non-Nix method)
	pip install -r requirements.txt
