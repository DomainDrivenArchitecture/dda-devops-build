adjust version no in build.py to release version no.
git commit -am "release"
git tag -am "release" [release version no]
git push --follow-tags
increase version no in build.py
git commit -am "version bump"
git push
pip3 install --upgrade --user ddadevops