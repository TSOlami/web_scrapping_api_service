from enum import Enum
from datetime import datetime
import uuid
from typing import Dict, Optional
import logging

class JobStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class QueueManager:
    def __init__(self):
        self.jobs: Dict[str, Dict] = {}
        self.last_request_times = []  # Store timestamps of last 3 requests
        self.logger = logging.getLogger(__name__)
        
    def can_make_request(self) -> bool:
        """Check if we can make a new request based on rate limits"""
        now = datetime.now()
        # Remove timestamps older than 1 minute
        self.last_request_times = [t for t in self.last_request_times 
                                 if (now - t).total_seconds() < 60]
        
        # If we have less than 3 requests in the last minute, we can proceed
        return len(self.last_request_times) < 3

    def record_request(self):
        """Record a new request timestamp"""
        self.last_request_times.append(datetime.now())
        self.logger.info(f"Recorded new request. Total requests in last minute: {len(self.last_request_times)}")

    def time_until_next_available(self) -> float:
        """Calculate seconds until next request slot is available"""
        if len(self.last_request_times) < 3:
            return 0
        
        oldest_request = min(self.last_request_times)
        seconds_since_oldest = (datetime.now() - oldest_request).total_seconds()
        return max(60 - seconds_since_oldest, 0)

    def create_job(self, scholarship_id: int) -> str:
        job_id = str(uuid.uuid4())
        self.jobs[job_id] = {
            "scholarship_id": scholarship_id,
            "status": JobStatus.PENDING,
            "created_at": datetime.now(),
            "completed_at": None,
            "error": None,
            "image_path": None
        }
        self.logger.info(f"Created new job {job_id} for scholarship {scholarship_id}")
        return job_id

    def update_job(self, job_id: str, status: JobStatus, image_path: Optional[str] = None, error: Optional[str] = None):
        if job_id in self.jobs:
            self.jobs[job_id]["status"] = status
            if status in [JobStatus.COMPLETED, JobStatus.FAILED]:
                self.jobs[job_id]["completed_at"] = datetime.now()
            if image_path:
                self.jobs[job_id]["image_path"] = image_path
            if error:
                self.jobs[job_id]["error"] = error
            
            self.logger.info(f"Updated job {job_id} - Status: {status.value}, Error: {error}, Image: {image_path}")

    def get_job_status(self, job_id: str) -> Optional[Dict]:
        status = self.jobs.get(job_id)
        self.logger.debug(f"Retrieved status for job {job_id}: {status}")
        return status 