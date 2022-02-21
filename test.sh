#!/usr/bin/env bash

cd .

git add .

DATE=$(date +%d/%B/%Y)
TIME=$(date +%T)

git commit -m "changes made on $DATE $TIME"

git push
