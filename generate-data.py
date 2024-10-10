import random
from datetime import datetime, timedelta
import json

def generate_conversation():
    sender_types = ["Courier Android", "Customer iOS"]
    courier_id = random.randint(10000000, 99999999)  # Unique courier ID
    customer_id = random.randint(10000000, 99999999)  # Unique customer ID
    order_id = random.randint(10000000, 99999999)  # Unique order ID
    message_sent_time = generate_unique_time()  # Generate unique message sent time

    conversations = []
    chat_started_by_message = True  # Flag to track the first message in a conversation
    sender_type = random.choice(sender_types)
    num_replies = random.randint(2, 5)  # Random number of replies (2, 3, or 5)

    for message_num in range(num_replies):
        # Prepare common fields
        common_fields = {
            "orderId": order_id,
            "messageSentTime": message_sent_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "chatStartedByMessage": chat_started_by_message
        }

        if sender_type.startswith("Courier"):
            conversation = {
                **common_fields,
                "senderAppType": sender_type,
                "courierId": courier_id,  # Unique courier ID
                "fromId": courier_id,
                "toId": customer_id,
                "orderStage": random.choice(["ACCEPTED", "IN_PROGRESS", "COMPLETED", "CANCELLED", "IN_TRANSIT", "PROCESSING", "DELAYED", "OUT_FOR_DELIVERY", "RETURNED", "AWAITING_PICKUP", "ARRIVED", "FAILED", "PENDING", "ACCEPTED", "ON_ROUTE", "DELIVERED"]),
                "customerId": customer_id  # Unique customer ID
            }
        else:
            conversation = {
                **common_fields,
                "senderAppType": sender_type,
                "customerId": customer_id,  # Unique customer ID
                "fromId": customer_id,
                "toId": courier_id,
                "orderStage": random.choice(["ACCEPTED", "IN_PROGRESS", "COMPLETED", "CANCELLED", "IN_TRANSIT", "PROCESSING", "DELAYED", "OUT_FOR_DELIVERY", "RETURNED", "AWAITING_PICKUP", "ARRIVED", "FAILED", "PENDING", "ACCEPTED", "ON_ROUTE", "DELIVERED"]),
                "courierId": courier_id  # Unique courier ID
            }

        conversations.append(conversation)
        chat_started_by_message = False  # Update flag for subsequent messages

        # Toggle sender type for the next message
        sender_type = "Customer iOS" if sender_type == "Courier Android" else "Courier Android"

        # Increment the message sent time by a random duration between 1 second and 1 minute
        message_sent_time += timedelta(seconds=random.randint(1, 60))

    # Add additional line with city code
    city_line = {
        "orderId": order_id,  # Unique order ID
        "cityCode": random_city_code()  # Use string format for city codes
    }
    conversations.append(city_line)

    return conversations

def generate_unique_time():
    global last_message_sent_time

    # Increment the last message sent time by a random duration between 1 second and 1 minute
    last_message_sent_time += timedelta(seconds=random.randint(1, 60))
    return last_message_sent_time

def random_city_code():
    cities = ["BCN", "NYC", "LON", "PAR", "BER", "TOK", "ROM", "MAD", "SYD", "MEX", "CAI", "AMS", "TOR", "IST", "SAN", "SIN", "RIO", "BUE", "CPT", "MUM"]
    return random.choice(cities)

# Set the initial message sent time
last_message_sent_time = datetime(2024, 2, 1, 10, 0, 0)

# Generate and save 20 conversations
conversations = []
for _ in range(20):  # Generate 20 conversations
    conversation = generate_conversation()
    conversations.extend(conversation)

# Output conversations as JSON in a single line
output_filename = "conversations.json"
with open(output_filename, "w") as file:
    for message in conversations:
        json.dump(message, file, separators=(",", ":"))
        file.write("\n")

print("Conversations saved to 'conversations.json'")
