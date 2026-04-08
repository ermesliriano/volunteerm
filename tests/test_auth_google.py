import app.auth.google as google_mod

def test_google_login(monkeypatch, client):
    def fake_verify(token, client_id):
        return {
            "sub": "google-sub-123",
            "email": "guser@example.com",
            "email_verified": True,
            "iss": "accounts.google.com",
        }

    monkeypatch.setattr(google_mod, "verify_google_id_token", fake_verify)

    resp = client.post("/auth/google", json={"credential": "fake-jwt"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
