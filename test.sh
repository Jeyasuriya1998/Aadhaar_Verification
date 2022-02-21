#!/usr/bin/env bash

cd .

git add .

DATE=$(date)

git commit -m "changes made on $DATE"

git push

osascript -e "dispaly notification 'pushed to remote' with title 'SUCCESS"