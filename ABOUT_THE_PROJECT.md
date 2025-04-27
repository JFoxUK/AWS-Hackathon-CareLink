# About the Project

## ✨ Inspiration

We were inspired to build CareLink to address a real-world problem:  
**How can we support remote patients** — especially in underserved or hard-to-reach areas — **without requiring expensive or complex medical infrastructure?**

We envisioned a lightweight, real-time healthcare monitoring system that could:
- Collect vital signs using simple devices
- Analyze data intelligently using AI
- Alert humans immediately if needed
- Remain scalable, deployable, and highly secure using serverless cloud technologies

---

## 🛠️ How We Built It

CareLink automatically collects **heart rate**, **blood oxygen**, and **temperature** readings. It uses:
- **AWS IoT Core** to securely transport health vitals.
- **AWS Lambda** for real-time serverless processing of incoming vitals.
- **Amazon SageMaker** to predict the **probability of patient instability** based on clinical weightings.
- **Amazon Bedrock (Titan Text G1 Lite)** to generate **readable AI health summaries** anchored to the SageMaker outputs.
- **Amazon DynamoDB** to store patient vitals, ML predictions, and AI summaries.
- **Amazon SNS** to send **instant critical alerts** via email.
- **API Gateway** to expose serverless APIs to a **React.js + Vite** healthcare web app where users can publish and view AI-generated assessments in real-time.

---

## 🧠 What We Learned

- How to **blend multiple AI models** (SageMaker + Bedrock) into a **hybrid, reliable system** for critical decision-making.
- How to engineer **responsible prompts** that anchor generative AI outputs to deterministic models.
- How to build **clinical-weighted machine learning** — not all abnormal vital signs are equally dangerous, and training AI to understand that saves lives.
- How AWS services like **IoT Core, Lambda, DynamoDB, SageMaker, and Bedrock** can work together to create **powerful real-time serverless healthcare systems**.
- How even a **simple local web app** becomes powerful when combined with cloud backends.

---

## 🚧 Challenges We Faced

### AI Reliability in Healthcare
Initially, Bedrock's AI could underplay critical health risks. To fix this, we:
- Trained a custom **SageMaker XGBoost model** using real-world vitals data.
- Anchored Bedrock prompts to **SageMaker model predictions** to generate safer, more clinical AI summaries.

### Designing a Clinical Weighting System
We built a **weighted risk model** because not all vital abnormalities are equally urgent:

| Vital Sign          | Condition        | Weight | Reason |
|---------------------|------------------|--------|--------|
| Heart Rate High     | HR > 120 bpm      | 0.4    | Elevated HR often compensatory |
| Heart Rate Low      | HR < 50 bpm       | 0.5    | Bradycardia sometimes normal but dangerous |
| Blood Oxygen Low    | BO < 90%          | 0.9    | Hypoxia needs urgent care |
| Temperature High    | Temp > 39°C       | 0.6    | High fever indicates severe infection |
| Temperature Low     | Temp < 35°C       | 0.8    | Hypothermia is extremely dangerous |

This enabled the SageMaker model to **prioritize the most life-threatening conditions** intelligently.

### Event Routing and Serialization
- **IoT Routing:** Real-time ingestion using MQTT into AWS Lambda needed careful scaling and error handling.
- **Serialization:** DynamoDB uses `Decimal` data types, requiring careful transformation before frontend consumption.

### User Experience
We wanted the front-end web app to feel **accessible, fast, and clinically appropriate** — despite running only locally during the hackathon.

---