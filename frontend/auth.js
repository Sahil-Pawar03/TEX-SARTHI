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

function setSession(token, email) {
  localStorage.setItem("auth_token", token);
  localStorage.setItem("auth_email", email || "");
}

function clearSession() {
  localStorage.removeItem("auth_token");
  localStorage.removeItem("auth_email");
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
      var email = getUserEmail();
      welcomeSpan.textContent = email ? "Welcome, " + email : "Welcome";
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
    // 1) If running with http(s) and backend reachable → POST /api/login
    // 2) If file:// or network fails → demo fallback that stores a fake token
    var shouldUseDemo = location.protocol === "file:";

    if (!shouldUseDemo) {
      var res = await fetch("/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email, password: password })
      });
      if (!res.ok) {
        throw new Error("Invalid credentials");
      }
      var data = await res.json().catch(function(){ return {}; });
      var token = data.token || "demo-token";
      setSession(token, email);
      location.href = "index.html";
      return;
    }

    // Demo fallback when no backend
    setSession("demo-token", email);
    location.href = "index.html";
  } catch (err) {
    // Network/CORS failure → demo fallback
    setSession("demo-token", email);
    location.href = "index.html";
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
    var shouldUseDemo = location.protocol === "file:";
    if (!shouldUseDemo) {
      var res = await fetch("/api/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: name, email: email, password: password })
      });
      if (!res.ok) {
        throw new Error("Signup failed");
      }
      var data = await res.json().catch(function(){ return {}; });
      var token = data.token || "demo-token";
      setSession(token, email);
      location.href = "index.html";
      return;
    }

    setSession("demo-token", email);
    location.href = "index.html";
  } catch (err) {
    // Network/CORS failure → demo fallback
    setSession("demo-token", email);
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


