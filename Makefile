SHELL := /usr/bin/env bash

PYTHON ?= python3
PYTEST ?= $(PYTHON) -m pytest
ANSIBLE_LINT ?= ansible-lint
ANSIBLE_INVENTORY ?= ansible-inventory
CATALOG := semaphore/templates/catalog.json
CONFIG ?= semaphore/setup/config.example.json

.DEFAULT_GOAL := help

.PHONY: help validate syntax lint test test-all test-syntax docs-check security inventory verify install \
	semaphore-plan semaphore-apply semaphore-report clean

help: ## Show available targets
	@grep -hE '^[a-zA-Z0-9_.-]+:.*?## ' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "} {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

validate: ## Validate YAML, Jinja, catalog, guard and build inventory
	$(PYTHON) scripts/validation/validate.py

syntax: ## Syntax-check every catalog playbook with the dev inventory
	$(PYTHON) scripts/validation/validate.py --syntax

lint: ## Run ansible-lint on the supported tree
	$(ANSIBLE_LINT)

test: ## Run unit tests
	$(PYTEST) -q tests/unit

test-syntax: ## Run the catalog syntax test suite
	$(PYTEST) -q tests/syntax

test-all: ## Run every test (integration is opt-in)
	$(PYTEST) -q

docs-check: ## Fail when generated template documentation is out of date
	$(PYTHON) scripts/reporting/render_catalog.py --check

security: ## Run static security tests
	$(PYTEST) -q tests/security

inventory: ## Print the resolved dev inventory
	$(ANSIBLE_INVENTORY) -i inventories/dev/hosts.yml --list

verify: ## Run installation verification against this checkout
	bash installation/verify.sh

install: ## Install on this Ubuntu host (requires sudo and INSTALL_USER)
	sudo bash installation/install.sh

semaphore-plan: ## Print the Semaphore provisioning plan without contacting the API
	$(PYTHON) -m infrastructure_manager.semaphore --config $(CONFIG)

semaphore-apply: ## Reconcile Semaphore resources (requires SEMAPHORE_API_TOKEN)
	$(PYTHON) -m infrastructure_manager.semaphore --config $(CONFIG) --apply

semaphore-report: ## Print the last provisioning report
	@cat reports/semaphore-provisioning.json 2>/dev/null || echo "no provisioning report yet"

clean: ## Remove local caches and generated reports
	rm -rf .pytest_cache .ansible
	rm -f reports/*.json reports/*.log
