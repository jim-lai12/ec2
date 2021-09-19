FROM python:2.7
WORKDIR /app

ADD . /app

RUN pip install -r requirements.txt \
&& mkdir /root/.aws \
&& touch /root/.aws/credentials \
&& touch /root/.aws/config \

CMD ["/app/run.sh","start"]
