# 💕 CareLink Hackathon Demo Script (Final)

## 🎬 1. Intro (30 seconds)

> "Hi, I'm [Your Name], and this is **CareLink**, our submission for the AWS Breaking Barriers Hackathon 2025.  
> CareLink shows how **IoT, serverless AWS services, machine learning via SageMaker, and generative AI via Bedrock** can be combined to create **equitable, real-time health monitoring** — even in remote or underserved communities."

---

## 🎬 2. Quick Architecture Overview (30 seconds)

> "The system works like this:  
> - Patient vitals like heart rate, blood oxygen, and temperature are sent to **AWS IoT Core**.  
> - An IoT Rule triggers a **Lambda function**.  
> - Lambda saves the vitals to **DynamoDB** and sends an **SNS alert** if critical thresholds are crossed.  
> - Our React dashboard retrieves the past **3 months** of vitals, and invokes **SageMaker** to predict instability based on the **latest 24 hours** of data.  
> - **Amazon Bedrock** then generates a full, clinically styled summary of the patient’s health history.
> - **Amazon Bedrock** also has a human like conversation about the data with an Ai Agent.

> *[Optional: Show the updated architecture diagram briefly.]*

---

## 🎬 3. Live Demo Walkthrough (3 minutes)

**Step 1: Publish New Vitals**

- Open AWS IoT Core → MQTT Test Client.
- Publish the following message:

```json
{
  "device_id": "carelink-health-monitor",
  "heart_rate": 135,
  "blood_oxygen": 85,
  "temperature": 39.5
}
```

> "Here, I'm simulating dangerous patient vitals — high heart rate and low oxygen — as if from a real-world wearable device."

---

**Step 2: Lambda & DynamoDB Reaction**

- Open CloudWatch Logs.
- Show Lambda execution (saving vitals to DynamoDB, SNS alert if triggered).

- Open DynamoDB Table (`carelink_alerts`) and show new record:
  - `heart_rate`, `blood_oxygen`, `temperature`
  - `timestamp`
  - `status` field (auto-classified as "stable" or "critical" based on rules)

> "CareLink ingested the vitals in real-time, performed clinical checks, saved the data, and triggered alerts if necessary — all serverless and at global scale."

---

**Step 3: Dashboard: AI Prediction and Summary**

- Open the React web app.
- Click "Fetch Latest Vitals & AI Summary."

> "Our dashboard fetches the latest 3 months of vitals, automatically analyzes the most recent 24-hour period with **SageMaker**, and generates a full health summary with **Bedrock**. If the user wants to, the AI agent can also have a human like conversation about the data with an Ai Agent." 

- Show:
  - AI circular progress meter (instability %)
  - Raw SageMaker probability displayed
  - Bedrock AI health summary (formatted cleanly)
  - Trend graph of vital signs over time
  - Human like conversation about the data with an Ai Agent

> "The AI not only gives a risk percentage but also produces a clinically readable history review — built entirely from real patient data."

---

## 🎬 4. Special Engineering Highlights (Important — 60 seconds)

> "During development, we realized **single vital readings aren't enough** to judge patient stability accurately.  
> So we pivoted — instead of predicting from one reading, we now send **the latest 24 hours of vitals** into SageMaker."

> "This 'fake memory' approach lets our XGBoost model spot real health trends without needing complex deep learning or RNNs,  
> which keeps the system **fast, serverless, and low-cost**."

> "We also faced challenges with **AI safety**.  
> Generative AI like Bedrock can sometimes understate medical risks.  
> So CareLink combines:  
> - **SageMaker ML risk classification**  
> - **Bedrock readable summaries**  
> - **Hard clinical thresholds enforced in Lambda**  
> This multi-layered approach guarantees patient safety first."

---

## 🎬 5. Closing (15 seconds)

> "In summary, CareLink shows how AWS IoT, serverless compute, machine learning, and generative AI can **democratize remote healthcare access** —  
> responsibly, safely, and in real time.  
> Thank you!"

---

# 🖊️ Recording Setup Checklist

Before recording the demo video, ensure you:

- [ ] Open AWS IoT Core (Test Client)
- [ ] Open CloudWatch Logs for Lambda
- [ ] Open DynamoDB Table (`carelink_alerts`)
- [ ] Open your React frontend dashboard
- [ ] Publish a "critical" vital message live
- [ ] Show the Lambda processing
- [ ] Show the database record creation
- [ ] Show the AI prediction + Bedrock summary
- [ ] (Optional) Show SNS email alert if triggered
- [ ] Keep browser clean, fullscreen for professional appearance

---

# 🚀 Good luck — CareLink is ready to impress! 💛

---
