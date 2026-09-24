# LegalLens AI Deployment Guide

This guide describes how to deploy the LegalLens AI application to production using Vercel (for the Next.js frontend) and Google Cloud Run (for the FastAPI backend).

## Deployment Architecture

The production architecture is:
- **Frontend**: Deployed to Vercel (Next.js serverless and static assets)
- **Backend**: Deployed to Google Cloud Run (FastAPI) via source deployment (Google Cloud Buildpacks)
- **Communication**: Frontend securely communicates with backend over HTTPS.

## 1. Google Cloud Run (Backend Deployment)

The backend uses **Source Deployment** via Google Cloud Buildpacks. **No Dockerfile is required.**

### Prerequisites
1. Install the [Google Cloud CLI](https://cloud.google.com/sdk/docs/install).
2. Authenticate and select your project:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

### Deployment Steps
Navigate to the `services/api` directory and run the deployment command. Note that we inject environment variables to configure storage and frontend integration.

```bash
cd services/api

gcloud run deploy legallens-api ^
  --source . ^
  --region REGION ^
  --allow-unauthenticated ^
  --set-env-vars "APP_ENV=production,FRONTEND_URL=https://YOUR-VERCEL-DOMAIN.vercel.app,DOCUMENT_STORAGE_DIR=/tmp/documents,GEMINI_API_KEYS=YOUR_GEMINI_KEY"
```
*(For production, it is highly recommended to manage `GEMINI_API_KEYS` using [Google Cloud Secret Manager](https://cloud.google.com/run/docs/configuring/secrets) rather than passing it via command line).*

### Backend Validation
After deployment, Cloud Run will output a URL (e.g., `https://legallens-api-xxx.a.run.app`).
1. **Health Check**: Open `https://legallens-api-xxx.a.run.app/health` in your browser. You should see `{"status":"ok",...}`.
2. **API Docs**: Open `https://legallens-api-xxx.a.run.app/docs` to view the Swagger UI.

### ⚠️ Important Cloud Run Limitation: Storage
Cloud Run instances are stateless and their file systems are ephemeral.
Because `DOCUMENT_STORAGE_DIR` is set to `/tmp/documents`:
- Uploaded PDFs will be stored in the memory-backed `/tmp` directory.
- **This means uploads will NOT persist across instance restarts or scale-out events.**
- This setup is sufficient for a demo/single-session flow where processing happens immediately after upload. If persistent access across long periods or multiple nodes is required, a persistent storage solution (like Google Cloud Storage) must be integrated into `DocumentStore`.

---

## 2. Vercel (Frontend Deployment)

The frontend is deployed to Vercel and configured to connect to your Cloud Run instance.

### Deployment Steps
1. Navigate to your [Vercel Dashboard](https://vercel.com/dashboard) and click **Add New... > Project**.
2. Import your GitHub repository.
3. Configure the project:
   - **Framework Preset**: Next.js
   - **Root Directory**: `apps/web`
   - **Build Command**: `npm run build`
   - **Install Command**: `npm install`
4. Add the required Environment Variable:
   - **Name**: `BACKEND_API_URL`
   - **Value**: Your Cloud Run Service URL (e.g., `https://legallens-api-xxx.a.run.app`)
5. Click **Deploy**.

> **Note**: Variables prefixed with `NEXT_PUBLIC_` are exposed to the client browser. For `LegalLens AI`, `BACKEND_API_URL` is intentionally **NOT** prefixed with `NEXT_PUBLIC_`, ensuring all API interactions are handled securely on the Next.js server side. The Gemini API Keys must never be added to Vercel (they belong in Cloud Run).

### Frontend Validation
Once deployed, verify that the frontend functions properly by uploading a document and processing it.

## 3. Local Validation Before Deployment

Before pushing to production, verify your changes locally:

### Start Backend
```bash
cd services/api
python -m venv .venv
call .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- Open `http://127.0.0.1:8000/health` to confirm the server is running.
- Use `http://127.0.0.1:8000/docs` to test PDF upload endpoints.

### Start Frontend
```bash
cd apps/web
npm install
npm run build
npm run start
```
- Open `http://localhost:3000` to interact with the frontend.
