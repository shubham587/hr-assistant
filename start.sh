#!/bin/bash

echo "🚀 Starting HR Assistant..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ and try again."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ and try again."
    exit 1
fi

# Create data directories
echo "📁 Creating data directories..."
mkdir -p data/documents data/chunks data/chroma_db

# Check if requirements are installed
if [ ! -f "backend/requirements.txt" ]; then
    echo "❌ backend/requirements.txt not found. Please run from the project root directory."
    exit 1
fi

echo "🔧 Installing Python dependencies..."
pip install -r backend/requirements.txt

# Check if frontend dependencies are installed
if [ ! -d "frontend/node_modules" ]; then
    echo "🔧 Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Make sure LM Studio is running on localhost:1234"
echo "2. Load the Mistral-7B-Instruct model in LM Studio"
echo "3. Run the backend: python backend/app.py"
echo "4. Run the frontend: cd frontend && npm run dev"
echo ""
echo "💡 The application will be available at:"
echo "   - Backend: http://localhost:5001"
echo "   - Frontend: http://localhost:3000"
echo ""
echo "🎉 Happy HR assisting!" 