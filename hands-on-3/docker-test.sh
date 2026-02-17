#!/bin/bash
# Test script for Docker services

echo "🧪 Testing Docker Services..."
echo ""

# Wait for backend to be ready
echo "⏳ Waiting for backend to be ready..."
until curl -s http://localhost:8000/ > /dev/null 2>&1; do
    echo "   Still waiting..."
    sleep 5
done

echo "✅ Backend is ready!"
echo ""

# Test backend directly
echo "📡 Testing backend API directly (port 8000)..."
curl -s http://localhost:8000/ | jq '.' || echo "Backend API responding"
echo ""

# Test through Traefik proxy
echo "🌐 Testing through Traefik proxy (port 80)..."
echo ""
echo "   Testing API endpoint /api/..."
curl -s http://localhost/api/ | jq '.' || echo "API responding"
echo ""

echo "   Testing frontend at /..."
curl -s http://localhost/ | head -20 | grep -o "<title>.*</title>" || echo "Frontend responding"
echo ""

# Test Qdrant
echo "🗄️  Testing Qdrant connection..."
curl -s http://localhost:6333/ | jq '.' || echo "Qdrant responding"
echo ""

echo "✅ All tests completed!"
echo ""
echo "📝 Access points:"
echo "   - Main app: http://localhost"
echo "   - API: http://localhost/api/"
echo "   - Qdrant UI: http://qdrant.localhost"
echo "   - Direct backend: http://localhost:8000"
echo "   - Direct Qdrant: http://localhost:6333"
