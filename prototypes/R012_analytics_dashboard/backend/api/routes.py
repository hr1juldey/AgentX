"""API routes."""
from fastapi import APIRouter
from models.schemas import DashboardMetrics, ChartData
from services.service import analytics_service

router = APIRouter(tags=["analytics"])


@router.get("/metrics", response_model=DashboardMetrics)
async def get_metrics():
    """Get dashboard metrics."""
    return await analytics_service.get_dashboard_metrics()


@router.get("/charts/user-growth", response_model=ChartData)
async def get_user_growth():
    """Get user growth chart data."""
    return await analytics_service.get_user_growth_data()


@router.get("/charts/request-volume", response_model=ChartData)
async def get_request_volume():
    """Get request volume chart data."""
    return await analytics_service.get_request_volume_data()


@router.get("/charts/response-time", response_model=ChartData)
async def get_response_time():
    """Get response time distribution chart data."""
    return await analytics_service.get_response_time_distribution()


@router.get("/summary")
async def get_summary():
    """Get summary statistics."""
    return await analytics_service.get_summary_stats()


@router.get("/health")
async def health():
    return {"status": "healthy"}
