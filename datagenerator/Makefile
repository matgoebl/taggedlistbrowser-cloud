IMAGE=$(shell basename $(PWD))

all: image

clean:

image:
	docker build -t $(IMAGE) .
	docker tag $(IMAGE) $(DOCKER_REGISTRY)/$(IMAGE)
	docker push $(DOCKER_REGISTRY)/$(IMAGE)

imagerun:
	docker build -t $(IMAGE) .
	docker run -it $(IMAGE)

.PHONY: all run clean image imagerun install-dry install wail uninstall init ping
