import { api } from "./api.js";
import { openLogPanel, scheduleForToday } from "./log.js";
import { openHistoryPanel } from "./history.js";
import { familyLink, exerciseLink } from "./links.js";

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
    renderGrid(progressData.families, todaysFamilies, familyPairs(catalog.schedule));
  }

  function renderSchedule(schedule) {
    const { day, families } = scheduleForToday(schedule);
    const label = day.charAt(0).toUpperCase() + day.slice(1);
    scheduleStrip.textContent =
      families.length > 0 ? `Today (${label}): ${families.join(" + ")}` : `Today (${label}): rest day`;
  }

  function familyPairs(schedule) {
    const dayOrder = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"];
    const pairs = [];
    const byKey = new Map();
    for (const day of dayOrder) {
      const dayFamilies = schedule[day] || [];
      if (dayFamilies.length === 0) continue;
      const key = dayFamilies.join("|");
      let entry = byKey.get(key);
      if (!entry) {
        entry = { families: dayFamilies, days: [] };
        byKey.set(key, entry);
        pairs.push(entry);
      }
      entry.days.push(day);
    }
    return pairs;
  }

  function dayLabel(days) {
    return days.map((d) => d.slice(0, 1).toUpperCase() + d.slice(1, 3)).join("/");
  }

  function renderGrid(families, todaysFamilies, pairs) {
    grid.innerHTML = "";
    const byName = new Map(families.map((fam) => [fam.family, fam]));
    const paired = new Set(pairs.flatMap((p) => p.families));
    const { day: todayDay } = scheduleForToday(catalog.schedule);
    const rowThemes = ["row-burgundy", "row-gold", "row-green"];

    pairs.forEach((pair, index) => {
      const row = document.createElement("div");
      row.className = "family-row " + rowThemes[index % rowThemes.length];

      const label = document.createElement("div");
      label.className = "family-row-days" + (pair.days.includes(todayDay) ? " is-today" : "");
      label.textContent = dayLabel(pair.days);
      row.appendChild(label);

      const cards = document.createElement("div");
      cards.className = "family-row-cards";
      for (const name of pair.families) {
        const fam = byName.get(name);
        if (fam) cards.appendChild(buildCard(fam, todaysFamilies));
      }
      row.appendChild(cards);

      grid.appendChild(row);
    });

    const leftovers = families.filter((fam) => !paired.has(fam.family));
    if (leftovers.length > 0) {
      const row = document.createElement("div");
      row.className = "family-row";

      const label = document.createElement("div");
      label.className = "family-row-days";
      label.textContent = "—";
      row.appendChild(label);

      const cards = document.createElement("div");
      cards.className = "family-row-cards";
      for (const fam of leftovers) {
        cards.appendChild(buildCard(fam, todaysFamilies));
      }
      row.appendChild(cards);

      grid.appendChild(row);
    }
  }

  function buildCard(fam, todaysFamilies) {
    const card = document.createElement("div");
    card.className = "family-card" + (todaysFamilies.includes(fam.family) ? " is-today" : "");
    card.innerHTML = `
      <h3>${familyLink(fam.family)}</h3>
      <div class="exercise-name">${exerciseLink(fam.exercise_name)}</div>
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

    return card;
  }

  return { refresh };
}
