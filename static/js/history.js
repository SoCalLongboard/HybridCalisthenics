import { api, ApiError } from "./api.js";

export async function openHistoryPanel({ family, onChanged }) {
  const overlay = document.createElement("div");
  overlay.className = "modal-overlay";
  overlay.innerHTML = `
    <div class="modal">
      <h2>${family} history</h2>
      <div id="history-list">Loading…</div>
      <div class="modal-actions">
        <button type="button" id="history-close">Close</button>
      </div>
    </div>
  `;
  document.body.appendChild(overlay);

  const list = overlay.querySelector("#history-list");
  overlay.querySelector("#history-close").addEventListener("click", () => overlay.remove());
  overlay.addEventListener("click", (e) => {
    if (e.target === overlay) overlay.remove();
  });

  async function render() {
    const sessions = await api.listSessions(family);
    if (sessions.length === 0) {
      list.innerHTML = "<p>No sessions logged yet.</p>";
      return;
    }

    list.innerHTML = "";
    for (const s of sessions) {
      const item = document.createElement("div");
      item.className = "history-item";
      item.innerHTML = `
        <div>
          <div><strong>${s.exercise_name}</strong> — ${s.date}</div>
          <div class="meta">
            sets: ${s.sets.join(", ")} · form: ${s.form_good ? "good" : "broken"}
            ${s.notes ? " · " + s.notes : ""}
          </div>
        </div>
        <div class="row-actions">
          <button type="button" class="edit-btn">Edit</button>
          <button type="button" class="danger delete-btn">Delete</button>
        </div>
      `;

      item.querySelector(".delete-btn").addEventListener("click", async () => {
        if (!confirm("Delete this session?")) return;
        await api.deleteSession(s.id);
        await render();
        onChanged();
      });

      item.querySelector(".edit-btn").addEventListener("click", () => {
        openEditRow(item, s, render, onChanged);
      });

      list.appendChild(item);
    }
  }

  function openEditRow(item, s, refresh, onChanged) {
    item.innerHTML = `
      <div style="width:100%">
        <input type="date" value="${s.date}" class="edit-date">
        <input type="text" value="${s.sets.join(",")}" class="edit-sets" placeholder="comma-separated reps">
        <div class="form-toggle">
          <label><input type="radio" name="edit-form-good" value="good" ${s.form_good ? "checked" : ""}> Good form</label>
          <label><input type="radio" name="edit-form-good" value="broken" ${!s.form_good ? "checked" : ""}> Broken</label>
        </div>
        <textarea class="edit-notes" rows="2">${s.notes || ""}</textarea>
        <div class="error-text edit-error"></div>
        <div class="modal-actions">
          <button type="button" class="edit-cancel">Cancel</button>
          <button type="button" class="primary edit-save">Save</button>
        </div>
      </div>
    `;

    item.querySelector(".edit-cancel").addEventListener("click", refresh);

    item.querySelector(".edit-save").addEventListener("click", async () => {
      const errorEl = item.querySelector(".edit-error");
      const date = item.querySelector(".edit-date").value;
      const setsRaw = item.querySelector(".edit-sets").value;
      const sets = setsRaw
        .split(",")
        .map((v) => parseInt(v.trim(), 10));

      if (sets.length === 0 || sets.some((v) => Number.isNaN(v) || v < 0)) {
        errorEl.textContent = "Enter comma-separated non-negative numbers.";
        return;
      }

      const formGood = item.querySelector('input[name="edit-form-good"]:checked').value === "good";
      const notes = item.querySelector(".edit-notes").value.trim() || null;

      try {
        await api.updateSession(s.id, { date, sets, form_good: formGood, notes });
        await refresh();
        onChanged();
      } catch (err) {
        errorEl.textContent = err instanceof ApiError ? err.detail : "Failed to save.";
      }
    });
  }

  await render();
}
