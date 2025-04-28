# --- CareLinkVitalsProcessor.py (Simplified) ---

import json
import boto3
import os
from datetime import datetime
from decimal import Decimal

# Initialize AWS resources
dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

# Environment variables
table_name = os.environ.get('DYNAMODB_TABLE', 'carelink_alerts')
sns_topic_arn = os.environ.get('SNS_TOPIC_ARN')

# Critical thresholds
heart_rate_upper = Decimal(os.environ.get('HEART_RATE_UPPER_LIMIT', '120'))
heart_rate_lower = Decimal(os.environ.get('HEART_RATE_LOWER_LIMIT', '50'))
blood_oxygen_lower = Decimal(os.environ.get('BLOOD_OXYGEN_LOWER_LIMIT', '90'))
temperature_upper = Decimal(os.environ.get('TEMPERATURE_UPPER_LIMIT', '39'))
temperature_lower = Decimal(os.environ.get('TEMPERATURE_LOWER_LIMIT', '35'))

# Reference to DynamoDB Table
table = dynamodb.Table(table_name)

def check_vitals_critical(heart_rate, blood_oxygen, temperature):
    criticals = []

    if heart_rate > heart_rate_upper:
        criticals.append(f"High Heart Rate: {heart_rate} bpm")
    if heart_rate < heart_rate_lower:
        criticals.append(f"Low Heart Rate: {heart_rate} bpm")
    if blood_oxygen < blood_oxygen_lower:
        criticals.append(f"Low Blood Oxygen: {blood_oxygen}%")
    if temperature > temperature_upper:
        criticals.append(f"High Temperature: {temperature} °C")
    if temperature < temperature_lower:
        criticals.append(f"Low Temperature: {temperature} °C")

    print(f"[Vitals Check] Critical Findings: {criticals}")
    return criticals

def publish_critical_alert(device_id, critical_messages, timestamp):
    try:
        message = "🚨 CareLink Critical Alert 🚨\n"
        message += f"Device ID: {device_id}\n"
        for msg in critical_messages:
            message += f"- {msg}\n"
        message += f"Timestamp: {timestamp}"

        print(f"[SNS] Publishing alert:\n{message}")

        sns.publish(
            TopicArn=sns_topic_arn,
            Message=message,
            Subject="CareLink Critical Health Alert"
        )

    except Exception as e:
        print(f"[SNS] Publish Error: {str(e)}")
        raise

def lambda_handler(event, context):
    print(f"[Lambda Start] Event: {json.dumps(event)}")

    try:
        device_id = event.get('device_id')
        heart_rate = Decimal(str(event.get('heart_rate')))
        blood_oxygen = Decimal(str(event.get('blood_oxygen')))
        temperature = Decimal(str(event.get('temperature')))
        timestamp = event.get('timestamp', datetime.utcnow().isoformat())

        item = {
            'device_id': device_id,
            'timestamp': timestamp,
            'heart_rate': heart_rate,
            'blood_oxygen': blood_oxygen,
            'temperature': temperature
        }

        print(f"[DynamoDB] Saving Item: {item}")
        table.put_item(Item=item)

        critical_messages = check_vitals_critical(heart_rate, blood_oxygen, temperature)

        if critical_messages:
            publish_critical_alert(device_id, critical_messages, timestamp)

        print("[Lambda End] Completed successfully")
        return {
            'statusCode': 200,
            'body': json.dumps('Vitals stored and alerts processed successfully.')
        }

    except Exception as e:
        print(f"[Lambda Error] {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps('Error processing vitals.')
        }
