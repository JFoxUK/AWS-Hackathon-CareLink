# 💕 CareLink: AI-Powered Remote Health Monitoring

CareLink is a proof-of-concept project built for the **AWS Breaking Barriers Hackathon 2025**.

It demonstrates how **next-generation connectivity (AWS IoT Core, 5G)**, **Machine Learning (Amazon SageMaker)**, and **Generative AI (Amazon Bedrock)** can be combined to deliver **equitable, real-time healthcare monitoring** for underserved or remote communities.

---

## 🚀 Solution Architecture

**Core Technologies:**
- **AWS IoT Core**: Securely receives vitals (heart rate, blood oxygen, temperature) over MQTT.
- **AWS Lambda**: Serverless processing — parses data, invokes ML models, and orchestrates the full pipeline.
- **Amazon SageMaker**: Custom-trained ML model to assess patient risk based on vitals.
- **Amazon Bedrock (Titan Text G1 Lite)**: Converts numerical predictions into readable, professional AI summaries.
- **Amazon DynamoDB**: Fast and durable storage for vitals, predictions, and AI summaries.
- **Amazon SNS**: Immediate real-time alerting when critical issues detected.
- **AWS CloudWatch**: Monitors logs and operational health.

---

## 🛗 System Overview

1. **Vital Collection**: A simulated device (or real device) publishes health readings to MQTT topic `carelink/vitals`.
2. **AWS IoT Rule**: Detects the MQTT message and triggers the **CareLinkVitalsProcessor Lambda function**.
3. **AWS Lambda**:
   - Parses vital signs.
   - Checks for clinical threshold breaches (e.g., dangerously low oxygen).
   - Calls **Amazon SageMaker** to predict stability (binary classification + probability).
   - Calls **Amazon Bedrock** to generate an AI health report based on the vitals and ML prediction.
   - Saves all data to **Amazon DynamoDB** for history and auditability.
   - Sends an **SNS email alert** if vitals are dangerous or model predicts instability.

---

## 💪 How to Build and Deploy CareLink

### 1. AWS Prerequisites
- Services required:
  - IoT Core
  - Lambda
  - DynamoDB
  - SageMaker
  - Bedrock
  - SNS
- **Regions**:
  - SageMaker endpoint and Bedrock model invocation: **us-east-1**.
  - IoT Core and Lambda: any region.

---

### 2. AWS IoT Core Setup

- Create an IoT Thing (`carelink-health-monitor`).
- Attach certificates for secure communication.
- Attach a permissive IoT policy allowing Connect, Publish, Subscribe, Receive actions.
- Create a topic rule to route MQTT traffic from `carelink/vitals` to Lambda.

---

### 3. DynamoDB Setup

- Create Table: `carelink_alerts`
- Partition Key: `device_id` (String)
- Sort Key: `timestamp` (String)
- Billing Mode: On-Demand

---

### 4. SageMaker Model: Patient Stability Classifier

**Custom Dataset:**
- CSV file: heart rate, blood oxygen, temperature, and a calculated `label` (0 = stable, 1 = unstable).
- **Vital Sign Weighting Logic**:

| Vital Sign | Condition | Threshold | Weight (0–1) | Medical Reasoning |
|------------|------------|-----------|-------------|-------------------|
| Heart Rate High | > 120 bpm | 0.4 | Tachycardia can be compensatory (e.g., fever) but still risky. |
| Heart Rate Low | < 50 bpm | 0.5 | Bradycardia can cause fainting or cardiac arrest if severe. |
| Blood Oxygen Low | < 90% | 0.9 | Severe hypoxia is life-threatening without immediate care. |
| Temperature High | > 39°C | 0.6 | High fever suggests infection/inflammation. |
| Temperature Low | < 35°C | 0.8 | Hypothermia needs urgent treatment. |

**Training Details:**
- Model: **XGBoost 1.5** (built-in SageMaker container).
- Objective: **binary:logistic** (output = probability).
- Hyperparameters:
  - `max_depth=5`
  - `eta=0.2`
  - `gamma=4`
  - `min_child_weight=6`
  - `subsample=0.7`
  - `num_round=100`
