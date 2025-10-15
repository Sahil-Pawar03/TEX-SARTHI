// TexSaarthi front-end auth utilities
// Purpose:
// - Minimal client-side session management for a static demo (no real backend required)
// - When a backend exists, login/signup endpoints are used; otherwise we fall back to demo mode
// - Session = token + email persisted in localStorage; presence of token = logged in

function getAuthToken() {
  return localStorage.getItem("auth_token");
}

function getUserEmail() {
  return localStorage.getItem("auth_email");
}

function getUserName() {
  return localStorage.getItem("auth_name");
}

// Local demo user store (for static/offline usage)
function getStoredUsers() {
  try {
    var raw = localStorage.getItem("auth_users");
    return raw ? JSON.parse(raw) : {};
  } catch (e) {
    return {};
  }
}

function saveStoredUsers(usersByEmail) {
  try {
    localStorage.setItem("auth_users", JSON.stringify(usersByEmail || {}));
  } catch (e) {
    // ignore
  }
}

function upsertLocalUser(name, email, password) {
  var users = getStoredUsers();
  var key = (email || "").toLowerCase();
  if (!key) return;
  users[key] = { name: name || (key.split("@")[0] || "User"), email: key, password: password || "" };
  saveStoredUsers(users);
}

function findLocalUser(email) {
  var users = getStoredUsers();
  var key = (email || "").toLowerCase();
  return users[key] || null;
}

function setSession(token, email, name) {
  localStorage.setItem("auth_token", token);
  localStorage.setItem("auth_email", email || "");
  if (name) {
    localStorage.setItem("auth_name", name);
  }
}

function clearSession() {
  localStorage.removeItem("auth_token");
  localStorage.removeItem("auth_email");
  localStorage.removeItem("auth_name");
}

function isLoggedIn() {
  return !!getAuthToken();
}

function updateTopbarUI() {
  var logoutBtn = document.getElementById("logout-btn");
  var welcomeSpan = document.getElementById("welcome-user");
  if (!logoutBtn && !welcomeSpan) return;

  if (isLoggedIn()) {
    if (logoutBtn) logoutBtn.classList.remove("hidden");
    if (welcomeSpan) {
      var name = getUserName();
      if (!name) {
        var email = getUserEmail();
        name = email && email.includes("@") ? email.split("@")[0] : "User";
      }
      welcomeSpan.textContent = name ? "Welcome, " + name : "Welcome";
      welcomeSpan.classList.remove("hidden");
    }
  } else {
    if (logoutBtn) logoutBtn.classList.add("hidden");
    if (welcomeSpan) welcomeSpan.classList.add("hidden");
  }
}

function protectPage() {
  var isLoginPage = location.pathname.endsWith("login.html");
  var isSignupPage = location.pathname.endsWith("signup.html");
  if (!isLoginPage && !isSignupPage && !isLoggedIn()) {
    location.href = "login.html";
  }
  if ((isLoginPage || isSignupPage) && isLoggedIn()) {
    location.href = "index.html";
  }
}

function attachLogoutHandler() {
  var logoutBtn = document.getElementById("logout-btn");
  if (!logoutBtn) return;
  logoutBtn.addEventListener("click", function (e) {
    e.preventDefault();
    clearSession();
    location.href = "login.html";
  });
}

function setupMenuToggle() {
  var toggle = document.getElementById("menu-toggle");
  var dropdown = document.getElementById("menu-dropdown");
  if (!toggle || !dropdown) return;

  function closeMenu() {
    dropdown.classList.add("hidden");
    toggle.setAttribute("aria-expanded", "false");
  }
  function openMenu() {
    dropdown.classList.remove("hidden");
    toggle.setAttribute("aria-expanded", "true");
  }

  toggle.addEventListener("click", function () {
    var isHidden = dropdown.classList.contains("hidden");
    if (isHidden) openMenu(); else closeMenu();
  });

  document.addEventListener("click", function (e) {
    if (!dropdown.contains(e.target) && !toggle.contains(e.target)) {
      closeMenu();
    }
  });
}

