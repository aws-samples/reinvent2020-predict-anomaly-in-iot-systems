import boto3
import json
import datetime
import argparse
import time
import logging

from awscrt import io
from awscrt.mqtt import Connection, Client, QoS
from awscrt import awsiot_mqtt_connection_builder

from station_sim import *
logging.basicConfig(level=logging.DEBUG,
                    format='%(filename)s: '
                    '%(levelname)s: '
                    '%(funcName)s(): '
                    '%(lineno)d:\t'
                    '%(message)s')
logger = logging.getLogger("device_simulator")

# Global Variables
TIME_FORMAT = '%Y%m%dT%H%M%SZ'
output_file = 'output.json'

class iot_client:
    def __init__(self, region, profile):
        # Boto3 Session used for creating IoT Client
        self.session = boto3.Session(region_name=region, profile_name=profile)
        # Setup the Iot Core Client
        self.client = self.session.client('iot-data')

    def publish(self, topic, payload):
        # print(payload)
        logger.info('{} -> {}'.format(topic, json.dumps(payload, indent=4)))
        self.client.publish(
            topic=topic,
            qos=1,
            payload=payload
        )

def create_simulation(config_file, mqtt_conn, topic_prefix):

    # Read the JSON into Python
    with open(config_file) as f:
        simulation_config = json.load(f)

    simulated_stations = []
    for bldg in simulation_config['buildings']:
        for ss in bldg['sensor_stations']:
            ss_sim = sensor_station_sim(mqtt_conn, bldg['building_id'], ss, topic_prefix)
            ss_sim.start_simulation()
            simulated_stations.append(ss_sim)
    return simulated_stations


def main():
    parser = argparse.ArgumentParser()
    # Arguments for testing IoT Core
    parser.add_argument('-p', '--prefix', type=str,
                        help='Prefix used for the IoT Core topic', default="reInvent2020")
    parser.add_argument('-r', '--region', type=str,
                        help='Region to publish messages to IoT Core', default = 'us-west-2')
    parser.add_argument('-a', '--aws_profile', type=str, default='default',
                        help='AWS profile to use for credentials. Default="default"')
    parser.add_argument('-f', '--file', required=True, type=str,
                        help='Configuration file for this simulation')
    args = parser.parse_args()

    # start device simulation mqtt client
    mqtt_conn = iot_client(args.region, args.aws_profile)
    station_sim_list = create_simulation(args.file, mqtt_conn, args.prefix)
    while(True):
        time.sleep(3600)

if __name__ == '__main__':
    main()