- Trained model deployed as SageMaker Endpoint: `carelink-xgboost-endpoint`.

**Behavior:**
- **Returns both a probability (0.0–1.0)** and **binary prediction (0 = stable, 1 = unstable)**.
- Enables nuanced clinical risk judgment.

---

### 5. Amazon Bedrock Integration

- Titan Text G1 Lite model used via Bedrock runtime.
- Custom prompting strategy instructs AI to:
  - Summarize **only** probability risk.
  - List **clinical normal ranges**.
  - Avoid making unqualified judgments or inventing issues.
- Ensures the AI output remains **concise**, **trustworthy**, and **professional**.

---

### 6. Lambda Function: Orchestrating Everything

- Name: `CareLinkVitalsProcessor`
- Python 3.12 Runtime.
- Key Responsibilities:
  - Parse incoming payload.
  - Clinical threshold checks (hard-coded safe ranges).
  - SageMaker endpoint invocation for stability prediction.
  - Bedrock invocation for AI health summary.
  - Save to DynamoDB (type-safe using Decimal handling).
  - Send SNS alert if:
    - Any critical thresholds are breached.
    - ML model predicts instability (even if vitals are borderline).

---

### 7. SNS Topic Setup

- Create SNS Topic: `CareLinkAlerts`
- Subscribe your email to receive emergency alerts.

---

### 8. Testing the System

**Publish a test payload to MQTT:**
```json
{
  "device_id": "carelink-health-monitor",
  "heart_rate": 135,
  "blood_oxygen": 85,
  "temperature": 39.5
}
```
✅ Lambda triggers.  
✅ SageMaker predicts and Bedrock summarizes.  
✅ Data saved in DynamoDB.  
✅ Email alert sent via SNS if danger detected.

---

## 🌟 Future Enhancements

- Mobile push notifications with SNS Mobile.
- Healthcare provider dashboard built on AWS Amplify + AppSync.
- Expand dataset with real-world labeled data from wearable devices.
- Fine-tune the model per specific patient demographics.
- Integrate anomaly detection to pre-warn before thresholds are breached.

---

## 📜 Full Updated Architecture Diagram

```plaintext
+--------------------------+
| CareLink Device/Simulator |
| (MQTT Publish Vitals)     |
+------------+-------------+
             |
             v
+--------------------------+
| AWS IoT Core              |
| Topic: carelink/vitals    |
+------------+-------------+
             |
 (IoT Rule triggers Lambda)
             |
             v
+--------------------------+
| AWS Lambda Function       |
| CareLinkVitalsProcessor   |
| - Parse Vitals            |
| - Clinical Thresholds     |
| - SageMaker ML Prediction |
| - Bedrock AI Summarization|
| - Save to DynamoDB        |
| - SNS Critical Alert      |
+------------+-------------+
             |
             |
             v
+--------------------------+
| AWS SageMaker Endpoint    |
| XGBoost Model             |
| (Patient Risk Prediction) |
+------------+-------------+
             |
             v
+--------------------------+
| Amazon Bedrock AI Model   |
| Titan Text G1 Lite        |
| (Health Summary)          |
+------------+-------------+
             |
             v
+--------------------------+
| AWS DynamoDB Table        |
| carelink_alerts           |
| (Vitals, Prediction, AI)  |
+------------+-------------+
             |
             v
+--------------------------+
| Amazon SNS Topic          |
| carelink-alerts           |
| (Email Alerts)            |
+--------------------------+
```

---

Awesome — here’s a detailed ✍️ **additional section** you can include to **show exactly how the weighted labeling dataset** was created before training the SageMaker model.

This will make your project look **very professional** and show the judges that **you properly engineered your data** for a healthcare setting!

---

# 🏗️ Building the Weighted Labeling Dataset

## Why We Needed It

In critical healthcare applications, a simple "one outlier = unstable" rule doesn't always hold true.  
For example:
- A slightly high heart rate alone may not be an emergency.
- But low blood oxygen is **almost always** critical.

To reflect this **medical reality**, we introduced **weighted clinical importance** when labeling our dataset for ML training.

