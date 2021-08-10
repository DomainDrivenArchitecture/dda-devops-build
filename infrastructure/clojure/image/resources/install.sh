#!/bin/bash
set -eux

function main() {
    upgradeSystem

    mkdir -p /usr/share/man/man1
    apt -qqy install openjdk-11-jre-headless leiningen curl build-essential libz-dev zlib1g-dev
    
    # shadow-cljs
    npm install -g --save-dev shadow-cljs

    # kubeconform & graalvm
    curl -Lo /tmp/kubeconform-v0.4.7.tar.gz https://github.com/yannh/kubeconform/releases/download/v0.4.7/kubeconform-linux-amd64.tar.gz
    curl -Lo /tmp/graalvm-ce-java11-linux-amd64-21.2.0.tar.gz https://github.com/graalvm/graalvm-ce-builds/releases/download/vm-21.2.0/graalvm-ce-java11-linux-amd64-21.2.0.tar.gz

    cd /tmp
    sha256sum --check CHECKSUMS

    tar -xf /tmp/kubeconform-v0.4.7.tar.gz
    cp kubeconform /usr/local/bin

    tar -xzf graalvm-ce-java11-linux-amd64-21.2.0.tar.gz
    mv graalvm-ce-java11-21.2.0 /usr/lib/jvm/
    ln -s /usr/lib/jvm/graalvm-ce-java11-21.2.0 /usr/lib/jvm/graalvm
    ln -s /usr/lib/jvm/graalvm/bin/gu /usr/local/bin

    update-alternatives --install /usr/bin/java java /usr/lib/jvm/graalvm/bin/java 2

    gu install native-image
    ln -s /usr/lib/jvm/graalvm/bin/native-image /usr/local/bin

    cleanupDocker
}

source /tmp/install_functions.sh
main