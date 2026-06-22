#!/bin/bash

# Login
LOGIN_RESPONSE=$(curl -s -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"intern@sps.com","password":"Test1234!"}')

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

# Get a ticket and extract key fields
echo "Checking API response structure for ticket detail..."
RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8000/tickets/f51f350b-02b4-49f8-91c7-1cb81364181f)

echo "Full response:"
echo $RESPONSE
