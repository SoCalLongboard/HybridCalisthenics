const BASE = "/api";

class ApiError extends Error {
  constructor(status, detail) {
    super(detail || `Request failed with status ${status}`);
    this.status = status;
    this.detail = detail;
  }
}

async function request(path, options = {}) {
  const resp = await fetch(BASE + path, {
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (resp.status === 204) {
    return null;
  }

  let body = null;
  const text = await resp.text();
  if (text) {
    try {
      body = JSON.parse(text);
    } catch {
      body = null;
    }
  }

  if (!resp.ok) {
    const detail = body && body.detail ? body.detail : resp.statusText;
    throw new ApiError(resp.status, detail);
  }

  return body;
}

export const api = {
  register: (username, password) =>
    request("/auth/register", { method: "POST", body: JSON.stringify({ username, password }) }),
  login: (username, password) =>
    request("/auth/login", { method: "POST", body: JSON.stringify({ username, password }) }),
  logout: () => request("/auth/logout", { method: "POST" }),
  me: () => request("/auth/me"),
  changePassword: (currentPassword, newPassword) =>
    request("/auth/change-password", {
      method: "POST",
      body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
    }),
  adminListUsers: () => request("/admin/users"),
  adminDisableUser: (id) => request(`/admin/users/${id}/disable`, { method: "POST" }),
  adminEnableUser: (id) => request(`/admin/users/${id}/enable`, { method: "POST" }),
  adminDeleteUser: (id) => request(`/admin/users/${id}`, { method: "DELETE" }),
  adminPromoteUser: (id) => request(`/admin/users/${id}/promote`, { method: "POST" }),
  adminDemoteUser: (id) => request(`/admin/users/${id}/demote`, { method: "POST" }),
  adminResetPassword: (id) => request(`/admin/users/${id}/reset-password`, { method: "POST" }),
  catalog: () => request("/catalog"),
  progress: () => request("/progress"),
  advance: (family) => request(`/progress/${encodeURIComponent(family)}/advance`, { method: "POST" }),
  listSessions: (family) => request(`/sessions?family=${encodeURIComponent(family)}`),
  createSession: (payload) => request("/sessions", { method: "POST", body: JSON.stringify(payload) }),
  updateSession: (id, payload) =>
    request(`/sessions/${id}`, { method: "PATCH", body: JSON.stringify(payload) }),
  deleteSession: (id) => request(`/sessions/${id}`, { method: "DELETE" }),
};

export { ApiError };
