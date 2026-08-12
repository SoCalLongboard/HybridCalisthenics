import { api, ApiError } from "./api.js";

export function initAuthScreen({ onAuthenticated }) {
  const screen = document.getElementById("auth-screen");
  const title = document.getElementById("auth-title");
  const form = document.getElementById("auth-form");
  const usernameInput = document.getElementById("auth-username");
  const passwordInput = document.getElementById("auth-password");
  const errorText = document.getElementById("auth-error");
  const submitBtn = document.getElementById("auth-submit");
  const switchLink = document.getElementById("auth-switch-link");
  const switchText = document.getElementById("auth-switch-text");

  let mode = "login";

  function render() {
    if (mode === "login") {
      title.textContent = "Log in";
      submitBtn.textContent = "Log in";
      switchText.textContent = "Need an account?";
      switchLink.textContent = "Register";
    } else {
      title.textContent = "Register";
      submitBtn.textContent = "Create account";
      switchText.textContent = "Already have an account?";
      switchLink.textContent = "Log in";
    }
    errorText.textContent = "";
  }

  switchLink.addEventListener("click", (e) => {
    e.preventDefault();
    mode = mode === "login" ? "register" : "login";
    render();
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    errorText.textContent = "";
    submitBtn.disabled = true;

    const username = usernameInput.value.trim();
    const password = passwordInput.value;

    try {
      if (mode === "register") {
        await api.register(username, password);
        await api.login(username, password);
      } else {
        await api.login(username, password);
      }
      form.reset();
      screen.classList.add("hidden");
      onAuthenticated();
    } catch (err) {
      if (err instanceof ApiError) {
        errorText.textContent = err.detail;
      } else {
        errorText.textContent = "Something went wrong. Please try again.";
      }
    } finally {
      submitBtn.disabled = false;
    }
  });

  render();

  return {
    show: () => screen.classList.remove("hidden"),
    hide: () => screen.classList.add("hidden"),
  };
}
