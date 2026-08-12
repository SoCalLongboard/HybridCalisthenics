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
