#!/bin/bash

function main() {

    upgradeSystem
    
    # do some stuff

    cleanupDocker
}

source /tmp/resources/install_functions.sh
main