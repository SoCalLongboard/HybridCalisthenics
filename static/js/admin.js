import { api, ApiError } from "./api.js";

export async function openAdminPanel({ currentUserId }) {
  const overlay = document.createElement("div");
  overlay.className = "modal-overlay";
  overlay.innerHTML = `
    <div class="modal modal-wide">
      <h2>User management</h2>
      <div class="error-text" id="admin-error"></div>
      <div id="admin-users-list">Loading…</div>
      <div class="modal-actions">
        <button type="button" id="admin-close">Close</button>
      </div>
    </div>
  `;
  document.body.appendChild(overlay);

  const list = overlay.querySelector("#admin-users-list");
  const errorEl = overlay.querySelector("#admin-error");
  overlay.querySelector("#admin-close").addEventListener("click", () => overlay.remove());
  overlay.addEventListener("click", (e) => {
    if (e.target === overlay) overlay.remove();
  });

  async function run(action) {
    errorEl.textContent = "";
    try {
      await action();
      await render();
    } catch (err) {
      errorEl.textContent = err instanceof ApiError ? err.detail : "Something went wrong.";
    }
  }

  async function render() {
    const users = await api.adminListUsers();

    list.innerHTML = "";
    for (const u of users) {
      const row = document.createElement("div");
      row.className = "history-item";
      const isSelf = u.id === currentUserId;
      row.innerHTML = `
        <div>
          <div><strong>${u.username}</strong> ${u.is_admin ? '<span class="badge ready">admin</span>' : ""} ${!u.is_active ? '<span class="badge">disabled</span>' : ""}</div>
          <div class="meta">
            joined ${u.created_at.slice(0, 10)} · last login ${u.last_login_at ? u.last_login_at.slice(0, 10) : "never"}
            ${u.must_change_password ? " · password reset pending" : ""}
          </div>
        </div>
        <div class="row-actions"></div>
      `;

      const actions = row.querySelector(".row-actions");

      if (u.is_active) {
        const disableBtn = document.createElement("button");
        disableBtn.type = "button";
        disableBtn.textContent = "Disable";
        disableBtn.disabled = isSelf;
        disableBtn.addEventListener("click", () => run(() => api.adminDisableUser(u.id)));
        actions.appendChild(disableBtn);
      } else {
        const enableBtn = document.createElement("button");
        enableBtn.type = "button";
        enableBtn.textContent = "Enable";
        enableBtn.addEventListener("click", () => run(() => api.adminEnableUser(u.id)));
        actions.appendChild(enableBtn);
      }

      const roleBtn = document.createElement("button");
      roleBtn.type = "button";
      roleBtn.textContent = u.is_admin ? "Demote" : "Promote";
      roleBtn.disabled = u.is_admin && isSelf;
      roleBtn.addEventListener("click", () =>
        run(() => (u.is_admin ? api.adminDemoteUser(u.id) : api.adminPromoteUser(u.id)))
      );
      actions.appendChild(roleBtn);

      const resetBtn = document.createElement("button");
      resetBtn.type = "button";
      resetBtn.textContent = "Reset password";
      resetBtn.addEventListener("click", () =>
        run(async () => {
          const result = await api.adminResetPassword(u.id);
          alert(`Temporary password for ${u.username}:\n\n${result.temporary_password}\n\nShare this with them now — it will not be shown again.`);
        })
      );
      actions.appendChild(resetBtn);

      const deleteBtn = document.createElement("button");
      deleteBtn.type = "button";
      deleteBtn.className = "danger";
      deleteBtn.textContent = "Delete";
      deleteBtn.disabled = isSelf;
      deleteBtn.addEventListener("click", () => {
        if (!confirm(`Permanently delete ${u.username} and all their data?`)) return;
        run(() => api.adminDeleteUser(u.id));
      });
      actions.appendChild(deleteBtn);

      list.appendChild(row);
    }
  }

  await render();
}
