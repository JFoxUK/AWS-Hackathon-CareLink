import json
import boto3
import os
from datetime import datetime
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
table_name = os.environ.get('DYNAMODB_TABLE', 'carelink_alerts')
table = dynamodb.Table(table_name)
model_id = os.environ.get('BEDROCK_MODEL_ID', 'amazon.titan-text-lite-v1')  # ✅ this stays here

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
    
    response = bedrock_runtime.invoke_model(     # ✅ Only call Bedrock here inside function
        modelId=model_id,
        body=json.dumps(body),
        contentType="application/json",
        accept="application/json"
    )
    
    response_body = json.loads(response['body'].read())
    return response_body.get('results', [{}])[0].get('outputText', 'No AI summary generated.')

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
        
        # Call Bedrock to generate alert summary
        alert_summary = generate_alert_summary(vitals)
        print("Generated alert summary:", alert_summary)

        # Current timestamp
        timestamp = datetime.utcnow().isoformat()

        # Save to DynamoDB
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
