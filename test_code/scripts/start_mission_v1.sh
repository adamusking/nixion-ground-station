#!/bin/bash
set -e

cd /home/nixctrl/cansat/nixion-ground-station
source venv/bin/activate

bash test_code/telegraf/start_telegraf_v2.sh &
sleep 3
python3 test_code/lora/mqtt_publisher_test.py &

wait
