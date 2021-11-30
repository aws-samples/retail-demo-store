# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import boto3
import json
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

TABLE_NAME = os.environ.get('WebsocketDynamoTableName')

dynamo = boto3.client('dynamodb')


def remove_browser_notification_connections(user_id, connection_ids):
    dynamo_key = {'userId': {'S': user_id}}
    dynamo_update_expression = {':c': {'SS': connection_ids}}
    logger.info(f"Deleting connection IDs {connection_ids} for user {user_id}")

    dynamo.update_item(
        TableName=TABLE_NAME,
        Key=dynamo_key,
        UpdateExpression='DELETE connectionIds :c',
        ExpressionAttributeValues=dynamo_update_expression
    )
    logger.info(f"Gone connections deleted")


def lambda_handler(event, context):
    logger.info('## ENVIRONMENT VARIABLES')
    logger.info(os.environ)
    logger.info('## EVENT')
    logger.info(event)

    body = json.loads(event['body'])
    user_id = body['data']['userId']
    product_id = body['data']['productId']

    api_url = 'https://' + event['requestContext']['domainName'] + '/' + event['requestContext']['stage']
    apigateway = boto3.client('apigatewaymanagementapi', endpoint_url=api_url)

    dynamo_entry = dynamo.get_item(
        TableName=TABLE_NAME,
        Key={
            'userId': {'S': user_id}
        }
    )

    if 'Item' in dynamo_entry:
        logger.info(f'Retrieved connection table entry: {dynamo_entry["Item"]}')
        gone_connections = []
        if 'connectionIds' in dynamo_entry['Item']:
            for connection_id in dynamo_entry['Item']['connectionIds']['SS']:
                try:
                    logger.info(f'Posting to connection ID: {connection_id}')
                    send_body = {'productId': product_id}
                    apigateway.post_to_connection(Data=json.dumps(send_body), ConnectionId=connection_id)
                except apigateway.exceptions.GoneException:
                    logger.info(f'Connection ID {connection_id} is gone, will remove.')
                    gone_connections.append(connection_id)
            if gone_connections:
                remove_browser_notification_connections(user_id, gone_connections)
    else:
        logger.info(f'No active WebSocket connections found for user {user_id}. No browser notifications sent.')

    return {
        'statusCode': 200,
        'body': json.dumps('Data sent')
    }
