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

&#8226; First item
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





