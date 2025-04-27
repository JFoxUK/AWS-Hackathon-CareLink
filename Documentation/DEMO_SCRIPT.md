# 💕 CareLink Hackathon Demo Script (Updated)

## 🎥 CareLink Hackathon Demo Script

## 🎬 1. Intro (30 seconds)

> "Hi, I'm [Your Name], and this is **CareLink**, our submission for the AWS Breaking Barriers Hackathon 2025.  
> CareLink demonstrates how **IoT connectivity, serverless architecture, machine learning with SageMaker, and Amazon Bedrock generative AI** can work together to create **equitable, real-time health monitoring** — even in underserved or remote communities."

## 🎬 2. Quick Architecture Overview (30 seconds)

> "The system works like this:  
> - A CareLink device, or simulator, publishes patient vitals like heart rate, blood oxygen, and temperature to AWS IoT Core.  
> - An IoT Rule triggers a Lambda function.  
> - The Lambda function performs critical threshold checks, predicts patient stability with a **SageMaker ML model**, analyzes the vitals with **Amazon Bedrock Titan Text G1 Lite** for an AI health summary, and saves everything to DynamoDB.  
> - If the vitals cross critical safety thresholds or the AI predicts instability, an **SNS email alert** is immediately sent to healthcare providers."

> *[Optional: Show the architecture diagram briefly here.]*

## 🎬 3. Live Demo Walkthrough (3 minutes)

**Step 1: Publish MQTT Test Vitals**

- Show the AWS IoT Core Test Client.
- Publish a message with slightly elevated vitals:

```json
{
  "device_id": "carelink-health-monitor",
  "heart_rate": 135,
  "blood_oxygen": 85,
  "temperature": 39.5
}
```

> "Here, I’m sending simulated patient vitals that are intentionally dangerous — a heart rate of 135 and blood oxygen of 85%."

**Step 2: Lambda, SageMaker, and DynamoDB Reaction**

- Quickly flip to Lambda → Monitoring → Logs.
- Show SageMaker model prediction in logs (0 = stable, 1 = unstable).
- Show Bedrock's AI health summary being generated.
- Show DynamoDB table.

> "Our Lambda immediately triggered. It parsed the vitals, ran critical threshold checks, invoked **SageMaker** for a machine learning stability prediction, and generated a human-readable health analysis with **Amazon Bedrock**."

- Show the DynamoDB record:
  - Vitals stored
  - AI `alert_summary` stored
  - ML model prediction stored

> "All vital signs, AI analysis, and the ML prediction are stored together for easy review."

**Step 3: SNS Email Alert**

- Show the SNS email alert you received.

> "Because the patient's vitals were critical, CareLink instantly sent an SNS email alert to medical staff."

## 🎬 4. AI vs Guardrails Insight (Important — 45 seconds)

> "You'll notice something very important here:  
> Our AI model — Titan Text G1 Lite — sometimes *understates* the risk. In one test, it suggested there was 'no immediate health concern' despite dangerously high vitals.  
> This is realistic. General-purpose AI isn't yet certified for highly regulated fields like healthcare.  
> That’s why CareLink uses a **hybrid approach**:  
> - **SageMaker ML predictions** for patient stability classification.  
> - **Generative AI** for helpful, contextual analysis.  
> - **Hard-coded clinical thresholds** to guarantee alerts for critical conditions.  
> This layered, "human-in-the-loop" system design is **essential for real-world, regulated, critical industries**."

## 🎬 5. Closing (15 seconds)

> "In summary, CareLink shows how AWS connectivity, serverless computing, SageMaker ML, and Bedrock AI can democratize healthcare monitoring,  
> while responsibly ensuring **patient safety** through built-in clinical safeguards.  
> Thank you for considering CareLink!"

# 🖊️ Recording Setup Checklist

Before recording the demo video, ensure you:

- [ ] Have AWS Console tabs open for:
  - IoT Core (Test Client)
  - Lambda Logs (CloudWatch)
  - DynamoDB Table (`carelink_alerts`)
  - SNS Email Inbox (ready to show the incoming alert)
- [ ] Have a test MQTT message prepared (dangerous vitals ready to publish)
- [ ] Fullscreen your browser (no distractions visible)
- [ ] Clear any unrelated browser tabs
- [ ] Keep the script nearby to reference timing and flow
- [ ] Start recording, then flow smoothly through the demo following the script!

---

# 🚀 Good luck from the CareLink team! 💛🚀

