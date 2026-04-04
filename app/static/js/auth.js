(function () {
  function meta(name) {
    const el = document.querySelector(`meta[name="${name}"]`);
    return el ? el.getAttribute("content") : "";
  }

  function showGoogleError(msg) {
    const box = document.getElementById("google-error");
    if (!box) return;
    box.textContent = msg;
    box.style.display = "block";
  }

  async function postGoogleCredential(credential, csrfToken) {
    const res = await fetch("/auth/google", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken
      },
      body: JSON.stringify({ credential })
    });

    let data = null;
    try { data = await res.json(); } catch (e) { /* ignore */ }

    if (!res.ok) {
      const err = (data && data.error) ? data.error : "No se pudo iniciar sesión con Google.";
      throw new Error(err);
    }

    return data;
  }

  window.handleCredentialResponse = async function (response) {
    try {
      const csrfToken = meta("csrf-token");
      const credential = response && response.credential ? response.credential : "";
      if (!credential) throw new Error("Respuesta de Google sin credential.");

      const data = await postGoogleCredential(credential, csrfToken);
      if (data && data.ok) {
        window.location.href = data.redirect || "/dashboard";
      } else {
        throw new Error("Respuesta inesperada del servidor.");
      }
    } catch (err) {
      showGoogleError(err.message || "Error desconocido.");
    }
  };

  window.addEventListener("load", function () {
    const clientId = meta("google-client-id");
    if (!clientId) return;

    if (!window.google || !google.accounts || !google.accounts.id) {
      showGoogleError("Google Identity Services no está disponible.");
      return;
    }

    google.accounts.id.initialize({
      client_id: clientId,
      callback: window.handleCredentialResponse
    });

    const btn = document.getElementById("google-btn");
    if (btn) {
      google.accounts.id.renderButton(btn, {
        type: "standard",
        theme: "outline",
        size: "large",
        text: "signin_with",
        shape: "rectangular",
        logo_alignment: "left"
      });
    }
  });
})();
