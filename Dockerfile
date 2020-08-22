FROM debian:jessie

RUN apt-get update \
    && apt-get install -y wget ghostscript build-essential libssl-dev libffi-dev python3 python3-pip python3-dev python3-venv

RUN cd $HOME && wget --no-check-certificate https://dl.xpdfreader.com/xpdf-tools-linux-4.02.tar.gz \
    && tar zxf xpdf-tools-linux-4.02.tar.gz && ln -s $HOME/xpdf-tools-linux-4.02/bin64/* /usr/bin/
