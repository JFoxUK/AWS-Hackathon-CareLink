# 💕 CareLink: AI-Powered Remote Health Monitoring

CareLink is a proof-of-concept project built for the **AWS Breaking Barriers Hackathon 2025**.

It demonstrates how **next-generation connectivity (AWS IoT Core, 5G) and Generative AI (Amazon Bedrock)** can be combined to deliver **equitable, real-time healthcare monitoring** for underserved or remote communities.

---

## 🚀 Solution Architecture

**Technologies Used:**
- **AWS IoT Core**: Receives and routes device vitals (heart rate, blood oxygen, temperature)
- **AWS Lambda**: Processes incoming health data, performs critical checks, and invokes AI analysis
- **Amazon Bedrock (Titan Text G1 Lite)**: Analyzes vitals and generates human-readable health summaries
- **Amazon DynamoDB**: Stores raw vitals and AI-generated alerts
- **Amazon SNS**: Sends real-time email alerts for critical health events
- **AWS CloudWatch**: Logs for monitoring and debugging

---

## 🛇 System Overview

1. Simulated CareLink device publishes health vitals to **MQTT topic `carelink/vitals`**.
2. **AWS IoT Rule** captures the message and triggers **Lambda function**.
3. **Lambda**:
   - Parses incoming health vitals
   - Performs critical health threshold checks
   - Invokes **Amazon Bedrock Titan Text G1 Lite** for AI analysis
   - Saves vitals + AI health summary into **DynamoDB**
   - Sends **SNS email alert** if vitals exceed danger thresholds.
4. (Optional extensions: Real-time front-end dashboards.)

---

## 💪 How to Deploy CareLink

### 1. Prerequisites
- AWS account with permissions to:
  - IoT Core
  - Lambda
  - DynamoDB
  - Amazon Bedrock
  - Amazon SNS
- Region: AWS Lambda can be deployed anywhere, but Bedrock model currently invoked from `us-east-1`.

### 2. Set Up AWS IoT Core

- Create a new **Thing**: `carelink-health-monitor`
- Generate and download:
  - Certificate
  - Public Key
  - Private Key
  - Amazon Root CA
- Create an **IoT Policy**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "iot:Connect",
        "iot:Publish",
        "iot:Subscribe",
        "iot:Receive"
      ],
      "Resource": "*"
    }
  ]
}
```
- Attach the Policy to the Certificate.

### 3. Create IoT Topic Rule

- Topic Rule Name: `carelink-vitals-rule`
- SQL Query:
```sql
SELECT * FROM 'carelink/vitals'
```
- Action: Invoke the **CareLinkVitalsProcessor Lambda function**.

### 4. Create DynamoDB Table

- Table name: `carelink_alerts`
- Partition key: `device_id` (String)
- Sort key: `timestamp` (String)
- Capacity mode: On-Demand

### 5. Create SNS Topic

- Create an SNS Topic (e.g., `CareLinkAlerts`)
- Subscribe an email address to receive critical health alerts.

### 6. Create Lambda Function

- Name: `CareLinkVitalsProcessor`
- Runtime: Python 3.12
- Environment Variables:
  - `DYNAMODB_TABLE = carelink_alerts`
  - `BEDROCK_MODEL_ID = amazon.titan-text-lite-v1`
  - `SNS_TOPIC_ARN = [Your SNS Topic ARN]`
  - `HEART_RATE_LIMIT = 120`
  - `BLOOD_OXYGEN_LIMIT = 90`
  - `TEMPERATURE_LIMIT = 39`
- Permissions:
  - Attach `AmazonDynamoDBFullAccess`
  - Attach `AmazonBedrockInvokeFullAccess`
  - Attach `AmazonSNSFullAccess`

**Special Note:**
If your region does not support Titan Text G1 Lite, create the Bedrock client like this:
```python
bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
```

### 7. Lambda Core Logic

- Parse incoming vitals from event
- Perform clinical threshold checks for heart rate, blood oxygen, and temperature
- Generate a natural language health summary using Bedrock
- Save original vitals and AI health summary into DynamoDB
- Trigger a critical alert email via SNS if thresholds are breached

### 8. Testing the System

**Publish to MQTT Topic:**
- Topic: `carelink/vitals`
- Example Payload:
```json
{
  "device_id": "carelink-health-monitor",
  "heart_rate": 135,
  "blood_oxygen": 85,
  "temperature": 39.5
}
```

✅ The AI should respond with a health analysis summary.
✅ If the vitals are dangerous, you will also receive an SNS email alert!

---

## 🌟 Future Improvements

- Real-time patient alerting via Amazon SNS Mobile Push.
- Front-end dashboard using AWS Amplify + AppSync.
- Expand device types (e.g., blood pressure monitors, ECGs).
- Integrate more advanced AI models via Bedrock.

---

## 📜 Architecture Diagram

```plaintext
+-------------------------+
| CareLink Device/Simulator|
| (MQTT Publish Vitals)    |
+-----------+-------------+
            |
            v
+-------------------------+
| AWS IoT Core             |
| Topic: carelink/vitals   |
+-----------+-------------+
            |
 (IoT Rule triggers Lambda)
            |
            v
+-------------------------+
| AWS Lambda Function     |
| CareLinkVitalsProcessor  |
|  - Parse Vitals          |
|  - Clinical Check        |
|  - Invoke Bedrock AI     |
|  - Save to DynamoDB      |
+-----------+-------------+
            |
            |
            ------------->------------
            |                         |
(optional step depending on values)   |
            |                         |
+-----------+-------------+           |
|  - Publish SNS Alert     |          |
+-----------+-------------+           |
            |                         |
            |------------<------------
            |                     
            v
+-------------------------+
| AWS DynamoDB Table       |
| carelink_alerts          |
| (Store Vitals + AI Summary) |
+-------------------------+
```

---

## 📜 License

MIT License — Feel free to fork, contribute, and build upon CareLink!

---

# 🚀 Ready for Deployment!

