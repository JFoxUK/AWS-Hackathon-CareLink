# If needed:
# !pip install sagemaker

import sagemaker
from sagemaker import image_uris
from sagemaker.inputs import TrainingInput
from sagemaker.estimator import Estimator
import boto3

# Setup SageMaker
sagemaker_session = sagemaker.Session()
role = sagemaker.get_execution_role()
region = boto3.Session().region_name

# S3 URIs
input_s3_uri = "s3://carelink-ai-datasets/carelink_weighted_normalized_training_set_large.csv"
output_s3_uri = f"s3://{sagemaker_session.default_bucket()}/carelink-xgboost/output"

# Get XGBoost built-in container
xgboost_image_uri = image_uris.retrieve(
    framework="xgboost",
    region=region,
    version="1.5-1"
)

# Define hyperparameters
hyperparameters = {
    "max_depth": "5",
    "eta": "0.2",
    "gamma": "4",
    "min_child_weight": "6",
    "subsample": "0.7",
    "verbosity": "1",
    "objective": "binary:logistic",
    "num_round": "100",
}

# Define Training Input
train_input = TrainingInput(
    input_s3_uri,
    content_type="text/csv"
)

# Define the Estimator
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

# Start Training Job
print("🚀 Starting properly weighted training...")
xgb_estimator.fit({"train": train_input})

print("✅ Proper weighted training completed!")

# Safe Deployment Section
sm_client = boto3.client('sagemaker')
endpoint_name = "carelink-xgboost-endpoint"

# Check if endpoint exists and delete it
existing_endpoints = sm_client.list_endpoints(NameContains=endpoint_name, MaxResults=1)['Endpoints']
if existing_endpoints:
    print(f"ℹ️ Deleting existing endpoint: {endpoint_name}")
    sm_client.delete_endpoint(EndpointName=endpoint_name)

# Deploy retrained model to same endpoint
print("🚀 Deploying retrained model to SageMaker endpoint...")
xgb_estimator.deploy(
    initial_instance_count=1,
    instance_type="ml.m5.large",
    endpoint_name=endpoint_name,
    wait=True
)

print("✅ Deployed properly weighted model to endpoint!")
