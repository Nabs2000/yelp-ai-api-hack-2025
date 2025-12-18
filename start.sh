#!/bin/bash

# Moving Assistant - Quick Start Script

echo "🚀 Starting Moving Assistant..."
echo ""

# Check if .env file exists
if [ ! -f "./backend/.env" ]; then
    echo "⚠️  Backend .env file not found!"
    echo "📝 Creating from .env.example..."
    cp ./backend/.env.example ./backend/.env
    echo "✅ Created backend/.env"
    echo "⚠️  Please edit backend/.env with your API keys before continuing!"
    echo ""
    exit 1
fi

# Check if frontend .env.local exists
if [ ! -f "./frontend/.env.local" ]; then
    echo "📝 Creating frontend/.env.local..."
    cp ./frontend/.env.example ./frontend/.env.local
    echo "✅ Created frontend/.env.local"
fi

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed!"
    echo "Please install Docker from https://www.docker.com/get-started"
    exit 1
fi

# Check for Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed!"
    echo "Please install Docker Compose"
    exit 1
fi

echo "🐳 Building and starting containers..."
echo ""

# Start containers
docker-compose up --build -d

echo ""
echo "✅ Moving Assistant is starting!"
echo ""
echo "📍 Services:"
echo "   Frontend: http://localhost"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📋 Useful commands:"
echo "   View logs:    docker-compose logs -f"
echo "   Stop:         docker-compose down"
echo "   Restart:      docker-compose restart"
echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are up
if curl -f http://localhost:8000/docs &> /dev/null; then
    echo "✅ Backend is ready!"
else
    echo "⚠️  Backend might still be starting..."
fi

if curl -f http://localhost &> /dev/null; then
    echo "✅ Frontend is ready!"
else
    echo "⚠️  Frontend might still be starting..."
fi

echo ""
echo "🎉 Done! Open http://localhost in your browser"
