import os
import boto3
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def load_embeddings_from_s3():
    # Load AWS credentials from environment variables
    aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    
    s3 = boto3.client('s3', 
                      aws_access_key_id=aws_access_key_id,
                      aws_secret_access_key=aws_secret_access_key)
    bucket_name = 'mentaai-embeddings'
    key = 'transcript_embeddings.json'

    # Download the file directly to memory
    response = s3.get_object(Bucket=bucket_name, Key=key)
    embeddings_data = json.loads(response['Body'].read().decode('utf-8'))

    return embeddings_data