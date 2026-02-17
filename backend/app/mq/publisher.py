"""
RabbitMQ Message Queue utilities for publishing and consuming messages
"""
import json
import asyncio
from typing import Dict, Any
from aio_pika import connect_robust, Message, DeliveryMode
from app.core.config import settings
from app.core.logging import setup_logging

logger = setup_logging()


class RabbitMQPublisher:
    """RabbitMQ Publisher for sending messages to queues"""
    
    def __init__(self):
        self.connection = None
        self.channel = None
    
    async def connect(self):
        """Establish connection to RabbitMQ"""
        try:
            self.connection = await connect_robust(
                host=settings.rabbitmq_host,
                port=settings.rabbitmq_port,
                login=settings.rabbitmq_user,
                password=settings.rabbitmq_password,
                virtualhost=settings.rabbitmq_vhost,
            )
            self.channel = await self.connection.channel()
            logger.info("rabbitmq_connected", host=settings.rabbitmq_host)
        except Exception as e:
            logger.error("rabbitmq_connection_failed", error=str(e))
            raise
    
    async def publish_message(self, queue_name: str, message: Dict[str, Any]):
        """
        Publish a message to a specific queue
        
        Args:
            queue_name: Name of the queue
            message: Message payload as dictionary
        """
        if not self.channel:
            await self.connect()
        
        try:
            # Declare queue (idempotent operation)
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
            
            logger.info(
                "message_published",
                queue=queue_name,
                message_id=message.get("job_id")
            )
            
        except Exception as e:
            logger.error(
                "message_publish_failed",
                queue=queue_name,
                error=str(e)
            )
            raise
    
    async def close(self):
        """Close RabbitMQ connection"""
        if self.connection:
            await self.connection.close()
            logger.info("rabbitmq_connection_closed")


# Global publisher instance
_publisher = None


async def get_publisher() -> RabbitMQPublisher:
    """Get or create RabbitMQ publisher instance"""
    global _publisher
    if _publisher is None:
        _publisher = RabbitMQPublisher()
        await _publisher.connect()
    return _publisher


async def publish_scrape_job(job_data: Dict[str, Any]):
    """
    Publish a scrape job to the scrape_jobs queue
    
    Args:
        job_data: Job data including job_id, user_id, source_type, search_query, filters
    """
    publisher = await get_publisher()
    await publisher.publish_message("scrape_jobs", job_data)
