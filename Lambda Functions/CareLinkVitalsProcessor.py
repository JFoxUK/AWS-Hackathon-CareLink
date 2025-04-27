import json
import boto3
import os
from datetime import datetime
from decimal import Decimal

# Initialize AWS resources
dynamodb = boto3.resource('dynamodb')
bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
sns = boto3.client('sns')
runtime_sm = boto3.client('runtime.sagemaker', region_name='us-east-1')

# Environment variables
table_name = os.environ.get('DYNAMODB_TABLE', 'carelink_alerts')
model_id = os.environ.get('BEDROCK_MODEL_ID', 'amazon.titan-text-lite-v1')
sns_topic_arn = os.environ.get('SNS_TOPIC_ARN')
sagemaker_endpoint_name = os.environ.get('SAGEMAKER_ENDPOINT_NAME', 'carelink-xgboost-endpoint')

# Critical thresholds
heart_rate_upper = Decimal(os.environ.get('HEART_RATE_UPPER_LIMIT', '120'))
heart_rate_lower = Decimal(os.environ.get('HEART_RATE_LOWER_LIMIT', '50'))
blood_oxygen_upper = Decimal('100')
blood_oxygen_lower = Decimal(os.environ.get('BLOOD_OXYGEN_LOWER_LIMIT', '90'))
temperature_upper = Decimal(os.environ.get('TEMPERATURE_UPPER_LIMIT', '39'))
temperature_lower = Decimal(os.environ.get('TEMPERATURE_LOWER_LIMIT', '35'))

# Reference to DynamoDB Table
table = dynamodb.Table(table_name)

def call_sagemaker_model(vitals):
    try:
        payload = f"{vitals['heart_rate']},{vitals['blood_oxygen']},{vitals['temperature']}"
        print(f"[SageMaker] Payload to endpoint: {payload}")

        response = runtime_sm.invoke_endpoint(
            EndpointName=sagemaker_endpoint_name,
            ContentType="text/csv",
            Body=payload
        )
        result = response['Body'].read().decode('utf-8')
        print(f"[SageMaker] Raw response body: {result}")

        prediction_probability = float(result.strip())
        model_prediction = 1 if prediction_probability >= 0.5 else 0
        print(f"[SageMaker] Converted prediction: {model_prediction} (probability: {prediction_probability})")
        
        return model_prediction, prediction_probability

    except Exception as e:
        print(f"[SageMaker] Error: {str(e)}")
        raise

