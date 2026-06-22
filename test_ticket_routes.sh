#!/bin/bash

# Login as an intern user
LOGIN_RESPONSE=$(curl -s -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"intern@sps.com","password":"Test1234!"}')

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

# Test ticket detail route with proper authorization
TICKET_ID="f51f350b-02b4-49f8-91c7-1cb81364181f"
echo "Testing GET /tickets/$TICKET_ID with auth token..."
curl -v -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8000/tickets/$TICKET_ID 2>&1 | grep -E "< HTTP|detail|Insufficient"
