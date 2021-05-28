#!/bin/bash
set -eux

function main() {
    upgradeSystem

    mkdir -p /usr/share/man/man1
    apt -qqy install openjdk-11-jre-headless leiningen curl

    curl -Lo /tmp/kubeconform.tar.gz https://github.com/yannh/kubeconform/releases/download/v0.4.7/kubeconform-linux-amd64.tar.gz
    
    cd /tmp
    sha256sum --check CHECKSUMS

    tar -xf /tmp/kubeconform.tar.gz
    cp kubeconform /usr/local/bin

    cleanupDocker
}

source /tmp/install_functions.sh
main