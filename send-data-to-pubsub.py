from google.cloud import pubsub_v1
from google.cloud import storage
import time

# Create a publisher client
publisher = pubsub_v1.PublisherClient()

# Specify the topic path
topic_path = 'projects/YOUR_PROJECT_ID/topics/YOUR_TOPIC_NAME'  # Replace with your project ID and topic name

# Check if the topic exists
try:
    topic = publisher.get_topic(request={"topic": topic_path})
except Exception as e:
    print(f'Topic does not exist or cannot be accessed: {e}')
    exit()

# Create a storage client
storage_client = storage.Client()

# Specify the bucket and file names
bucket_name = 'YOUR_BUCKET_NAME'  # Replace with your bucket name
file_name = 'YOUR_FILE_NAME.json'  # Replace with your file name

# Get the bucket and blob
bucket = storage_client.bucket(bucket_name)
blob = bucket.blob(file_name)

# Read the file line by line
try:
    with blob.open("r") as f_in:
        for line in f_in:
            # Data must be a bytestring
            data = line.encode('utf-8')
            # Publish the data to the topic
            future = publisher.publish(topic=topic.name, data=data)
            print(f'Message published with ID: {future.result()}')
            # Sleep for 1 second before publishing the next message
            time.sleep(1)
except Exception as e:
    print(f'Error reading file or publishing messages: {e}')
