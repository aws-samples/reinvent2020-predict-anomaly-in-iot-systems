import boto3
import json
import datetime
import argparse
import time
import threading
import logging

from awscrt import io
from awscrt.mqtt import Connection, Client, QoS
from awscrt import awsiot_mqtt_connection_builder

import numpy as np

# Global Variables
TIME_FORMAT = '%Y%m%dT%H%M%SZ'
LOG = False
output_file = 'output.json'
mqtt_data = []
enable_cv_readings = False
enable_water_readings = False

logger = logging.getLogger("device_simulator.station_sim")

class sensor_station_sim:
    def __init__(self, mqtt_conn, building_id, config, topic_prefix):
        self.mqtt_client = mqtt_conn
        self.building_id = building_id
        self.config = config
        self.topic_prefix = topic_prefix
        self.measurement_counter = [0] * len(self.config['measurements'])
    
    def _publish(self, topic, msg):
        logger.debug('Topic: {}, Msg {}'.format(topic, msg))
        self.mqtt_client.publish(topic, msg)

    def _simulate_measurements(self):
        logger.info('Measurement generated at {}'.format(self.config['sensor_station_id']))
        topic = '{}/{}/{}'.format(self.topic_prefix, self.building_id, self.config['sensor_station_id'])
        for i, metric in enumerate(self.config['measurements']):
            if 'content' in metric:
                data_value = round(metric['content'][self.measurement_counter[i]], 4)
                if 'drift' in metric:
                    data_value += self.measurement_counter[i] * metric['drift']
                if 'scale' in metric:
                    data_value *= metric['scale']
                self.measurement_counter[i] += 1
                if self.measurement_counter[i] >= len(metric['content']):
                    self.measurement_counter[i] = 0
            elif ('mean' in metric and 'std' in metric):
                data_value = round(np.random.normal(metric['mean'], metric['std'], 1)[0], 4)
            payload = {
                'data_type': metric['type'],
                'unit': metric['unit'],
                'data_value': data_value,
                'measurement_timestamp': int(time.time_ns() // 1000000),
                'building_id': self.building_id,
                'sensor_station_id': self.config['sensor_station_id']
            }
            self._publish(topic, json.dumps(payload))

    def run_period_measurements(self):
        self._simulate_measurements()
        threading.Timer(self.config['measure_frequency'],
                        self.run_period_measurements).start()

    def start_simulation(self):
        logger.info('Simulation started for {}'.format(self.config['sensor_station_id']))
        self.run_period_measurements()