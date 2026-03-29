#!/bin/bash
echo "Starting PortfolioIQ dev environment..."
cd backend && uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
cd ../frontend && npm run dev &
FRONTEND_PID=$!
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"
wait
