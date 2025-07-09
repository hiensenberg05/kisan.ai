# project.ai

A full-stack AI-powered application with a RAG (Retrieval-Augmented Generation) engine, Google Cloud integration, and a modern frontend.

---

## Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Google Cloud Setup](#google-cloud-setup)
- [Environment Variables](#environment-variables)
- [Backend Setup](#backend-setup)
- [Frontend Setup](#frontend-setup)
- [Running the App](#running-the-app)
- [Notes](#notes)

---

## Features
- RAG (Retrieval-Augmented Generation) engine integration
- Google Cloud Storage for data
- Modern React frontend
- Audio, vision, and text tools

---

## Prerequisites
- Python 3.8+
- Node.js 16+
- Google Cloud account
- Google Cloud SDK (gcloud CLI)

---

## Google Cloud Setup

1. **Create a Google Cloud Storage Bucket:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/storage/browser)
   - Create a new bucket (note the name, e.g., `your-bucket-name`)

2. **Upload Data Folder:**
   - Upload your data (documents, images, etc.) to the bucket.

3. **Create a Service Account & Download Credentials:**
   - Go to IAM & Admin > Service Accounts
   - Create a new service account with Storage Object Admin role
   - Download the JSON key file and place it in the project root (e.g., `projectkisan-465305-386ada2795ef.json`)

4. **Enable Required APIs:**
   - Cloud Storage API
   - Any other APIs required by your RAG engine

---

## Google CLI Setup

1. **Install Google Cloud SDK:**
   - [Download and install instructions](https://cloud.google.com/sdk/docs/install)

2. **Initialize gcloud:**
   ```sh
   gcloud init
   gcloud auth activate-service-account --key-file=projectkisan-465305-386ada2795ef.json
   gcloud config set project your-gcp-project-id
   ```

---

## Environment Variables

1. Copy `env_example.txt` to `.env` and fill in the values:
   ```sh
   cp env_example.txt .env
   # Edit .env and set your values
   ```
2. Make sure `.env` is in your `.gitignore`.

---

## Backend Setup

1. **Create and activate a virtual environment:**
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
3. **Run the backend:**
   ```sh
   python backend/main.py
   ```

---

## Frontend Setup

1. **Install dependencies:**
   ```sh
   cd frontend
   npm install
   ```
2. **Run the frontend:**
   ```sh
   npm run dev
   ```

---

## Running the App

- Backend runs on [http://localhost:8000](http://localhost:8000)
- Frontend runs on [http://localhost:5173](http://localhost:5173) (default Vite port)

---

## Notes
- Do **NOT** commit your `.env` or credential files.
- Make sure to update your environment variables as needed.
- For RAG engine setup, refer to your specific engine's documentation for API keys and endpoints.
- For any issues, check the logs or open an issue. 