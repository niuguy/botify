#!/bin/bash

# Exit on error
set -e

echo "🚀 Starting deployment process..."

# Update system packages
echo "📦 Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker if not installed
if ! command -v docker &> /dev/null; then
    echo "🐳 Installing Docker..."
    sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
    sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
    sudo apt-get update
    sudo apt-get install -y docker-ce
    sudo systemctl start docker
    sudo systemctl enable docker
fi

# Install Docker Compose if not installed
if ! command -v docker-compose &> /dev/null; then
    echo "🐳 Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Pull latest changes if git repository exists
if [ -d .git ]; then
    echo "📥 Pulling latest changes..."
    git pull
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️ .env file not found! Please create one from .env.example"
    exit 1
fi

# Build and start containers
echo "🏗️ Building and starting containers..."
docker-compose down
docker-compose build
docker-compose up -d

# Run migrations
echo "🔄 Running database migrations..."
docker-compose exec -T web python manage.py migrate

# Collect static files
echo "📚 Collecting static files..."
docker-compose exec -T web python manage.py collectstatic --noinput

echo "✅ Deployment completed successfully!"