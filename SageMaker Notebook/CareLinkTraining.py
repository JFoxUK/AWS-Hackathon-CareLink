# If needed:
# !pip install sagemaker

import sagemaker
from sagemaker import image_uris
from sagemaker.inputs import TrainingInput
from sagemaker.estimator import Estimator
import boto3
import time

# Setup SageMaker
sagemaker_session = sagemaker.Session()
role = sagemaker.get_execution_role()
region = boto3.Session().region_name

# S3 URIs
input_s3_uri = "s3://carelink-ai-datasets/carelink_weighted_training_set.csv"  # NEW dataset
output_s3_uri = f"s3://{sagemaker_session.default_bucket()}/carelink-xgboost/output"

# Get built-in XGBoost container image
xgboost_image_uri = image_uris.retrieve(
    framework="xgboost",
    region=region,
    version="1.5-1"
)

# Hyperparameters
hyperparameters = {
    "max_depth": "5",
    "eta": "0.2",
    "gamma": "4",
    "min_child_weight": "6",
    "subsample": "0.7",
    "verbosity": "1",
    "objective": "binary:logistic",
    "num_round": "100"
}

# Training input
train_input = TrainingInput(
    input_s3_uri,
    content_type="text/csv"
)

# Define Estimator
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

# Start training
print("🚀 Starting training...")
xgb_estimator.fit({"train": train_input})
print("✅ Training job completed!")

# Setup SageMaker client
sm_client = boto3.client('sagemaker')
endpoint_name = "carelink-xgboost-endpoint"

# Cleanly delete existing endpoint (if any)
try:
    print(f"ℹ️ Checking for existing endpoint: {endpoint_name}")
    sm_client.delete_endpoint(EndpointName=endpoint_name)
    print(f"✅ Deleted existing endpoint: {endpoint_name}")
except sm_client.exceptions.ClientError as e:
    if "Could not find" in str(e):
        print(f"✅ No existing endpoint found to delete.")
    else:
        raise e

# Important: Wait a few seconds after deleting the endpoint
time.sleep(5)

# Cleanly delete existing endpoint configuration (if any)
try:
    print(f"ℹ️ Checking for existing endpoint config: {endpoint_name}")
    sm_client.delete_endpoint_config(EndpointConfigName=endpoint_name)
    print(f"✅ Deleted existing endpoint config: {endpoint_name}")
except sm_client.exceptions.ClientError as e:
    if "Could not find" in str(e):
        print(f"✅ No existing endpoint config found to delete.")
    else:
        raise e

# Deploy the retrained model to the same endpoint name
print("🚀 Deploying new model...")
xgb_predictor = xgb_estimator.deploy(
    initial_instance_count=1,
    instance_type="ml.m5.large",
    endpoint_name=endpoint_name,  # reuse the same endpoint name
    wait=True  # wait until deployment is complete
)
print("✅ Successfully deployed retrained model to endpoint!")
