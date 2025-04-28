# 💕 CareLink: AI-Powered Remote Health Monitoring

CareLink is a proof-of-concept project built for the **AWS Breaking Barriers Hackathon 2025**.

It showcases how **next-generation connectivity (AWS IoT Core, 5G)**, **Machine Learning (Amazon SageMaker)**, and **Generative AI (Amazon Bedrock)** can be combined to deliver **equitable, real-time healthcare monitoring** for underserved and remote communities.

---

## 🚀 Solution Architecture

**Core Technologies:**
- **AWS IoT Core**: Securely receives vitals (heart rate, blood oxygen, temperature) via MQTT.
- **AWS Lambda**: Serverless processing to parse data, invoke ML models, and orchestrate the full pipeline.
- **Amazon SageMaker**: Custom-trained ML model predicts patient stability based on vitals.
- **Amazon Bedrock (Titan Text G1 Lite)**: Converts numerical predictions into professional, readable AI summaries.
- **Amazon DynamoDB**: Durable, low-latency storage for vitals, predictions, and summaries.
- **Amazon SNS**: Delivers real-time alerts when critical issues are detected.
- **AWS CloudWatch**: Observability for logs, metrics, and operational health.

---

## 🛗 System Overview

1. **Vital Collection**: A simulated or real device publishes health readings to the MQTT topic `carelink/vitals`.
2. **AWS IoT Rule**: Triggers the **CareLinkVitalsProcessor Lambda** on new messages.
3. **AWS Lambda**:
   - Parses vitals and checks clinical thresholds (e.g., dangerously low oxygen).
   - Calls **Amazon SageMaker** for a stability prediction (binary + probability).
   - Calls **Amazon Bedrock** for a readable AI health report.
   - Stores results in **DynamoDB**.
   - Sends an **SNS alert** if critical conditions are detected or predicted.

---

## 💪 How to Build and Deploy CareLink

### 1. AWS Prerequisites
- Required services:
  - IoT Core
  - Lambda
  - DynamoDB
  - SageMaker
  - Bedrock
  - SNS
- **Regions**:
  - SageMaker and Bedrock: **us-east-1**.
  - IoT Core and Lambda: any supported region.

---

### 2. AWS IoT Core Setup

- Create an IoT Thing (`carelink-health-monitor`).
- Attach certificates and a permissive IoT policy.
- Create a rule to route MQTT traffic from `carelink/vitals` to Lambda.

---

### 3. DynamoDB Setup

- Table name: `carelink_alerts`
- Partition Key: `device_id` (String)
- Sort Key: `timestamp` (String)
- Billing Mode: On-Demand

---

### 4. SageMaker Model: Patient Stability Classifier

**Custom Dataset:**
- CSV format with heart rate, blood oxygen, temperature, and `label` (0 = stable, 1 = unstable).
- **Vital Sign Weighting Logic**:

| Vital Sign | Condition | Threshold | Weight | Clinical Reasoning |
|------------|------------|-----------|--------|--------------------|
| Heart Rate High | > 120 bpm | 0.4 | Risky but sometimes compensatory (e.g., fever) |
| Heart Rate Low | < 50 bpm | 0.5 | Bradycardia can cause fainting or cardiac arrest |
| Blood Oxygen Low | < 90% | 0.9 | Severe hypoxia demands immediate care |
| Temperature High | > 39°C | 0.6 | Suggests infection or inflammation |
| Temperature Low | < 35°C | 0.8 | Hypothermia needs urgent treatment |

**Training Details:**
- Model: **XGBoost 1.5** (SageMaker built-in container).
- Objective: **binary:logistic**.
- Hyperparameters:
  - `max_depth=5`, `eta=0.2`, `gamma=4`, `min_child_weight=6`, `subsample=0.7`, `num_round=100`
- Endpoint: `carelink-xgboost-endpoint`.

---

### 5. Amazon Bedrock Integration

- **Model**: Titan Text G1 Lite.
- **Prompt Strategy**:
  - Summarize risk probability.
  - List normal clinical ranges.
  - Avoid speculative or judgmental language.
- Ensures summaries are **clear**, **trustworthy**, and **actionable**.

---

### 6. Lambda Function: Orchestrating the Pipeline

