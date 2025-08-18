# 🌾 KrishiMitra.AI

**KrishiMitra.AI** is an **Agentic AI-powered Digital Agronomist & Market Advisor** designed to empower farmers with real-time, personalized, and multilingual support. Built with a **custom RAG engine**, **Google Cloud integration**, and a **modern React frontend**, it delivers actionable insights on crop health, markets, and government schemes—all accessible through natural voice or text in local languages.  

---

## 📑 Table of Contents

- [✨ Features](#-features)  
- [⚙️ Prerequisites](#-prerequisites)  
- [☁️ Google Cloud Setup](#-google-cloud-setup)  
- [🔐 Environment Variables](#-environment-variables)  
- [🧠 Backend Setup](#-backend-setup)  
- [🖼️ Frontend Setup](#-frontend-setup)  
- [🚀 Running the App](#-running-the-app)  
- [📝 Notes](#-notes)  

---

## ✨ Features

- 🌱 **Digital Agronomist & Market Advisor** – Combines roles of agronomist, market analyst, and government scheme navigator.  
- 📸 **Instant Crop Disease Diagnosis** – Upload diseased crop images, get AI diagnosis with cost-effective remedies and subsidy checks.  
- 📊 **Real-Time Market Insights** – Location-aware crop prices, trend analysis, and selling recommendations.  
- 🏛️ **Government Scheme Guidance** – Simple explanations of subsidies and schemes in local languages with direct application links.  
- 🎙️ **Voice-First, Regional Language Interaction** – Farmers can speak in their dialect; AI responds naturally, removing literacy barriers.  
- 🌾 **Crop Growth Monitoring** – Upload periodic images for visual growth tracking, predictive yield risks, and progress alerts.  
- ☀️ **Weather-Linked Alerts** – Early warnings for climatic events and irrigation reminders via weather data.  
- 💰 **Asset Management Tracker** – Calculates investments and expected returns for each crop stage based on land size.  
- ✅ **Transparency & Trust** – Each recommendation includes sources and confidence scores.  
- 📱 **Farmer-Centric Design** – Lightweight, mobile-first interface optimized for low-end devices and low-digital-literacy users.  

---

## ⚙️ Prerequisites

- [Python 3.8+](https://www.python.org/downloads/)  
- [Node.js 16+](https://nodejs.org/)  
- [Google Cloud SDK (gcloud CLI)](https://cloud.google.com/sdk/docs/install)  
- Google Cloud Account with billing enabled  

---

## ☁️ Google Cloud Setup

### 1. Create a Cloud Storage Bucket  
- Go to [Google Cloud Console](https://console.cloud.google.com/storage/browser)  
- Create a new bucket (e.g., `your-bucket-name`)  
- Upload your data folder (documents, images, etc.)  

### 2. Create a Service Account  
- Navigate to **IAM & Admin > Service Accounts**  
- Click **Create Service Account**  
- Assign role: `Storage Object Admin`  
- Generate a **JSON key file** and save it in the project root (e.g., `projectkisan-465305-386ada2795ef.json`)  

### 3. Enable Required Google Cloud APIs  
- Cloud Storage API  
- Speech-to-Text API  
- Text-to-Speech API  
- Cloud Vision API (optional for image tools)  

### 4. Set `GOOGLE_APPLICATION_CREDENTIALS`  
Add to `.env`:  
```env
GOOGLE_APPLICATION_CREDENTIALS=projectkisan-465305-386ada2795ef.json
# 1. Navigate to backend
cd backend

# 2. Create virtual environment
python -m venv venv

# 3. Activate environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run backend server
uvicorn main:app --reload

# 1. Navigate to frontend
cd frontend

# 2. Install dependencies
npm install

# 3. Start development server
npm run dev
