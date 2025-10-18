#!/bin/bash
# start_redis.sh
# Easy Redis startup script for Management Team project
#
# PURPOSE:
# Starts Redis server with appropriate configuration for persistent agent memory.
# Handles different platforms (macOS, Linux, Docker) automatically.
#
# USAGE:
#   ./scripts/start_redis.sh
#
# WHAT IT DOES:
# 1. Detects platform (macOS/Linux/Docker)
# 2. Checks if Redis is already running
# 3. Starts Redis using the appropriate method
# 4. Verifies connection
# 5. Shows connection info

set -e  # Exit on error

echo "=================================================="
echo "🔴 Redis Startup - Management Team Memory System"
echo "=================================================="
echo ""

# Check if Redis is already running
if lsof -Pi :6379 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "✅ Redis is already running on port 6379"
    echo ""
    redis-cli ping 2>/dev/null && echo "✅ Connection test: PONG" || echo "⚠️  Warning: Redis not responding"
    echo ""
    echo "Connection info:"
    echo "  Host: localhost"
    echo "  Port: 6379"
    echo ""
    echo "To stop Redis:"
    echo "  macOS:  brew services stop redis"
    echo "  Linux:  sudo systemctl stop redis"
    echo "  Docker: docker stop redis-management"
    exit 0
fi

echo "📋 Detecting platform..."

# Detect platform and start Redis
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo "Platform: macOS"
    echo ""

    if command -v brew &> /dev/null; then
        echo "🍺 Homebrew detected"

        if brew list redis &> /dev/null; then
            echo "✅ Redis already installed"
        else
            echo "📦 Installing Redis via Homebrew..."
            brew install redis
        fi

        echo "🚀 Starting Redis..."
        brew services start redis

    else
        echo "❌ Homebrew not found!"
        echo ""
        echo "Install Homebrew first:"
        echo "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        echo ""
        echo "Or install Redis manually:"
        echo "  https://redis.io/docs/getting-started/installation/install-redis-on-mac-os/"
        exit 1
    fi

elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    echo "Platform: Linux"
    echo ""

    if command -v systemctl &> /dev/null; then
        echo "🐧 systemd detected"

        if systemctl list-units --full -all | grep -Fq "redis.service" || \
           systemctl list-units --full -all | grep -Fq "redis-server.service"; then
            echo "✅ Redis service found"

            echo "🚀 Starting Redis..."
            sudo systemctl start redis-server 2>/dev/null || sudo systemctl start redis 2>/dev/null

        else
            echo "📦 Redis not installed. Installing..."

            if command -v apt-get &> /dev/null; then
                # Debian/Ubuntu
                sudo apt-get update
                sudo apt-get install -y redis-server
                sudo systemctl start redis-server

            elif command -v yum &> /dev/null; then
                # CentOS/RHEL
                sudo yum install -y redis
                sudo systemctl start redis

            else
                echo "❌ Package manager not recognized"
                echo "Install Redis manually: https://redis.io/docs/getting-started/installation/install-redis-on-linux/"
                exit 1
            fi
        fi
    else
        echo "⚠️  systemd not found, trying Docker..."
        if command -v docker &> /dev/null; then
            echo "🐳 Starting Redis in Docker..."
            docker run -d --name redis-management -p 6379:6379 redis
        else
            echo "❌ Cannot start Redis (no systemd or Docker)"
            exit 1
        fi
    fi

else
    # Other platforms - try Docker
    echo "Platform: $OSTYPE"
    echo "🐳 Trying Docker..."

    if command -v docker &> /dev/null; then
        echo "🚀 Starting Redis in Docker..."
        docker run -d --name redis-management -p 6379:6379 redis
    else
        echo "❌ Docker not found"
        echo ""
        echo "Install Docker: https://docs.docker.com/get-docker/"
        echo "Or install Redis manually: https://redis.io/docs/getting-started/installation/"
        exit 1
    fi
fi

# Wait for Redis to start
echo ""
echo "⏳ Waiting for Redis to start..."
for i in {1..10}; do
    if redis-cli ping 2>/dev/null | grep -q "PONG"; then
        echo "✅ Redis started successfully!"
        break
    fi
    sleep 1
    if [ $i -eq 10 ]; then
        echo "❌ Redis failed to start"
        echo "Check logs:"
        echo "  macOS:  brew services info redis"
        echo "  Linux:  sudo journalctl -u redis"
        echo "  Docker: docker logs redis-management"
        exit 1
    fi
done

# Show connection info
echo ""
echo "=================================================="
echo "✅ Redis Running"
echo "=================================================="
echo "📍 Host: localhost"
echo "📍 Port: 6379"
echo "📍 Status: READY"
echo ""
echo "Test connection:"
echo "  redis-cli ping"
echo ""
echo "View stored data:"
echo "  redis-cli KEYS 'project:*'"
echo ""
echo "To stop Redis:"
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "  brew services stop redis"
elif command -v systemctl &> /dev/null; then
    echo "  sudo systemctl stop redis-server"
else
    echo "  docker stop redis-management"
fi
echo ""
echo "=================================================="
echo "🧠 Ready for persistent agent memory!"
echo "=================================================="
