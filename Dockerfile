FROM python:3

ARG MON_DATA_PATH
ARG DB_PATH

RUN pip install websocket-client

COPY pyblitzortung/gatherer.py /opt/pyblitzortung/pyblitzortung.py

CMD ["/opt/pyblitzortung/pyblitzortung.py", "-d", "$DB_PATH", "-m", "$MON_DATA_PATH"]