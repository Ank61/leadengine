# RabbitMQ Integration - Complete Documentation

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Configuration](#configuration)
4. [Publisher](#publisher)
5. [Consumer](#consumer)
6. [Message Format](#message-format)
7. [Error Handling](#error-handling)
8. [Monitoring](#monitoring)
9. [Best Practices](#best-practices)

---

## Overview

RabbitMQ is used as the message broker for asynchronous job processing in the LeadEngine application.

### Why RabbitMQ?

- ✅ **Decoupling**: API and workers are independent
- ✅ **Scalability**: Add more workers to handle load
- ✅ **Reliability**: Messages persisted to disk
- ✅ **Load Balancing**: Messages distributed across workers
- ✅ **Fault Tolerance**: Messages requeued if worker fails

### Message Pattern

**Point-to-Point (Work Queue)**
- One queue: `scrape_jobs`
- Multiple producers: API endpoints
- Multiple consumers: Workers
- Each message consumed by exactly ONE worker

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    PRODUCERS (API)                       │
│  - POST /api/v1/jobs/scrape                             │
│  - Creates job in database                              │
│  - Publishes message to queue                           │
└─────────────────────────────────────────────────────────┘
                         ↓ AMQP Protocol
┌─────────────────────────────────────────────────────────┐
│                    RABBITMQ BROKER                       │
│                                                          │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Queue: scrape_jobs                               │  │
│  │  - Durable: Yes                                   │  │
│  │  - Auto-delete: No                                │  │
│  │  - Messages: Persistent                           │  │
│  └───────────────────────────────────────────────────┘  │
│                                                          │
└─────────────────────────────────────────────────────────┘
                         ↓ AMQP Protocol
┌─────────────────────────────────────────────────────────┐
│                 CONSUMERS (Workers)                      │
│  - Worker 1 (processes message 1, 4, 7, ...)           │
│  - Worker 2 (processes message 2, 5, 8, ...)           │
│  - Worker 3 (processes message 3, 6, 9, ...)           │
└─────────────────────────────────────────────────────────┘
```

---

## Configuration

### Environment Variables

Add to `.env`:

```env
# RabbitMQ Configuration
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
RABBITMQ_VHOST=/
```

### Settings Class

**File:** `app/core/config.py`

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    rabbitmq_user: str
    rabbitmq_password: str
    rabbitmq_host: str
    rabbitmq_port: int
    rabbitmq_vhost: str
    
    model_config = ConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings = Settings()
```

### Connection URL

```python
# Format
amqp://user:password@host:port/vhost

# Example
amqp://guest:guest@localhost:5672/
```

---

## Publisher

### Publisher Class

**File:** `app/mq/publisher.py`

```python
class RabbitMQPublisher:
    """RabbitMQ Publisher for sending messages to queues"""
    
    def __init__(self):
        self.connection = None
        self.channel = None
    
    async def connect(self):
        """Establish connection to RabbitMQ"""
        self.connection = await connect_robust(
            host=settings.rabbitmq_host,
            port=settings.rabbitmq_port,
            login=settings.rabbitmq_user,
            password=settings.rabbitmq_password,
            virtualhost=settings.rabbitmq_vhost,
        )
        self.channel = await self.connection.channel()
    
    async def publish_message(self, queue_name: str, message: Dict[str, Any]):
        """Publish a message to a specific queue"""
        if not self.channel:
            await self.connect()
        
        # Declare queue (idempotent)
        queue = await self.channel.declare_queue(queue_name, durable=True)
        
        # Create message
        message_body = Message(
            body=json.dumps(message).encode(),
            delivery_mode=DeliveryMode.PERSISTENT,
        )
        
        # Publish to queue
        await self.channel.default_exchange.publish(
            message_body,
            routing_key=queue_name,
        )
```

### Publishing a Message

```python
from app.mq.publisher import publish_scrape_job

# Publish scrape job
await publish_scrape_job({
    "job_id": "987fcdeb-51a2-43d7-b123-456789abcdef",
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "industry": "SaaS",
    "geography": "Sydney, Australia",
    "keywords": ["B2B", "enterprise"],
    "source_types": ["google", "linkedin"],
    "search_query": "saas companies sydney",
    "filters": {}
})
```

### Publisher Features

- **Connection Pooling**: Reuses connection across requests
- **Auto-reconnect**: Reconnects if connection drops
- **Persistent Messages**: Messages saved to disk
- **Durable Queues**: Queue survives broker restart
- **Error Handling**: Logs and raises exceptions

---

## Consumer

### Consumer Class

**File:** `workers/scraper_worker.py`

```python
class ScrapeWorker:
    """Worker that consumes scrape job messages from RabbitMQ"""
    
    async def connect(self):
        """Establish connection to RabbitMQ"""
        self.connection = await connect_robust(
            host=settings.rabbitmq_host,
            port=settings.rabbitmq_port,
            login=settings.rabbitmq_user,
            password=settings.rabbitmq_password,
            virtualhost=settings.rabbitmq_vhost,
        )
        
        self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=1)
    
    async def process_message(self, message: IncomingMessage):
        """Process a single message"""
        async with message.process(requeue=False):
            payload = json.loads(message.body)
            await self.process_scrape_job(payload)
    
    async def start(self):
        """Start consuming messages"""
        await self.connect()
        
        queue = await self.channel.declare_queue("scrape_jobs", durable=True)
        await queue.consume(self.process_message)
        
        # Keep running
        while not self.should_stop:
            await asyncio.sleep(1)
```

### Consumer Features

- **Event-Driven**: Processes messages immediately
- **Prefetch Control**: `prefetch_count=1` (one at a time)
- **Auto-acknowledge**: Message removed after processing
- **Requeue on Failure**: `requeue=False` (don't requeue)
- **Graceful Shutdown**: Handles Ctrl+C properly

### Starting the Consumer

```bash
cd backend
.\start_worker.ps1
```

Or:

```bash
$env:PYTHONPATH="D:\Coding\Live\LeadEngine\backend"
.\venv\Scripts\python.exe workers\scraper_worker.py
```

---

## Message Format

### Scrape Job Message

```json
{
  "job_id": "987fcdeb-51a2-43d7-b123-456789abcdef",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "industry": "SaaS",
  "geography": "Sydney, Australia",
  "keywords": ["B2B", "enterprise", "cloud"],
  "source_types": ["google", "linkedin"],
  "search_query": "saas companies sydney",
  "filters": {
    "company_size": "50-200",
    "revenue": ">1M"
  }
}
```

### Message Properties

- **Content-Type**: `application/json`
- **Delivery Mode**: `2` (persistent)
- **Encoding**: `UTF-8`
- **Priority**: Not used (FIFO)

### Message Size

- **Recommended**: < 100 KB
- **Maximum**: 128 MB (RabbitMQ default)
- **Large Payloads**: Store in database, send reference

---

## Error Handling

### Publisher Errors

```python
try:
    await publish_scrape_job(message_payload)
except Exception as e:
    logger.error("message_publish_failed", error=str(e))
    # Handle error (retry, alert, etc.)
    raise
```

### Consumer Errors

```python
async def process_message(self, message: IncomingMessage):
    async with message.process(requeue=False):
        try:
            payload = json.loads(message.body)
            await self.process_scrape_job(payload)
        except Exception as e:
            logger.error("message_processing_failed", error=str(e))
            # Update job status to "failed"
            # Don't requeue (requeue=False)
```

### Connection Errors

```python
# Publisher auto-reconnects
self.connection = await connect_robust(...)  # "robust" = auto-reconnect

# Consumer handles connection loss
try:
    await worker.start()
except ConnectionError:
    logger.error("rabbitmq_connection_lost")
    # Retry connection
```

### Dead Letter Queue (Optional)

For failed messages:

```python
queue = await channel.declare_queue(
    "scrape_jobs",
    durable=True,
    arguments={
        "x-dead-letter-exchange": "dlx",
        "x-dead-letter-routing-key": "failed_jobs"
    }
)
```

---

## Monitoring

### RabbitMQ Management UI

**URL:** http://localhost:15672

**Credentials:**
- Username: `guest`
- Password: `guest`

**Features:**
- View queues and messages
- Monitor connections and channels
- Check message rates
- View consumer details

### Key Metrics

**Queue Metrics:**
- **Ready**: Messages waiting to be consumed
- **Unacked**: Messages being processed
- **Total**: Total messages in queue

**Consumer Metrics:**
- **Consumers**: Number of active consumers
- **Prefetch**: Messages per consumer
- **Ack Rate**: Messages acknowledged per second

### Monitoring Commands

```bash
# List queues
rabbitmqctl list_queues

# List consumers
rabbitmqctl list_consumers

# Queue details
rabbitmqctl list_queues name messages consumers

# Connection status
rabbitmqctl list_connections
```

### Application Logging

```python
# Publisher logs
logger.info("message_published", queue="scrape_jobs", message_id=job_id)

# Consumer logs
logger.info("message_received", job_id=job_id)
logger.info("message_processed", job_id=job_id, duration=2.15)
```

---

## Best Practices

### 1. Use Durable Queues

```python
queue = await channel.declare_queue("scrape_jobs", durable=True)
```

**Why:** Queue survives broker restart

### 2. Use Persistent Messages

```python
message = Message(
    body=json.dumps(data).encode(),
    delivery_mode=DeliveryMode.PERSISTENT
)
```

**Why:** Messages saved to disk

### 3. Set Prefetch Count

```python
await channel.set_qos(prefetch_count=1)
```

**Why:** Prevents worker overload

### 4. Handle Errors Gracefully

```python
async with message.process(requeue=False):
    try:
        await process_job(payload)
    except Exception as e:
        logger.error("job_failed", error=str(e))
        # Update job status to "failed"
        # Don't requeue to avoid infinite loop
```

### 5. Use Connection Pooling

```python
# Reuse connection across requests
_publisher = None

async def get_publisher():
    global _publisher
    if _publisher is None:
        _publisher = RabbitMQPublisher()
        await _publisher.connect()
    return _publisher
```

### 6. Implement Graceful Shutdown

```python
def signal_handler(signum, frame):
    print("Shutting down...")
    asyncio.create_task(worker.stop())

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
```

### 7. Monitor Queue Length

```python
# Alert if queue grows too large
if queue_length > 1000:
    send_alert("Queue backlog detected")
    # Scale up workers
```

### 8. Use Message TTL (Optional)

```python
# Messages expire after 1 hour
queue = await channel.declare_queue(
    "scrape_jobs",
    arguments={"x-message-ttl": 3600000}  # milliseconds
)
```

### 9. Implement Retry Logic

```python
MAX_RETRIES = 3

for attempt in range(MAX_RETRIES):
    try:
        await publish_message(queue, data)
        break
    except Exception as e:
        if attempt == MAX_RETRIES - 1:
            raise
        await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

### 10. Log Everything

```python
logger.info("message_published", queue=queue_name, message_id=msg_id)
logger.info("message_received", message_id=msg_id)
logger.info("message_processed", message_id=msg_id, duration=duration)
logger.error("message_failed", message_id=msg_id, error=str(e))
```

---

## Troubleshooting

### Connection Refused

**Error:** `Connection refused to localhost:5672`

**Solution:**
1. Check RabbitMQ is running: `rabbitmqctl status`
2. Check port 5672 is open
3. Verify credentials in `.env`

### Messages Not Consumed

**Error:** Messages stuck in queue

**Solution:**
1. Check worker is running
2. Check worker logs for errors
3. Verify queue name matches

### Memory Issues

**Error:** RabbitMQ using too much memory

**Solution:**
1. Set message TTL
2. Implement dead letter queue
3. Increase worker count
4. Reduce prefetch count

### Slow Processing

**Error:** Messages processed slowly

**Solution:**
1. Add more workers
2. Optimize scraping logic
3. Increase prefetch count
4. Use async operations

---

## Summary

RabbitMQ provides:
- ✅ **Reliable Messaging**: Persistent, durable queues
- ✅ **Scalability**: Add workers for higher throughput
- ✅ **Decoupling**: API and workers independent
- ✅ **Load Balancing**: Messages distributed automatically
- ✅ **Fault Tolerance**: Messages requeued on failure

For more information:
- [RabbitMQ Documentation](https://www.rabbitmq.com/documentation.html)
- [aio-pika Documentation](https://aio-pika.readthedocs.io/)
- `SCRAPE_JOB_SYSTEM.md` - Complete system documentation
