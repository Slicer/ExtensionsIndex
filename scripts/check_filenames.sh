#!/bin/bash

set -eu
set -o pipefail

script_dir=$(cd $(dirname $0) || exit 1; pwd)

root_dir=$script_dir/..

cd $root_dir

msg="Looking for unexpected files"
echo "$msg"

unexpected_files=$(find . -mindepth 1 \( -type d \( \
  -path ./.circleci -o \
  -path ./.idea -o \
  -path ./.github -o \
  -path ./.git -o \
  -path ./ARCHIVE -o \
  -path ./scripts \
\) -o -type f \( \
  -name .pre-commit-config.yaml -o \
  -name .git-blame-ignore-revs  -o \
  -name README.md -o \
  -name "*.json" \
\)  \)  -prune -o -print)

for unexpected_file in $unexpected_files; do
  echo $unexpected_file
done
if [[ $unexpected_files != "" ]]; then
  echo "$msg - failed"
  exit 1
else
  echo "$msg - done"
fi
