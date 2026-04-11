/* RetailOS v2 — Main JS */

// ── Live search helper ──────────────────────────────────────────────────────
function liveSearch(inputId, tableId) {
  const input = document.getElementById(inputId);
  const table = document.getElementById(tableId);
  if (!input || !table) return;
  input.addEventListener('input', function () {
    const q = this.value.toLowerCase();
    table.querySelectorAll('tbody tr').forEach(row => {
      if (!row.querySelector('td')) return;
      row.style.display = row.innerText.toLowerCase().includes(q) ? '' : 'none';
    });
  });
}

// ── Confirm delete helper ───────────────────────────────────────────────────
function confirmDelete(name) {
  return confirm('Delete "' + name + '"? This cannot be undone.');
}

// ── Overlay helper: fix pointer-events on all overlay inputs/buttons ────────
function fixOverlayInputs(root) {
  const scope = root || document;
  // Fix both Bootstrap modal-content AND custom overlay divs
  scope.querySelectorAll(
    '.modal-content input, .modal-content select, .modal-content textarea, .modal-content button,' +
    '[id$="Overlay"] input, [id$="Overlay"] select, [id$="Overlay"] textarea, [id$="Overlay"] button,' +
    '[id$="overlay"] input, [id$="overlay"] select, [id$="overlay"] textarea, [id$="overlay"] button'
  ).forEach(el => {
    el.style.pointerEvents = 'auto';
    el.style.position      = 'relative';
    el.style.zIndex        = '10';
  });
}

document.addEventListener('DOMContentLoaded', function () {
  fixOverlayInputs();

  // Re-apply whenever a Bootstrap modal shows
  document.addEventListener('shown.bs.modal', function (e) {
    fixOverlayInputs(e.target);
    const first = e.target.querySelector('input:not([type=hidden]), select, textarea');
    if (first) setTimeout(() => { try { first.focus(); } catch(ex){} }, 100);
  });
});

// Expose globally so overlay show functions can call it
window.fixOverlayInputs = fixOverlayInputs;
