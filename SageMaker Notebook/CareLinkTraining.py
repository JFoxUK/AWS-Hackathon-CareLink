# Install and import SageMaker SDK (if not already installed)
# !pip install sagemaker

import sagemaker
from sagemaker import image_uris
from sagemaker.inputs import TrainingInput
from sagemaker.estimator import Estimator
import boto3

# Set basic SageMaker session and role
sagemaker_session = sagemaker.Session()
role = sagemaker.get_execution_role()
region = boto3.Session().region_name

# Set S3 locations
input_s3_uri = "s3://carelink-ai-datasets/carelink_large_dataset.csv"  # your uploaded dataset
output_s3_uri = f"s3://{sagemaker_session.default_bucket()}/carelink-xgboost/output"

# Retrieve the XGBoost built-in image URI for your region
xgboost_image_uri = image_uris.retrieve(
    framework="xgboost",
    region=region,
    version="1.5-1"  # Good stable version, can also use 1.7-1 if preferred
)

# Define hyperparameters for training
hyperparameters = {
    "max_depth": "5",
    "eta": "0.2",
    "gamma": "4",
    "min_child_weight": "6",
    "subsample": "0.7",
    "verbosity": "1",
    "objective": "binary:logistic",  # Very important! Binary classification!
    "num_round": "100"
}

# Set up the training input
train_input = TrainingInput(
    input_s3_uri,
    content_type="text/csv"  # our dataset is CSV
)

# Define the estimator (training job configuration)
xgb_estimator = Estimator(
    image_uri=xgboost_image_uri,
    role=role,
    instance_count=1,
    instance_type="ml.m5.large",  # Good balance of speed and cost
    volume_size=5,  # GB
    max_run=3600,  # 1 hour max
    output_path=output_s3_uri,
    hyperparameters=hyperparameters
)

# Start the training job
xgb_estimator.fit({"train": train_input})

print("✅ Training job launched successfully!")


from sagemaker.model import Model
from sagemaker.predictor import Predictor

# Deploy the trained model to an endpoint
xgb_predictor = xgb_estimator.deploy(
    initial_instance_count=1,
    instance_type="ml.m5.large",  # Same size as training for simplicity
    endpoint_name="carelink-xgboost-endpoint"  # Friendly name
)

print("✅ Deployed SageMaker endpoint successfully!")
