# dda-devops-build

[![Slack](https://img.shields.io/badge/chat-clojurians-green.svg?style=flat)](https://clojurians.slack.com/messages/#dda-pallet/) | [<img src="https://meissa-gmbh.de/img/community/Mastodon_Logotype.svg" width=20 alt="team@social.meissa-gmbh.de"> team@social.meissa-gmbh.de](https://social.meissa-gmbh.de/@team) | [Website & Blog](https://domaindrivenarchitecture.org)

# Setup
```
sudo apt install python3-pip
#sudo pip3 install pip3 --upgrade
pip3 install pybuilder python-terraform ddadevops --user
pip3 install boto3 --user
export PATH=$PATH:~/.local/bin
```

# Update lib
pip3 install --pre ddadevops==0.4.0.dev0 --user

# Snapshot
1. pyb publish upload
2. Versions nr in build.py: hochzählen, *.dev0 anfügen
3. sudo pip3 install --pre ddadevops==0.4.0.dev0 --user


# Release
1. Versions nr in build.py: *.dev0 entfernen
1. git commit -m "release"
2. git tag [version]
3. pyb publish upload
4. git push && git push --tag
5. Versions nr in build.py: hochzählen, *.dev0 anfügen
7. git commit & push
8. sudo pip3 install --pre ddadevops==0.4.0.dev0 --user

## License

Copyright © 2019 meissa GmbH
Licensed under the [Apache License, Version 2.0](LICENSE) (the "License")
