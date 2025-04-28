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
- CSV format with engineered features + stability label.
- **Vital Sign Weighting Logic**:

| Vital Sign | Condition | Threshold | Weight | Clinical Reasoning |
|------------|------------|-----------|--------|--------------------|
| Heart Rate High | > 120 bpm | 0.4 | Risky but sometimes compensatory (e.g., fever) |
| Heart Rate Low | < 50 bpm | 0.5 | Bradycardia can cause fainting or cardiac arrest |
| Blood Oxygen Low | < 90% | 0.9 | Severe hypoxia demands immediate care |
| Temperature High | > 39°C | 0.6 | Suggests infection or inflammation |
| Temperature Low | < 35°C | 0.8 | Hypothermia needs urgent treatment |

---

# 📈 CareLink Model Feature Table

| Feature Name               | Type        | Description                                                      | Range / Encoding          |
|-----------------------------|-------------|------------------------------------------------------------------|----------------------------|
| `heart_rate_normalized`     | Continuous  | Patient's heart rate normalized between 0–1.                    | 0.0 – 1.0                  |
| `blood_oxygen_normalized`   | Continuous  | Patient's blood oxygen saturation normalized between 0–1.        | 0.0 – 1.0                  |
| `temperature_normalized`    | Continuous  | Patient's body temperature normalized between 0–1.               | 0.0 – 1.0                  |
| `hr_high`                   | Binary      | 1 if heart rate > 120 bpm, else 0.                                | 0 or 1                     |
| `hr_low`                    | Binary      | 1 if heart rate < 50 bpm, else 0.                                 | 0 or 1                     |
| `bo_low`                    | Binary      | 1 if blood oxygen < 90%, else 0.                                  | 0 or 1                     |
| `temp_high`                 | Binary      | 1 if temperature > 39°C, else 0.                                  | 0 or 1                     |
| `temp_low`                  | Binary      | 1 if temperature < 35°C, else 0.                                  | 0 or 1                     |
| `label`                     | Target      | 1 = unstable patient, 0 = stable patient.                         | 0 or 1                     |

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

```
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

# 📚 FAQ: Engineering CareLink's Dataset

### Why Normalize the Vitals?

- Different units: HR vs SpO2 vs Temperature vary in scale.
- Normalization ensures all features contribute **equally** to predictions.
- Prevents domination by large-value features (e.g., heart rate).

---

### Why Add Binary Flags for Thresholds?

- Binary flags make it **easier** for the ML model to spot clinical emergencies.
- Instead of requiring deep tree-splitting, threshold breaches are **immediately obvious**.

---

### Why Weight Vital Signs Differently?

- Medical reality: not all abnormalities are equally dangerous.
- Low oxygen is way riskier than a high heart rate.
- Weighting vital signs based on clinical urgency makes the model **much more realistic**.

---

### How Is Instability Determined?

- Cumulative risk score calculated from breaches and weights.
- Threshold of 0.5 defines "unstable" vs "stable."
- Allows **multiple small issues** OR **one big issue** to trigger instability.

---

# 🏁 Final Thoughts

CareLink is **not just an IoT app** — it was designed with **clinical reasoning, robust feature engineering**, and **AI safety practices** to make **real-world-ready remote healthcare possible**.

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