async function handleLoginSubmit(e) {
  if (e && e.preventDefault) e.preventDefault();
  var emailInput = document.getElementById("email-input");
  var passInput = document.getElementById("password-input");
  var errorBox = document.getElementById("login-error");
  if (errorBox) errorBox.classList.add("hidden");

  var email = emailInput ? emailInput.value.trim() : "";
  var password = passInput ? passInput.value : "";

  if (!email || !password) {
    showLoginError("Please enter email and password.");
    return;
  }

  try {
    // Strategy:
    // 1) Try backend when on http(s)
    // 2) On failure or when offline (file://), validate against locally stored users
    var shouldUseDemo = false; // we have a backend at http://localhost:3000

    if (!shouldUseDemo) {
      var res = await fetch("http://localhost:3000/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email, password: password })
      });
      if (res.ok) {
        var data = await res.json().catch(function(){ return {}; });
        var token = data.token || "demo-token";
        var name = data.name || (email && email.split("@")[0]) || "";
        // Optionally sync to local store for future offline use
        upsertLocalUser(name, email, password);
        setSession(token, email, name);
        location.href = "index.html";
        return;
      }
      // If backend rejects, attempt local validation next
    }

    // Local validation path (offline/demo or backend failure)
    var localUser = findLocalUser(email);
    if (!localUser) {
      showLoginError("Account not found. Please sign up first.");
      return;
    }
    if ((localUser.password || "") !== password) {
      showLoginError("Invalid credentials");
      return;
    }
    setSession("demo-token", localUser.email, localUser.name);
    location.href = "index.html";
  } catch (err) {
    // Network/CORS failure → attempt local validation
    var localUserCatch = findLocalUser(email);
    if (localUserCatch && (localUserCatch.password || "") === password) {
      setSession("demo-token", localUserCatch.email, localUserCatch.name);
      location.href = "index.html";
      return;
    }
    showLoginError("Login failed. Please check your credentials and try again.");
  }
}

function showLoginError(message) {
  var errorBox = document.getElementById("login-error");
  if (!errorBox) return;
  errorBox.textContent = message;
  errorBox.classList.remove("hidden");
}

async function handleSignupSubmit(e) {
  if (e && e.preventDefault) e.preventDefault();
  var nameInput = document.getElementById("name-input");
  var emailInput = document.getElementById("signup-email-input");
  var passInput = document.getElementById("signup-password-input");
  var errorBox = document.getElementById("signup-error");
  if (errorBox) errorBox.classList.add("hidden");

  var name = nameInput ? nameInput.value.trim() : "";
  var email = emailInput ? emailInput.value.trim() : "";
  var password = passInput ? passInput.value : "";

  if (!name || !email || !password) {
    showSignupError("Please fill in name, email and password.");
    return;
  }

  try {
    // Same strategy as login: real API first, otherwise demo fallback
    var shouldUseDemo = false; // we have a backend at http://localhost:3000
    if (!shouldUseDemo) {
      var res = await fetch("http://localhost:3000/api/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: name, email: email, password: password })
      });
      if (!res.ok) {
        throw new Error("Signup failed");
      }
      var data = await res.json().catch(function(){ return {}; });
      var token = data.token || "demo-token";
      var nameFromApi = data.name || name || (email && email.split("@")[0]) || "";
      // Sync to local store for offline login later
      upsertLocalUser(nameFromApi, email, password);
      setSession(token, email, nameFromApi);
      location.href = "index.html";
      return;
    }

    // Demo/offline signup → persist locally
    upsertLocalUser(name, email, password);
    setSession("demo-token", email, (email && email.split("@")[0]));
    location.href = "index.html";
  } catch (err) {
    // Network/CORS failure → store locally and proceed
    upsertLocalUser(name, email, password);
    setSession("demo-token", email, (email && email.split("@")[0]));
    location.href = "index.html";
  }
}

function showSignupError(message) {
  var errorBox = document.getElementById("signup-error");
  if (!errorBox) return;
  errorBox.textContent = message;
  errorBox.classList.remove("hidden");
}

function initAuthPage() {
  protectPage();
  updateTopbarUI();
  attachLogoutHandler();
  setupMenuToggle();

  var loginForm = document.getElementById("login-form");
  if (loginForm) {
    loginForm.addEventListener("submit", handleLoginSubmit);
  }
  var signupForm = document.getElementById("signup-form");
  if (signupForm) {
    signupForm.addEventListener("submit", handleSignupSubmit);
  }
}

document.addEventListener("DOMContentLoaded", initAuthPage);


