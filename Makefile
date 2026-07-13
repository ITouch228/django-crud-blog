VENV = .venv

ifeq ($(OS),Windows_NT)
	BIN = $(VENV)/Scripts
else
	BIN = $(VENV)/bin
endif

PYTHON = $(BIN)/python
RUFF = $(BIN)/ruff

.DEFAULT_GOAL := help

.PHONY: help
help: ## Показать список команд
	@echo Доступные команды:
	@echo   install        Установить зависимости
	@echo   run            Запустить сервер разработки
	@echo   migrate        Применить миграции
	@echo   makemigrations Создать миграции
	@echo   createsuperuser Создать суперпользователя
	@echo   test           Запустить тесты
	@echo   lint           Проверить код линтером ruff check
	@echo   format         Форматировать код ruff format
	@echo   fix            Исправить авто-ошибки и отформатировать
	@echo   check          Линтер + тесты
	@echo   clean          Очистить временные файлы

.PHONY: install
install: ## Установить зависимости
	$(PYTHON) -m pip install -r requirements.txt -r requirements-dev.txt

.PHONY: run
run: ## Запустить сервер разработки
	$(PYTHON) manage.py runserver

.PHONY: migrate
migrate: ## Применить миграции
	$(PYTHON) manage.py migrate

.PHONY: makemigrations
makemigrations: ## Создать миграции
	$(PYTHON) manage.py makemigrations

.PHONY: createsuperuser
createsuperuser: ## Создать суперпользователя
	$(PYTHON) manage.py createsuperuser

.PHONY: test
test: ## Запустить тесты
	$(PYTHON) manage.py test

.PHONY: lint
lint: ## Проверить код линтером (ruff check)
	$(RUFF) check .

.PHONY: format
format: ## Форматировать код (ruff format)
	$(RUFF) format .

.PHONY: fix
fix: ## Исправить авто-ошибки и отформатировать (ruff check --fix + ruff format)
	$(RUFF) check . --fix
	$(RUFF) format .

.PHONY: check
check: ## Линтер + тесты
	$(RUFF) check .
	$(PYTHON) manage.py test

.PHONY: clean
clean: ## Очистить временные файлы
	$(PYTHON) -c "import shutil, pathlib; [shutil.rmtree(p) for p in pathlib.Path('.').rglob('__pycache__')]; [shutil.rmtree(p, ignore_errors=True) for p in ('.pytest_cache', '.ruff_cache') if p]"
