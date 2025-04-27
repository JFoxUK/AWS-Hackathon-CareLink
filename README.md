# 💕 CareLink: AI-Powered Remote Health Monitoring

CareLink is a proof-of-concept project built for the **AWS Breaking Barriers Hackathon 2025**.

It demonstrates how **next-generation connectivity (AWS IoT Core, 5G), Machine Learning (Amazon SageMaker)**, and **Generative AI (Amazon Bedrock)** can be combined to deliver **equitable, real-time healthcare monitoring** for underserved or remote communities.

---

## 🚀 Solution Architecture

**Technologies Used:**
- **AWS IoT Core**: Receives and routes device vitals (heart rate, blood oxygen, temperature)
- **AWS Lambda**: Processes incoming health data, performs critical checks, invokes AI/ML models
- **Amazon SageMaker**: Trained ML model to predict patient stability based on vitals
- **Amazon Bedrock (Titan Text G1 Lite)**: Analyzes vitals and ML predictions to generate human-readable health summaries
- **Amazon DynamoDB**: Stores raw vitals, ML predictions, and AI-generated alerts
- **Amazon SNS**: Sends real-time email alerts for critical health events
- **AWS CloudWatch**: Logs for monitoring and debugging

---

## 🚷 System Overview

1. Simulated CareLink device publishes health vitals to **MQTT topic `carelink/vitals`**.
2. **AWS IoT Rule** captures the message and triggers **Lambda function**.
3. **Lambda**:
   - Parses incoming health vitals
   - Performs critical health threshold checks
   - **Invokes SageMaker endpoint** to classify the patient's status (stable/unstable)
   - **Invokes Bedrock Titan Text G1 Lite** to generate a health summary using the ML model prediction
   - Saves vitals, model prediction, and AI health summary into **DynamoDB**
   - Sends **SNS email alert** if vitals exceed danger thresholds or ML model predicts instability
4. (Optional extensions: Real-time front-end dashboards.)

---

## 💪 How to Deploy CareLink

### 1. Prerequisites
- AWS account with permissions to:
  - IoT Core
  - Lambda
  - DynamoDB
  - SageMaker
  - Amazon Bedrock
  - Amazon SNS
- Regions:
  - **Lambda** and **IoT Core**: Any
  - **SageMaker endpoint**: Deployed in `us-east-1`
  - **Bedrock model invocation**: `us-east-1`

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

### 6. Train and Deploy SageMaker Model

- Train a binary XGBoost model using health vitals (heart rate, blood oxygen, temperature) as input.
- Objective: `binary:logistic`
- Deploy model as a real-time endpoint (e.g., `carelink-xgboost-endpoint`) in **us-east-1** region.

### 7. Create Lambda Function

- Name: `CareLinkVitalsProcessor`
- Runtime: Python 3.12
- Environment Variables:
  - `DYNAMODB_TABLE = carelink_alerts`
  - `BEDROCK_MODEL_ID = amazon.titan-text-lite-v1`
  - `SNS_TOPIC_ARN = [Your SNS Topic ARN]`
  - `SAGEMAKER_ENDPOINT_NAME = carelink-xgboost-endpoint`
  - `HEART_RATE_UPPER_LIMIT = 120`
  - `HEART_RATE_LOWER_LIMIT = 50`
  - `BLOOD_OXYGEN_LOWER_LIMIT = 90`
  - `TEMPERATURE_UPPER_LIMIT = 39`
  - `TEMPERATURE_LOWER_LIMIT = 35`
- Permissions:
  - Attach `AmazonDynamoDBFullAccess`
  - Attach `AmazonSageMakerFullAccess`
  - Attach `AmazonBedrockInvokeFullAccess`
  - Attach `AmazonSNSFullAccess`

**Special Note:**
- If your Lambda is in a region without Bedrock models, set the Bedrock client:
```python
bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
```

### 8. Lambda Core Logic

- Parse incoming vitals from event.
- Perform clinical threshold checks.
- Call **SageMaker model** for prediction (stable or unstable).
- Call **Bedrock** with vitals + prediction for AI-generated health summary.
- Save all into **DynamoDB**.
- Send SNS alerts if vitals or prediction are critical.

### 9. Testing the System

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

✅ The AI will respond with a health analysis summary.
✅ If dangerous, an SNS alert email will be triggered!

---

## 🌟 Future Improvements

- Real-time patient alerting via Amazon SNS Mobile Push.
- Front-end dashboard using AWS Amplify + AppSync.
- Expand device types (e.g., blood pressure monitors, ECGs).
- Integrate more advanced AI models via Bedrock.
- Fine-tuned ML models for specific demographics.

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
|  - Invoke SageMaker ML   |
|  - Invoke Bedrock AI     |
|  - Save to DynamoDB      |
|  - Publish SNS Alert     |
+-----------+-------------+
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

## 🔗 Links

[DEMO VIDEO](https://youtu.be/G8T9yV4iqx0)  
[DEMO SCRIPT](https://github.com/JFoxUK/AWS-Hackathon-CareLink/blob/main/DEMO_SCRIPT.md)  
[DEVPOST SUBMISSION]()

---

## ✍️ Author

[GitHub](https://github.com/JFoxUK)  
[LinkedIn](https://linkedin.com/in/jfoxuk)  
[Devpost](https://devpost.com/JFoxUK)

---

# 🚀 Ready for Deployment!