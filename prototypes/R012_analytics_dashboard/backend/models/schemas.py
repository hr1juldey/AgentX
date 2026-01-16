"""
Request and response schemas for Analytics Dashboard API with enhanced Swagger documentation.

This module provides schemas for dashboard metrics and chart data.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class MetricData(BaseModel):
    """Schema for a single metric data point.

    Represents one measurement at a specific time.
    """

    timestamp: datetime = Field(
        ...,
        description="When the metric was recorded",
        examples=["2024-01-15T10:00:00Z"]
    )
    value: float = Field(
        ...,
        description="Metric value",
        examples=[42.5, 100.0]
    )
    label: Optional[str] = Field(
        None,
        description="Optional label for the data point",
        examples=["Server 1", "Region A"]
    )


class TimeSeriesData(BaseModel):
    """Schema for time-series data.

    Used for charts showing trends over time.
    """

    labels: List[str] = Field(
        ...,
        description="Time labels (x-axis)",
        examples=[["10:00", "11:00", "12:00"], ["Mon", "Tue", "Wed"]]
    )
    values: List[float] = Field(
        ...,
        description="Data values (y-axis)",
        examples=[[10.5, 15.2, 12.8]]
    )

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "labels": ["10:00", "11:00", "12:00", "13:00"],
                "values": [10.5, 15.2, 12.8, 18.3]
            }]
        }
    }


class DashboardMetrics(BaseModel):
    """Schema for dashboard metrics summary.

    Key performance indicators for the dashboard.
    """

    total_users: int = Field(
        ...,
        description="Total registered users",
        examples=[1000, 5000]
    )
    active_sessions: int = Field(
        ...,
        description="Currently active user sessions",
        examples=[50, 200]
    )
    total_requests: int = Field(
        ...,
        description="Total API requests processed",
        examples=[100000, 500000]
    )
    avg_response_time: float = Field(
        ...,
        description="Average API response time in milliseconds",
        examples=[125.5, 250.0]
    )
    success_rate: float = Field(
        ...,
        description="Success rate percentage (0-100)",
        examples=[99.5],
        ge=0.0,
        le=100.0
    )
    cpu_usage: float = Field(
        ...,
        description="CPU usage percentage (0-100)",
        examples=[45.2],
        ge=0.0,
        le=100.0
    )
    memory_usage: float = Field(
        ...,
        description="Memory usage percentage (0-100)",
        examples=[62.8],
        ge=0.0,
        le=100.0
    )

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "total_users": 1000,
                "active_sessions": 50,
                "total_requests": 100000,
                "avg_response_time": 125.5,
                "success_rate": 99.5,
                "cpu_usage": 45.2,
                "memory_usage": 62.8
            }]
        }
    }


class ChartData(BaseModel):
    """Schema for chart data.

    Complete data for rendering a visualization.
    """

    title: str = Field(
        ...,
        description="Chart title",
        examples=["User Growth", "Response Time Trends"]
    )
    type: str = Field(
        ...,
        description="Chart type (line, bar, pie, etc.)",
        examples=["line", "bar", "pie", "area"]
    )
    data: TimeSeriesData = Field(
        ...,
        description="Time-series data for the chart"
    )


class MetricsQuery(BaseModel):
    """Schema for metrics query.

    Request metrics for a specific time range.
    """

    start_date: datetime = Field(
        ...,
        description="Start of time range (inclusive)",
        examples=["2024-01-01T00:00:00Z"]
    )
    end_date: datetime = Field(
        ...,
        description="End of time range (inclusive)",
        examples=["2024-01-31T23:59:59Z"]
    )
    granularity: str = Field(
        default="hour",
        description="Data granularity (minute, hour, day, week, month)",
        examples=["minute", "hour", "day", "week", "month"]
    )

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "start_date": "2024-01-01T00:00:00Z",
                "end_date": "2024-01-31T23:59:59Z",
                "granularity": "day"
            }]
        }
    }


class ErrorResponse(BaseModel):
    """Schema for error response."""

    error: str = Field(
        ...,
        description="Error type",
        examples=["ValidationError", "QueryError"]
    )
    message: str = Field(
        ...,
        description="Error message",
        examples=["Invalid date range", "Query too broad"]
    )
    detail: Optional[str] = Field(
        None,
        description="Additional technical details"
    )
