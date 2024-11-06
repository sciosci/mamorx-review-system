VERSION=v1
DOCKERUSER=hush205

build:
	docker build -f Dockerfile -t mamorx-service .

push:
	docker tag mamorx-service $(DOCKERUSER)/mamorx-service:$(VERSION)
	docker push $(DOCKERUSER)/mamorx-service:$(VERSION)
	docker tag mamorx-service $(DOCKERUSER)/mamorx-service:latest
	docker push $(DOCKERUSER)/mamorx-service:latest
