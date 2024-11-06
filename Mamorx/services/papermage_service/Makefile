VERSION=v1
DOCKERUSER=hush205

build:
	docker build -f Dockerfile -t papermage-service .

push:
	docker tag papermage-service $(DOCKERUSER)/papermage-service:$(VERSION)
	docker push $(DOCKERUSER)/papermage-service:$(VERSION)
	docker tag papermage-service $(DOCKERUSER)/papermage-service:latest
	docker push $(DOCKERUSER)/papermage-service:latest
