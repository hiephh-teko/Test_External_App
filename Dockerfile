FROM vietanhs0817/python:3.6

WORKDIR /sample
ADD requirements.txt /sample/

RUN pip install -r requirements.txt

ADD . /sample/

RUN chmod a+x set_env.sh

RUN apt-get update && apt-get -y install cron

ADD ./bash/crontab /etc/cron.d/scan

RUN chmod 0644 /etc/cron.d/scan

RUN crontab /etc/cron.d/scan

RUN chmod a+x /sample/bash/*

RUN find /sample/bash -type d -exec chmod 755 {} \;

RUN touch /var/log/cron.log

CMD cron -f
