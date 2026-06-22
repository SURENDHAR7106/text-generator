/* ══════════════════════════════════════════
   AI Text Generator – Frontend Logic
   ══════════════════════════════════════════ */

const API_BASE = "http://127.0.0.1:5000";

// ── DOM References ──
const promptInput  = document.getElementById("promptInput");
const styleSelect  = document.getElementById("styleSelect");
const tempSlider   = document.getElementById("tempSlider");
const tokenSlider  = document.getElementById("tokenSlider");
const tempValue    = document.getElementById("tempValue");
const tokenValue   = document.getElementById("tokenValue");
const charCounter  = document.getElementById("charCounter");
const generateBtn  = document.getElementById("generateBtn");
const outputBox    = document.getElementById("outputBox");
const loader       = document.getElementById("loader");
const errorToast   = document.getElementById("errorToast");
const statsBar     = document.getElementById("statsBar");
const wordCount    = document.getElementById("wordCount");
const charCount    = document.getElementById("charCount");
const copyBtn      = document.getElementById("copyBtn");
const copyLabel    = document.getElementById("copyLabel");

// ── Slider Live Update ──
tempSlider.addEventListener("input",  () => tempValue.textContent  = parseFloat(tempSlider.value).toFixed(2));
tokenSlider.addEventListener("input", () => tokenValue.textContent = tokenSlider.value);

// ── Character Counter ──
promptInput.addEventListener("input", () => {
  const len = promptInput.value.length;
  charCounter.textContent = `${len} / 2000`;
  charCounter.classList.toggle("warning", len > 1800);
});

// ── Show / Hide Loader ──
function setLoading(active) {
  loader.classList.toggle("active", active);
  outputBox.style.display = active ? "none" : "block";
  generateBtn.disabled = active;
  generateBtn.innerHTML = active
    ? '<span class="btn-icon">⏳</span> Generating…'
    : '<span class="btn-icon">✦</span> Generate Text';
}

// ── Show Error ──
function showError(msg) {
  errorToast.textContent = "⚠ " + msg;
  errorToast.classList.add("visible");
  setTimeout(() => errorToast.classList.remove("visible"), 6000);
}

// ── Render Output ──
function renderOutput(text) {
  outputBox.innerHTML = "";           // clear placeholder
  outputBox.textContent = text;
  outputBox.classList.add("has-content", "slide-in");
  setTimeout(() => outputBox.classList.remove("slide-in"), 400);

  // Update stats bar
  const words = text.trim().split(/\s+/).filter(Boolean).length;
  wordCount.textContent = `${words} word${words !== 1 ? "s" : ""}`;
  charCount.textContent = `${text.length} characters`;
  statsBar.style.display = "flex";

  // Reset copy button label
  copyLabel.textContent = "Copy";
  copyBtn.classList.remove("copied");
}

// ══════════════════════════════════════
//  MAIN ACTION: Generate Text
// ══════════════════════════════════════
async function handleGenerate() {
  const prompt = promptInput.value.trim();
  if (!prompt) { showError("Please enter a prompt before generating."); return; }

  errorToast.classList.remove("visible");
  setLoading(true);

  try {
    const res = await fetch(`${API_BASE}/api/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        prompt,
        style:      styleSelect.value,
        temperature: parseFloat(tempSlider.value),
        max_tokens: parseInt(tokenSlider.value)
      })
    });

    const data = await res.json();
    if (!res.ok) { showError(data.error || "Generation failed."); return; }
    renderOutput(data.result);

  } catch (err) {
    showError("Cannot reach the server. Make sure server.py is running on port 5000.");
  } finally {
    setLoading(false);
  }
}

// ══════════════════════════════════════
//  MODIFICATION: Summarize / Expand / Rewrite / Continue
// ══════════════════════════════════════
async function handleModify(action) {
  // Use output box text if available, else fall back to prompt
  const outputText = outputBox.classList.contains("has-content") ? outputBox.textContent.trim() : "";
  const text = outputText || promptInput.value.trim();

  if (!text) { showError("No text available. Generate text first or enter a prompt."); return; }

  errorToast.classList.remove("visible");
  setLoading(true);

  try {
    const res = await fetch(`${API_BASE}/api/modify`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        action,
        text,
        style:       styleSelect.value,
        temperature: parseFloat(tempSlider.value),
        max_tokens:  parseInt(tokenSlider.value)
      })
    });

    const data = await res.json();
    if (!res.ok) { showError(data.error || "Modification failed."); return; }
    renderOutput(data.result);

  } catch (err) {
    showError("Cannot reach the server. Make sure server.py is running on port 5000.");
  } finally {
    setLoading(false);
  }
}

// ══════════════════════════════════════
//  CLEAR
// ══════════════════════════════════════
function handleClear() {
  promptInput.value = "";
  charCounter.textContent = "0 / 2000";
  charCounter.classList.remove("warning");

  outputBox.innerHTML = `
    <div class="output-placeholder">
      <div class="placeholder-icon">✦</div>
      <p>Your generated text will appear here.</p>
      <p class="placeholder-sub">Enter a prompt and click <strong>Generate Text</strong> to get started.</p>
    </div>`;
  outputBox.classList.remove("has-content");
  statsBar.style.display = "none";
  errorToast.classList.remove("visible");
  copyLabel.textContent = "Copy";
  copyBtn.classList.remove("copied");
}

// ══════════════════════════════════════
//  COPY TO CLIPBOARD
// ══════════════════════════════════════
async function handleCopy() {
  const text = outputBox.classList.contains("has-content") ? outputBox.textContent.trim() : "";
  if (!text) { showError("Nothing to copy yet."); return; }

  try {
    await navigator.clipboard.writeText(text);
    copyLabel.textContent = "Copied!";
    copyBtn.classList.add("copied");
    setTimeout(() => {
      copyLabel.textContent = "Copy";
      copyBtn.classList.remove("copied");
    }, 2500);
  } catch {
    showError("Clipboard access denied by your browser.");
  }
}

// ── Generate on Ctrl + Enter ──
promptInput.addEventListener("keydown", (e) => {
  if (e.ctrlKey && e.key === "Enter") handleGenerate();
});
