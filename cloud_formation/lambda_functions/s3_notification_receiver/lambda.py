import boto3
import logging
import json
import os
import base64

logging.basicConfig(level=logging.DEBUG,
                    format='%(filename)s: '
                    '%(levelname)s: '
                    '%(funcName)s(): '
                    '%(lineno)d:\t'
                    '%(message)s')
logger = logging.getLogger('readings_update')
logger.setLevel(logging.INFO)
PLOT_KEY = 'plots/'

def lambda_handler(event, context):
    sm_runtime_client = boto3.client('sagemaker-runtime')
    s3 = boto3.resource('s3')
    sm_client = boto3.client('sagemaker')
    sagemaker_endpoints = sm_client.list_endpoints()['Endpoints']
    endpoint = None
    for ep in sagemaker_endpoints:
        if 'pytorch-inference' in ep['EndpointName']:
            endpoint = ep['EndpointName']

    for rec in event['Records']:
        logger.info('New Record !!!!!!!!!!!!!!! {}'.format(rec))
        bucket = rec['s3']['bucket']['name']
        key = rec['s3']['object']['key']
        obj = s3.Object(bucket, key)
        csv_payload = obj.get()['Body'].read()
        logger.info('Payload:')
        logger.info(csv_payload)
        response = sm_runtime_client.invoke_endpoint(
            EndpointName=endpoint,
            Body=csv_payload,
            ContentType='text/csv'
        )
        loss_string = ''
        response_decoded = json.loads(response['Body'].read().decode('utf-8'))
        logger.info(response_decoded)
        for loss in response_decoded['prediction_loss_by_colum_index']:
            loss_string += '{:.2E}_'.format(loss)
        new_key = PLOT_KEY + key.split('/')[-1]
        plt_object = s3.Object(bucket, '{}_{}plt.png'.format(new_key, loss_string))
        plt_object.put(Body=base64.b64decode(response_decoded['plot']))


    logger.info(event)
    logger.info(context)
    return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Inferencing successful",
            }),
        }
