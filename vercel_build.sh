#!/bin/bash
set -e

echo "=== Installing Flutter SDK on Vercel ==="
if [ ! -d "flutter" ]; then
  git clone https://github.com/flutter/flutter.git -b stable --depth 1 flutter
fi

export PATH="$PATH:$(pwd)/flutter/bin"
flutter --version

echo "=== Building Flutter Web ==="
cd mobile
flutter pub get
flutter build web --release --dart-define=API_URL=${API_URL:-"http://127.0.0.1:8000"}

echo "=== Copying vercel.json into web build ==="
cp vercel.json build/web/ 2>/dev/null || true

echo "=== Build Complete ==="
