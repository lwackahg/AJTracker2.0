"""
Scheduler utility for automating tasks like database backups and performance monitoring.
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging
from .backup import run_daily_backup
from ..services.analytics_service import AnalyticsService
from flask import current_app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskScheduler:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TaskScheduler, cls).__new__(cls)
            cls._instance.scheduler = BackgroundScheduler()
            cls._instance.analytics_service = AnalyticsService()
            cls._instance._initialize_jobs()
        return cls._instance
    
    def _initialize_jobs(self):
        """Initialize all scheduled jobs."""
        # Schedule daily backup at 2 AM
        self.scheduler.add_job(
            run_daily_backup,
            trigger=CronTrigger(hour=2),
            id='daily_backup',
            name='Daily Database Backup',
            replace_existing=True
        )
        
        # Schedule hourly performance metrics collection
        self.scheduler.add_job(
            self._collect_performance_metrics,
            trigger=CronTrigger(minute=0),  # Run at the start of every hour
            id='performance_metrics',
            name='Hourly Performance Metrics',
            replace_existing=True
        )
        
        # Schedule weekly analytics report
        self.scheduler.add_job(
            self._generate_weekly_report,
            trigger=CronTrigger(day_of_week='mon', hour=5),  # Run every Monday at 5 AM
            id='weekly_report',
            name='Weekly Analytics Report',
            replace_existing=True
        )
    
    def start(self):
        """Start the scheduler."""
        try:
            if not self.scheduler.running:
                self.scheduler.start()
                logger.info("Scheduler started successfully")
        except Exception as e:
            logger.error(f"Failed to start scheduler: {str(e)}")
            raise
    
    def shutdown(self):
        """Shutdown the scheduler."""
        try:
            if self.scheduler.running:
                self.scheduler.shutdown()
                logger.info("Scheduler shut down successfully")
        except Exception as e:
            logger.error(f"Failed to shutdown scheduler: {str(e)}")
            raise
    
    def _collect_performance_metrics(self):
        """Collect and store performance metrics."""
        try:
            metrics = self.analytics_service.collect_performance_metrics()
            logger.info(f"Performance metrics collected: {metrics}")
        except Exception as e:
            logger.error(f"Failed to collect performance metrics: {str(e)}")
    
    def _generate_weekly_report(self):
        """Generate weekly analytics report."""
        try:
            report = self.analytics_service.generate_weekly_report()
            logger.info("Weekly analytics report generated successfully")
        except Exception as e:
            logger.error(f"Failed to generate weekly report: {str(e)}")
