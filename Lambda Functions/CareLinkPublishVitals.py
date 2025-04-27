import json
import boto3
import os

iot_client = boto3.client('iot-data')

topic = 'carelink/vitals'

def lambda_handler(event, context):
    try:
        print("Received event:", event)

        # Direct access to event fields
        body = {
            "device_id": event['device_id'],
            "heart_rate": event['heart_rate'],
            "blood_oxygen": event['blood_oxygen'],
            "temperature": event['temperature']
        }

        print("Publishing to IoT topic:", topic)
        response = iot_client.publish(
            topic=topic,
            qos=1,
            payload=json.dumps(body)
        )
        print("Publish response:", response)

        return {
            'statusCode': 200,
            'body': json.dumps('Vitals published successfully')
        }

    except Exception as e:
        print("Error during Lambda execution:", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps(str(e))
        }
