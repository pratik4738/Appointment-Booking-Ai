#!/bin/bash
# start_backend.sh - Start the FastAPI backend

echo "🚀 Starting Calendar Agent Backend..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Load environment variables
if [ -f ".env" ]; then
    export $(cat .env | xargs)
fi

# Check for required credentials
if [ ! -f "credentials.json" ] && [ ! -f "token.pickle" ]; then
    echo "⚠️  Google Calendar credentials not found!"
    echo "Please run: python google_calendar_setup.py"
    echo "Or the app will run in demo mode with mock data."
fi

# Start the backend
echo "Starting FastAPI server on http://localhost:8000"
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload

---

#!/bin/bash
# start_frontend.sh - Start the Streamlit frontend

echo "🎨 Starting Calendar Agent Frontend..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Start Streamlit app
echo "Starting Streamlit app on http://localhost:8501"
streamlit run streamlit_app.py --server.address 0.0.0.0 --server.port 8501

---

#!/bin/bash
# setup_project.sh - Complete project setup script

echo "📅 Setting up AI Calendar Agent Project"
echo "======================================"

# Create project directory structure
mkdir -p logs
mkdir -p data
mkdir -p tests

# Create virtual environment
echo "1. Creating virtual environment..."
python -m venv venv
source venv/bin/activate

# Install dependencies
echo "2. Installing Python dependencies..."
pip install -r requirements.txt

# Setup environment file
if [ ! -f ".env" ]; then
    echo "3. Creating environment configuration..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your API keys and configuration"
else
    echo "3. Environment file already exists"
fi

# Setup Google Calendar
echo "4. Setting up Google Calendar integration..."
if [ ! -f "credentials.json" ]; then
    echo "⚠️  Please add your credentials.json file from Google Cloud Console"
    echo "   Then run: python google_calendar_setup.py"
else
    python google_calendar_setup.py
fi

# Create startup scripts
echo "5. Making scripts executable..."
chmod +x start_backend.sh
chmod +x start_frontend.sh

# Final instructions
echo ""
echo "✅ Setup complete! Next steps:"
echo ""
echo "1. Edit .env file with your OpenAI API key"
echo "2. Add credentials.json from Google Cloud Console"
echo "3. Run Google Calendar setup: python google_calendar_setup.py"
echo "4. Start backend: ./start_backend.sh"
echo "5. Start frontend: ./start_frontend.sh"
echo ""
echo "🌐 Frontend will be available at: http://localhost:8501"
echo "🔧 Backend API docs at: http://localhost:8000/docs"

---

@echo off
REM start_windows.bat - Windows startup script

echo Starting AI Calendar Agent...

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Start both backend and frontend
echo Starting services...
start "Calendar Backend" cmd /k "python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload"
timeout /t 5 /nobreak > nul
start "Calendar Frontend" cmd /k "streamlit run streamlit_app.py --server.address 0.0.0.0 --server.port 8501"

echo.
echo Services started!
echo Frontend: http://localhost:8501
echo Backend API: http://localhost:8000/docs
echo.
pause