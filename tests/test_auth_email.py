def test_signup_and_login(client):
    # signup
    resp = client.post("/auth/signup", data={
        "email": "user@example.com",
        "password": "password123",
        "password2": "password123",
    }, follow_redirects=False)
    assert resp.status_code in (302, 303)

    # logout
    resp = client.post("/auth/logout", follow_redirects=False)
    assert resp.status_code in (302, 303)

    # login
    resp = client.post("/auth/login", data={
        "email": "user@example.com",
        "password": "password123",
        "remember": "y",
    }, follow_redirects=False)
    assert resp.status_code in (302, 303)
