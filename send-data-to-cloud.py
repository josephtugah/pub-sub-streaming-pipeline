from google.cloud import storage

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    # Upload the file
    blob.upload_from_filename(source_file_name)

    print(f"File {source_file_name} uploaded to {destination_blob_name}.")

# Specify the parameters
bucket_name = 'YOUR_BUCKET_NAME'  # Replace with your bucket name
source_file_name = 'YOUR_LOCAL_FILE_PATH'  # Path to your local file
destination_blob_name = 'YOUR_DESIRED_BLOB_NAME'  # Desired name in the bucket

# Call the upload function
upload_blob(bucket_name, source_file_name, destination_blob_name)
