FROM ubuntu

RUN mkdir /MediaServerGuard

COPY ./* /MediaServerGuard/

RUN apt update -y
RUN apt upgrade -y
RUN apt install python3 python3-pip git -y

RUN pip3 install -r /MediaServerGuard/linuxrequirements.txt


WORKDIR /MediaServerGuard
CMD ["python3", "app.py"]