"""
RabbitMQ Consumer Worker for Scrape Jobs
Point-to-Point Pattern: Listens to scrape_jobs queue and processes messages immediately

This is an EVENT-DRIVEN LISTENER, not a scheduled job.
- Continuously listens to the queue
- Processes messages as they arrive
- No polling or cron jobs needed
"""
import asyncio
import json
import hashlib
import signal
import sys
from datetime import datetime
from aio_pika import connect_robust, IncomingMessage, ExchangeType
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models import ScrapeJob, RawLead
from app.core.config import settings


# Configuration
MAX_RETRIES = 3
QUEUE_NAME = "scrape_jobs"
PREFETCH_COUNT = 1  # Process one message at a time


class ScrapeWorker:
    """Worker that consumes scrape job messages from RabbitMQ"""
    
    def __init__(self):
        self.connection = None
        self.channel = None
        self.should_stop = False
        
    async def connect(self):
        """Establish connection to RabbitMQ"""
        print("🔌 Connecting to RabbitMQ...")
        print(f"   Host: {settings.rabbitmq_host}:{settings.rabbitmq_port}")
        print(f"   VHost: {settings.rabbitmq_vhost}")
        
        self.connection = await connect_robust(
            host=settings.rabbitmq_host,
            port=settings.rabbitmq_port,
            login=settings.rabbitmq_user,
            password=settings.rabbitmq_password,
            virtualhost=settings.rabbitmq_vhost,
        )
        
        self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=PREFETCH_COUNT)
        
        print("✓ Connected to RabbitMQ successfully!")
        
    async def process_message(self, message: IncomingMessage):
        """
        Process a single scrape job message
        
        This function is called automatically when a message arrives in the queue.
        It's event-driven - no polling needed!
        """
        async with message.process(requeue=False):
            try:
                # Parse message payload
                payload = json.loads(message.body)
                
                job_id = payload["job_id"]
                user_id = payload["user_id"]
                
                print("\n" + "="*60)
                print(f"📨 NEW MESSAGE RECEIVED")
                print("="*60)
                print(f"Job ID: {job_id}")
                print(f"User ID: {user_id}")
                print(f"Industry: {payload.get('industry', 'N/A')}")
                print(f"Geography: {payload.get('geography', 'N/A')}")
                print(f"Keywords: {payload.get('keywords', [])}")
                print(f"Source Types: {payload.get('source_types', [])}")
                print(f"Search Query: {payload.get('search_query', 'N/A')}")
                print("="*60)
                
                # Process the job
                await self.process_scrape_job(payload)
                
            except Exception as e:
                print(f"\n❌ ERROR processing message: {str(e)}")
                import traceback
                traceback.print_exc()
    
    async def process_scrape_job(self, payload: dict):
        """Process a scrape job"""
        
        job_id = payload["job_id"]
        user_id = payload["user_id"]
        
        db: Session = SessionLocal()
        
        try:
            # 1. Get job from database
            job = db.query(ScrapeJob).filter(ScrapeJob.id == job_id).first()
            
            if not job:
                print(f"⚠️  Job {job_id} not found in database")
                return
            
            # 2. Update status to RUNNING
            print(f"\n🏃 Starting job processing...")
            job.status = "running"
            job.started_at = datetime.utcnow()
            db.commit()
            print(f"✓ Job status updated to: RUNNING")
            
            # 3. Run the scraper
            print(f"\n🔍 Running scraper...")
            results = await self.run_scraper(payload)
            print(f"✓ Scraper completed. Found {len(results)} results")
            
            # 4. Save raw leads to database
            print(f"\n💾 Saving raw leads to database...")
            saved_count = 0
            duplicate_count = 0
            
            for item in results:
                # Generate hash for deduplication
                hash_value = hashlib.sha256(
                    json.dumps(item, sort_keys=True).encode()
                ).hexdigest()
                
                # Check if already exists
                existing = db.query(RawLead).filter(
                    RawLead.data_hash == hash_value
                ).first()
                
                if existing:
                    duplicate_count += 1
                    continue
                
                # Create new raw lead
                raw = RawLead(
                    scrape_job_id=job_id,
                    user_id=user_id,
                    raw_payload=item,
                    data_hash=hash_value,
                    source_url=item.get("source_url", "")
                )
                
                db.add(raw)
                saved_count += 1
            
            # 5. Update job status to COMPLETED
            job.total_found = len(results)
            job.total_processed = saved_count
            job.status = "completed"
            job.completed_at = datetime.utcnow()
            db.commit()
            
            # 6. Print summary
            print(f"✓ Saved {saved_count} new leads")
            if duplicate_count > 0:
                print(f"⊘ Skipped {duplicate_count} duplicates")
            
            duration = (job.completed_at - job.started_at).total_seconds()
            
            print("\n" + "="*60)
            print(f"✅ JOB COMPLETED SUCCESSFULLY")
            print("="*60)
            print(f"Job ID: {job_id}")
            print(f"Status: {job.status}")
            print(f"Total Found: {job.total_found}")
            print(f"Total Processed: {job.total_processed}")
            print(f"Duration: {duration:.2f} seconds")
            print("="*60 + "\n")
            
        except Exception as e:
            print(f"\n❌ JOB FAILED: {str(e)}")
            
            # Update job status to FAILED
            if job:
                job.status = "failed"
                job.completed_at = datetime.utcnow()
                db.commit()
            
            raise e
            
        finally:
            db.close()
    
    async def run_scraper(self, payload: dict):
        """
        Run the actual scraper logic
        
        TODO: Replace this with real scraping logic
        Currently returns dummy data for testing
        """
        # Simulate scraping delay
        await asyncio.sleep(2)
        
        # Extract criteria from payload
        industry = payload.get("industry", "Unknown")
        geography = payload.get("geography", "Unknown")
        keywords = payload.get("keywords", [])
        source_types = payload.get("source_types", [])
        search_query = payload.get("search_query", "")
        
        # Dummy data for testing
        # TODO: Replace with actual scraping logic based on:
        # - industry
        # - geography
        # - keywords
        # - source_types
        # - search_query
        
        dummy_results = [
            {
                "company_name": f"Acme Corp ({industry})",
                "website": "https://acme.com",
                "industry": industry,
                "location": geography,
                "email": "contact@acme.com",
                "phone": "+1-555-0100",
                "source_url": "https://example.com/acme",
                "matched_keywords": keywords[:2] if keywords else [],
                "confidence": 0.85
            },
            {
                "company_name": f"Beta Solutions ({industry})",
                "website": "https://beta.com",
                "industry": industry,
                "location": geography,
                "email": "info@beta.com",
                "phone": "+1-555-0200",
                "source_url": "https://example.com/beta",
                "matched_keywords": keywords[:1] if keywords else [],
                "confidence": 0.92
            },
            {
                "company_name": f"Gamma Tech ({industry})",
                "website": "https://gamma.tech",
                "industry": industry,
                "location": geography,
                "email": "hello@gamma.tech",
                "phone": "+1-555-0300",
                "source_url": "https://example.com/gamma",
                "matched_keywords": keywords if keywords else [],
                "confidence": 0.78
            }
        ]
        
        return dummy_results
    
    async def start(self):
        """Start the worker and begin consuming messages"""
        
        # Connect to RabbitMQ
        await self.connect()
        
        # Declare queue (idempotent - safe to call multiple times)
        queue = await self.channel.declare_queue(QUEUE_NAME, durable=True)
        
        print(f"\n{'='*60}")
        print(f"🎧 WORKER STARTED - LISTENING FOR MESSAGES")
        print(f"{'='*60}")
        print(f"Queue: {QUEUE_NAME}")
        print(f"Prefetch: {PREFETCH_COUNT} message(s) at a time")
        print(f"Pattern: Point-to-Point (Event-Driven Listener)")
        print(f"\n💡 This worker will process messages IMMEDIATELY as they arrive.")
        print(f"   No polling or cron jobs needed!")
        print(f"\n⏳ Waiting for messages... (Press Ctrl+C to stop)")
        print(f"{'='*60}\n")
        
        # Start consuming messages
        await queue.consume(self.process_message)
        
        # Keep running until stopped
        while not self.should_stop:
            await asyncio.sleep(1)
    
    async def stop(self):
        """Gracefully stop the worker"""
        print("\n\n🛑 Stopping worker...")
        self.should_stop = True
        
        if self.connection:
            await self.connection.close()
            print("✓ RabbitMQ connection closed")
        
        print("✓ Worker stopped gracefully\n")


# Global worker instance
worker = None


def signal_handler(signum, frame):
    """Handle shutdown signals (Ctrl+C)"""
    print("\n\n⚠️  Shutdown signal received...")
    if worker:
        asyncio.create_task(worker.stop())


async def main():
    """Main entry point"""
    global worker
    
    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and start worker
    worker = ScrapeWorker()
    
    try:
        await worker.start()
    except KeyboardInterrupt:
        print("\n\n⚠️  Keyboard interrupt received...")
    except Exception as e:
        print(f"\n\n❌ Worker crashed: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        await worker.stop()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("SCRAPE JOB WORKER")
    print("="*60)
    print("Event-Driven RabbitMQ Consumer")
    print("Point-to-Point Pattern")
    print("="*60 + "\n")
    
    asyncio.run(main())

