#!/usr/bin/env bash

set -e

BASE_URL="http://localhost:5000"
DATASET="test_dataset.csv"
TARGET="income"
MODEL="RandomForest"

echo "=========================================="
echo " MLOps API Endpoint Tests"
echo "=========================================="


# --------------------------------------------------
# 1. Health check
# --------------------------------------------------

echo ""
echo "[1/8] Health check..."

curl -sSf \
    "$BASE_URL/api/health"

echo ""
echo "✓ Health check passed"


# --------------------------------------------------
# 2. Upload dataset
# --------------------------------------------------

echo ""
echo "[2/8] Uploading dataset..."

curl -sSf \
    -X POST \
    "$BASE_URL/api/datasets/upload" \
    -F "file=@server/tests/fixtures/$DATASET"

echo ""
echo "✓ Dataset upload passed"


# --------------------------------------------------
# 3. Get dataset information
# --------------------------------------------------

echo ""
echo "[3/8] Getting dataset information..."

curl -sSf \
    "$BASE_URL/api/datasets/$DATASET"

echo ""
echo "✓ Dataset information passed"


# --------------------------------------------------
# 4. Generate profile
# --------------------------------------------------

echo ""
echo "[4/8] Generating profile..."

curl -sSf \
    -X POST \
    "$BASE_URL/api/profile" \
    -H "Content-Type: application/json" \
    -d "{
        \"dataset_id\": \"$DATASET\"
    }"

echo ""
echo "✓ Profiling passed"


# --------------------------------------------------
# 5. Get recommendation
# --------------------------------------------------

echo ""
echo "[5/8] Predicting best model..."

curl -sSf \
    -X POST \
    "$BASE_URL/api/recommendation" \
    -H "Content-Type: application/json" \
    -d "{
        \"dataset_id\": \"$DATASET\",
        \"target_column\": \"$TARGET\"
    }"

echo ""
echo "✓ Recommendation passed"


# --------------------------------------------------
# 6. Verify model
# --------------------------------------------------

echo ""
echo "[6/8] Running 15% vs 85% verification..."

curl -sSf \
    -X POST \
    "$BASE_URL/api/verify" \
    -H "Content-Type: application/json" \
    -d "{
        \"dataset_id\": \"$DATASET\",
        \"target_column\": \"$TARGET\",
        \"model\": \"$MODEL\"
    }"

echo ""
echo "✓ Verification passed"


# --------------------------------------------------
# 7. Optimize model
# --------------------------------------------------

echo ""
echo "[7/8] Running optimization..."

curl -sSf \
    -X POST \
    "$BASE_URL/api/optimize" \
    -H "Content-Type: application/json" \
    -d "{
        \"dataset_id\": \"$DATASET\",
        \"target_column\": \"$TARGET\",
        \"model\": \"$MODEL\"
    }"

echo ""
echo "✓ Optimization passed"


# --------------------------------------------------
# 8. Download model
# --------------------------------------------------

echo ""
echo "[8/8] Downloading best model..."

curl -sSf \
    "$BASE_URL/api/models/best/download" \
    -o /tmp/best_model.pkl

if [ -s /tmp/best_model.pkl ]; then
    echo "✓ Model download passed"
    ls -lh /tmp/best_model.pkl
else
    echo "✗ Model download failed"
    exit 1
fi


echo ""
echo "=========================================="
echo " ✓ ALL API TESTS PASSED"
echo "=========================================="