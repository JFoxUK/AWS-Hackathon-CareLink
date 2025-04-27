import json
import boto3
import os
from datetime import datetime
from decimal import Decimal

# Initialize AWS resources
dynamodb = boto3.resource('dynamodb')
bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
sns = boto3.client('sns')

# Environment variables
table_name = os.environ.get('DYNAMODB_TABLE', 'carelink_alerts')
model_id = os.environ.get('BEDROCK_MODEL_ID', 'amazon.titan-text-lite-v1')
sns_topic_arn = os.environ.get('SNS_TOPIC_ARN')

# Critical thresholds
heart_rate_limit = Decimal(os.environ.get('HEART_RATE_LIMIT', '120'))
blood_oxygen_limit = Decimal(os.environ.get('BLOOD_OXYGEN_LIMIT', '90'))
temperature_limit = Decimal(os.environ.get('TEMPERATURE_LIMIT', '39'))  # Optional temperature limit

# Reference to DynamoDB Table
table = dynamodb.Table(table_name)

def generate_alert_summary(vitals):
    prompt = (
        f"Analyze the following patient vitals and determine if there is any health risk. "
        f"Return a short, clear English summary:\n\n"
        f"Heart Rate: {vitals['heart_rate']} bpm\n"
        f"Blood Oxygen: {vitals['blood_oxygen']} %\n"
        f"Temperature: {vitals['temperature']} °C"
    )
    
    body = {
        "inputText": prompt,
        "textGenerationConfig": {
            "temperature": 0.2,
            "maxTokenCount": 200,
            "topP": 0.9,
            "stopSequences": []
        }
    }
    
    response = bedrock_runtime.invoke_model(
        modelId=model_id,
        body=json.dumps(body),
        contentType="application/json",
        accept="application/json"
    )
    
    response_body = json.loads(response['body'].read())
    return response_body.get('results', [{}])[0].get('outputText', 'No AI summary generated.')

def check_vitals_critical(heart_rate, blood_oxygen, temperature):
    critical_messages = []
    
    if heart_rate > heart_rate_limit:
        critical_messages.append(f"High Heart Rate: {heart_rate} bpm.")
    if blood_oxygen < blood_oxygen_limit:
        critical_messages.append(f"Low Blood Oxygen: {blood_oxygen}%.")
    if temperature > temperature_limit:
        critical_messages.append(f"High Temperature: {temperature} °C.")

    return critical_messages

def publish_critical_alert(device_id, critical_messages, timestamp):
    alert_msg = "CareLink Critical Alert\n"
    alert_msg += f"Device: {device_id}\n"
    for msg in critical_messages:
        alert_msg += msg + "\n"
    alert_msg += f"Timestamp: {timestamp}"

    sns.publish(
        TopicArn=sns_topic_arn,
        Message=alert_msg,
        Subject="CareLink Critical Health Alert"
    )



def lambda_handler(event, context):
    print("Received event:", json.dumps(event))

    try:
        # Extract vitals
        device_id = event.get('device_id')
        heart_rate = Decimal(str(event.get('heart_rate')))
        blood_oxygen = Decimal(str(event.get('blood_oxygen')))
        temperature = Decimal(str(event.get('temperature')))
        
        vitals = {
            "heart_rate": float(heart_rate),
            "blood_oxygen": float(blood_oxygen),
            "temperature": float(temperature)
        }
        
        # Generate AI health summary
        alert_summary = generate_alert_summary(vitals)
        print("Generated alert summary:", alert_summary)

        # Current timestamp
        timestamp = datetime.utcnow().isoformat()

        # Save vitals and AI summary into DynamoDB
        table.put_item(
            Item={
                'device_id': device_id,
                'timestamp': timestamp,
                'heart_rate': heart_rate,
                'blood_oxygen': blood_oxygen,
                'temperature': temperature,
                'alert_summary': alert_summary
            }
        )

        # Check if vitals are critical
        critical_messages = check_vitals_critical(heart_rate, blood_oxygen, temperature)

        if critical_messages:
            publish_critical_alert(device_id, critical_messages, timestamp)

        return {
            'statusCode': 200,
            'body': json.dumps('Vitals stored with AI alert successfully')
        }
    except Exception as e:
        print("Error:", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps('Error processing vitals with AI')
        }
