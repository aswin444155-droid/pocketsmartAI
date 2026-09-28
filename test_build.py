import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import io, base64
from PIL import Image
from fastapi.testclient import TestClient
import app

client = TestClient(app.app)
print("=== POCKETSMART AI BUILD VERIFICATION ===")

# 1. Startup
r = client.get("/startup")
assert r.status_code == 200
print("[PASS] GET /startup")

# 2. Pages
pages = [
    "/", "/login", "/register", "/dashboard",
    "/history", "/home-planner", "/party-planner", "/jewelry-planner"
]
for p in pages:
    r = client.get(p)
    assert r.status_code == 200, f"Failed {p}: {r.status_code}"
    print(f"[PASS] GET {p}")

# 3. Static files
r = client.get("/static/styles.css")
assert r.status_code == 200
r = client.get("/static/css/styles.css")
assert r.status_code == 200
print("[PASS] Static files served")

# 4. Auth
r = client.post("/register", json={
    "username": "aswin",
    "password": "secretpassword",
    "full_name": "Aswin Santhosh",
    "email": "aswin@example.com"
})
assert r.status_code == 200
print("[PASS] User registration: aswin")

r = client.post("/token", data={"username": "aswin", "password": "secretpassword"})
assert r.status_code == 200
token = r.json()["access_token"]
print("[PASS] User authentication & JWT token generation")

# 5. Home Generation
print("Testing Home Planner with Gemini...")
r = client.post("/generate-home", json={
    "budget": 45000,
    "rooms": "1 BHK",
    "style": "Contemporary",
    "room_types": ["Living Room"],
    "platforms": ["Amazon", "Flipkart", "IKEA"],
    "preferences": "Compact and durable"
})
assert r.status_code == 200
data_home = r.json()
assert "recommendations" in data_home, f"Home failed: {data_home}"
print("[PASS] POST /generate-home succeeded")

# 6. Party Generation
print("Testing Party Generation with Gemini...")
r = client.post("/generate-party", json={
    "budget": 30000,
    "event_type": "Birthday Party",
    "guests": "15",
    "location": "Home",
    "food_preference": "Vegetarian",
    "includes": ["Catering", "Decoration", "Cake"],
    "notes": "Simple evening gathering"
})
assert r.status_code == 200
data_party = r.json()
assert "recommendations" in data_party, f"Party failed: {data_party}"
print("[PASS] POST /generate-party succeeded")

# 7. Jewelry Generation with outfit image
print("Testing Jewelry Generation with Outfit Image...")
img = Image.new("RGB", (64, 64), color="navy")
buf = io.BytesIO()
img.save(buf, format="JPEG")
img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

r = client.post("/generate-jewelry", json={
    "budget": 15000,
    "occasion": "Wedding Reception",
    "jewelry_types": ["Earrings", "Necklace"],
    "metal_preference": "Gold",
    "platforms": ["Amazon", "Flipkart"],
    "style_preferences": "Traditional",
    "image": img_b64
})
assert r.status_code == 200
data_jwl = r.json()
assert "recommendations" in data_jwl, f"Jewelry failed: {data_jwl}"
print("[PASS] POST /generate-jewelry (multimodal) succeeded")

# 8. Check History
r = client.get("/api/history")
assert r.status_code == 200
hist = r.json()
total_entries = hist.get("total", 0)
print(f"[PASS] GET /api/history - Total saved: {total_entries}")
assert total_entries >= 3

print("\n=== ALL BUILD VERIFICATION TESTS PASSED SUCCESSFULLY! ===")
