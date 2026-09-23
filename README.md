# NADTFE — Network Anomaly Detection and Threat Forecasting Engine

A production-ready machine learning system for detecting network intrusions and anomalous traffic patterns. Built with scikit-learn, FastAPI, React, Docker, and deployed on AWS EC2 with automated CI/CD pipelines.

## Features

- **Binary Classification**: Detects normal vs. attack traffic with precision and recall optimized for security use cases
- **Real-Time Scoring API**: FastAPI service with sub-100ms latency for streaming network logs
- **Interactive Dashboard**: React frontend for single-record classification and historical analysis
- **Production Deployment**: Containerized architecture with automated testing and deployment via GitHub Actions
- **Model Monitoring**: `/health` endpoint for liveness checks and model readiness verification

## Architecture

```
Backend (Python)          Frontend (React)           Infrastructure
├── src/ml/               ├── src/components/        ├── Dockerfile (backend)
│   ├── data_loader       │   ├── RecordForm         ├── src/frontend/Dockerfile
│   ├── feature_engineering   │   ├── ResultPanel    ├── docker-compose.yml
│   └── train_model       │   └── HistoryTable       ├── .github/workflows/
├── src/backend/          ├── src/fields.js          └── AWS EC2 deployment
│   ├── main (FastAPI)    └── src/api.js
│   ├── schemas           
│   └── simulate_stream   
└── models/
    ├── rf_baseline.joblib
    └── onehot_encoder.joblib
```

## Quickstart

### Prerequisites
- Python 3.8+
- Node.js 18+
- Docker (for containerized deployment)
- AWS CLI (for EC2 deployment)

### Local Setup

```bash
git clone https://github.com/Khaled4262/Network-Anomaly-Detection-and-Threat-Forecasting-Engine.git
cd Network-Anomaly-Detection-and-Threat-Forecasting-Engine
pip install -r requirements.txt
```

Download `KDDTrain+.txt` and `KDDTest+.txt` from [NSL-KDD on Kaggle](https://www.kaggle.com/datasets/hassan06/nslkdd?resource=download) and place in `data/`.

### Train Model

```bash
python -m src.ml.data_loader
python -m src.ml.feature_engineering
python -m src.ml.train
```

### Run API

```bash
python -m uvicorn src.backend.main:app --reload
```

API available at `http://127.0.0.1:8000`. OpenAPI docs at `/docs`.

### Run Frontend

```bash
cd src/frontend
npm install
npm run dev
```

### Stream Test Records

```bash
python -m src.backend.simulate_stream --n 50 --delay 0.5
```

## Deployment

### Docker

```bash
docker-compose up
```

Frontend: `http://localhost:80`
API: `http://localhost:8000`

### AWS EC2

Build and push images:

```bash
docker build -f src/frontend/Dockerfile -t nadtfe-frontend .
docker build -t nadtfe-backend .
```

Push to ECR, then deploy on t2.micro instance with auto-scaling group and security group configuration (ports 80, 8000).

### CI/CD Pipeline

GitHub Actions automatically:
- Runs tests on push/PR
- Builds Docker images
- Pushes to ECR
- Deploys to EC2 on main branch merge

See `.github/workflows/` for pipeline configuration.

## Model

**Algorithm**: RandomForestClassifier 

**Performance**: Evaluated on NSL-KDD test set with precision, recall, F1, and confusion matrix.

**Encoding**: One-hot encoding for categorical features (protocol_type, service, flag) with `handle_unknown="ignore"` for unseen values at inference.

## Dataset

**NSL-KDD**: Refined version of KDD Cup 1999 dataset. 125,973 training records, 22,544 test records. Labels: normal or attack type (DoS, Probe, R2L, U2R).


## Tech Stack

| Layer | Technology |
|-------|------------|
| ML | Python 3, scikit-learn, pandas, NumPy, joblib |
| Backend | FastAPI, uvicorn, Pydantic |
| Frontend | React 19, Vite, fetch API |
| DevOps | Docker, Docker Compose, GitHub Actions |
| Cloud | AWS EC2, ECR, security groups |

## Development

Install dev dependencies:

```bash
pip install pytest black flake8
```

Run tests:

```bash
pytest
```

Format and lint:

```bash
black src/
flake8 src/
```



## License

MIT