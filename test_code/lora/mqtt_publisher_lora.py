import time, random
import os
import csv
import json
import struct
from datetime import datetime
from dotenv import load_dotenv
from paho.mqtt import client as mqtt_client
from lora_test import receive_packets, lora

env_path = "/home/nixctrl/cansat/nixion-ground-station/test_code/.env"

load_dotenv(env_path)

broker = os.getenv("BROKER")
port = int(os.getenv("PORT"))
topic = os.getenv("TOPIC")
client_id = os.getenv("CLIENT_ID_1")
username = os.getenv("MQTT_USER")       
password = os.getenv("MQTT_PASSWORD")   

header_names = ["time","packetID","temperature","humidity","pressure","altitude","speed",
                "latitude_cansat","longitude_cansat","latitude_ground","longitude_ground",
                "battery","lora_rssi","lora_snr","lora_data_rate","lora_transmit_time","lora_status",
                "received_packets","lost_packets","azimuth","elevation"]

file_exists = os.path.isfile('/srv/ftp/data/data_local.csv')
if not file_exists:
    with open('/srv/ftp/data/data_local.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header_names)
        writer.writeheader()

connected = False
lora_status = 0
received_packets = 0
lost_packets = 0
last_packet_id = None

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

def publish_mqtt(client, data, msg_count):
    if connected:
        data_json = json.dumps(data)
        result = client.publish(topic, data_json)
        status = result[0]
        if status == 0:
            print("\n---Publishing to MQTT---")
            print(f"Sent message #{msg_count} to topic `{topic}`")
        else:
            print(f"Failed to send message to topic {topic}")

def main():
    client = connect_mqtt()
    client.loop_start()

    telemetry_format = '<H H H H H H L L L L B'
    telemetry_size = struct.calcsize(telemetry_format)
    msg_count = 1
    global received_packets, lost_packets, last_packet_id, lora_status

    while True:
        print("\n---RECEIVING---")
        raw_data = receive_packets()
        byte_array = bytearray(raw_data)
        print(f"Bytearray: {byte_array}")

        now = datetime.now()
        receive_time = now.isoformat()
        lora_status = 1

        unpacked = struct.unpack(telemetry_format, byte_array[:telemetry_size])
        packetID,temperature,humidity,pressure,altitude,speed,latitude_cansat,longitude_cansat,latitude_ground,longitude_ground,battery = unpacked

        temperature /= 100
        humidity /= 100
        pressure /= 10
        altitude /= 100
        speed /= 100
        latitude_cansat /= 1000000
        longitude_cansat /= 1000000
        latitude_ground /= 1000000
        longitude_ground /= 1000000

        print(f"""
Packet ID: {packetID}
Temperature: {temperature:.2f} °C
Humidity: {humidity:.2f} %
Pressure: {pressure:.2f} hPa
Altitude: {altitude:.2f} m
Speed: {speed:.2f} m/s
Latitude (CanSat): {latitude_cansat:.6f}
Longitude (CanSat): {longitude_cansat:.6f}
Latitude (Ground): {latitude_ground:.6f}
Longitude (Ground): {longitude_ground:.6f}
Battery: {battery} %
""")

        ack = f"ACK{int(packetID)}"
        ack_list = [ord(c) for c in ack]

        print("\n---TRANSMITTING ACK---")
        time.sleep(0.5)
        lora.beginPacket()
        lora.write(ack_list, len(ack_list))
        lora.endPacket()
        lora.wait()
        print(f"Sent ACK: {ack}")
        print("Transmit time: {0:.2f} ms | Data rate: {1:.2f} byte/s".format(
            lora.transmitTime(), lora.dataRate()))

        if last_packet_id is None:
            received_packets += 1
            last_packet_id = packetID
        else:
            gap = packetID - last_packet_id - 1
            if gap > 0:
                lost_packets += gap
            received_packets += 1
            last_packet_id = packetID

        data = {
            "time": receive_time,
            "packetID": packetID,
            "temperature": temperature,
            "humidity": humidity,
            "pressure": pressure,
            "altitude": altitude,
            "speed": speed,
            "latitude_cansat": latitude_cansat,
            "longitude_cansat": longitude_cansat,
            "latitude_ground": latitude_ground,
            "longitude_ground": longitude_ground,
            "battery": battery,
            "lora_rssi": lora.packetRssi(),
            "lora_snr": lora.snr(),
            "lora_data_rate": lora.dataRate(),
            "lora_transmit_time": lora.transmitTime(),
            "lora_status": lora_status,
            "received_packets": received_packets,
            "lost_packets": lost_packets,
            "azimuth": round(random.uniform(0, 360), 2),
            "elevation": round(random.uniform(-10, 90), 2)
        }

        with open('/srv/ftp/data/data_local.csv', 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=header_names)
            writer.writerow(data)

        publish_mqtt(client, data, msg_count)
        msg_count += 1
        

if __name__ == "__main__":
    main()