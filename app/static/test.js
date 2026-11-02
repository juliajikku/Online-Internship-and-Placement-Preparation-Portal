// Timer, auto-save every 30 seconds (NFR3) and automatic submit when time runs out.
(function () {
  var form = document.getElementById("testform");
  var timer = document.getElementById("timer");
  var state = document.getElementById("savestate");
  var left = parseInt(timer.dataset.seconds, 10);
  var submitted = false;

  function render() {
    var m = Math.floor(left / 60), s = left % 60;
    timer.textContent = (m < 10 ? "0" : "") + m + ":" + (s < 10 ? "0" : "") + s;
    if (left <= 60) { timer.className = "low"; }
  }

  function save() {
    fetch(form.dataset.saveUrl, { method: "POST", body: new FormData(form), credentials: "same-origin" })
      .then(function (r) { return r.json(); })
      .then(function (j) { state.textContent = j.saved ? "Answers saved" : ""; })
      .catch(function () { state.textContent = "Could not save (will retry)"; });
  }

  form.addEventListener("submit", function () { submitted = true; });
  form.addEventListener("change", function () { state.textContent = "Unsaved changes"; });
  render();
  setInterval(function () {
    left -= 1;
    if (left <= 0 && !submitted) { left = 0; render(); submitted = true; form.submit(); return; }
    render();
  }, 1000);
  setInterval(function () { if (!submitted) { save(); } }, 30000);
})();
