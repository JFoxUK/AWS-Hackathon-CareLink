# --- CareLinkPublishVitals.py (Final Correct Version) ---

import json
import boto3
import os

# --- Setup ---
iot_client = boto3.client('iot-data')
topic = 'carelink/vitals'

# --- Lambda Handler ---
def lambda_handler(event, context):
    try:
        print("[Lambda Start] Event:", json.dumps(event))

        # Accepts a list of vitals
        vitals_list = event.get('vitals', [])
        device_id = event.get('device_id', 'unknown-device')

        if not vitals_list:
            raise ValueError("No vitals data provided.")

        # Publish each vital record individually
        for vitals in vitals_list:
            body = {
                "device_id": device_id,
                "heart_rate": vitals['heart_rate'],
                "blood_oxygen": vitals['blood_oxygen'],
                "temperature": vitals['temperature'],
                "timestamp": vitals.get('timestamp')  # Optional, can fallback on processor side
            }

            print("[IoT Publish] Publishing to topic:", topic)
            response = iot_client.publish(
                topic=topic,
                qos=1,
                payload=json.dumps(body)
            )
            print("[IoT Publish] Response:", response)

        print("[Lambda End] All vitals published successfully.")
        return {
            'statusCode': 200,
            'body': json.dumps('Vitals published to IoT successfully.')
        }

    except Exception as e:
        print("[Lambda Error]", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps('Error publishing vitals to IoT.')
        }
