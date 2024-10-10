# GCP Data Engineering Project: Streaming Data Pipeline with Pub/Sub and Apache Beam/Dataflow

Pub/Sub is a publish/subscribe (Pub/Sub) service, a messaging service where the senders of messages are decoupled from the receivers of messages. It is a fully managed messaging service designed to support real-time messaging between applications. It enables reliable, asynchronous communication by decoupling senders and receivers, making it ideal for building event-driven systems.

Dataflow is a Google Cloud service that provides unified stream and batch data processing at scale. Use Dataflow to create data pipelines that read from one or more sources, transform the data, and write the data to a destination. Dataflow is built on the open source Apache Beam project. Apache Beam lets you write pipelines using a language-specific SDK. Apache Beam supports Java, Python, and Go SDKs, as well as multi-language pipelines. Dataflow executes Apache Beam pipelines. If you decide later to run your pipeline on a different platform, such as Apache Flink or Apache Spark, you can do so without rewriting the pipeline code. The following is a challenging task I came across and the corresponding solution I developed

# <u>DataPipeline Challenge</u>
We have a "conversations.json" file containing the "customer_courier_chat_messages" event data, which includes information about individual messages exchanged between customers and couriers through the in-app chat. A sample of the event data is provided.

```json
{
  "senderAppType": "Courier Android",
  "courierId": 15814271,
  "fromId": 15814271,
  "toId": 52048502,
  "chatStartedByMessage": true,
  "orderId": 98014164,
  "orderStage": "ON_ROUTE",
  "customerId": 52048502,
  "messageSentTime": "2024-02-01T10:00:32Z"
},
{
...
}
```
Additionally, you have access to the "orders" event, which contains the "orderId" and "cityCode" fields.
```json
{
  "orderId":24497171,
  "cityCode":"AMS"},
{
...
}
```
We will simulate the streaming of conversations between Couriers and Customers using our prepared data, which consists of a total of 400 conversations. Each conversation begins with a message from either the Courier or the Customer. This initial message is followed by a crucial message containing the "orderId" and "cityCode." Subsequent messages will then follow in chronological order, with each conversation consisting of 2 to 5 messages. If you're interested in the original data generation process, you can find the code in my GitHub repository. Here’s an example of a complete conversation:

```json
{"orderId":74816237,"messageSentTime":"2024-02-01T10:00:29Z","chatStartedByMessage":true,"senderAppType":"Courier Android","courierId":35808291,"fromId":35808291,"toId":19929216,"orderStage":"ACCEPTED","customerId":19929216}
{"orderId":74816237,"messageSentTime":"2024-02-01T10:01:29Z","chatStartedByMessage":false,"senderAppType":"Customer iOS","customerId":19929216,"fromId":19929216,"toId":35808291,"orderStage":"AWAITING_PICKUP","courierId":35808291}
{"orderId":74816237,"messageSentTime":"2024-02-01T10:01:51Z","chatStartedByMessage":false,"senderAppType":"Courier Android","courierId":35808291,"fromId":35808291,"toId":19929216,"orderStage":"ACCEPTED","customerId":19929216}
{"orderId":74816237,"messageSentTime":"2024-02-01T10:02:10Z","chatStartedByMessage":false,"senderAppType":"Customer iOS","customerId":19929216,"fromId":19929216,"toId":35808291,"orderStage":"IN_PROGRESS","courierId":35808291}
{"orderId":74816237,"cityCode":"SYD"}
```

The task is to build a data pipeline that aggregates individual messages into distinct conversations, ensuring each conversation is unique per order. The data should be divided into two tables: "conversations" and "orders". This separation will streamline future analysis and data processing. The final table, "customer_courier_conversations," must include the following required fields:

&#8226; order_id  
&#8226; city_code  
&#8226; first_courier_message: Timestamp of the first courier message  
&#8226; first_customer_message: Timestamp of the first customer message  
&#8226; num_messages_courier: Number of messages sent by courier  
&#8226; num_messages_customer: Number of messages sent by customer  
&#8226; first_message_by: The first message sender (courier or customer)  
&#8226; conversation_started_at: Timestamp of the first message in the conversation  
&#8226; first_responsetime_delay_seconds: Time (in secs) elapsed until the first message was responded  
&#8226; last_message_time: Timestamp of the last message sent  
&#8226; last_message_order_stage: The stage of the order when the last message was sent

In this project, I will present my solution and provide a comprehensive, step-by-step guide on how to achieve the task. The focus will be on constructing a streaming pipeline utilizing various Google Cloud Platform (GCP) services, including:

