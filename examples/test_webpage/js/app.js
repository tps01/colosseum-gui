import { inspectLot, startProduction } from "./backend.js";

const $ = (sel) => document.querySelector(sel);

function showView(name) {
  document.querySelectorAll("[data-view]").forEach((el) => {
    el.hidden = el.dataset.view !== name;
  });
  document.querySelectorAll(".nav-btn").forEach((btn) => {
    const current = btn.dataset.go === name;
    if (current) btn.setAttribute("aria-current", "page");
    else btn.removeAttribute("aria-current");
  });
}

function selectedSku() {
  return $("#widget-select").value;
}

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-go]").forEach((el) => {
    el.addEventListener("click", (event) => {
      if (el.tagName === "A") event.preventDefault();
      showView(el.dataset.go);
    });
  });

  $("#queue-btn").addEventListener("click", () => {
    const note = $("#queue-note");
    note.hidden = false;
    note.textContent = `Queued ${selectedSku()} for the next shift.`;
  });

  const start = $("[data-testid='start-btn']");
  const status = $("[data-testid='run-status']");
  const lot = $("[data-testid='lot-number']");

  start.addEventListener("click", async () => {
    start.disabled = true;
    start.textContent = "Starting…";
    status.hidden = true;
    lot.hidden = true;
    try {
      const result = await startProduction(selectedSku());
      status.textContent = "Running";
      status.hidden = false;
      lot.textContent = `Lot ${result.lot} (${result.sku})`;
      lot.hidden = false;
    } finally {
      start.disabled = false;
      start.textContent = "Start production";
    }
  });

  const inspect = $("[data-testid='inspect-btn']");
  const grade = $("[data-testid='inspect-result']");

  inspect.addEventListener("click", async () => {
    inspect.disabled = true;
    inspect.textContent = "Inspecting…";
    grade.hidden = true;
    try {
      const result = await inspectLot();
      grade.textContent = `Grade ${result.grade} of 10`;
      grade.hidden = false;
    } finally {
      inspect.disabled = false;
      inspect.textContent = "Inspect last lot";
    }
  });

  showView("home");
});
