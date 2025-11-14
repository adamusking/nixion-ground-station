import time
import os
import json
import random
from dotenv import load_dotenv
from paho.mqtt import client as mqtt_client

load_dotenv()

broker = os.getenv("BROKER")
port = int(os.getenv("PORT"))
topic = os.getenv("TOPIC")
client_id = os.getenv("CLIENT_ID_1")
username = os.getenv("MQTT_USER")       
password = os.getenv("MQTT_PASSWORD")   

def get_data():
    data = {
        "host": client_id,
        "temperature": round(random.uniform(15, 35), 2),
        "humidity": round(random.uniform(20, 80), 2),
        "pressure": round(random.uniform(950, 1050), 2),
        "altitude": round(random.uniform(0, 1000), 2),
        "speed": round(random.uniform(0, 20), 2),
        "latitude": 48.6200,
        "longitude": 18.3330,
        "latitude_ground": 48.622576,
        "longitude_ground": 18.336452,
        "lora_status": 1,      
        "5.8ghz_status": 0,    
        "received_packets": random.randint(800, 1000),
        "lost_packets": random.randint(0, 50),
        "rssi": round(random.uniform(-90, -30), 2),
        "snr": round(random.uniform(5, 25), 2),
        "data_rate": round(random.uniform(1000, 50000), 2),
        "battery": round(random.uniform(20, 100), 2),
        "azimuth": round(random.uniform(0, 360), 2),      
        "elevation": round(random.uniform(-10, 90), 2)    
}
    return json.dumps(data)

connected = False

def connect_mqtt():
    def on_connect(client, userdata, flags, reasonCode, properties=None):
        global connected
        if reasonCode == 0:
            print("Connected to MQTT Broker!")
            connected = True
        else:
            print(f"Failed to connect, reason code {reasonCode}")

    client = mqtt_client.Client(client_id=client_id)
    client.username_pw_set(username=username, password=password)  
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def publish(client):
    global connected
    msg_count = 1
    while True:
        if connected:
            data = get_data()
            result = client.publish(topic, data)
            status = result[0]
            if status == 0:
                print(f"Sent message #{msg_count} to topic `{topic}`")
            else:
                print(f"Failed to send message to topic {topic}")
            msg_count += 1
        time.sleep(1)

def run():
    client = connect_mqtt()
    client.loop_start()
    publish(client)
    client.loop_stop()

if __name__ == '__main__':
    run()
 