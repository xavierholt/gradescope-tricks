FROM ubuntu:18.04

# This is not a good Dockerfile!
# It's designed to build even with my crappy rural internet.
# A better one would do all this in a single RUN command.

ENV DEBIAN_FRONTEND="noninteractive"
ENV TZ="Etc/UTC"

RUN echo 'APT::Acquire::Retries "3";' > /etc/apt/apt.conf.d/80-retries

RUN apt-get update
RUN apt-get install --no-install-recommends -y sudo
RUN apt-get install --no-install-recommends -y gcc g++
RUN apt-get install --no-install-recommends -y valgrind
RUN apt-get install --no-install-recommends -y python3 python3-pip
RUN apt-get install --no-install-recommends -y gdb
# RUN apt-get clean
# RUN rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache gradescope-utils
RUN useradd -MU student

RUN mkdir /autograder
WORKDIR /autograder
