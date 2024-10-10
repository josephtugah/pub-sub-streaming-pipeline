# Run with python streaming-beam-dataflow.py 
import apache_beam as beam  # type: ignore
from apache_beam.io.gcp.pubsub import ReadFromPubSub  # type: ignore
from apache_beam.io.gcp.bigquery import WriteToBigQuery  # type: ignore
import json
from apache_beam.options.pipeline_options import PipelineOptions  # type: ignore

# Define your Dataflow pipeline options
options = PipelineOptions(
    runner='DataflowRunner',  # for Dataflow job change to runner='DataflowRunner'
    project='YOUR_PROJECT_ID',  # Replace with your Google Cloud project ID
    region='YOUR_REGION',  # e.g., 'us-west1'
    temp_location='gs://YOUR_BUCKET_NAME/temp',  # Replace with your GCS bucket name
    staging_location='gs://YOUR_BUCKET_NAME/staging',  # Replace with your GCS bucket name
    streaming=True,  # Enable streaming mode
    service_account_email='YOUR_SERVICE_ACCOUNT_EMAIL',  # Replace with your service account email
    # Dataflow parameters that are optional
    job_name='YOUR_JOB_NAME',  # Set the Dataflow job name here
    # num_workers=3,  # Specify the number of workers
    max_num_workers=20,  # Specify the maximum number of workers
    # disk_size_gb=100,  # Specify the disk size in GB per worker
    autoscaling_algorithm='THROUGHPUT_BASED',  # Specify the autoscaling algorithm
    # machine_type='n1-standard-4',  # Specify the machine type for the workers
)

# Define your Beam pipeline
with beam.Pipeline(options=options) as pipeline:
    # Read the input data from Pub/Sub
    messages = pipeline | ReadFromPubSub(subscription='projects/YOUR_PROJECT_ID/subscriptions/YOUR_SUBSCRIPTION_NAME')

    # Parse the JSON messages
    parsed_messages = messages | beam.Map(lambda msg: json.loads(msg))

    # Extract the desired fields for 'conversations' table
    conversations_data = parsed_messages | beam.Map(lambda data: {
        'senderAppType': data.get('senderAppType', 'N/A'),
        'courierId': data.get('courierId', None),
        'fromId': data.get('fromId', None),
        'toId': data.get('toId', None),
        'chatStartedByMessage': data.get('chatStartedByMessage', False),
        'orderId': data.get('orderId', None),
        'orderStage': data.get('orderStage', 'N/A'),
        'customerId': data.get('customerId', None),
        'messageSentTime': data.get('messageSentTime', None),
    }) | beam.Filter(lambda data: data['orderId'] is not None and data['customerId'] is not None)

    # Extract the desired fields for 'orders' table
    orders_data = parsed_messages | beam.Map(lambda data: {
        'cityCode': data.get('cityCode', 'N/A'),
        'orderId': data.get('orderId', None),
    }) | beam.Filter(lambda data: data['orderId'] is not None and data['cityCode'] != 'N/A')

    # Define the schema for the 'conversations' table
    conversations_schema = {
        'fields': [
            {'name': 'senderAppType', 'type': 'STRING'},
            {'name': 'courierId', 'type': 'INTEGER'},
            {'name': 'fromId', 'type': 'INTEGER'},
            {'name': 'toId', 'type': 'INTEGER'},
            {'name': 'chatStartedByMessage', 'type': 'BOOLEAN'},
            {'name': 'orderId', 'type': 'INTEGER'},
            {'name': 'orderStage', 'type': 'STRING'},
            {'name': 'customerId', 'type': 'INTEGER'},
            {'name': 'messageSentTime', 'type': 'TIMESTAMP'}
        ]
    }

    # Define the schema for the 'orders' table
    orders_schema = {
        'fields': [
            {'name': 'cityCode', 'type': 'STRING'},
            {'name': 'orderId', 'type': 'INTEGER'}
        ]
    }

    # Write the conversations data to the 'conversations' table in BigQuery
    conversations_data | 'Write conversations to BigQuery' >> WriteToBigQuery(
        table='YOUR_PROJECT_ID:YOUR_DATASET_NAME.conversations',  # Replace with your BigQuery table name
        schema=conversations_schema,
        create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
        write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND
    )

    # Write the orders data to the 'orders' table in BigQuery
    orders_data | 'Write orders to BigQuery' >> WriteToBigQuery(
        table='YOUR_PROJECT_ID:YOUR_DATASET_NAME.orders',  # Replace with your BigQuery table name
        schema=orders_schema,
        create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
        write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND
    )
