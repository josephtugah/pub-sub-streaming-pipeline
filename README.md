# GCP Data Engineering Project: Streaming Data Pipeline with Pub/Sub and Apache Beam/Dataflow

Google Cloud Pub/Sub is a fully managed messaging service designed to support real-time messaging between applications. It enables reliable, asynchronous communication by decoupling senders and receivers, making it ideal for building event-driven systems.

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


