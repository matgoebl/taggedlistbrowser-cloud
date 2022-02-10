Tagged List Browser - Cloud Demo
================================
(c) 2021 Copyright: Matthias Goebl
e-mail: matthias dot goebl at goebl dot net

This is my flask-on-kubernetes evaluation.

Published under the Apache License 2.0.


Installation
------------

Expected environment variables
- KUBECONFIG: path to kubeconfig file
- KUBEURL: external base URL for ingress
- DOCKER_REGISTRY: host:port for docker registry


Install with static data set:

    make install


Install with dynamically updating data set (just a demo, look at "/id/www.example.com"):

    make datagenerator-companion


Tagged List UseCase
-------------------

src/model/* contains a set of files with lists, i.e. host names.
The lists are merged into a larger model.
The list items can be tagged, in this example with 'service' and 'user'.

The data set can be queried via a simple user interface provided via flask.
Alternatively the command line version taggedlistquery.sh can be used.


Integrated Ressources
---------------------

This project contains
- [jQuery](https://jquery.com/) under MIT license.
- [jQuery json-viewer](https://github.com/abodelot/jquery.json-viewer) under MIT License, patched to display mailto: links.
