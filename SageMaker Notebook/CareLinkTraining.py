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
input_s3_uri = "s3://carelink-ai-datasets/carelink_final_training_set_fixed_10k.csv"
output_s3_uri = f"s3://{sagemaker_session.default_bucket()}/carelink-xgboost/output"

# --- Get the correct XGBoost container for the region ---
xgboost_image_uri = image_uris.retrieve(
    framework="xgboost",
    region=region,
    version="1.5-1"
)

# --- Updated hyperparameters for smoother and more reliable model ---
hyperparameters = {
    "max_depth": "4",               # 🌟 Shallower trees for softer decision boundaries
    "eta": "0.2",                   # 🌟 Slightly faster learning rate; good for convergence
    "gamma": "5",                   # 🌟 High gamma = aggressive pruning of weak splits
    "min_child_weight": "8",         # 🌟 Prevent overfitting by requiring more examples to split
    "subsample": "0.7",              # 🌟 Randomly sample rows to prevent overfitting
    "verbosity": "1",                # 🌟 Show training logs
    "objective": "binary:logistic",  # 🌟 Standard binary classification
    "scale_pos_weight": "5",         # 🌟 Handle class imbalance
    "num_round": "300",              # 🌟 More boosting rounds
    "grow_policy": "depthwise",      # 🌟 Balanced tree depth
    "eval_metric": "logloss",        # 🌟 Optimize probability estimates
    "lambda": "2"                    # 🌟 L2 regularization for better generalization
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
print("🚀 Starting properly weighted and regularized training...")
xgb_estimator.fit({"train": train_input})
print("✅ Training completed successfully!")

# --- Safe Deployment Section ---
sm_client = boto3.client('sagemaker')
endpoint_name = "carelink-xgboost-endpoint"
model_name = xgb_estimator.latest_training_job.name  # Auto-capture latest model name

# --- Delete existing endpoint if it exists ---
existing_endpoints = sm_client.list_endpoints(NameContains=endpoint_name, MaxResults=1)['Endpoints']
if existing_endpoints:
    print(f"ℹ️ Deleting existing endpoint: {endpoint_name}")
    sm_client.delete_endpoint(EndpointName=endpoint_name)
    print("⌛ Waiting 180 seconds for endpoint to fully delete...")
    time.sleep(180)  # ✨ Wait for full deletion to avoid create conflicts

# --- Delete existing endpoint config if it exists ---
existing_configs = sm_client.list_endpoint_configs(NameContains=endpoint_name, MaxResults=1)['EndpointConfigs']
if existing_configs:
    print(f"ℹ️ Deleting existing endpoint config: {endpoint_name}")
    sm_client.delete_endpoint_config(EndpointConfigName=endpoint_name)

# --- Delete previous model if it exists ---
existing_models = sm_client.list_models(NameContains=model_name, MaxResults=1)['Models']
if existing_models:
    print(f"ℹ️ Deleting existing model: {model_name}")
    sm_client.delete_model(ModelName=model_name)

# --- Deploy retrained model to SageMaker Endpoint ---
print("🚀 Deploying updated model to SageMaker endpoint...")
xgb_estimator.deploy(
    initial_instance_count=1,
    instance_type="ml.m5.large",
    endpoint_name=endpoint_name,
    wait=True
)
print("✅ Deployed properly weighted and regularized model to endpoint!")
