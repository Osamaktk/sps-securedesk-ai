@echo off
echo === TEST 1: Classify - Production server down ===
curl.exe -s -X POST http://127.0.0.1:8001/api/classify -H "Content-Type: application/json" -d "{\"subject\":\"Production server is down\",\"description\":\"All VMs unreachable since 9am\"}"
echo.
echo === TEST 2: Classify - Admin access ===
curl.exe -s -X POST http://127.0.0.1:8001/api/classify -H "Content-Type: application/json" -d "{\"subject\":\"Need admin access to production database\",\"description\":\"Requesting root access for deployment\"}"
echo.
echo === TEST 3: Classify - Phishing ===
curl.exe -s -X POST http://127.0.0.1:8001/api/classify -H "Content-Type: application/json" -d "{\"subject\":\"Phishing email received\",\"description\":\"Got a suspicious email asking for my password\"}"
echo.
echo === TEST 4: Classify - Simple question ===
curl.exe -s -X POST http://127.0.0.1:8001/api/classify -H "Content-Type: application/json" -d "{\"subject\":\"How do I update my profile picture\",\"description\":\"Just a simple question\"}"
echo.
echo === TEST 5: Summarise ===
curl.exe -s -X POST http://127.0.0.1:8001/api/summarise -H "Content-Type: application/json" -d "{\"subject\":\"VPN issue\",\"description\":\"Cannot connect to VPN since morning\",\"timeline\":[]}"
echo.
echo === TEST 6: Chat ===
curl.exe -s -X POST http://127.0.0.1:8001/api/chat -H "Content-Type: application/json" -d "{\"session_id\":\"test456\",\"message\":\"How do I connect to VPN?\",\"user_id\":\"test\"}"
echo.
pause