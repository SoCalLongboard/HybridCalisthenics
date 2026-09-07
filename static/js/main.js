import { api } from "./api.js";
import { initAuthScreen } from "./auth.js";
import { initDashboard } from "./dashboard.js";
import { initChangePasswordScreen } from "./change-password.js";
import { openAdminPanel } from "./admin.js";

const appMain = document.getElementById("app-main");
const appHeader = document.getElementById("app-header");
const logoutBtn = document.getElementById("logout-btn");
const adminBtn = document.getElementById("admin-btn");
const currentUserLabel = document.getElementById("current-user");

const dashboard = initDashboard();

async function showApp(user) {
  document.getElementById("auth-screen").classList.add("hidden");
  changePasswordScreen.hide();
  appHeader.classList.remove("hidden");
  appMain.classList.remove("hidden");
  currentUserLabel.textContent = user.username;
  adminBtn.classList.toggle("hidden", !user.is_admin);
  adminBtn.onclick = () => openAdminPanel({ currentUserId: user.id });
  await dashboard.refresh();
}

async function routeAfterLogin() {
  const user = await api.me();
  if (user.must_change_password) {
    document.getElementById("auth-screen").classList.add("hidden");
    changePasswordScreen.show();
    return;
  }
  await showApp(user);
}

const authScreen = initAuthScreen({
  onAuthenticated: routeAfterLogin,
});

const changePasswordScreen = initChangePasswordScreen({
  onChanged: routeAfterLogin,
});

logoutBtn.addEventListener("click", async () => {
  await api.logout();
  appHeader.classList.add("hidden");
  appMain.classList.add("hidden");
  authScreen.show();
});

(async function boot() {
  try {
    await routeAfterLogin();
  } catch {
    authScreen.show();
  }
})();
