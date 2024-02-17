.PHONY: build
build:
	docker-compose run --rm funeraria sh -c "python manage.py collectstatic --noinput"

.PHONY: deploy
deploy:build
	docker-compose -f docker-compose-deploy.yml run --rm gcloud sh -c "gcloud app deploy --project funeraria-388607 --quiet"