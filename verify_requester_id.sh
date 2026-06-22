#!/bin/bash

# Login as an intern user
LOGIN_RESPONSE=$(curl -s -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"intern@sps.com","password":"Test1234!"}')

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
INTERN_ID=$(echo $LOGIN_RESPONSE | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)

echo "Intern user ID: $INTERN_ID"
echo "Token: $TOKEN"
echo ""

# Get a specific ticket and check the requester_id
echo "Ticket detail response:"
curl -s -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8000/tickets/f51f350b-02b4-49f8-91c7-1cb81364181f | grep -o '"requester_id":[^,}]*'
