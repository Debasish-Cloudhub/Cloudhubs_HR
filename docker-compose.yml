#!/bin/bash
# CloudHub HR Portal - Quick Start Script

set -e

echo "🚀 CloudHub HR Portal - Starting up..."
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null 2>&1; then
    echo "❌ Docker Compose is not installed."
    exit 1
fi

echo "✅ Docker found"
echo ""
echo "📦 Building and starting containers..."
echo ""

# Start containers
docker compose -f docker/docker-compose.yml up --build -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Wait for backend health check
MAX_RETRIES=30
COUNTER=0
while [ $COUNTER -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend is ready!"
        break
    fi
    COUNTER=$((COUNTER+1))
    echo "   Waiting... ($COUNTER/$MAX_RETRIES)"
    sleep 3
done

echo ""
echo "🎉 CloudHub HR Portal is running!"
echo ""
echo "═══════════════════════════════════════"
echo "  Frontend:  http://localhost:3000"
echo "  API:       http://localhost:8000"
echo "  API Docs:  http://localhost:8000/docs"
echo "═══════════════════════════════════════"
echo ""
echo "Demo Credentials:"
echo "  Admin:    admin@cloudhub.in    / Admin@123"
echo "  Employee: john.doe@cloudhub.in / Employee@123"
echo "  Manager:  manager@cloudhub.in  / Manager@123"
echo ""
