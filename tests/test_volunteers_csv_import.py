import io

def signup(client, email, password="password123"):
    return client.post("/auth/signup", data={
        "email": email,
        "password": password,
        "password2": password,
    }, follow_redirects=False)

def test_csv_import_admin(client):
    signup(client, "admin@example.com")

    csv_content = (
        "full_name,email,phone,city,availability,notes\n"
        "Ada Lovelace,[email protected],600,Madrid,Fines de semana,OK\n"
    ).encode("utf-8")

    data = {
        "file": (io.BytesIO(csv_content), "volunteers.csv"),
    }

    resp = client.post("/volunteers/import", data=data, content_type="multipart/form-data", follow_redirects=False)
    assert resp.status_code in (302, 303)

    resp = client.get("/volunteers")
    assert resp.status_code == 200
    assert b"Ada Lovelace" in resp.data
