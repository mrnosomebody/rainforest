import logging
from datetime import datetime

from celery import shared_task

from reports.services import generate_summary_report

logger = logging.getLogger(__name__)


@shared_task
def generate_report_task(start_date: datetime, end_date: datetime) -> dict:
    logger.info("Generating report for period {start_date} - {end_date}: {report}")
    report = generate_summary_report(start_date, end_date)
    logger.info(f"Report generated for period {start_date} - {end_date}: {report}")

    return report
