import { api } from "./api.js";
import { initAuthScreen } from "./auth.js";
import { initDashboard } from "./dashboard.js";

const appMain = document.getElementById("app-main");
const appHeader = document.getElementById("app-header");
const logoutBtn = document.getElementById("logout-btn");
const currentUserLabel = document.getElementById("current-user");

const dashboard = initDashboard();

async function showApp(user) {
  document.getElementById("auth-screen").classList.add("hidden");
  appHeader.classList.remove("hidden");
  appMain.classList.remove("hidden");
  currentUserLabel.textContent = user.username;
  await dashboard.refresh();
}

const authScreen = initAuthScreen({
  onAuthenticated: async () => {
    const user = await api.me();
    await showApp(user);
  },
});

logoutBtn.addEventListener("click", async () => {
  await api.logout();
  appHeader.classList.add("hidden");
  appMain.classList.add("hidden");
  authScreen.show();
});

(async function boot() {
  try {
    const user = await api.me();
    await showApp(user);
  } catch {
    authScreen.show();
  }
})();
