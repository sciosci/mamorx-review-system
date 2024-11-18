PAPERMAGE_VERSION=v1
MAMORX_VERSION=v1
WEB_VERSION=v1
DOCKERUSER=hush205

build-papermage:
	docker build -f services/papermage_service/Dockerfile -t papermage-service .

push-papermage:
	docker tag papermage-service $(DOCKERUSER)/papermage-service:$(VERSION)
	docker push $(DOCKERUSER)/papermage-service:$(VERSION)
	docker tag papermage-service $(DOCKERUSER)/papermage-service:latest
	docker push $(DOCKERUSER)/papermage-service:latest


build-mamorx:
	docker build -f services/mamorx_service/Dockerfile -t mamorx-service .

push-mamorx:
	docker tag mamorx-service $(DOCKERUSER)/mamorx-service:$(VERSION)
	docker push $(DOCKERUSER)/mamorx-service:$(VERSION)
	docker tag mamorx-service $(DOCKERUSER)/mamorx-service:latest
	docker push $(DOCKERUSER)/mamorx-service:latest


build-web:
	docker build -f services/web_service/Dockerfile -t web-service .

push-web:
	docker tag web-service $(DOCKERUSER)/web-service:$(VERSION)
	docker push $(DOCKERUSER)/web-service:$(VERSION)
	docker tag web-service $(DOCKERUSER)/web-service:latest
	docker push $(DOCKERUSER)/web-service:latest


build-mamorx-worker:
	docker build -f services/mamorx_worker/Dockerfile -t mamorx-worker .

push-mamorx-worker:
	docker tag mamorx-worker $(DOCKERUSER)/mamorx-worker:$(VERSION)
	docker push $(DOCKERUSER)/mamorx-worker:$(VERSION)
	docker tag mamorx-worker $(DOCKERUSER)/mamorx-worker:latest
	docker push $(DOCKERUSER)/mamorx-worker:latest
