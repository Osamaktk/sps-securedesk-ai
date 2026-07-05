import sys
print("Testing imports...")
try:
    from ai.main import app
    print("ai.main: OK")
except Exception as e:
    print(f"ai.main FAIL: {e}")
    sys.exit(1)

print("All imports OK")
