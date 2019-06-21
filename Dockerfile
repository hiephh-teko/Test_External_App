FROM vietanhs0817/python:3.6

WORKDIR /sample
ADD requirements.txt /sample/

RUN pip install --no-cache-dir -r requirements.txt

ADD . /sample/

ADD ./bash/crontab /etc/cron.d/scan

RUN chmod 0644 /etc/cron.d/scan

RUN crontab /etc/cron.d/scan

RUN chmod 777 -R /sample/bash/

RUN find /sample/bash -type d -exec chmod 755 {} \;

RUN touch /var/log/cron.log

CMD crond -f
