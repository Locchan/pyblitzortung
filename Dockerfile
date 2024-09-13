FROM python:3

ARG MON_DATA_PATH
ARG DB_PATH

ENV MON_DATA_PATH ${MON_DATA_PATH}
ENV DB_PATH ${DB_PATH}

RUN pip install websocket-client PyMySQL 

COPY pyblitzortung/gatherer.py /opt/pyblitzortung/pyblitzortung.py

CMD python -u /opt/pyblitzortung/pyblitzortung.py -d ${DB_PATH} -m ${MON_DATA_PATH}