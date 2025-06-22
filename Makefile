PROJECT_NAME = qa-tools
SERVICE_NAME = app
CONTAINER_NAME = $(PROJECT_NAME)-$(SERVICE_NAME)

.PHONY: start stop rebuild purge black ruff mypy pytest

start:
	docker compose up -d

stop:
	docker compose down

rebuild:
	docker compose build --no-cache

purge:
	docker compose down --volumes --remove-orphans
	docker image rm $(PROJECT_NAME)-$(SERVICE_NAME):latest || true

shell:
	docker exec -it $(CONTAINER_NAME) sh

test:
	docker exec -it $(CONTAINER_NAME) pytest

black:
	docker exec -it $(CONTAINER_NAME) black app

ruff:
	docker exec -it $(CONTAINER_NAME) ruff check app --fix

mypy:
	docker exec -it $(CONTAINER_NAME) mypy app
