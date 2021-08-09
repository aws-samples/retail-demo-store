# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import boto3
import json
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

table_name = os.environ.get('WebsocketDynamoTableName')

dynamo = boto3.client('dynamodb')


def lambda_handler(event, context):
    logger.info('## ENVIRONMENT VARIABLES')
    logger.info(os.environ)
    logger.info('## EVENT')
    logger.info(event)

    try:
        user_id = event['queryStringParameters']['userId']
    except KeyError:
        logger.info("'userId' not provided in query string.")
        return {
            'statusCode': 400,
            'body': json.dumps('Missing query parameter userId.')
        }

    connection_id = event['requestContext']['connectionId']
    dynamo_key = {'userId': {'S': user_id}}
    dynamo_update_expression = {':c': {'SS': [connection_id]}}
    logger.info(f"Deleting connection ID {connection_id} for user {user_id}")

    dynamo.update_item(
        TableName=table_name,
        Key=dynamo_key,
        UpdateExpression='DELETE connectionIds :c',
        ExpressionAttributeValues=dynamo_update_expression
    )

    return {
        'statusCode': 200,
        'body': json.dumps('Disconnected')
    }
