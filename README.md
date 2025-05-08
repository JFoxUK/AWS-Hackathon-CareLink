# 💕 CareLink: AI-Powered Remote Health Monitoring

CareLink is a proof-of-concept project for the **AWS Breaking Barriers Hackathon 2025**.

It demonstrates how **next-generation connectivity (AWS IoT Core)**, **Machine Learning (Amazon SageMaker)**, and **Generative AI (Amazon Bedrock)** can combine to deliver **real-time, equitable healthcare monitoring** — especially for remote and underserved communities.

---

## 🚀 Solution Architecture

**Core AWS Services:**
- **AWS IoT Core** — Ingests vital signs securely via MQTT.
- **AWS Lambda** — Parses incoming vitals and saves them to storage.
- **Amazon DynamoDB** — Stores historical patient vitals for retrieval and analysis.
- **Amazon SNS** — Sends instant alerts if critical thresholds are breached.
- **Amazon SageMaker** — Predicts the probability of patient instability using machine learning.
- **Amazon Bedrock (Titan Text G1 Lite)** — Generates clinical-style summaries based on patient history.
- **Amazon Bedrock (Nova Sonic)** — Have a human like conversation about the data with an Ai Agent.
- **AWS CloudWatch** — Logs and monitors system operations.

---

## 🛗 Updated System Overview

1. **Vital Collection**  
   Devices or simulators publish patient vitals (heart rate, blood oxygen, temperature) to the MQTT topic `carelink/vitals`.

2. **AWS IoT Core ➔ Lambda**  
   An IoT rule triggers the **CareLinkVitalsProcessor Lambda** on every new vital sign message:
   - Parses the data.
   - Saves the raw vitals directly to **DynamoDB**.
   - If critical thresholds are breached, sends an **SNS alert** immediately.

3. **Frontend Dashboard**  
   The React dashboard fetches historical vitals from **DynamoDB** by calling a **separate Lambda**:
   - Sends the latest 24 hours of vitals to **SageMaker** for a stability prediction.
   - Sends the latest 24 hours of vitals to **Bedrock** for an AI-written clinical summary.
   - Displays:
     - Instability Risk Meter (with live percentage)
     - Raw prediction probability (exact model output)
     - Bedrock AI Clinical Summary
     - Graphs of vitals over time for the past 3 months of data
     - Have a human like conversation about the data with an Ai Agent
---

## 🧠 Machine Learning Model: SageMaker Stability Classifier

### Training Overview:

- We created a **clinically realistic synthetic dataset** using engineered thresholds.
- Features:
  - **Heart Rate (normalized)**
  - **Blood Oxygen (normalized)**
  - **Temperature (normalized)**
- Output:
  - **Binary label**: Stable (0) vs Unstable (1)

**Focus:**  
⚡ Emphasize safety by minimizing false negatives (missing real instability is worse than sending a false alert).

**Model Details:**
- **Type**: Binary classification
- **Algorithm**: XGBoost
- **Training Location**: SageMaker in `us-east-1`

---

## 📈 Feature Table

| Feature Name               | Type        | Description                                                      | Range         |
|-----------------------------|-------------|------------------------------------------------------------------|---------------|
| `heart_rate_normalized`     | Continuous  | Normalized patient heart rate                                    | 0.0 – 1.0     |
| `blood_oxygen_normalized`   | Continuous  | Normalized blood oxygen saturation                               | 0.0 – 1.0     |
| `temperature_normalized`    | Continuous  | Normalized body temperature                                      | 0.0 – 1.0     |
| `label`                     | Target      | 1 = unstable patient, 0 = stable patient                         | 0 or 1        |

---

## 🗄️ DynamoDB Storage

**Table Name**: `carelink_alerts`  
**Schema**:

| Field | Type | Description |
|------|------|-------------|
| `device_id` | String | Patient's device ID |
| `timestamp` | String (ISO 8601) | Exact time of the reading |
| `heart_rate` | Number | Heart rate (bpm) |
| `blood_oxygen` | Number | Blood oxygen (%) |
| `temperature` | Number | Temperature (°C) |
| `status` | String | `"stable"` or `"unstable"` label for basic flagging |

✅ **Only raw vitals + status are stored** — no SageMaker predictions or Bedrock summaries saved.

---

## 📋 Updated System Diagram

```
  Device/Simulator
       |
  [ MQTT Publish ]
       |
       v
  AWS IoT Core (carelink/vitals)
       |
  IoT Rule
       |
       v
  AWS Lambda (CareLinkVitalsProcessor)
  - Save raw vitals to DynamoDB
  - Send SNS alerts if critical
       |
       v
  AWS DynamoDB (carelink_alerts)

  (Separately)
  
  Frontend Dashboard
       |
  ➔ Lambda (Fetch vitals)
       |
  ➔ SageMaker (Predict risk based on latest 24h vitals)
       |
  ➔ Bedrock (Summarize last 3 months of vitals)
       |
  ➔ Bedrock (Nova Sonic) (Have a human like conversation about the data with an Ai Agent)
       |
  ➔ React Frontend (Display meter, graph, raw score, AI summary)
```

---

## 🧠 Bedrock AI Clinical Summaries

- **Model**: Titan Text G1 Lite
- **Prompt Strategy**:
  - Summarize vitals history factually.
  - Highlight increases, decreases, and trends.
  - Avoid guessing or proposing clinical treatments.
  - Output designed for quick review by healthcare workers.

---

## 📋 Frontend Features (React)

| Feature | Details |
|---------|---------|
| Instability Risk Meter | Animated circular meter showing SageMaker prediction |
| Raw Probability Display | Exact model output shown alongside the meter |
| Bedrock AI Summary | Auto-generated clinical summary of patient's history |
| Vitals Over Time Graph | Smooth, clean Chart.js graphs (no background fills) |
| Developer Input Panel | Bulk upload of test JSON vitals (accordion panel) |

---

## 📚 Why Normalize Vitals?

- Different clinical signs (HR, SpO2, Temp) operate at different numeric scales.
- Normalization ensures **fair weighting** during model training.
- Prevents HR from overwhelming oxygen and temperature in model influence.

---

## 🌟 Future Enhancements

- Real wearable integration (BLE/5G)
- Admin dashboard for multi-patient management
- Mobile app with SNS Push
- Fine-tuned Bedrock prompts for different clinical personas (nurse vs doctor)

---

# 🏁 Final Thoughts

CareLink shows how **AI + IoT + Cloud** can bridge the healthcare access gap —  
bringing **trusted, automated support** to frontline healthcare workers everywhere.

---

## 📜 License

MIT License — fork, build, and improve freely!

---

## 🔗 Important Links

- [Demo Video](https://youtu.be/cR94Yz0m0Eg)  
- [Demo Script](https://github.com/JFoxUK/AWS-Hackathon-CareLink/blob/main/DEMO_SCRIPT.md)  
- [Try the app, follow the README steps to start Nova Sonic, then, the app will also open wiht Nova integrated](https://github.com/JFoxUK/AWS-Hackathon-CareLink/tree/main/carelink-web/CareLink%20App%20Using%20AWS%20Example%20of%20Nova%20Sonic/speech-to-speech)

---

## ✍️ Author

- [GitHub](https://github.com/JFoxUK)  
- [LinkedIn](https://linkedin.com/in/jfoxuk)  
- [Devpost](https://devpost.com/JFoxUK)

---

# 🚀 CareLink — Democratizing Remote Healthcare Through AI + IoT

---
