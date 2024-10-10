CREATE VIEW `your_project_id.your_dataset.customer_courier_conversations_view` AS
SELECT
  o.orderId AS order_id,  -- Unique identifier for the order
  o.cityCode AS city_code,  -- Code representing the city for the order
  MIN(CASE
      WHEN m.senderAppType LIKE '%Courier%' THEN m.messageSentTime  -- Time of the first message from a courier
  END) AS first_courier_message,
  MIN(CASE
      WHEN m.senderAppType LIKE '%Customer%' THEN m.messageSentTime  -- Time of the first message from a customer
  END) AS first_customer_message,
  COUNT(CASE
      WHEN m.senderAppType LIKE '%Courier%' THEN 1  -- Count of messages from couriers
  END) AS num_messages_courier,
  COUNT(CASE
      WHEN m.senderAppType LIKE '%Customer%' THEN 1  -- Count of messages from customers
  END) AS num_messages_customer,
  CASE
    WHEN MIN(CASE
              WHEN m.senderAppType LIKE '%Courier%' AND m.chatStartedByMessage = TRUE THEN m.senderAppType
              WHEN m.senderAppType LIKE '%Customer%' AND m.chatStartedByMessage = TRUE THEN m.senderAppType
          END) LIKE '%Customer%' THEN 'Customer'
    WHEN MIN(CASE
              WHEN m.senderAppType LIKE '%Courier%' AND m.chatStartedByMessage = TRUE THEN m.senderAppType
              WHEN m.senderAppType LIKE '%Customer%' AND m.chatStartedByMessage = TRUE THEN m.senderAppType
          END) LIKE '%Courier%' THEN 'Courier'
    ELSE 'Unknown'  -- Default case if the sender type is unknown
  END AS first_message_by,
  MIN(m.messageSentTime) AS conversation_started_at,  -- Timestamp when the conversation started
  ABS(TIMESTAMP_DIFF(
    MIN(CASE
        WHEN m.senderAppType LIKE '%Customer%' THEN m.messageSentTime  -- Time of the first customer message
    END),
    MIN(CASE
        WHEN m.senderAppType LIKE '%Courier%' THEN m.messageSentTime  -- Time of the first courier message
    END),
    SECOND
  )) AS first_responsetime_delay_seconds,  -- Time difference between first customer and courier messages
  MAX(m.messageSentTime) AS last_message_time,  -- Timestamp of the last message in the conversation
  last_stage_table.orderStage AS last_message_order_stage  -- Stage of the order for the last message
FROM
  `your_project_id.your_dataset.orders` AS o  -- Table containing order information
JOIN
  `your_project_id.your_dataset.conversations` AS m  -- Table containing conversation messages
ON
  o.orderId = m.orderId  -- Join condition on orderId
LEFT JOIN (
  SELECT
    orderId,
    messageSentTime,
    orderStage
  FROM (
    SELECT
      orderId,
      messageSentTime,
      orderStage,
      ROW_NUMBER() OVER (PARTITION BY orderId ORDER BY messageSentTime DESC) as rn  -- Get the latest message for each order
    FROM
      `your_project_id.your_dataset.conversations`
  ) WHERE rn = 1
) AS last_stage_table
ON
  o.orderId = last_stage_table.orderId  -- Join to get the last message stage
GROUP BY
  o.orderId,
  o.cityCode,
  last_stage_table.orderStage;  -- Group by order ID, city code, and last message stage
