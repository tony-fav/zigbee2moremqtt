FROM python:3-alpine
ADD ./zigbee2moremqtt.py /
RUN pip install paho.mqtt
CMD [ "python", "./zigbee2moremqtt.py" ]