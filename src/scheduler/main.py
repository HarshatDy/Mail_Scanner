"""
Main scheduler for the Email Scanner system.
Handles automated email scanning at scheduled intervals.
"""

import time
import signal
import sys
from datetime import datetime
from typing import Optional

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from src.config.config_manager import get_config
from src.utils.logger import get_logger
from src.scheduler.jobs import run_scheduled_scan


class EmailScannerScheduler:
    """Scheduler for automated email scanning."""
    
    def __init__(self):
        self.config = get_config()
        self.logger = get_logger("scheduler")
        self.scheduler = BackgroundScheduler()
        self.running = False
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
        sys.exit(0)
    
    def start(self):
        """Start the scheduler."""
        try:
            self.logger.info("Starting Email Scanner Scheduler...")
            
            # Add scheduled jobs
            scan_times = self.config.scheduler.scan_times
            timezone = self.config.scheduler.timezone
            
            for scan_time in scan_times:
                hour, minute = scan_time.split(':')
                self.scheduler.add_job(
                    func=run_scheduled_scan,
                    trigger=CronTrigger(hour=int(hour), minute=int(minute), timezone=timezone),
                    id=f'email_scan_{scan_time}',
                    name=f'Email Scan at {scan_time}',
                    max_instances=1,
                    coalesce=True
                )
                self.logger.info(f"Added scheduled scan job for {scan_time}")
            
            # Start the scheduler
            self.scheduler.start()
            self.running = True
            
            self.logger.info("Scheduler started successfully!")
            self.logger.info(f"Scan times: {scan_times}")
            self.logger.info(f"Timezone: {timezone}")
            self.logger.info("Press Ctrl+C to stop the scheduler")
            
            # Keep the main thread alive
            try:
                while self.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.logger.info("Received keyboard interrupt")
                self.stop()
                
        except Exception as e:
            self.logger.error(f"Error starting scheduler: {e}")
            raise
    
    def stop(self):
        """Stop the scheduler."""
        if self.running:
            self.logger.info("Stopping scheduler...")
            self.scheduler.shutdown(wait=True)
            self.running = False
            self.logger.info("Scheduler stopped")
    
    def add_job(self, func, trigger, **kwargs):
        """Add a new job to the scheduler."""
        return self.scheduler.add_job(func, trigger, **kwargs)
    
    def remove_job(self, job_id):
        """Remove a job from the scheduler."""
        self.scheduler.remove_job(job_id)
    
    def get_jobs(self):
        """Get all scheduled jobs."""
        return self.scheduler.get_jobs()
    
    def pause_job(self, job_id):
        """Pause a specific job."""
        self.scheduler.pause_job(job_id)
    
    def resume_job(self, job_id):
        """Resume a specific job."""
        self.scheduler.resume_job(job_id)


def start_scheduler():
    """Start the email scanner scheduler."""
    scheduler = EmailScannerScheduler()
    scheduler.start()


def run_immediate_scan():
    """Run an immediate email scan."""
    logger = get_logger("immediate_scan")
    logger.info("Running immediate email scan...")
    
    success = run_scheduled_scan()
    
    if success:
        logger.info("✅ Immediate scan completed successfully")
    else:
        logger.error("❌ Immediate scan failed")
    
    return success


def get_scheduler_status():
    """Get the current status of the scheduler."""
    try:
        scheduler = EmailScannerScheduler()
        jobs = scheduler.get_jobs()
        
        status = {
            "running": scheduler.running,
            "job_count": len(jobs),
            "next_run": None,
            "jobs": []
        }
        
        if jobs:
            next_job = min(jobs, key=lambda x: x.next_run_time)
            status["next_run"] = next_job.next_run_time.isoformat()
            
            for job in jobs:
                status["jobs"].append({
                    "id": job.id,
                    "name": job.name,
                    "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                    "trigger": str(job.trigger)
                })
        
        return status
        
    except Exception as e:
        return {
            "error": str(e),
            "running": False
        } 