![Pubsub pipeline flow](https://github.com/user-attachments/assets/bf8a8150-b0c8-4823-872b-6acd1e0e5f5c)

&#8226; Google Cloud Storage (GCS) is utilized to store the "conversations.json" file, offering reliable and scalable object storage for your data.

&#8226; Google Cloud Pub/Sub is employed to publish the contents of the "conversations.json" file to a specified topic, enabling asynchronous communication and decoupling of message producers and consumers. This service ensures reliable and scalable message delivery.

&#8226; Google Cloud Dataflow, built on the Apache Beam framework, is used to construct and execute a streaming data processing pipeline. It facilitates the real-time transformation of conversations data. By leveraging Dataflow, we can effectively partition the data into two tables: "conversations" and "orders."

&#8226; Google BigQuery serves as the repository for the processed conversations data. It provides a scalable and efficient platform for querying and analyzing streaming data, enabling insightful data retrieval and analysis.

&#8226; Using Client Libraries in Python, we define and provision a GCS bucket, Pub/Sub topic, subscription, and BigQuery dataset with tables. This approach allows for the automation of resource creation, ensuring a consistent and reproducible infrastructure setup for efficient data storage, messaging, and analysis.

# <u>Pub/Sub Topic and Subscription</u>
To enhance your understanding of how Pub/Sub operates, take a look at the message lifecycle example, which demonstrates the process of message transmission within the system.

![pub_sub_flow (1)](https://github.com/user-attachments/assets/4af2d96b-4145-49e6-a669-d99bee81e7fe)

A publisher application sends a message to a Pub/Sub topic. The message is written to storage. Along with writing the message to storage, Pub/Sub delivers the message to all the attached subscriptions of the topic. In this example, it's a single subscription. The subscription sends the message to an attached subscriber application. The subscriber sends an acknowledgment to Pub/Sub that they have processed the message. After at least one subscriber for each subscription has acknowledged the message, Pub/Sub deletes the message from storage.

There are options for creating the Pub/Sub topic and subscription including using the GCP console to manually set up the Topic and Subscription. In this project, I used Pub/Sub client libray in python to create my topic and subscription.
Leverage the provided code in my repository by running the command python topic-subscription.py

# <u>Pub/Sending Data to Pub/Sub</u>
We have several options for transmitting data from the bucket to Pub/Sub not limited to:

&#8226; Export the data directly from the bucket to Pub/Sub

<img width="916" alt="Data to PubSub" src="https://github.com/user-attachments/assets/725e9b6c-bba8-4abb-91bc-c1b6e8e5d5c2">

&#8226; Import the data directly from the topic to Pub/Sub

<img width="565" alt="import to pubsub" src="https://github.com/user-attachments/assets/cad1e0a8-08bc-424b-9295-825a146022b5">

Both methods entail starting a Dataflow batch job using the 'Cloud Storage Text File to Pub/Sub (Batch)' template. However, these options are primarily designed for smaller datasets.

&#8226; For larger volumes of data, alternative methods are necessary to efficiently send data to Pub/Sub. In such instances, I suggest utilizing Python code, which is better suited for managing and processing significant amounts of data.
To execute the code, run the command `python send-data-to-pubsub.py` in your terminal. Be sure to supply the required parameters: topic path, bucket name, and file name.

# <u>Streaming Apache Beam/Dataflow pipeline</u>

Apache Beam is a versatile framework that offers flexibility for both batch and streaming data processing, making it a widely applicable tool in various use cases.

The [Direct Runner](https://beam.apache.org/documentation/runners/direct/) executes pipelines on your machine and is designed to validate that pipelines adhere to the Apache Beam model as closely as possible. Using the Direct Runner for testing and development helps ensure that pipelines are robust across different Beam runners. The Direct Runner is not designed for production pipelines, because it's optimized for correctness rather than performance.

The [Google Cloud](https://beam.apache.org/documentation/runners/dataflow/) Dataflow Runner uses the Cloud Dataflow managed service. When you run your pipeline with the Cloud Dataflow service, the runner uploads your executable code and dependencies to a Google Cloud Storage bucket and creates a Cloud Dataflow job, which executes your pipeline on managed resources in Google Cloud Platform.

Transforming your Apache Beam pipeline from DirectRunner to DataflowRunner for creating a Dataflow job is a straightforward process that requires just a few modifications. The job_name and other lines after it in the following code are optional. However, you may want to consider adjusting the number of workers to enhance the job's performance. For more information on Pipeline options, refer to this [documentation](https://cloud.google.com/dataflow/docs/reference/pipeline-options#python).

If you want to specify a Service account, make sure it has these roles: BigQuery Admin, Dataflow Worker, Pub/Sub Admin, Storage Object Viewer.

```
<...>
#Define your Dataflow pipeline options
options = PipelineOptions(
    runner='DirectRunner',     #for Dataflow job change to DataflowRunner
    project='your-project-id',
    region='you-region',     #for Dataflow job change to e.g. us-west1
    temp_location='gs://your-bucket/temp',
    staging_location='gs://your-bucket/staging',
    streaming=True,    #Enable streaming mode
    #Dataflow parameters that are optional
    #job_name='streaming-conversations'   
    #num_workers=5,    
    #max_num_workers=10,    
    #disk_size_gb=100,    
    #autoscaling_algorithm='THROUGHPUT_BASED',    
    #machine_type='n1-standard-4',    
    #service_account_email='your-service-account@your-project.iam.gserviceaccount.com'  
<...>
```
Autoscaling will be enabled for Dataflow Streaming Engine even without specifying optional parameters. Workers will scale between 1 and 100 unless maxNumWorkers is specified

<img width="800" alt="DataflowJob" src="https://github.com/user-attachments/assets/9de081c1-9dde-4a23-9ce4-cbaa967e874a">

To initiate the streaming process using Apache Beam and Dataflow, execute the following command in your second terminal:

```bash
python streaming-beam-dataflow.py
```
Running the provided scripts (python send-data-to-pubsub.py and python streaming-beam-dataflow.py) in each terminal will trigger a series of actions:

&#8226; **Publish Messages**: Messages will be published to the Pub/Sub topic.

&#8226; **Read Data**: The pipeline will read data from a Pub/Sub subscription using the ReadFromPubSub transform.

&#8226; **Extract Fields**: Desired fields from the parsed messages will be extracted for the "conversations" and "orders" tables using the beam.Map transform and lambda functions.

&#8226; **Write to BigQuery**: The processed "conversations" and "orders" data will be written to the respective BigQuery tables using the WriteToBigQuery transform.

# <u>BigQuery Streaming Buffer</u>
By default, BigQuery utilizes a designated storage area known as the "streaming buffer" to manage streaming data. This temporary storage space retains incoming data for a brief period before it is fully committed and integrated into the permanent table.
<img width="664" alt="BigQueryStreaming" src="https://github.com/user-attachments/assets/275c0db6-77fe-463f-8566-f6f7a524da4f">

When you cease streaming data, the streaming buffer no longer receives continuous updates. At this point, BigQuery initiates the process of flushing the buffered data into the main table storage. During this process, the data is reorganized and compressed to ensure efficient storage. This step is crucial for maintaining data consistency and integrity before the data is fully committed to the table.

The time required for streamed data to be completely committed and visible in the table varies based on several factors, including the buffer size, data volume, and BigQuery's internal processing capabilities. Typically, this flushing process takes a few minutes but can extend up to 90 minutes for the data to become visible in the table.

In the example provided, the updated information can be found in the "Storage info" section. If streaming was in progress, at the details section of the table, you will see 'Streaming Buffer Statistics' section, because it has ended, you only see the 'Storage info' section.

# <u>Querying the Final Table</u>
The final step is to create the "customer_courier_conversations" table. In this instance, we will generate a view, which acts as a virtual table defined by a SQL query. This custom SQL code will facilitate the transformation of the data to align with the specific requirements of the task.

You can create the use the google cloud console to create the view in BigQuery or you can also use the bq command line tool other methods.
<img width="790" alt="create-view" src="https://github.com/user-attachments/assets/662db5ba-4e51-4190-824b-92943f08dc32">

Views serve as virtual references to a collection of data, providing reusable access without the need to physically store the data. In contrast, materialized views are defined using SQL like regular views but actually store the data physically. However, materialized views have limitations in terms of query support. Given the considerable size of my query, a regular view was the more appropriate option in this instance.

After initiating the streaming process, you can execute the saved view after a short wait.
<img width="911" alt="view-query" src="https://github.com/user-attachments/assets/1b4a8f56-3f3a-4b09-b0fa-3e98c10711e7">

```bash
SELECT * FROM `your-project-id.dataset.view`
```

Let's examine one of the conversations by extracting all messages associated with the "orderId" 99219869  from the "conversations.json" file
<img width="896" alt="order-exam" src="https://github.com/user-attachments/assets/b906ab5f-47e1-43e6-a31c-9979541278b7">

We identify one message. The conversation began with customer message in  Buenos Aires (city_code: BUE) at 10:00:10. The courier responded after 6 seconds at 10:00:16. The last message was received from the customer at 10:01:50 and the last message order stage was recorded as ARRIVED.

Please be aware that, in my situation, the time difference between the first and last messages was just about 1 minute 40 seconds, leading to a swift analysis. As new data streams continuously into the source, the view is automatically updated in real-time to reflect these changes. Consequently, whenever you query the view, you will receive the most current data that meets the specified criteria.


To test with larger datasets, you can find the `generate-the-data.py` code in my GitHub repository. This code enables you to create additional conversations, helping you evaluate the scalability of the project.

Throughout this article, I have referenced the following sources for specific details and concepts:

- [Google Cloud Dataflow Overview](https://cloud.google.com/dataflow/docs/overview)
- [Google Cloud Pub/Sub Overview](https://cloud.google.com/pubsub/docs/overview)
- [Apache Beam Dataflow Runner Documentation](https://beam.apache.org/documentation/runners/dataflow/)
- [Apache Beam Direct Runner Documentation](https://beam.apache.org/documentation/runners/direct/)
- [BigQuery Views Introduction](https://cloud.google.com/bigquery/docs/views-intro)
