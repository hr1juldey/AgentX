# R012: Analytics Dashboard (Level 6)

Real-time analytics dashboard with data aggregation and visualization.

## Features

- **Real-time Metrics**: Live dashboard with key performance indicators
- **Data Aggregation**: Time series aggregation and statistics
- **Interactive Charts**: Line charts, bar charts, and histograms
- **Auto-refresh**: Automatic data refresh every 30 seconds
- **Responsive Design**: Mobile-friendly dashboard layout

## Tech Stack

- **Backend**: FastAPI + NumPy + Pandas
- **Frontend**: Next.js + shadcn/ui + Recharts
- **Port**: 8012

## Quick Start

### Backend
```bash
cd backend
pip install -e .
python main.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Metrics Tracked

- Total Users
- Active Sessions
- Total Requests
- Average Response Time
- Success Rate
- CPU Usage
- Memory Usage

## Notes

- Uses mock data for demonstration
- Recharts for visualization
- Auto-refreshes every 30 seconds
