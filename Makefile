IMAGE_NAME = birth-map-agent-demo:latest

.PHONY: build run login

login:
	@echo "Logging in to Artifactory docker registry"
	@if [ -z "$(ARTIFACTORY_DOCKER_USER)" ] || [ -z "$(ARTIFACTORY_DOCKER_PASSWORD)" ]; then \
		echo "ARTIFACTORY_DOCKER_USER and ARTIFACTORY_DOCKER_PASSWORD must be set (or use .env)"; exit 1; \
	fi
	@docker login $(ARTIFACTORY_DOCKER_REGISTRY) -u "$(ARTIFACTORY_DOCKER_USER)" -p "$(ARTIFACTORY_DOCKER_PASSWORD)"

build: login
	@echo "Building docker image using BASE_IMAGE=$(BASE_IMAGE)"
	@docker build \
		--build-arg BASE_IMAGE=$(BASE_IMAGE) \
		$(if $(PIP_INDEX_URL),--build-arg PIP_INDEX_URL=$(PIP_INDEX_URL)) \
		$(if $(PIP_EXTRA_INDEX_URL),--build-arg PIP_EXTRA_INDEX_URL=$(PIP_EXTRA_INDEX_URL)) \
		-t $(IMAGE_NAME) .

run:
	@echo "Running container on port 8000"
	@docker run --rm -p 8000:8000 --env-file .env $(IMAGE_NAME)
