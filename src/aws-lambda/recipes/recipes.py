import json

def handler(event, _):
    http_method = event['httpMethod'].lower()

    if http_method == 'get':
        return {
            "statusCode": 200,
            "body": json.dumps('Recipes!')
        }
    else:
        return {
            "statusCode": 405
        }