#IMAGE=$(shell basename $(PWD))
IMAGE=taggedlistbrowser
NAME=$(IMAGE)1
NAMESPACE=default
WEBUSER=demo
WEBPASS_CMD=echo 'Test-It!'
#WEBPASS_CMD=aws secretsmanager --profile someprofile get-secret-value --secret-id $(WEBUSER) --no-cli-pager --output json | jq -r .SecretString
WEBPASS=$(shell $(WEBPASS_CMD))

PYTHON_MODULES=flask python-dotenv PyYAML gunicorn jsonpath-ng
VENV=.venv
export BUILDTAG:=$(shell date +%Y%m%d.%H%M%S)

HELM_OPTS:=--set image.repository=$(DOCKER_REGISTRY)/$(IMAGE) --set image.tag=$(BUILDTAG) --set ingresspath.basicauthsecret=basicauth-$(IMAGE) --set image.pullPolicy=Always
APP_URL:=$(shell echo "$(KUBEURL)/$(NAME)/" | sed -e "s|://|://$(WEBUSER):$(WEBPASS)@|")

all: install-with-datagenerator wait ping

requirements.txt:
	python3 -m pip install --user virtualenv
	python3 -m virtualenv $(VENV) && . $(VENV)/bin/activate && python3 -m pip install --upgrade pip && python3 -m pip install $(PYTHON_MODULES)
	. $(VENV)/bin/activate && python3 -m pip freeze --all | grep -v pkg_resources==0.0.0 > requirements.txt

$(VENV): requirements.txt
	python3 -m pip install --user virtualenv
	python3 -m virtualenv $(VENV) && . $(VENV)/bin/activate && python3 -m pip install -r requirements.txt
	touch $(VENV)

venv: $(VENV)

run: venv
	. $(VENV)/bin/activate && cd src/ && FLASK_ENV=development VERBOSE=2 python3 ./app.py

run-gunicorn: $(VENV)
	. $(VENV)/bin/activate && cd src && gunicorn --bind 0.0.0.0:8888 --access-logfile - wsgi:app

clean:
	rm -rf $(VENV)
	find -iname "*.pyc" -delete 2>/dev/null || true
	find -name __pycache__ -type d -exec rm -rf '{}' ';' 2>/dev/null || true

distclean: clean
	rm -rf requirements.txt

image: $(VENV)
	docker build --build-arg BUILDTAG=$(BUILDTAG) -t $(IMAGE) .
	docker tag $(IMAGE) $(DOCKER_REGISTRY)/$(IMAGE):$(BUILDTAG)
	docker push $(DOCKER_REGISTRY)/$(IMAGE):$(BUILDTAG)

imagerun: $(VENV)
	docker build -t $(IMAGE) .
	docker run -it $(IMAGE)

install-dry:
	helm install --dry-run --debug $(HELM_OPTS) --namespace=$(NAMESPACE) $(NAME) ./taggedlistbrowser-helm

install: image basicauth_secret_update
	helm lint ./taggedlistbrowser-helm
	helm upgrade --install $(HELM_OPTS) --namespace=$(NAMESPACE) $(NAME) ./taggedlistbrowser-helm

basicauth_secret_update:
	-kubectl create namespace $(NAMESPACE)
	$(WEBPASS_CMD) | htpasswd -i -n "$(WEBUSER)" | kubectl --namespace=$(NAMESPACE) create secret generic basicauth-$(IMAGE) --from-file=auth=/dev/stdin --dry-run=client --output=yaml --save-config | kubectl apply -f -

wait:
	sleep 15

uninstall:
	-helm uninstall --namespace=$(NAMESPACE) $(NAME)
	-kubectl --namespace=$(NAMESPACE) delete secret basicauth-$(IMAGE)

ping:
	curl -si "$(APP_URL)"

www:
	w3m -o confirm_qq=false "$(APP_URL)"

http_yaml:
	curl -si "$(APP_URL)?i=*&t=.&q=&f=&o=yaml"

install-with-datagenerator:
	cd datagenerator/ && make
	make HELM_OPTS="$(HELM_OPTS) --set companioncontainer.enabled=true --set companioncontainer.repository=$(DOCKER_REGISTRY)/datagenerator" install

get-javascript-dependencies:
	cd src/static/ && wget https://code.jquery.com/jquery-3.6.0.min.js
	cd src/static/ && wget https://raw.githubusercontent.com/abodelot/jquery.json-viewer/master/json-viewer/jquery.json-viewer.js
	cd src/static/ && wget https://raw.githubusercontent.com/abodelot/jquery.json-viewer/master/json-viewer/jquery.json-viewer.css

.PHONY: all run run-gunicorn clean distclean image imagerun install-dry install wait uninstall init ping www install-with-datagenerator
