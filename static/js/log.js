import { api, ApiError } from "./api.js";

const WEEKDAYS = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"];

function todayIso() {
  const d = new Date();
  const offset = d.getTimezoneOffset();
  const local = new Date(d.getTime() - offset * 60 * 1000);
  return local.toISOString().slice(0, 10);
}

export function openLogPanel({ family, exerciseName, onSaved }) {
  const overlay = document.createElement("div");
  overlay.className = "modal-overlay";
  overlay.innerHTML = `
    <div class="modal">
      <h2>Log ${family} — ${exerciseName}</h2>
      <label>Date
        <input type="date" id="log-date" value="${todayIso()}">
      </label>
      <div id="set-rows"></div>
      <button type="button" id="add-set">+ Add set</button>
      <div class="form-toggle">
        <label><input type="radio" name="form-good" value="good" checked> Good form</label>
        <label><input type="radio" name="form-good" value="broken"> Form broke down</label>
      </div>
      <label>Notes
        <textarea id="log-notes" rows="2"></textarea>
      </label>
      <div class="error-text" id="log-error"></div>
      <div class="caution-banner hidden" id="log-caution"></div>
      <div class="modal-actions">
        <button type="button" id="log-cancel">Cancel</button>
        <button type="button" class="primary" id="log-save">Save</button>
      </div>
    </div>
  `;
  document.body.appendChild(overlay);

  const setRows = overlay.querySelector("#set-rows");
  const addSetBtn = overlay.querySelector("#add-set");
  const errorText = overlay.querySelector("#log-error");
  const cautionBanner = overlay.querySelector("#log-caution");
  const saveBtn = overlay.querySelector("#log-save");
  const cancelBtn = overlay.querySelector("#log-cancel");

  function addSetRow(value = "") {
    const row = document.createElement("div");
    row.className = "set-row";
    row.innerHTML = `
      <input type="number" min="0" step="1" placeholder="reps" value="${value}">
      <button type="button" class="remove-set">×</button>
    `;
    row.querySelector(".remove-set").addEventListener("click", () => {
      row.remove();
    });
    setRows.appendChild(row);
  }

  addSetRow();
  addSetRow();
  addSetBtn.addEventListener("click", () => addSetRow());

  function close() {
    overlay.remove();
  }

  cancelBtn.addEventListener("click", close);
  overlay.addEventListener("click", (e) => {
    if (e.target === overlay) close();
  });

  saveBtn.addEventListener("click", async () => {
    errorText.textContent = "";
    const inputs = [...setRows.querySelectorAll("input")];
    const sets = inputs.map((i) => parseInt(i.value, 10));

    if (sets.length === 0 || sets.some((v) => Number.isNaN(v) || v < 0)) {
      errorText.textContent = "Enter a non-negative number of reps for every set.";
      return;
    }

    const date = overlay.querySelector("#log-date").value;
    const formGood = overlay.querySelector('input[name="form-good"]:checked').value === "good";
    const notes = overlay.querySelector("#log-notes").value.trim() || null;

    saveBtn.disabled = true;
    try {
      const result = await api.createSession({ family, date, sets, form_good: formGood, notes });
      if (result.caution) {
        cautionBanner.textContent = result.caution_reason;
        cautionBanner.classList.remove("hidden");
        saveBtn.textContent = "Close";
        saveBtn.disabled = false;
        cancelBtn.classList.add("hidden");
        addSetBtn.disabled = true;
        saveBtn.onclick = () => {
          close();
          onSaved();
        };
      } else {
        close();
        onSaved();
      }
    } catch (err) {
      errorText.textContent = err instanceof ApiError ? err.detail : "Failed to save session.";
      saveBtn.disabled = false;
    }
  });
}

export function scheduleForToday(schedule) {
  const day = WEEKDAYS[new Date().getDay()];
  return { day, families: schedule[day] || [] };
}