- Name: `CareLinkVitalsProcessor`
- Python 3.12
- Core tasks:
  - Parse payload.
  - Check clinical thresholds.
  - Invoke SageMaker and Bedrock.
  - Save results to DynamoDB.
  - Send SNS alert if:
    - Critical thresholds are breached.
    - ML predicts instability.

---

### 7. SNS Topic Setup

- Topic name: `CareLinkAlerts`
- Subscribe your email to receive critical notifications.

---

### 8. Testing the System

Test payload:
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
✅ Data saved to DynamoDB.  
✅ Email alert sent if risk detected.

---

## 🌟 Future Enhancements

- Mobile app notifications via SNS Mobile Push.
- Amplify + AppSync healthcare provider dashboard.
- Expanded dataset with real-world wearables.
- Demographic-specific model fine-tuning.
- Early anomaly detection to pre-empt instability.

---

# 📋 Full Updated Architecture Diagram

```+--------------------------+
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
+--------------------------+```

---

# 🏗️ Building a Clinically Weighted Dataset

## Why It Matters

In healthcare, **not all vital signs are equally urgent**.  
For example:
- A slightly elevated heart rate may be benign.
- Low blood oxygen almost always requires immediate intervention.

We reflected this by **applying weighted clinical importance** to each vital during labeling.

Rather than simple threshold breaches, we calculated a **cumulative risk score** to classify stability more realistically.

---

## 📈 Vital Sign Weighting Table

| Vital sign         | Threshold | Weight | Clinical Rationale                  |
|--------------------|-----------|--------|-------------------------------------|
| Heart Rate High    | > 120 bpm | 0.4    | Often compensatory                  |
| Heart Rate Low     | < 50 bpm  | 0.5    | Symptomatic bradycardia dangerous   |
| Blood Oxygen Low   | < 90%     | 0.9    | Life-threatening hypoxia            |
| Temperature High   | > 39°C    | 0.6    | Indicates infection or inflammation |
| Temperature Low    | < 35°C    | 0.8    | Hypothermia escalates rapidly       |

---

## ⚙️ Labeling Logic (Pseudo-code)

```python
risk_score = 0

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

label = 1 if risk_score >= 0.5 else 0
```

✅ Captures both **multiple minor risks** and **single major risks**.  
✅ Reflects **real-world triage logic**.

---

## 📦 Data Preprocessing

- Cleaned unrealistic values (e.g., HR > 300 bpm discarded).
- Applied weighted labeling.
- Normalized features (0–1 range) to prevent model bias.
- Split into training (80%) and testing (20%) sets.
- Uploaded to S3 bucket: `carelink-ai-datasets`.

---

## 🚀 Benefits of This Approach

- **Clinical realism:** Mirrors actual triage thinking.
- **Improved ML generalization:** Learns vital sign interdependencies.
- **Transparency:** Easier for healthcare providers to trust.

---

# 📋 Mini Example

| Heart Rate | Blood Oxygen | Temperature | Risk Score | Label |
|------------|--------------|-------------|------------|-------|
| 130        | 95%          | 37°C         | 0.4        | 0     |
| 60         | 88%          | 36°C         | 0.9        | 1     |
| 48         | 93%          | 36°C         | 0.5        | 1     |
| 85         | 92%          | 34°C         | 0.8        | 1     |

---

🧮 **Why Normalize?**  
- Different vitals vary in range (HR vs SpO2 vs Temp).  
- Normalization ensures **equal model attention** across features.  
- Improves training stability and prediction quality.

---

# 🏁 Summary

CareLink’s dataset wasn’t just assembled — it was **thoughtfully engineered** to simulate real clinical environments.  
This deliberate approach sets CareLink apart from typical hackathon projects: it was built for **trust**, **realism**, and **scalability**.

---

## 📜 License

MIT License — fork, build, and improve freely!

---

## 🔗 Important Links

- [Demo Video](https://youtu.be/cR94Yz0m0Eg)  
- [Demo Script](https://github.com/JFoxUK/AWS-Hackathon-CareLink/blob/main/DEMO_SCRIPT.md)  
- [Devpost Submission]() (link coming soon)

---

## ✍️ Author

- [GitHub](https://github.com/JFoxUK)  
- [LinkedIn](https://linkedin.com/in/jfoxuk)  
- [Devpost](https://devpost.com/JFoxUK)

---

# 🚀 CareLink — Democratizing Remote Healthcare Through AI + IoT

---
