FROM ubuntu

docker ps -a
docker images
docker images -a
docker images
docker run -ti --rm alpine:3.4 /bin/sh
docker run -ti --rm ubuntu:20.04

docker build -t name/image:version .
docker rmi $(docker images -q --filter "dangling=true")

sudo apt update
sudo apt install ghostscript

gs -sDEVICE=txtwrite -o pdf_dump2.txt test2.pdf
gs -sDEVICE=txtwrite -dFirstPage=192 -dLastPage=193 -o pdf_dump2.txt test.pdf
pdftotext -f 192 -l 193 -enc UTF-8 test.pdf

wget --no-check-certificate https://dl.xpdfreader.com/XpdfReader-linux32-4.02.run


wget --no-check-certificate https://dl.xpdfreader.com/xpdf-tools-linux-4.02.tar.gz
tar zxf xpdf-tools-linux-4.02.tar.gz
export PATH=/home/xpdf-tools-linux-4.02/bin64:$PATH
pdftotext -f 192 -l 193 -raw test2.pdf

gs -sDEVICE=txtwrite -dProvideUnicode -dExtractText -dFirstPage=192 -dLastPage=193 -o pdf_dump2.txt test.pdf
pdftotext -f 192 -l 193 -enc UTF-8 test.pdf
pdftohtml -f 192 -l 193 -enc UTF-8 test.pdf
pdftops

apt install 
sudo apt install -y build-essential libssl-dev libffi-dev python3 python3-pip python3-dev python3-venv
pip3 install pdfminer

pdf2txt.py -p 192,193 -o out.html test.pdf
pdftotext -f 578 -l 579 -enc UTF-8 algo.pdf
pdftotext -f 68 -l 68 -enc UTF-8 test.pdf