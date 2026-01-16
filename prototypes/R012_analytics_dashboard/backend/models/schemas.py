"""Request and response schemas."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class MetricData(BaseModel):
    """Metric data point."""
    timestamp: datetime
    value: float
    label: Optional[str] = None


class TimeSeriesData(BaseModel):
    """Time series data."""
    labels: List[str]
    values: List[float]


class DashboardMetrics(BaseModel):
    """Dashboard metrics."""
    total_users: int
    active_sessions: int
    total_requests: int
    avg_response_time: float
    success_rate: float
    cpu_usage: float
    memory_usage: float


class ChartData(BaseModel):
    """Chart data for visualization."""
    title: str
    type: str  # line, bar, pie, etc.
    data: TimeSeriesData