def generate_alert_summary(vitals, model_prediction, prediction_probability):
    try:
        # Pull the limits here
        heart_rate_low = 50
        heart_rate_high = 120
        blood_oxygen_low = 90
        blood_oxygen_high = 100
        temperature_low = 35
        temperature_high = 39

        prompt = (
            f"Analyze the patient's vitals and provide a short, clear summary for a healthcare provider. "
            f"Vitals received:\n"
            f"- Heart Rate: {vitals['heart_rate']} bpm\n"
            f"- Blood Oxygen: {vitals['blood_oxygen']} %\n"
            f"- Temperature: {vitals['temperature']} °C\n\n"
            f"AI Model Prediction:\n"
            f"- Instability Risk Probability: {prediction_probability}\n"
            f"- Binary Decision (0 = stable, 1 = unstable): {model_prediction}\n\n"
            f"- The closer to 0 the less likely the patient is to be unstable.\n"
            f"- Example: 0.5 = 50% unstable. 0.1 = 10% unstable (likely safe). 0.7 = 70% unstable (likely unstable).\n\n"
            f"Clinical Ranges:\n"
            f"- Heart Rate: {heart_rate_low}-{heart_rate_high} bpm\n"
            f"- Blood Oxygen: {blood_oxygen_low}-{blood_oxygen_high} %\n"
            f"- Temperature: {temperature_low}-{temperature_high} °C\n\n"
            f"Summarize ONLY the probability and clinical ranges. "
            f"Do NOT comment directly on the vitals, patient, or AI model. "
            f"Be concise and professional."
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

        print(f"[Bedrock] Model ID: {model_id}")
        print(f"[Bedrock] Request Body: {json.dumps(body)}")

        response = bedrock_runtime.invoke_model(
            modelId=model_id,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json"
        )

        response_body = json.loads(response['body'].read())
        print(f"[Bedrock] Raw response body: {response_body}")

        if "results" in response_body and response_body["results"]:
            summary = response_body["results"][0]["outputText"]
            print(f"[Bedrock] Parsed AI summary: {summary}")
            return summary
        else:
            print("[Bedrock] No AI summary found in response.")
            return "No AI summary generated."

    except Exception as e:
        print(f"[Bedrock] Error: {str(e)}")
        raise

    try:
        prompt = (
            f"Analyze the patient's vitals and provide a short, clear summary for a healthcare provider. "
            f"Vitals received:\n"
            f"- Heart Rate: {vitals['heart_rate']} bpm\n"
            f"- Blood Oxygen: {vitals['blood_oxygen']} %\n"
            f"- Temperature: {vitals['temperature']} °C\n\n"
            f"AI Model Prediction:\n"
            f"- Instability Risk Probability: {prediction_probability}\n"
            f"- Binary Decision (0 = stable, 1 = unstable): {model_prediction}\n\n"
            f"- The closer to 0 the less likley the patient is to being unstable\n"
            f"- Example, 0.5 a 50% chance of being unstable\n"
            f"- Example, 0.1 a 10% chance of being unstable and therfore is not likely\n"
            f"- Example, 0.7 a 70% chance of being unstable and therefore is likely\n"
            f"Summarise the vitals but do not comment if they are within or out of the safe ranges. "
            f"Comment on the probbability score and what that could mean for the patient. "
            f"Always list out but not not compare to our results, the upper and lower limits as follows:\n"
            f"- Heart Rate: {heart_rate_lower} - {heart_rate_upper} bpm\n"
            f"- Blood Oxygen: {blood_oxygen_lower} - {blood_oxygen_upper} %\n"
            f"- Temperature: {temperature_lower} - {temperature_upper} °C\n\n"
            f"Do not comment on the binary decision. "
            f"Do not comment on the vitals. "
            f"Do not comment on the AI model. "
            f"Do not comment on the patient. "
            f"Do not comment on the healthcare provider. "
            f"Do not fabricate issues. Be concise and professional."
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

        print(f"[Bedrock] Model ID: {model_id}")
        print(f"[Bedrock] Request Body: {json.dumps(body)}")

        response = bedrock_runtime.invoke_model(
            modelId=model_id,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json"
        )

        response_body = json.loads(response['body'].read())
        print(f"[Bedrock] Raw response body: {response_body}")

        if "results" in response_body and response_body["results"]:
            summary = response_body["results"][0]["outputText"]
            print(f"[Bedrock] Parsed AI summary: {summary}")
            return summary
        else:
            print("[Bedrock] No AI summary found in response.")
            return "No AI summary generated."

    except Exception as e:
        print(f"[Bedrock] Error: {str(e)}")
        raise

def check_vitals_critical(heart_rate, blood_oxygen, temperature):
    critical_messages = []

    if heart_rate > heart_rate_upper:
        critical_messages.append(f"High Heart Rate: {heart_rate} bpm.")
    if heart_rate < heart_rate_lower:
        critical_messages.append(f"Low Heart Rate: {heart_rate} bpm.")
    if blood_oxygen < blood_oxygen_lower:
        critical_messages.append(f"Low Blood Oxygen: {blood_oxygen}%.")
    if temperature > temperature_upper:
        critical_messages.append(f"High Temperature: {temperature} °C.")
    if temperature < temperature_lower:
        critical_messages.append(f"Low Temperature: {temperature} °C.")

    print(f"[Vitals Check] Critical messages: {critical_messages}")
    return critical_messages

def publish_critical_alert(device_id, critical_messages, timestamp):
    try:
        alert_msg = "CareLink Critical Alert\n"
        alert_msg += f"Device: {device_id}\n"
        for msg in critical_messages:
            alert_msg += msg + "\n"
        alert_msg += f"Timestamp: {timestamp}"

        print(f"[SNS] Publishing alert: {alert_msg}")

        sns.publish(
            TopicArn=sns_topic_arn,
            Message=alert_msg,
            Subject="CareLink Critical Health Alert"
        )

    except Exception as e:
        print(f"[SNS] Error publishing alert: {str(e)}")
        raise

def lambda_handler(event, context):
    print(f"[Lambda Start] Received event: {json.dumps(event)}")

    try:
        device_id = event.get('device_id')
        heart_rate = Decimal(str(event.get('heart_rate')))
        blood_oxygen = Decimal(str(event.get('blood_oxygen')))
        temperature = Decimal(str(event.get('temperature')))

        vitals = {
            "heart_rate": float(heart_rate),
            "blood_oxygen": float(blood_oxygen),
            "temperature": float(temperature)
        }

        print(f"[Vitals] Parsed vitals: {vitals}")

        model_prediction, prediction_probability = call_sagemaker_model(vitals)
        alert_summary = generate_alert_summary(vitals, model_prediction, prediction_probability)

        timestamp = datetime.utcnow().isoformat()

        item_to_save = {
            'device_id': device_id,
            'timestamp': timestamp,
            'heart_rate': heart_rate,
            'blood_oxygen': blood_oxygen,
            'temperature': temperature,
            'model_prediction': Decimal(str(model_prediction)),
            'prediction_probability': Decimal(str(prediction_probability)),
            'alert_summary': alert_summary
        }

        print(f"[DynamoDB] Storing item: {item_to_save}")
        table.put_item(Item=item_to_save)

        critical_messages = check_vitals_critical(heart_rate, blood_oxygen, temperature)

        if critical_messages or model_prediction == 1:
            publish_critical_alert(device_id, critical_messages + [f"AI Predicted Critical: {model_prediction}"], timestamp)

        print("[Lambda End] Success")
        return {
            'statusCode': 200,
            'body': json.dumps('Vitals stored with AI and ML alert successfully')
        }

    except Exception as e:
        print(f"[Lambda Error] {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps('Error processing vitals with AI and ML')
        }
