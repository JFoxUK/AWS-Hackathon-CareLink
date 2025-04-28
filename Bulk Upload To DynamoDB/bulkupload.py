import boto3
import json
import time

# --- CONFIG ---
table_name = 'carelink_alerts'  # Your table name
region_name = 'eu-north-1'      # Your region
json_file_path = 'patient_vitals_1year_dynamodb.json'  # Your JSON file location

# --- SETUP AWS RESOURCES ---
dynamodb = boto3.client('dynamodb', region_name=region_name)

# --- LOAD JSON FILE ---
with open(json_file_path, 'r') as f:
    records = json.load(f)

# --- BATCH WRITE FUNCTION ---
def batch_write(items, table_name):
    request_items = {table_name: items}
    response = dynamodb.batch_write_item(RequestItems=request_items)
    unprocessed = response.get('UnprocessedItems', {})
    return unprocessed

# --- MAIN ---
batch_size = 25  # DynamoDB limit

print(f"🚀 Starting batch upload to DynamoDB table: {table_name}")

for i in range(0, len(records), batch_size):
    batch = records[i:i+batch_size]
    unprocessed = batch_write(batch, table_name)

    if unprocessed:
        print("⚠️ Some unprocessed items detected, retrying...")
        while unprocessed:
            time.sleep(2)
            unprocessed = batch_write(unprocessed.get(table_name, []))
    else:
        print(f"✅ Batch {i//batch_size + 1} uploaded successfully.")

print("🎯 All data uploaded to DynamoDB!")
