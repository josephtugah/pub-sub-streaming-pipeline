![pub_sub_flow (1)](https://github.com/user-attachments/assets/4af2d96b-4145-49e6-a669-d99bee81e7fe)# GCP Data Engineering Project: Streaming Data Pipeline with Pub/Sub and Apache Beam/Dataflow

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

<img width="498" alt="pubsub message system" src="https://github.com/user-attachments/assets/1d3d194c-1ccf-45ba-af05-055fee70a91a">
