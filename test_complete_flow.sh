#!/bin/bash
set -e

# Step 1: Login
echo "=== Step 1: Login ==="
LOGIN_RESPONSE=$(curl -s -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"intern@sps.com","password":"Test1234!"}')

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
echo "Token obtained: ${TOKEN:0:50}..."

# Step 2: Get the list of tickets as the frontend would
echo -e "\n=== Step 2: Get list of tickets ==="
LIST_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8000/tickets)
echo "Got ticket list (first 100 chars): ${LIST_RESPONSE:0:100}..."

# Step 3: Extract first ticket ID
TICKET_ID=$(echo $LIST_RESPONSE | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
echo "First ticket ID: $TICKET_ID"

# Step 4: Try to get ticket detail
echo -e "\n=== Step 4: Get ticket detail ==="
DETAIL_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8000/tickets/$TICKET_ID)

echo "Response status:"
curl -s -w "\nHTTP Status: %{http_code}\n" -o /dev/null -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8000/tickets/$TICKET_ID

echo "Response (first 150 chars): ${DETAIL_RESPONSE:0:150}..."
echo ""
echo "=== Complete Response ==="
echo $DETAIL_RESPONSE | head -c 300
echo "..."
