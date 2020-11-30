#!/bin/bash

if [[ -z "$ENVIRONMENT" ]]; then
	ENVIRONMENT=DEV
fi

echo "Using Environment $ENVIRONMENT"

if [ -n "$AWS_PROFILE" ]; then
	AWS_ARGS="--profile $AWS_PROFILE "
fi

if [ -z "$AWS_REGION" ]; then
	AWS_REGION=$(aws configure get region)
fi


AWS_ARGS="$AWS_ARGS--region $AWS_REGION "


AWS_ACCOUNT_ID=$(aws sts get-caller-identity --output text --query 'Account' $AWS_ARGS)


S3_BUCKET=$(echo "$HYPHEN_PREFIX-$AWS_ACCOUNT_ID-$AWS_REGION-${ENVIRONMENT}" | tr '[:upper:]' '[:lower:]')

echo "Bucket name : $S3_BUCKET";

bucketstatus=$(aws s3api head-bucket --bucket "${S3_BUCKET}" $AWS_ARGS 2>&1)

if [ -z "$bucketstatus" ]
then
  echo "Bucket exists : $S3_BUCKET";
else
  echo "Bucket doesn't exist, creating";
  aws s3api create-bucket --bucket "$S3_BUCKET" --create-bucket-configuration LocationConstraint="$AWS_REGION" $AWS_ARGS;  
fi
aws s3 cp ../sagemaker/model.tar.gz s3://$S3_BUCKET/sagemaker_models/model.tar.gz $AWS_ARGS;

INGEST_PIPELINE_STACK_NAME=$HYPHEN_PREFIX-${ENVIRONMENT}

echo $ENVIRONMENT 
echo $S3_BUCKET 
echo $INGEST_PIPELINE_STACK_NAME

data_processing_pipeline_dir=$(pwd)

echo "Deploying ingest pipeline"
sam package \
	--template-file ./template.yaml \
	--s3-bucket $S3_BUCKET \
	--output-template-file ./packaged.yaml $AWS_ARGS
sam deploy \
	--template-file ./packaged.yaml \
	--stack-name $INGEST_PIPELINE_STACK_NAME \
	--capabilities CAPABILITY_IAM CAPABILITY_AUTO_EXPAND $AWS_ARGS
	