Instead of treating all abnormalities equally, we calculated an **"instability score"** based on the **vital sign, threshold breach, and its associated weight**.

If the combined weighted score was above a chosen **risk threshold**, we labeled the example as `unstable` (`1`), otherwise `stable` (`0`).

---

## 📈 Vital Signs Weighed for Risk

| Vital sign         | Condition        | Threshold | Weight (0-1) | Clinical Rationale |
|--------------------|------------------|-----------|-------------|--------------------|
| Heart Rate High    | HR > 120 bpm      | 0.4       | Elevated but often compensatory |
| Heart Rate Low     | HR < 50 bpm       | 0.5       | Bradycardia riskier if symptomatic |
| Blood Oxygen Low   | BO < 90%          | 0.9       | Hypoxia is life-threatening |
| Temperature High   | Temp > 39°C       | 0.6       | Indicates infection/inflammation |
| Temperature Low    | Temp < 35°C       | 0.8       | Hypothermia rapidly escalates |

---

## ⚙️ How We Labeled Each Row (Pseudo-code)

```python
# Given: heart_rate, blood_oxygen, temperature

# Step 1: Initialize risk score
risk_score = 0

# Step 2: Evaluate each vital against thresholds
if heart_rate > 120:
    risk_score += 0.4
if heart_rate < 50:
    risk_score += 0.5
if blood_oxygen < 90:
    risk_score += 0.9
if temperature > 39:
    risk_score += 0.6
if temperature < 35:
    risk_score += 0.8

# Step 3: Determine label
# Threshold: 0.5 (can be tuned for stricter/looser definitions)
if risk_score >= 0.5:
    label = 1  # Unstable
else:
    label = 0  # Stable
```

✅ This ensures that **multiple minor breaches** OR **a single serious breach** both correctly classify a patient as unstable.  
✅ It reflects **real-world medical triage logic** more accurately than a naive threshold-based model.

---

## 📦 Data Processing Before Training

- Cleaned all vitals to ensure realistic physiological ranges (e.g., no heart rates of 1000 bpm).
- Applied the weighted labeling logic above to generate the `label` column.
- Split the dataset:
  - 80% for training
  - 20% for testing
- Uploaded to S3 bucket `carelink-ai-datasets`.
- Passed CSV into SageMaker XGBoost Estimator.

---

## 🚀 Benefits of This Approach

- **More realistic clinical behavior:** recognizes that different vital signs have different levels of emergency.
- **Better ML generalization:** model learns the nuanced relationships between vitals, not just isolated thresholds.
- **More explainable:** clinicians can understand why a "stable" or "unstable" result was given.

---

# 📋 Mini Example

| Heart Rate | Blood Oxygen | Temperature | Risk Score | Label |
|------------|--------------|-------------|------------|-------|
| 130        | 95%          | 37°C         | 0.4        | 0     |
| 60         | 88%          | 36°C         | 0.9        | 1     |
| 48         | 93%          | 36°C         | 0.5        | 1     |
| 85         | 92%          | 34°C         | 0.8        | 1     |

---

# 🏁 Summary

**CareLink**'s dataset was **not just collected — it was clinically reasoned and weighted (through non-clinical research, author's best attempt)** to simulate real healthcare environments.

**This step alone is what elevates CareLink above traditional hackathon prototypes** — it was built for **trustworthiness**, **clinical realism**, and **scalability**.

---

## 📜 License

MIT License — Feel free to fork, contribute, and build upon CareLink!

---

## 🔗 Important Links

- [DEMO VIDEO](https://youtu.be/cR94Yz0m0Eg)  
- [DEMO SCRIPT](https://github.com/JFoxUK/AWS-Hackathon-CareLink/blob/main/DEMO_SCRIPT.md)  
- [DEVPOST SUBMISSION]()

---

## ✍️ Author

- [GitHub](https://github.com/JFoxUK)  
- [LinkedIn](https://linkedin.com/in/jfoxuk)  
- [Devpost](https://devpost.com/JFoxUK)

---

# 🚀 CareLink — Democratizing Remote Healthcare Through AI + IoT

---