import os
import json
import time
import paho.mqtt.client as mqtt

MQTT_HOST = os.getenv('MQTT_HOST')
MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
MQTT_USER = os.getenv('MQTT_USER')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD')
MQTT_CLIENT = os.getenv('MQTT_CLIENT', 't2t2m2p2m2ha-dekala')
MQTT_QOS = int(os.getenv('MQTT_QOS', 1))

# from secrets import MQTT_HOST, MQTT_PORT, MQTT_USER, MQTT_PASSWORD, MQTT_CLIENT, MQTT_QOS

sage_switch_topic = 'zigbee2mqtt/Sage Switch 1/'
extra_bathroom_switch_topic = 'cmnd/tasmota_87F311/'

press_on_time = 0
press_on_count = 0
press_off_time = 0
press_off_count = 0

# publish() defaults to not retained in this project

def send_press_on():
    global press_on_count
    publish(sage_switch_topic + 'more_actions', payload='on_%d' % press_on_count)
    if press_on_count == 1:
        publish(extra_bathroom_switch_topic + 'Power1', payload='ON')
    elif press_on_count == 2:
        publish(extra_bathroom_switch_topic + 'Power2', payload='ON')
    elif press_on_count == 3:
        publish(extra_bathroom_switch_topic + 'Power3', payload='ON')
    else:
        print('screaming into the void')
    press_on_count = 0

def send_press_off():
    global press_off_count
    publish(sage_switch_topic + 'more_actions', payload='off_%d' % press_off_count)
    if press_off_count == 1:
        publish(extra_bathroom_switch_topic + 'Power1', payload='OFF')
    elif press_off_count == 2:
        publish(extra_bathroom_switch_topic + 'Power2', payload='OFF')
    elif press_off_count == 3:
        publish(extra_bathroom_switch_topic + 'Power3', payload='OFF')
    else:
        print('screaming into the void')
    press_off_count = 0

def millis():
    return round(time.monotonic() * 1000)

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print('Connected with result code '+str(rc))
    if rc == 0:
        client.subscribe(sage_switch_topic + '#')

def on_message(client, userdata, msg):
    global press_on_time
    global press_on_count
    global press_off_time
    global press_off_count

    payload_str = str(msg.payload.decode("utf-8"))
    if msg.topic == sage_switch_topic + 'action':
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