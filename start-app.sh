#!/bin/bash

echo "Starting EduMentor AI Application..."
echo "=================================="

# Check if dependencies are installed
echo "Checking dependencies..."

# Check if Python dependencies are installed
python -c "import sentence_transformers" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Python dependencies not found. Installing..."
    pip install -r requirements.txt
    echo "Running comprehensive dependency fix script..."
    ./fix-all-dependencies.sh
fi

# Check if Node dependencies are installed
if [ ! -d "frontend-react/node_modules" ]; then
    echo "Node.js dependencies not found. Installing..."
    cd frontend-react
    npm install
    cd ..
fi

echo "Dependencies checked!"
echo ""

# Start the backend server
echo "Starting backend API server..."
python api.py &
BACKEND_PID=$!
echo "Backend server started with PID: $BACKEND_PID"
echo "Backend API available at: http://localhost:8000"
echo ""

# Wait a moment for the backend to start
sleep 3

# Start the frontend development server
echo "Starting frontend development server..."
cd frontend-react
npm run dev &
FRONTEND_PID=$!
echo "Frontend server started with PID: $FRONTEND_PID"
echo "Frontend application available at: http://localhost:3000"
cd ..

echo ""
echo "=================================="
echo "EduMentor AI is now running!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"
echo "=================================="

# Function to cleanup processes
cleanup() {
    echo ""
    echo "Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "Servers stopped. Goodbye!"
    exit 0
}

# Set up trap to catch Ctrl+C
trap cleanup SIGINT

# Wait for processes
wait