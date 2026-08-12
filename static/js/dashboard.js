import { api } from "./api.js";
import { openLogPanel, scheduleForToday } from "./log.js";
import { openHistoryPanel } from "./history.js";

export function initDashboard() {
  const grid = document.getElementById("family-grid");
  const scheduleStrip = document.getElementById("schedule-strip");
  let catalog = null;

  async function refresh() {
    const [catalogData, progressData] = await Promise.all([
      catalog ? Promise.resolve(catalog) : api.catalog(),
      api.progress(),
    ]);
    catalog = catalogData;

    const { families: todaysFamilies } = scheduleForToday(catalog.schedule);
    renderSchedule(catalog.schedule);
    renderGrid(progressData.families, todaysFamilies);
  }

  function renderSchedule(schedule) {
    const { day, families } = scheduleForToday(schedule);
    const label = day.charAt(0).toUpperCase() + day.slice(1);
    scheduleStrip.textContent =
      families.length > 0 ? `Today (${label}): ${families.join(" + ")}` : `Today (${label}): rest day`;
  }

  function renderGrid(families, todaysFamilies) {
    grid.innerHTML = "";
    for (const fam of families) {
      const card = document.createElement("div");
      card.className = "family-card" + (todaysFamilies.includes(fam.family) ? " is-today" : "");
      card.innerHTML = `
        <h3>${fam.family}</h3>
        <div class="exercise-name">${fam.exercise_name}</div>
        <div class="milestone">Milestone: ${fam.milestone}</div>
        <div class="progress-bar-track">
          <div class="progress-bar-fill" style="width:${fam.progress_percent}%"></div>
        </div>
        ${fam.ready_to_advance ? '<span class="badge ready">Ready to advance</span>' : ""}
        <div class="actions">
          <button type="button" class="log-btn">Log workout</button>
          <button type="button" class="history-btn">History</button>
          ${fam.ready_to_advance ? '<button type="button" class="primary advance-btn">Advance</button>' : ""}
        </div>
      `;

      card.querySelector(".log-btn").addEventListener("click", () => {
        openLogPanel({
          family: fam.family,
          exerciseName: fam.exercise_name,
          onSaved: refresh,
        });
      });

      card.querySelector(".history-btn").addEventListener("click", () => {
        openHistoryPanel({ family: fam.family, onChanged: refresh });
      });

      const advanceBtn = card.querySelector(".advance-btn");
      if (advanceBtn) {
        advanceBtn.addEventListener("click", async () => {
          advanceBtn.disabled = true;
          try {
            await api.advance(fam.family);
          } finally {
            await refresh();
          }
        });
      }

      grid.appendChild(card);
    }
  }

  return { refresh };
}
