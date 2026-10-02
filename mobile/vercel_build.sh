#!/bin/bash
set -e

echo "=== Current working directory: $(pwd) ==="
echo "=== Installing Flutter SDK on Vercel ==="

# Download Flutter to home directory if not present
if [ ! -d "$HOME/flutter" ]; then
  git clone https://github.com/flutter/flutter.git -b stable --depth 1 "$HOME/flutter"
fi

export PATH="$PATH:$HOME/flutter/bin"
flutter --version

echo "=== Navigating to mobile directory if needed ==="
if [ -d "mobile" ]; then
  cd mobile
fi

flutter pub get
flutter build web --release --dart-define=API_URL=${API_URL:-"http://127.0.0.1:8000"}

echo "=== Copying vercel.json into web build ==="
cp vercel.json build/web/ 2>/dev/null || true

echo "=== Build Complete ==="
