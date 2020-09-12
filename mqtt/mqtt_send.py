import paho.mqtt.client as mqtt
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
# The callback for when a PUBLISH message is received from the server.

client = mqtt.Client()
client.on_connect = on_connect
client.connect("localhost", 1883, 60)

    
for i in range(1, 10000):
    client.publish("eclipse", "Hello" + str(i), qos=0, retain=True)
    import time
    print("Published", i)
    time.sleep(0.1)
# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()

