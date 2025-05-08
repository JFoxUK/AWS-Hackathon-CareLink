# 🌐 CareLink Web App

[![Built with React](https://img.shields.io/badge/Built%20With-React-blue)](https://react.dev/)
[![Powered by AWS](https://img.shields.io/badge/Powered%20By-AWS-orange)](https://aws.amazon.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

A lightweight React.js client to submit patient vitals and display real-time AI health summaries, backed by AWS IoT, Lambda, SageMaker, and Bedrock.

---

## 🚀 Features

- Submit **Heart Rate**, **Blood Oxygen**, and **Temperature** vitals.
- Publish vitals securely to AWS IoT Core via API Gateway and Lambda.
- Fetch the latest AI health analysis (SageMaker + Bedrock).
- Dynamic risk probability: Visual percentage.
- Simple, clean, healthcare-themed responsive UI.

---

## 🛠️ Built With

- [React.js](https://react.dev/) (Vite setup)
- [Axios](https://axios-http.com/) for API integration
- [AWS API Gateway](https://aws.amazon.com/api-gateway/)
- [AWS Lambda](https://aws.amazon.com/lambda/)
- [AWS IoT Core](https://aws.amazon.com/iot-core/)
- [Amazon SageMaker](https://aws.amazon.com/sagemaker/)
- [Amazon Bedrock](https://aws.amazon.com/bedrock/)
- [Amazon Bedrock (Nova Sonic)](https://aws.amazon.com/bedrock/nova-sonic/)
---

## ⚡ Configuration

To try the app, follow the README steps to start Nova Sonic, then, the app will also open wiht Nova integrated.
Also, inside `App.jsx`, update the `API_BASE_URL` with your deployed **API Gateway** endpoint.
The steps are [here](https://github.com/JFoxUK/AWS-Hackathon-CareLink/blob/main/carelink-web/CareLink%20App%20Using%20AWS%20Example%20of%20Nova%20Sonic/speech-to-speech/workshops/README.md).
---

## 🚀 Deploy in 1-Click

### Vercel

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new)

> Tip: Set your environment variable `VITE_API_BASE_URL` during Vercel setup.

---

### AWS Amplify

[![Deploy to Amplify Console](https://oneclick.amplifyapp.com/button.svg)](https://console.aws.amazon.com/amplify/home#/deploy)

> Tip: When linking GitHub repo, set a build environment variable:  
> `VITE_API_BASE_URL = https://your-api-id.execute-api.region.amazonaws.com/prod`

---

## 📷 Quick Preview

> _Submit vitals → Get instant stability risk → AI generates health analysis_

![CareLink Web Screenshot](https://your-screenshot-link.png)

---

## 📜 License

Licensed under the [MIT License](https://opensource.org/licenses/MIT).

---

## ✍️ Authors

- [GitHub](https://github.com/JFoxUK)  
- [LinkedIn](https://linkedin.com/in/jfoxuk)  
- [Devpost](https://devpost.com/JFoxUK)

---

# 🚑 CareLink — Democratizing Remote Healthcare with AI + IoT

---
