# dda-devops-build

[![Slack](https://img.shields.io/badge/chat-clojurians-green.svg?style=flat)](https://clojurians.slack.com/messages/#dda-pallet/) | [<img src="https://meissa-gmbh.de/img/community/Mastodon_Logotype.svg" width=20 alt="team@social.meissa-gmbh.de"> team@social.meissa-gmbh.de](https://social.meissa-gmbh.de/@team) | [Website & Blog](https://domaindrivenarchitecture.org)


# Release
1. Versions nr in build.py: *.dev0 entfernen
1. git commit -m "release"
2. git tag [version]
3. pyb publish upload
4. git push -t
5. Versions nr in build.py: hochzählen, *.dev0 anfügen
7. git commit & push
8. sudo pip3 install ddadevops==0.3.4.dev1 --pre

## License

Copyright © 2019 meissa GmbH
Licensed under the [Apache License, Version 2.0](LICENSE) (the "License")
