#!/bin/bash

# Login as an intern user
LOGIN_RESPONSE=$(curl -s -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"intern@sps.com","password":"Test1234!"}')

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
INTERN_ID="3b272c81-f1ca-4eb4-9a40-7bbcf2c52990"

echo "Checking tickets for permission issues..."
echo "Intern ID: $INTERN_ID"
echo ""

# Test a few ticket IDs
TICKETS=("f7809a6c-ad47-4a37-86aa-43a5cb25b7ed" "4b16456f-492f-43fc-aee3-f001cc88df66")

for TICKET_ID in "${TICKETS[@]}"; do
  echo "Ticket $TICKET_ID:"
  curl -s -H "Authorization: Bearer $TOKEN" \
    http://127.0.0.1:8000/tickets/$TICKET_ID 2>&1 | head -1 | grep -o '"requester_id":[^,}]*'
  echo ""
done
