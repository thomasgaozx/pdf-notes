FROM debian:buster

RUN apt-get update \
    && apt-get install -y wget ghostscript build-essential libssl-dev \
    poppler-utils libffi-dev python3 python3-pip python3-dev python3-venv

RUN pip3 install Pillow numpy Flask

COPY img_service.py /root/

WORKDIR /root

CMD ["python3", "img_service.py"]
