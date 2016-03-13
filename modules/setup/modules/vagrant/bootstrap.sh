#!/usr/bin/env bash

function main {
  set -x
  apt-get update
  apt-get install -y nginx vim emacs postgresql-9.3 python-dev python-virtualenv

  install_docker
  if docker ps | grep elasticsearch; then
    echo "elasticsearch+kibna image already present, not redownloading"
  else
    docker pull nshou/elasticsearch-kibana
  fi

  if docker ps | grep elasticsearch; then
    echo "elasticsearch+kibana is already running, not relaunching"
  else
    docker run -d -p 9200:9200 -p 5601:5601 nshou/elasticsearch-kibana
  fi

  install_rvm

}

function install_docker {
  if docker --version | grep "Docker version"; then
    echo "already installed docker - not reinstalling"
  else
    curl -sSL https://get.docker.com/ | sh
  fi
  echo "adding vagrant to the docker user group"
  usermod -aG docker vagrant
}

function install_rvm {
  curl -sSL https://rvm.io/mpapis.asc | sudo gpg --import -
  \curl -sSL https://get.rvm.io | bash -s stable
}

main
