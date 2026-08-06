# NADTFE — Network Anomaly Detection and Threat Forecasting Engine

A machine learning system for detecting network intrusions and anomalous traffic, built on the NSL-KDD dataset. This project is an end-to-end exercise in applied ML engineering. From data preprocessing through a real-time inference API and (eventually) cloud deployment, this projec is built to bridge cybersecurity experience with practical machine learning skills.

## Project Goals
- Train a classifier to distinguish normal network traffic from attack traffic using the NSL-KDD dataset.
- Wrap the trained model in a real-time API that can score incoming traffic on the fly.
- Containerize and deploy the system so it's demonstrable, not just a local notebook.
- Document tradeoffs (metric choice, preprocessing decisions, model selection, etc.)

## Dataset
NSL-KDD is a refined version of the classic KDD Cup 1999 dataset, which is used as a benchmark for network intrusion detection. Each row is a network connection record described by 41 features (protocol type, service, byte counts, error rates, etc.) with a label identifying it as normal traffic or one of several attack categories.

**Known limitation:** NSL-KDD reflects network traffic patterns from 1999 and is heavily used in ML tutorials, so it alone doesn't demonstrate strong differentiation. This project treats it as a starting point for the pipeline, not the end goal. The deployment, explainability, and evaluation choices are where the differentiation comes from.

## Setup

```bash
git clone https://github.com/Khaled4262/Network-Anomaly-Detection-and-Threat-Forecasting-Engine.git
cd Network-Anomaly-Detection-and-Threat-Forecasting-Engine
pip install -r requirements.txt
```

Download `KDDTrain+.txt` and `KDDTest+.txt` from the [NSL-KDD dataset page](https://www.kaggle.com/datasets/hassan06/nslkdd?resource=download) and place them in a local `data/` directory 

```bash
python src/data_loader.py         # load + profile the raw dataset
python src/feature_engineering.py # encode categorical features
```

## Project Status

### Data Setup & Classical ML 

- [x] Repository structure, .gitignore, and Git/GitHub sync
- [x] NSL-KDD ingestion (data_loader.py) — loads raw text, applies official column names, profiles class distribution and missing values (0 missing values confirmed in both train/test)
- [x] Binary target preparation (prepare_targets) — collapses attack subtypes into a binary normal vs. attack label
- [x] Categorical feature encoding (feature_engineering.py) — one-hot encodes protocol_type, service, flag, fit on training data only, with handle_unknown="ignore" to safely handle unseen categories at test/inference time
- [ ] Numeric feature scaling — intentionally skipped for the RandomForest baseline, since tree-based splits are invariant to feature scale. Will revisit if a distance- or gradient-based model (e.g. logistic regression, SVM) is added for comparison.
- [ ] Train/test split wiring
- [ ] Baseline RandomForestClassifier training
- [ ] Evaluation (precision, recall, F1, confusion matrix, accuracy alone is misleading given class imbalance in NSL-KDD)
- [ ] Model persistence via joblib

### API & Real-Time Pipeline (to be started)
### Containerization & Deployment (to be started)

### Planned follow-ons
XGBoost/LightGBM comparison against the RandomForest baseline, multiclass (5-category) attack classification, SHAP-based explainability tied to attack signatures, and possibly benchmarking against a more current dataset (e.g. CICIDS2017).

## Tech Stack
Python, pandas, NumPy, scikit-learn, joblib, FastAPI, Docker, and AWS EC2.
