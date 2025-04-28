# --- CareLinkGetLatestVitals.py (Fully Updated for Trends + AI Summaries, Better Bedrock Prompt) ---

import json
import boto3
import os
from boto3.dynamodb.conditions import Key
from datetime import datetime, timedelta

# --- SETUP AWS RESOURCES ---
dynamodb = boto3.resource('dynamodb')
sagemaker_runtime = boto3.client('runtime.sagemaker', region_name='us-east-1')
bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')

# --- ENVIRONMENT VARIABLES ---
table_name = os.environ.get('DYNAMODB_TABLE', 'carelink_alerts')
sagemaker_endpoint_name = os.environ.get('SAGEMAKER_ENDPOINT_NAME', 'carelink-xgboost-endpoint')
bedrock_model_id = os.environ.get('BEDROCK_MODEL_ID', 'amazon.titan-text-lite-v1')

# --- REFERENCE TABLE ---
table = dynamodb.Table(table_name)

# --- HANDLER ---
def lambda_handler(event, context):
    print("[Lambda Start] Event:", json.dumps(event))

    try:
        device_id = event.get('device_id', 'patient-001')
        months_back = int(event.get('months_back', 3))

        if not device_id:
            raise ValueError("Device ID must be provided.")

        # Fetch past 3 months
        cutoff_date = datetime.utcnow() - timedelta(days=30*months_back)
        cutoff_iso = cutoff_date.isoformat()

        print(f"[Query] Fetching vitals since: {cutoff_iso}")

        response = table.query(
            KeyConditionExpression=Key('device_id').eq(device_id) & Key('timestamp').gte(cutoff_iso),
            ScanIndexForward=True
        )

        vitals = response.get('Items', [])

        # Sort vitals just in case
        vitals.sort(key=lambda x: x['timestamp'])

        if not vitals:
            return {
                'statusCode': 404,
                'body': json.dumps('No vitals found.')
            }

        # --- PREPARE DATA FOR SAGEMAKER ---
        latest_24hr = vitals[-24:]  # last 24 readings (assume 1/hr readings)

        if len(latest_24hr) < 24:
            raise ValueError("Not enough recent vitals for prediction.")

        payload_list = []
        for v in latest_24hr:
            heart_rate_scaled = (float(v['heart_rate']) - 50) / (120 - 50)
            blood_oxygen_scaled = (float(v['blood_oxygen']) - 90) / (100 - 90)
            temperature_scaled = (float(v['temperature']) - 35) / (39 - 35)
            payload_list.append(f"{heart_rate_scaled},{blood_oxygen_scaled},{temperature_scaled}")

        # SageMaker expects 1 CSV row
        payload_csv = ",".join(payload_list)

        print("[SageMaker] Sending Payload:", payload_csv)

        # --- INVOKE SAGEMAKER ---
        prediction = sagemaker_runtime.invoke_endpoint(
            EndpointName=sagemaker_endpoint_name,
            ContentType="text/csv",
            Body=payload_csv
        )
        prediction_value = float(prediction['Body'].read().decode('utf-8').strip())

        print("[SageMaker] Prediction Probability:", prediction_value)

        # --- PREPARE DATA FOR BEDROCK ---
        trend_summary_prompt = (
            "You are a clinical assistant AI.\n"
            "Analyze the patient's vitals over the past 24 hours.\n"
            "Summarize any notable *trends* ONLY (e.g., increasing heart rate, dropping oxygen, fever spikes).\n"
            "Ignore individual values. Do NOT list raw numbers.\n"
            "Write briefly in clinical, professional language.\n\n"
            "Patient Vitals (timestamp, heart rate bpm, oxygen %, temperature °C):\n"
        )

        for v in latest_24hr:
            trend_summary_prompt += f"- {v['timestamp']}: {v['heart_rate']} bpm, {v['blood_oxygen']}%, {v['temperature']}°C\n"

        trend_summary_prompt += "\nSummary:"

        bedrock_body = {
            "inputText": trend_summary_prompt,
            "textGenerationConfig": {
                "temperature": 0.2,
                "maxTokenCount": 500,
                "topP": 0.9,
                "stopSequences": []
            }
        }

        bedrock_response = bedrock_runtime.invoke_model(
            modelId=bedrock_model_id,
            body=json.dumps(bedrock_body),
            contentType="application/json",
            accept="application/json"
        )

        bedrock_result = json.loads(bedrock_response['body'].read())
        summary_text = bedrock_result.get('results', [{}])[0].get('outputText', "No summary generated.")

        print("[Bedrock] Summary:", summary_text)

        # --- FINAL RETURN ---
        clean_vitals = [
            {
                'timestamp': v['timestamp'],
                'heart_rate': float(v['heart_rate']),
                'blood_oxygen': float(v['blood_oxygen']),
                'temperature': float(v['temperature'])
            }
            for v in vitals
        ]

        return {
            'statusCode': 200,
            'body': json.dumps({
                'vitals_history': clean_vitals,
                'sagemaker_prediction': prediction_value,
                'bedrock_summary': summary_text
            })
        }

    except Exception as e:
        print("[Lambda Error]", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps('Error retrieving and analyzing vitals.')
        }
