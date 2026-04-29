#!/usr/bin/env bash
set -euo pipefail

echo "=== AstroNumeric Audit ==="
echo ""

echo "1) Backend smoke (Railway prod)"
bash ./check_backend.sh
echo ""

echo "2) Regenerate Xcode project (XcodeGen)"
(cd AstroNumeric-iOS && xcodegen generate)
echo ""

echo "3) iOS build + tests (iPhone 17 Pro simulator)"
xcodebuild test \
  -project AstroNumeric-iOS/AstroNumeric.xcodeproj \
  -scheme AstroNumeric \
  -destination 'platform=iOS Simulator,name=iPhone 17 Pro' \
  test

echo ""
echo "✅ Audit complete"

