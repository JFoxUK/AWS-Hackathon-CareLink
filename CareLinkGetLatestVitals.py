import json
import boto3
import os
from boto3.dynamodb.conditions import Key
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('DYNAMODB_TABLE', 'carelink_alerts')
table = dynamodb.Table(table_name)

# Helper to fix Decimal issues
def convert_decimal(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, dict):
        return {k: convert_decimal(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [convert_decimal(i) for i in obj]
    return obj

def lambda_handler(event, context):
    try:
        response = table.query(
            KeyConditionExpression=Key('device_id').eq('carelink-health-monitor'),
            ScanIndexForward=False,
            Limit=1
        )
        
        if response['Items']:
            clean_item = convert_decimal(response['Items'][0])
            return {
                'statusCode': 200,
                'body': json.dumps(clean_item)
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps('No data found')
            }
    except Exception as e:
        print("Error:", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps(str(e))
        }
