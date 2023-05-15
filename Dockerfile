FROM python:3.10-alpine

ENV PYTHONUNBUFFERED=1
RUN apk add --no-cache openssh \
    && pip install -U pip \
    && rm -rf /var/cache/apk/*
COPY . .
RUN pip install -r requirements.txt
EXPOSE 22
ENTRYPOINT ["/ec2_ssh_exec.py"]