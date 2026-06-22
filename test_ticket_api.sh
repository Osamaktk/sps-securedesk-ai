#!/bin/bash

# Login as an intern user
LOGIN_RESPONSE=$(curl -s -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"intern@sps.com","password":"Test1234!"}')

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
echo "Token: $TOKEN"

# Get the list of tickets
echo -e "\n\nGetting tickets list..."
curl -s -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8000/tickets | head -100
