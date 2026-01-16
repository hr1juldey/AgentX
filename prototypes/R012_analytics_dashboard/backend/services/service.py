"""Analytics dashboard service with data aggregation."""
import logging
import random
from datetime import datetime, timedelta
from typing import List
import numpy as np

from models.schemas import DashboardMetrics, TimeSeriesData, ChartData

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for analytics and metrics aggregation."""

    def __init__(self):
        """Initialize the analytics service."""
        self._generate_mock_data()

    def _generate_mock_data(self):
        """Generate mock data for demonstration."""
        self.user_growth = [100 + i * 10 + random.randint(-5, 15) for i in range(30)]
        self.request_counts = [500 + i * 20 + random.randint(-50, 100) for i in range(30)]
        self.response_times = [100 + random.randint(-20, 50) for _ in range(100)]

    async def get_dashboard_metrics(self) -> DashboardMetrics:
        """Get aggregated dashboard metrics."""
        return DashboardMetrics(
            total_users=random.randint(1000, 5000),
            active_sessions=random.randint(100, 500),
            total_requests=random.randint(10000, 50000),
            avg_response_time=random.uniform(50, 200),
            success_rate=random.uniform(95, 99.9),
            cpu_usage=random.uniform(20, 80),
            memory_usage=random.uniform(40, 90),
        )

    async def get_user_growth_data(self) -> ChartData:
        """Get user growth time series data."""
        labels = [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(29, -1, -1)]
        return ChartData(
            title="User Growth (Last 30 Days)",
            type="line",
            data=TimeSeriesData(labels=labels, values=self.user_growth),
        )

    async def get_request_volume_data(self) -> ChartData:
        """Get request volume time series data."""
        labels = [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(29, -1, -1)]
        return ChartData(
            title="Request Volume (Last 30 Days)",
            type="bar",
            data=TimeSeriesData(labels=labels, values=self.request_counts),
        )

    async def get_response_time_distribution(self) -> ChartData:
        """Get response time distribution data."""
        # Create histogram buckets
        hist, bins = np.histogram(self.response_times, bins=10)
        labels = [f"{int(bins[i])}-{int(bins[i+1])}ms" for i in range(len(bins)-1)]
        return ChartData(
            title="Response Time Distribution",
            type="bar",
            data=TimeSeriesData(labels=labels, values=hist.tolist()),
        )

    async def get_summary_stats(self) -> dict:
        """Get summary statistics."""
        return {
            "total_prototypes": 12,
            "active_prototypes": 10,
            "total_tests": 150,
            "test_pass_rate": 94.5,
            "avg_build_time": "2.5min",
            "deployment_status": "healthy",
        }


# Global service instance
analytics_service = AnalyticsService()
