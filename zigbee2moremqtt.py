import os
import json
import time
import paho.mqtt.client as mqtt

MQTT_HOST = os.getenv('MQTT_HOST')
MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
MQTT_USER = os.getenv('MQTT_USER')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD')
MQTT_CLIENT = os.getenv('MQTT_CLIENT', 'zigbee2moremqtt')
MQTT_QOS = int(os.getenv('MQTT_QOS', 1))
SAGE_SWITCH_TOPIC = os.getenv('SAGE_SWITCH_TOPIC')

ON_1_PRESS_TOPIC = os.getenv('ON_1_PRESS_TOPIC', '')
ON_2_PRESS_TOPIC = os.getenv('ON_2_PRESS_TOPIC', '')
ON_3_PRESS_TOPIC = os.getenv('ON_3_PRESS_TOPIC', '')
ON_1_PRESS_PAYLOAD = os.getenv('ON_1_PRESS_PAYLOAD', '')
ON_2_PRESS_PAYLOAD = os.getenv('ON_2_PRESS_PAYLOAD', '')
ON_3_PRESS_PAYLOAD = os.getenv('ON_3_PRESS_PAYLOAD', '')

OFF_1_PRESS_TOPIC = os.getenv('OFF_1_PRESS_TOPIC', '')
OFF_2_PRESS_TOPIC = os.getenv('OFF_2_PRESS_TOPIC', '')
OFF_3_PRESS_TOPIC = os.getenv('OFF_3_PRESS_TOPIC', '')
OFF_1_PRESS_PAYLOAD = os.getenv('OFF_1_PRESS_PAYLOAD', '')
OFF_2_PRESS_PAYLOAD = os.getenv('OFF_2_PRESS_PAYLOAD', '')
OFF_3_PRESS_PAYLOAD = os.getenv('OFF_3_PRESS_PAYLOAD', '')

# from secrets import MQTT_HOST, MQTT_PORT, MQTT_USER, MQTT_PASSWORD, MQTT_CLIENT, MQTT_QOS, SAGE_SWITCH_TOPIC, ON_1_PRESS_TOPIC, ON_2_PRESS_TOPIC, ON_3_PRESS_TOPIC, OFF_1_PRESS_TOPIC, OFF_2_PRESS_TOPIC, OFF_3_PRESS_TOPIC, ON_1_PRESS_PAYLOAD, ON_2_PRESS_PAYLOAD, ON_3_PRESS_PAYLOAD, OFF_1_PRESS_PAYLOAD, OFF_2_PRESS_PAYLOAD, OFF_3_PRESS_PAYLOAD

press_on_time = 0
press_on_count = 0
press_off_time = 0
press_off_count = 0

# publish() defaults to not retained in this project

def send_press_on():
    global press_on_count
    publish(SAGE_SWITCH_TOPIC + 'more_actions', payload='on_%d' % press_on_count)
    if press_on_count == 1:
        if ON_1_PRESS_TOPIC: publish(ON_1_PRESS_TOPIC, payload=ON_1_PRESS_PAYLOAD)
    elif press_on_count == 2:
        if ON_2_PRESS_TOPIC: publish(ON_2_PRESS_TOPIC, payload=ON_2_PRESS_PAYLOAD)
    elif press_on_count == 3:
        if ON_3_PRESS_TOPIC: publish(ON_3_PRESS_TOPIC, payload=ON_3_PRESS_PAYLOAD)
    else:
        print('screaming into the void')
    press_on_count = 0

def send_press_off():
    global press_off_count
    publish(SAGE_SWITCH_TOPIC + 'more_actions', payload='off_%d' % press_off_count)
    if press_off_count == 1:
        if OFF_1_PRESS_TOPIC: publish(OFF_1_PRESS_TOPIC, payload=OFF_1_PRESS_PAYLOAD)
    elif press_off_count == 2:
        if OFF_2_PRESS_TOPIC: publish(OFF_2_PRESS_TOPIC, payload=OFF_2_PRESS_PAYLOAD)
    elif press_off_count == 3:
        if OFF_3_PRESS_TOPIC: publish(OFF_3_PRESS_TOPIC, payload=OFF_3_PRESS_PAYLOAD)
    else:
        print('screaming into the void')
    press_off_count = 0

def millis():
    return round(time.monotonic() * 1000)

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print('Connected with result code '+str(rc))
    if rc == 0:
        client.subscribe(SAGE_SWITCH_TOPIC + '#')

def on_message(client, userdata, msg):
    global press_on_time
    global press_on_count
    global press_off_time
    global press_off_count

    payload_str = str(msg.payload.decode("utf-8"))
    if msg.topic == SAGE_SWITCH_TOPIC + 'action':
        if payload_str == 'on':
            press_on_count += 1
            press_on_time = millis()
            if press_off_count > 0:
                send_press_off()
        elif payload_str == 'off':
            press_off_count += 1
            press_off_time = millis()
            if press_on_count > 0:
                send_press_on()

client = mqtt.Client(MQTT_CLIENT)
client.username_pw_set(MQTT_USER , MQTT_PASSWORD)
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_HOST, port=MQTT_PORT)

# Redefine Publish with The QOS Setting
def publish(topic, payload=None, qos=MQTT_QOS, retain=False, properties=None):
    print('%s: %s' % (topic, payload))
    client.publish(topic, payload=payload, qos=qos, retain=retain, properties=properties)

client.loop_start()

press_timeout = 1000

while True:
    if (press_on_count > 0) and (millis()-press_on_time > press_timeout):
        send_press_on()

    if (press_off_count > 0) and (millis()-press_off_time > press_timeout):
        send_press_off()