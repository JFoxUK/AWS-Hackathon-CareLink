# If needed:
# !pip install sagemaker

import sagemaker
from sagemaker import image_uris
from sagemaker.inputs import TrainingInput
from sagemaker.estimator import Estimator
import boto3
import time

# --- Setup SageMaker Session ---
sagemaker_session = sagemaker.Session()
role = sagemaker.get_execution_role()
region = boto3.Session().region_name

# --- Corrected S3 paths ---
input_s3_uri = "s3://carelink-ai-datasets/patient_vitals_24h_memory_fixed.csv"  # <--- UPDATED FILE
output_s3_uri = f"s3://{sagemaker_session.default_bucket()}/carelink-xgboost/output"

# --- Get the correct XGBoost container for the region ---
xgboost_image_uri = image_uris.retrieve(
    framework="xgboost",
    region=region,
    version="1.5-1"
)

# --- Updated hyperparameters for time-sequence learning ---
hyperparameters = {
    "max_depth": "8",               # Deeper to learn more complex temporal patterns
    "eta": "0.05",                  # Slower learning to capture subtle trends
    "gamma": "1",                   # Mild regularization
    "min_child_weight": "6",         # Avoid tiny random splits
    "subsample": "0.8",              # Regularization
    "colsample_bytree": "0.8",       # Feature selection
    "verbosity": "1",
    "objective": "binary:logistic",  # Predict if unstable
    "scale_pos_weight": "2",         # Balance slightly
    "num_round": "800",              # More rounds for slow eta
    "grow_policy": "depthwise",
    "eval_metric": "logloss",
    "lambda": "1",
    "alpha": "0.5"
}

# --- Define Training Input from S3 ---
train_input = TrainingInput(
    input_s3_uri,
    content_type="text/csv",
    s3_data_type="S3Prefix"
)

# --- Define the XGBoost Estimator ---
xgb_estimator = Estimator(
    image_uri=xgboost_image_uri,
    role=role,
    instance_count=1,
    instance_type="ml.m5.large",
    volume_size=5,
    max_run=3600,
    output_path=output_s3_uri,
    hyperparameters=hyperparameters
)

# --- Start Training Job ---
print("\ud83d\ude80 Starting properly weighted and regularized training...")
xgb_estimator.fit({"train": train_input})
print("\u2705 Training completed successfully!")

# --- Safe Deployment Section ---
sm_client = boto3.client('sagemaker')
endpoint_name = "carelink-xgboost-endpoint"
model_name = xgb_estimator.latest_training_job.name

# --- Delete existing endpoint if it exists ---
existing_endpoints = sm_client.list_endpoints(NameContains=endpoint_name, MaxResults=1)['Endpoints']
if existing_endpoints:
    print(f"\u2139\ufe0f Deleting existing endpoint: {endpoint_name}")
    sm_client.delete_endpoint(EndpointName=endpoint_name)
    print("\u231b Waiting 180 seconds for endpoint to fully delete...")
    time.sleep(180)

# --- Delete existing endpoint config if it exists ---
existing_configs = sm_client.list_endpoint_configs(NameContains=endpoint_name, MaxResults=1)['EndpointConfigs']
if existing_configs:
    print(f"\u2139\ufe0f Deleting existing endpoint config: {endpoint_name}")
    sm_client.delete_endpoint_config(EndpointConfigName=endpoint_name)

# --- Delete previous model if it exists ---
existing_models = sm_client.list_models(NameContains=model_name, MaxResults=1)['Models']
if existing_models:
    print(f"\u2139\ufe0f Deleting existing model: {model_name}")
    sm_client.delete_model(ModelName=model_name)

# --- Deploy retrained model to SageMaker Endpoint ---
print("\ud83d\ude80 Deploying updated model to SageMaker endpoint...")
xgb_estimator.deploy(
    initial_instance_count=1,
    instance_type="ml.m5.large",
    endpoint_name=endpoint_name,
    wait=True
)
print("\u2705 Deployed properly weighted and regularized model to endpoint!")
