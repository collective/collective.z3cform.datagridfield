#!/bin/sh

# see https://community.plone.org/t/not-using-bootstrap-py-as-default/620
rm -rf ./lib ./include ./local ./bin
virtualenv --clear .
./bin/pip install -r requirements.txt
./bin/buildout
