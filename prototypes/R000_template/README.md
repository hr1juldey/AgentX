# AGENTX Prototype - Master Template

This is the master full-stack template for AGENTX prototypes. Each prototype follows this structure with a FastAPI backend and Next.js frontend using shadcn/ui components.

## 📁 Project Structure

```
prototypes/R000_template/
├── backend/                    # FastAPI Backend
│   ├── config/                # Configuration settings
│   ├── models/                # Pydantic schemas
│   ├── services/              # Business logic
│   ├── api/                   # FastAPI routes
│   ├── tests/                 # Pytest tests
│   ├── scripts/               # Run/Test/Lint scripts
│   └── data/                  # SQLite database
├── frontend/                   # Next.js Frontend
│   ├── app/                   # Next.js App Router
│   ├── components/ui/         # shadcn/ui components
│   ├── lib/                   # Utilities
│   └── scripts/               # Dev/Build/Lint scripts
├── README.md                  # This file
├── PRD.md                     # Product Requirements Document
└── docker-compose.yml         # Docker Compose (optional)
```

## 🚀 Quick Start

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .

# Run development server
./scripts/run.sh
# Or: python main.py
```

Backend runs on `http://localhost:8001`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
./scripts/dev.sh
# Or: npm run dev
```

Frontend runs on `http://localhost:3000`

## 🧪 Testing

### Backend Tests

```bash
cd backend
./scripts/test.sh
# Or: pytest tests/ --cov
```

### Frontend Linting

```bash
cd frontend
./scripts/lint.sh
# Or: npm run lint
```

## 📝 Using This Template

To create a new prototype:

1. Copy this directory to `prototypes/RXXX_new_prototype/`
2. Update `backend/.env` with your prototype name
3. Update `frontend/.env.local` with your prototype name
4. Customize `backend/api/routes.py` for your API endpoints
5. Customize `frontend/app/page.tsx` for your UI
6. Update `PRD.md` with your prototype's requirements

## 🏗️ Template Features

### Backend (FastAPI)
- ✅ Pydantic Settings for configuration
- ✅ CORS middleware configured
- ✅ Example CRUD endpoints
- ✅ Pytest tests with coverage
- ✅ SQLite database support
- ✅ Service layer pattern

### Frontend (Next.js 15)
- ✅ App Router
- ✅ TypeScript
- ✅ Tailwind CSS
- ✅ shadcn/ui components (Button, Input, Card)
- ✅ Client-side data fetching
- ✅ Health check indicator

## 🔧 Configuration

### Backend Environment (.env)

```bash
APP_NAME=Your Prototype Name
APP_VERSION=0.1.0
DEBUG=true
HOST=0.0.0.0
PORT=8001
DATABASE_URL=sqlite:///./data/database.db
FRONTEND_URL=http://localhost:3000
```

### Frontend Environment (.env.local)

```bash
NEXT_PUBLIC_API_URL=http://localhost:8001
NEXT_PUBLIC_APP_NAME=Your Prototype Name
NODE_ENV=development
```

## 📚 Documentation

- **FastAPI**: https://fastapi.tiangolo.com/
- **Next.js**: https://nextjs.org/docs
- **shadcn/ui**: https://ui.shadcn.com/
- **Tailwind CSS**: https://tailwindcss.com/docs

## 🐛 Troubleshooting

### Backend
- **Port already in use**: Change `PORT` in `.env`
- **Import errors**: Ensure virtual environment is activated
- **Database errors**: Delete `data/database.db` and restart

### Frontend
- **Module not found**: Run `npm install`
- **Port already in use**: Next.js will automatically use next available port
- **API connection fails**: Check backend is running and `NEXT_PUBLIC_API_URL` is correct

## 📝 License

Part of the AGENTX project.
