help: ## make [target]
	@echo ""
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'
	@echo

develop:  ## Build Docker image for tests
	@echo "--> Build Docker image for tests."
	docker-compose --file docker/development/docker-compose.yml build

full-develop:
	@echo "--> Build Docker image for tests."
	docker-compose --file docker/development/docker-compose.yml build --no-cache

test: ## Run all tests (pytest) inside docker.
	@echo "--> Testing on Docker."
	docker-compose --file docker/development/docker-compose.yml run --rm test py.test -s --cov-report term --cov-report html

bash: ## Run bash for container.
	@echo "--> Starting bash"
	docker-compose --file docker/development/docker-compose.yml run --rm test bash
