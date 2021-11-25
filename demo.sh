#! /bin/bash

# This script runs the example tests.
# It'll build a Docker image when first run.

dot="$(cd "$(dirname "$0")" && pwd)"

if docker image inspect autograder &> /dev/null; then
  : Image already exists, no need to rebuild.
else
  docker build --tag autograder "$dot"
fi

docker run --rm \
  -v "$dot/source:/autograder/source:ro" \
  -v "$dot/submission:/autograder/submission:ro" \
  -v "$dot/results:/autograder/results" \
  autograder \
  /autograder/source/run_autograder readonly
python3 format-results.py
