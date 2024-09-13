FROM python:3

ARG MON_DATA_PATH
ARG DB_PATH

RUN pip install websocket-client

COPY pyblitzortung/gatherer.py /opt/pyblitzortung/pyblitzortung.py

ENTRYPOINT /opt/pyblitzortung/pyblitzortung.py --database-path $DB_PATH --metrics-path $MON_DATA_PATH