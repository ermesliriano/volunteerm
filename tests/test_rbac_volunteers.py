import io

def signup(client, email, password="password123"):
    return client.post("/auth/signup", data={
        "email": email,
        "password": password,
        "password2": password,
    }, follow_redirects=False)

def logout(client):
    return client.post("/auth/logout", follow_redirects=False)

def test_reader_cannot_create_volunteer(client):
    signup(client, "reader@example.com")
    resp = client.get("/volunteers/new")
    assert resp.status_code == 403

def test_admin_can_create_volunteer(client):
    # email está en ADMIN_EMAILS -> admin
    signup(client, "admin@example.com")
    resp = client.get("/volunteers/new")
    assert resp.status_code == 200

    resp = client.post("/volunteers/new", data={
        "full_name": "Ada Lovelace",
        "email": "[email protected]",
        "phone": "600",
        "city": "Madrid",
        "availability": "Fines de semana",
        "notes": "Test",
    }, follow_redirects=False)
    assert resp.status_code in (302, 303)

    resp = client.get("/volunteers")
    assert resp.status_code == 200
    assert b"Ada Lovelace" in resp.data
