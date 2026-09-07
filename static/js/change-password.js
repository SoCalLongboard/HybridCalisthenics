import { api, ApiError } from "./api.js";

export function initChangePasswordScreen({ onChanged }) {
  const screen = document.getElementById("force-change-screen");
  const form = document.getElementById("force-change-form");
  const currentInput = document.getElementById("force-change-current");
  const newInput = document.getElementById("force-change-new");
  const errorText = document.getElementById("force-change-error");
  const submitBtn = document.getElementById("force-change-submit");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    errorText.textContent = "";
    submitBtn.disabled = true;

    try {
      await api.changePassword(currentInput.value, newInput.value);
      form.reset();
      screen.classList.add("hidden");
      onChanged();
    } catch (err) {
      errorText.textContent = err instanceof ApiError ? err.detail : "Something went wrong. Please try again.";
    } finally {
      submitBtn.disabled = false;
    }
  });

  return {
    show: () => screen.classList.remove("hidden"),
    hide: () => screen.classList.add("hidden"),
  };
}
