#!/bin/bash
set -eux

function main() {
    mkdir -p /usr/share/man/man1
    apt update && apt -qqy install openjdk-11-jre-headless
    npm install -g --save-dev shadow-cljs

    cleanupDocker
}

source /tmp/install_functions.sh
main