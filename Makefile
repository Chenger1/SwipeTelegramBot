init-db:
	docker-compose exec bot aerich init -t loader.TORTOISE_ORM
	docker-compose exec bot aerich init-db

migrate-db:
	docker-compose exec bot aerich migrate
	docker-compose exec bot aerich upgade


compile:
	docker-compose exec bot pybabel compile -d locales -D swipebot
