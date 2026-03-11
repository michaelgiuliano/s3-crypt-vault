import boto3

def test_s3_connection_localstack():
    """
    Test if the application can connect to LocalStack S3 and create a bucket.
    """
    
    s3 = boto3.client(
        's3', 
        endpoint_url="http://localhost:4566", 
        region_name="us-east-1",
        aws_access_key_id="test",
        aws_secret_access_key="test"
    )

    bucket_name = "test-vault"

    s3.create_bucket(Bucket=bucket_name)
    response = s3.list_buckets()
    buckets = [b['Name'] for b in response['Buckets']]

    assert bucket_name in buckets
    print(f"\nSuccessfully verified bucket: {bucket_name}")