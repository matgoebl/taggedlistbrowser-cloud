#IMAGE=$(shell basename $(PWD))
IMAGE=taggedlistbrowser
NAME=$(IMAGE)1
WEBUSER=demo
WEBPASS=Test-It!
PYTHON_MODULES=flask python-dotenv PyYAML gunicorn

HELM_OPTS=--set image.repository=$(DOCKER_REGISTRY)/$(IMAGE) --set image.tag=latest --set basicAuthUsers.$(WEBUSER)=$(WEBPASS) --set image.pullPolicy=Always
APP_URL:=$(shell echo "$(KUBEURL)/$(NAME)/" | sed -e "s|://|://$(WEBUSER):$(WEBPASS)@|")

all: image install wait ping

venv:
	virtualenv venv --python=python3 && . venv/bin/activate && pip3 install $(PYTHON_MODULES)

requirements.txt: venv
	. venv/bin/activate && pip3 freeze | grep -v pkg_resources==0.0.0 > requirements.txt

run:	venv
	. venv/bin/activate && cd src/ && python3 ./app.py

run-gunicorn:	venv
	. venv/bin/activate && cd src && gunicorn --bind 0.0.0.0:8888 --access-logfile - wsgi:app

clean:
	rm -rf venv requirements.txt
	-find -name __pycache__ -type d -exec rm -rf '{}' ';' 2>/dev/null

image: requirements.txt
	docker build -t $(IMAGE) .
	docker tag $(IMAGE) $(DOCKER_REGISTRY)/$(IMAGE)
	docker push $(DOCKER_REGISTRY)/$(IMAGE)

imagerun: requirements.txt
	docker build -t $(IMAGE) .
	docker run -it $(IMAGE)

install-dry:
	helm install --dry-run --debug $(HELM_OPTS) $(NAME) ./$(IMAGE)-helm

install: uninstall image
	helm lint ./$(IMAGE)-helm
	helm install $(HELM_OPTS) $(NAME) ./$(IMAGE)-helm

wait:
	sleep 15

uninstall:
	-helm uninstall $(NAME)

ping:
	curl -si "$(APP_URL)"

www:
	w3m -o confirm_qq=false "$(APP_URL)"

datagenerator-companion:
	cd datagenerator/ && make
	make HELM_OPTS="$(HELM_OPTS) --set companioncontainer.enabled=true --set companioncontainer.repository=$(DOCKER_REGISTRY)/datagenerator" install

.PHONY: all run run-gunicorn clean image imagerun install-dry install wail uninstall init ping www datawriter-companion
