#!/bin/bash

if [ -z "$1" ]; then
  echo "❌ Error: Version is required!"
  echo "Usage: $0 <version>"
  echo "Example: $0 0.1.0"
  exit 1
fi

VERSION=$1

BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
VCS_REF=$(git rev-parse --short HEAD)

echo "🔨 Building FlightKit Docker Image"
echo "📌 Version: $VERSION"
echo "📅 Build Date: $BUILD_DATE"
echo "🔗 VCS Ref: $VCS_REF"
echo ""

docker buildx create --name multiplatform --use 2>/dev/null || docker buildx use multiplatform
docker buildx inspect --bootstrap

docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --build-arg BUILD_DATE=$BUILD_DATE \
  --build-arg VCS_REF=$VCS_REF \
  --provenance=false \
  --sbom=false \
  -t ghcr.io/sysp0/flightkit:$VERSION \
  -t ghcr.io/sysp0/flightkit:latest \
  --push \
  .

if [ $? -eq 0 ]; then
  echo ""
  echo "✅ Multi-platform image built and pushed successfully!"
  echo "📦 Platforms: linux/amd64, linux/arm64"
  echo "🏷️  Tags: $VERSION, latest"
  echo ""
  
  echo "🔍 Inspecting manifest:"
  docker buildx imagetools inspect ghcr.io/sysp0/flightkit:$VERSION
else
  echo ""
  echo "❌ Build failed!"
  exit 1
fi