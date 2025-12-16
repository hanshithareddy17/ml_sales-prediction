# ML Sales Forecast Web App

End-to-end sales forecasting app with a Flask backend (LSTM model + PostgreSQL) and a React frontend.

## Project Structure

- backend/ – Flask API, DB access, and forecasting endpoint
- frontend/ – React dashboard (Create React App)
- models/ – Trained LSTM model artifacts (SavedModel, scaler, metadata)
- ml_training/ – Standalone training and ML utilities

## Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL (local or AWS RDS)

## Environment Configuration

Copy the sample and fill in your values:

```bash
cp .env.example .env
```

Set the PostgreSQL connection details (for local or RDS) and adjust `REACT_APP_API_URL` when building the frontend for deployment.

## Local Backend Setup

From the project root:

```bash
python -m venv .venv
# Windows PowerShell
.venv\\Scripts\\Activate.ps1
pip install -r backend/requirements.txt
python backend/app.py
```

Backend will run on http://127.0.0.1:5000.

## Local Frontend Setup

```bash
cd frontend
npm install
npm start
```

Open http://localhost:3000 to use the dashboard.

## AWS Deployment (High Level)

### 1. Database (AWS RDS PostgreSQL)

- Create a PostgreSQL RDS instance.
- Open port 5432 to your app (security group).
- Put the RDS endpoint, DB name, user, and password into `.env` on the backend host.

### 2. Backend on EC2 (or similar)

On your EC2 instance:

```bash
git clone <your-repo-url>.git
cd ml_sales-prediction
python -m venv .venv
source .venv/bin/activate  # or .venv\\Scripts\\activate on Windows
pip install -r backend/requirements.txt
cp .env.example .env  # then edit with RDS details
python backend/app.py  # or run via gunicorn/uwsgi behind Nginx
```

Expose port 5000 via a security group or put Nginx/ALB in front of it.

### 3. Frontend on S3/CloudFront (or EC2)

Build the production bundle with the correct API URL:

```bash
cd frontend
REACT_APP_API_URL="https://your-backend-domain" npm run build
```

Then deploy the `frontend/build` directory to:

- An S3 bucket + CloudFront distribution, or
- A web server (e.g. Nginx) on EC2.

Once this is done, the same codebase you commit to GitHub can be used both locally and on AWS by just changing environment variables.
