SECRETS_DIR := "./.secrets"

.PHONY: all
all: help

.PHONY: help
help:
	@echo "Commands: "
	@echo "secrets - create secrets"
	@echo "redeploy - pull updates, rebuild and rerun docker containersg"

.PHONY: secrets
secrets:
	mkdir -p $(SECRETS_DIR)/bot $(SECRETS_DIR)/mongo
	touch $(SECRETS_DIR)/bot/access_token $(SECRETS_DIR)/bot/group_id
	touch $(SECRETS_DIR)/mongo/username $(SECRETS_DIR)/mongo/password

.PHONY: redeploy
	git pull && docker compose build && docker copmpose down && docker compose up -d