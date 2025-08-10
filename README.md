# 🌾 kisan.ai

A full-stack AI-powered application featuring a custom Retrieval-Augmented Generation (RAG) engine, Google Cloud integration, and a modern React frontend.

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

- 🔎 Custom RAG (Retrieval-Augmented Generation) engine
- ☁️ Google Cloud Storage integration for document/image handling
- 🧠 Multimodal AI: Audio, vision, and text tools
- ⚛️ Modern React frontend (Vite)
- 🎙️ Google Speech-to-Text & Text-to-Speech APIs

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
- Assign the role: `Storage Object Admin`
- After creating, click **Add Key > Create new key > JSON**
- Save the JSON key file in the root of your project directory, e.g.,  
  `projectkisan-465305-386ada2795ef.json`

### 3. Enable Required Google Cloud APIs

- **Cloud Storage API**
- **Speech-to-Text API**
- **Text-to-Speech API**
- **Cloud Vision API** (optional, for image-based tools)

### 4. Set `GOOGLE_APPLICATION_CREDENTIALS`

Set the environment variable to point to your credentials file:

#### On Mac/Linux:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="projectkisan-465305-386ada2795ef.json"
```

#### On Windows (CMD):

```cmd
set GOOGLE_APPLICATION_CREDENTIALS=projectkisan-465305-386ada2795ef.json
```

#### On Windows (PowerShell):

```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS="projectkisan-465305-386ada2795ef.json"
```

Or add it to your `.env` file as:
```env
GOOGLE_APPLICATION_CREDENTIALS=projectkisan-465305-386ada2795ef.json
```

---

## 🔐 Environment Variables

### 1. Create a `.env` File

Copy the example file and edit it:

```bash
cp env_example.txt .env
```

Edit `.env` with your values for:
- `GOOGLE_APPLICATION_CREDENTIALS`
- Bucket name
- Any API keys or service endpoints required by your RAG engine

### 2. Ignore Sensitive Files

Ensure the following are in your `.gitignore`:

```
.env
*.json
```

---

## 🧠 Backend Setup

### 1. Create a Virtual Environment

```bash
python -m venv venv
```

### 2. Activate It

- **Mac/Linux**:
  ```bash
  source venv/bin/activate
  ```
- **Windows**:
  ```cmd
  venv\Scripts\activate
  ```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Backend

```bash
python backend/main.py
```

---

## 🖼️ Frontend Setup

### 1. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 2. Run the Frontend

```bash
npm run dev
```

---

## 🚀 Running the App

- **Backend**: [http://localhost:8000](http://localhost:8000)
- **Frontend**: [http://localhost:5173](http://localhost:5173)

---

## 📝 Notes

- Do **NOT** commit your `.env` or credential `.json` files.
- Make sure `GOOGLE_APPLICATION_CREDENTIALS` is correctly set for all environments.
- Refer to your RAG engine’s documentation for additional configs and endpoints.
- Use `gcloud auth list` and `gcloud config list` to verify current auth status.
- For debugging, use verbose logs or open an issue.

---

Built with 💡 by Team project.ai
