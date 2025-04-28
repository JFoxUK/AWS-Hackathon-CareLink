# About the Project

## ✨ Inspiration

We were inspired to build CareLink to address a real-world healthcare challenge:  
**How can we support remote patients — especially in underserved or isolated areas — without requiring expensive infrastructure, hospital networks, or constant monitoring staff?**

We envisioned a lightweight, scalable healthcare monitoring system that could:
- Collect patient vital signs with simple edge devices
- Analyze trends intelligently using AI
- Instantly alert caregivers to potential instability
- Stay affordable, fast, and secure through serverless cloud technologies

---

## 🛠️ How We Built It

CareLink collects **heart rate**, **blood oxygen**, and **temperature** readings. It uses:
- **AWS IoT Core** for secure, real-time transmission of patient vitals.
- **AWS Lambda** to process and route data instantly without managing servers.
- **Amazon DynamoDB** to store incoming vital signs over time.
- **Amazon SageMaker** to **predict patient instability risk** based on recent vitals.
- **Amazon Bedrock (Titan Text G1 Lite)** to **summarize 3 months of patient history** into a clear, clinical-style report.
- **Amazon SNS** to send **real-time alerts** when dangerous conditions are detected.
- **API Gateway** and a **React.js + Vite** frontend to allow caregivers to publish and view AI assessments in real time.

---

## 🔄 Why We Pivoted Our Machine Learning Approach

Originally, we planned to predict patient instability based on **only the latest single reading** (heart rate, blood oxygen, temperature).

However, during testing, we realized:
- One-off readings are **too noisy** and often **misleading** in clinical practice.
- Real clinicians **always assess trends**, not single datapoints.

### Our Pivot:
- We **pivoted** to use the **latest 24 hours of vitals** for each patient (one reading per hour).
- We **collapsed 24 hours of data into one row** by serializing them as **long feature vectors** for SageMaker.
- Example:  
  Instead of 3 features, our model input became **72 features** (24 readings × 3 vitals).

This gave the model **"fake memory"** — the ability to see and learn trends **without needing complex RNN or LSTM architectures**.

✅ Much better real-world performance.  
✅ Still compatible with SageMaker's managed XGBoost — **no heavy PyTorch/TensorFlow** deployments needed.

---

## 🚧 Challenges We Faced

### 1. SageMaker Endpoint Design

- **Latency**:  
  Realized that for rapid API-driven apps, **complex large models** were too slow.  
  XGBoost stayed fast (~<500ms per inference).

- **Input Limits**:  
  Had to serialize the 24 hours' worth of vitals carefully to stay under payload size limits.

- **Deployment Region Constraints**:  
  Had to split the architecture (SageMaker/Bedrock in `us-east-1`, Lambda in `eu-north-1`) and manage cross-region communication.

---

### 2. Clinical Weighting of Vitals

In real life, **not all vital sign abnormalities are equally dangerous**.  
So we engineered clinical weighting logic when building the training dataset:

| Vital Sign          | Condition        | Weight | Reason |
|---------------------|------------------|--------|--------|
| Heart Rate High     | HR > 120 bpm      | 0.4    | Often compensatory, less critical |
| Heart Rate Low      | HR < 50 bpm       | 0.5    | Bradycardia can cause fainting, cardiac arrest |
| Blood Oxygen Low    | BO < 90%          | 0.9    | Hypoxia demands immediate intervention |
| Temperature High    | Temp > 39°C       | 0.6    | High fever suggests severe infection |
| Temperature Low     | Temp < 35°C       | 0.8    | Hypothermia is extremely dangerous |

This clinical feature engineering made the model **much safer and more realistic**.

---

### 3. Bedrock Summarization Anchoring

Early on, Bedrock AI sometimes produced summaries that were **too optimistic** or **speculative**.  
We fixed this by:
- Anchoring Bedrock prompts to the **SageMaker risk score**.
- Asking for factual reporting based **only on the data provided**.

---

### 4. Data Serialization and Frontend Cleanliness

- DynamoDB JSON storage needed careful serialization (e.g., `Decimal` handling).
- We spent time ensuring the React frontend was:
  - **Clinically styled** (clear fonts, readable graphs)
  - **Fast and mobile-friendly**
  - **Directly showing both raw AI outputs and readable summaries**

---

## 🧠 What We Learned

- **How to pivot fast** when clinical realism shows flaws in early plans.
- **How to extend simpler ML models** (like XGBoost) with clever data design instead of adding infrastructure burden.
- **How to combine SageMaker + Bedrock** safely for real-world healthcare apps.
- **How AWS serverless tools** (IoT Core, Lambda, DynamoDB) enable real-time pipelines without scaling headaches.

---

# 📈 Final Solution Architecture

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
  ➔ SageMaker (Predict risk on 24hr window)
       |
  ➔ Bedrock (Summarize last 24hrs of vitals)
       |
  ➔ React Frontend (Displays AI results beautifully with latest 3 months of data in a chart)
```

---