// ==========================================================================
// Constants & State Management
// ==========================================================================
const COACHING_DISPLAY_NAMES = {
  "civilsdaily": "Civilsdaily",
  "drishti ias": "Drishti IAS",
  "pwonlyias": "PWOnlyIAS",
  "rau ias": "Rau IAS",
  "superkalam": "Superkalam",
  "unacademy": "Unacademy"
};
const COACHING_LIST = ["Civilsdaily", "Drishti IAS", "PWOnlyIAS", "Rau IAS", "Superkalam", "Unacademy"];

let currentCoaching = "";
let currentSubject = "";
let questionsList = [];

// API Base URL (running on same local port)
const API_BASE = "http://localhost:8000/api";

// ==========================================================================
// Initialization
// ==========================================================================
document.addEventListener("DOMContentLoaded", () => {
  initDropdowns();
  bindSelectors();
});

// Load coachings and subjects on start
async function initDropdowns() {
  try {
    const res = await fetch(`${API_BASE}/list-config`);
    const data = await res.json();
    
    const coachingSelect = document.getElementById("coaching-select");
    const subjectSelect = document.getElementById("subject-select");
    
    // Clear and populate Coaching select
    coachingSelect.innerHTML = `<option value="" disabled selected>Select Coaching...</option>`;
    data.coachings.forEach(c => {
      const opt = document.createElement("option");
      opt.value = c;
      opt.textContent = COACHING_DISPLAY_NAMES[c] || c.toUpperCase();
      coachingSelect.appendChild(opt);
    });
    
    // Clear and populate Subject select
    subjectSelect.innerHTML = `<option value="" disabled selected>Select GS Paper...</option>`;
    data.subjects.forEach(s => {
      const opt = document.createElement("option");
      opt.value = s;
      opt.textContent = s.toUpperCase().replace("GS", "GS ");
      subjectSelect.appendChild(opt);
    });
    
    // Restore selection from localStorage
    const savedCoaching = localStorage.getItem("editor_coaching");
    const savedSubject = localStorage.getItem("editor_subject");
    
    if (savedCoaching && data.coachings.includes(savedCoaching)) {
      coachingSelect.value = savedCoaching;
      currentCoaching = savedCoaching;
    }
    if (savedSubject && data.subjects.includes(savedSubject)) {
      subjectSelect.value = savedSubject;
      currentSubject = savedSubject;
    }
    
    if (currentCoaching && currentSubject) {
      loadQuestions();
    }
    
  } catch (error) {
    console.error("Failed to fetch server config: ", error);
    document.getElementById("editor-results-count").textContent = "❌ Error connecting to editor backend server. Make sure server.py is running on port 8000.";
  }
}

function bindSelectors() {
  const coachingSelect = document.getElementById("coaching-select");
  const subjectSelect = document.getElementById("subject-select");
  
  const checkAndLoad = () => {
    currentCoaching = coachingSelect.value;
    currentSubject = subjectSelect.value;
    
    // Save to localStorage
    if (currentCoaching) localStorage.setItem("editor_coaching", currentCoaching);
    if (currentSubject) localStorage.setItem("editor_subject", currentSubject);
    
    if (currentCoaching && currentSubject) {
      loadQuestions();
    }
  };
  
  coachingSelect.addEventListener("change", checkAndLoad);
  subjectSelect.addEventListener("change", checkAndLoad);
}

// ==========================================================================
// Metadata & Matching Helpers
// ==========================================================================
function getFolderName(coaching) {
  const key = coaching.toLowerCase();
  return key; // e.g. "drishti ias", "superkalam" match folder name directly
}

function getMetaTag(metadataString, tagKey) {
  if (!metadataString) return "";
  const regex = new RegExp(`\\[${tagKey}:\\s*([^\\]]+)\\]`, "i");
  const match = metadataString.match(regex);
  return match ? match[1].trim() : "";
}

function renderMetadataItem(label, val) {
  if (!val) return "";
  return `
    <div class="meta-tag-item">
      <span class="meta-tag-label">${label}:</span>
      <span class="meta-tag-val">${val}</span>
    </div>
  `;
}

// Looks up corresponding compiled question entry to load detailed taxonomy and marks
function findCompiledQuestion(coaching, subject, qNum, statementText) {
  let dataSet = [];
  const paperKey = subject.toLowerCase();
  if (paperKey === "gs1") {
    dataSet = window.GS1_DATA || [];
  } else if (paperKey === "gs2") {
    dataSet = window.GS2_DATA || [];
  } else if (paperKey === "gs3") {
    dataSet = window.GS3_DATA || [];
  } else {
    return null; // For gs4 or unknown
  }
  
  const cleanString = (text) => {
    if (!text) return "";
    // 1. Remove Question ID lines (e.g. **Question ID: ...** or [Question ID: ...])
    let cleanText = text.replace(/\*\*Question ID:\s*[a-zA-Z0-9_-]+\*\*/gi, "");
    cleanText = cleanText.replace(/\[?Question ID:\s*[a-zA-Z0-9_-]+\]?/gi, "");
    
    // 2. Remove ## Question X ... header prefixes if present
    cleanText = cleanText.replace(/^##\s+Question\s+\d+\s*(?:\([^\)]*\))?\s*/gi, "");
    
    // 3. Lowercase, keep only alphanumeric, and truncate
    return cleanText.toLowerCase()
      .replace(/[^a-z0-9]/g, "")
      .substring(0, 100);
  };
  
  const targetClean = cleanString(statementText);
  if (!targetClean) return null;
  
  // 1. Try to find match by statement similarity
  let match = dataSet.find(q => {
    const qClean = cleanString(q.statement);
    return qClean.includes(targetClean) || targetClean.includes(qClean);
  });
  
  // 2. Fallback: match by index question number (removed since sequential numbering doesn't align with syllabus ids)
  
  return match || null;
}

// ==========================================================================
// Load and Render Questions (Website Style)
// ==========================================================================
async function loadQuestions(scrollToQNum = null) {
  const grid = document.getElementById("editor-grid");
  const loading = document.getElementById("editor-loading");
  const statusCount = document.getElementById("editor-results-count");
  
  // Show loading state
  loading.style.display = "block";
  grid.innerHTML = "";
  grid.appendChild(loading);
  statusCount.textContent = "Loading file...";
  
  try {
    const url = `${API_BASE}/get-questions?coaching=${encodeURIComponent(currentCoaching)}&subject=${encodeURIComponent(currentSubject)}`;
    const res = await fetch(url);
    const data = await res.json();
    
    loading.style.display = "none";
    
    if (data.error) {
      const coachingSuffix = currentCoaching.toLowerCase().replace(/ /g, "_");
      statusCount.textContent = `❌ File error: ${data.error}`;
      grid.innerHTML = `<div class="no-results-state" style="padding: 40px; text-align: center; border: 1px dashed var(--border-color); border-radius: 12px; color: var(--text-muted);">
        <p>File not found or empty: <strong>solved paper/${currentSubject}/${currentSubject}_${coachingSuffix}.md</strong></p>
        <p style="font-size: 13px; margin-top: 8px;">Ensure that the GS Paper file exists for this coaching provider.</p>
      </div>`;
      return;
    }
    
    questionsList = data.questions || [];
    const displayCoaching = COACHING_DISPLAY_NAMES[currentCoaching] || currentCoaching.toUpperCase();
    const displaySubject = currentSubject.toUpperCase().replace("GS", "GS ");
    statusCount.textContent = `Loaded ${questionsList.length} questions for ${displayCoaching} - ${displaySubject}`;
    
    if (questionsList.length === 0) {
      grid.innerHTML = `<div style="text-align: center; padding: 40px; color: var(--text-muted);">This file contains no question blocks.</div>`;
      return;
    }
    
    // Render editor cards in exact website layout style
    questionsList.forEach(q => {
      // Find matching compiled question details
      const compiledQ = findCompiledQuestion(currentCoaching, currentSubject, q.q_num, q.statement);
      
      const qId = compiledQ ? compiledQ.id : `Q${q.q_num}`;
      const qMarks = compiledQ ? compiledQ.marks : "10";
      const qSyllabus = compiledQ ? getMetaTag(compiledQ.metadata, "Subject") : "";
      const qSectionGroup = compiledQ ? getMetaTag(compiledQ.metadata, "Section Group") : "";
      const qMicrotopic = compiledQ ? getMetaTag(compiledQ.metadata, "Microtopic") : "";
      const qSubtopic = compiledQ ? getMetaTag(compiledQ.metadata, "Subtopic") : "";
      const qMacrotag = compiledQ ? getMetaTag(compiledQ.metadata, "Macrotag") : "";
      const qMicrotag = compiledQ ? getMetaTag(compiledQ.metadata, "Microtag") : "";
      
      const card = document.createElement("article");
      card.className = "q-card expanded";
      card.id = `editor-card-${q.q_num}`;
      
      card.innerHTML = `
        <!-- Card Header (Website Style) -->
        <div class="q-card-header">
          <div class="q-card-header-main">
            <div class="q-badge-row">
              <span class="q-id">${qId}</span>
              <span class="q-year">${q.year || "Unknown"}</span>
              <span class="q-subject">${currentSubject.toUpperCase().replace("GS", "GS ")}</span>
              <span class="q-marks">${qMarks} Marks</span>
            </div>
            <h3 class="q-statement">${q.statement}</h3>
          </div>
          <div class="save-status-badge clean" id="status-${q.q_num}">✓ Saved</div>
        </div>
        
        <!-- Card Content (Website Style) -->
        <div class="q-card-content" style="max-height: none; overflow: visible;">
          <div class="expanded-inner">
            
            <!-- Detailed Taxonomy Metadata Box -->
            ${compiledQ ? `
            <div class="metadata-details-box">
              <div class="meta-tags-grid">
                ${renderMetadataItem("Syllabus Point (L3)", qSyllabus)}
                ${renderMetadataItem("Section Group (L4)", qSectionGroup)}
                ${renderMetadataItem("Microtopic (L5)", qMicrotopic)}
                ${renderMetadataItem("Subtopic (L6)", qSubtopic)}
                ${renderMetadataItem("Macrotag", qMacrotag)}
                ${renderMetadataItem("Microtag", qMicrotag)}
              </div>
            </div>
            ` : ""}
            
            <!-- Coaching Tabs -->
            <div class="answer-tabs-wrapper">
              <div class="answer-tabs-header">Choose Solved Answer from Coaching Institute</div>
              
              <div class="institute-tabs">
                ${COACHING_LIST.map(inst => {
                  const instKey = inst.toLowerCase();
                  const isCurrent = currentCoaching.toLowerCase() === instKey;
                  const hasAnswer = compiledQ ? !!compiledQ.answers[inst] : isCurrent;
                  
                  const statusClass = hasAnswer ? "present" : "missing";
                  const activeClass = isCurrent ? "active" : "";
                  const badge = hasAnswer ? "✓" : "✕";
                  
                  return `
                    <button class="inst-tab-btn ${statusClass} ${activeClass}" data-inst="${instKey}">
                      <span class="tab-badge">${badge}</span>
                      <span>${inst}</span>
                    </button>
                  `;
                }).join("")}
              </div>
              
              <!-- Side-by-Side Split Viewport Container -->
              <div class="editor-split-container" id="viewport-${q.q_num}">
                
                <!-- Left Pane: Edit Area -->
                <div class="editor-pane">
                  <div class="pane-label">Edit Markdown</div>
                  <textarea class="editor-textarea" id="textarea-${q.q_num}" placeholder="Paste or type answer markdown here...">${q.answer}</textarea>
                </div>
                
                <!-- Right Pane: Rendered Preview styled exactly like website answer viewport -->
                <div class="editor-pane">
                  <div class="pane-label">Live Preview (Website View)</div>
                  <div class="editor-preview-viewport markdown-body" id="preview-${q.q_num}"></div>
                </div>
                
              </div>
              
              <!-- Actions Footer Bar -->
              <div class="editor-actions-bar">
                <span style="font-size: 12px; color: var(--text-muted);">
                  Shortcut: Press <strong>Ctrl + Enter</strong> inside the box to save.
                </span>
                <button class="save-btn" id="save-btn-${q.q_num}" disabled>
                  <span>💾</span> Save Changes
                </button>
              </div>
            </div>
            
          </div>
        </div>
      `;
      
      grid.appendChild(card);
      
      // Bind event listeners to textarea
      const textarea = card.querySelector(`.editor-textarea`);
      const saveBtn = card.querySelector(`.save-btn`);
      const statusBadge = card.querySelector(`.save-status-badge`);
      
      // Listen to input changes (marks card as unsaved and auto-resizes both panes)
      textarea.addEventListener("input", () => {
        autoResize(q.q_num);
        updatePreview(q.q_num);
        saveBtn.disabled = false;
        statusBadge.className = "save-status-badge unsaved";
        statusBadge.textContent = "● Unsaved";
      });
      
      // Key shortcuts inside the editor
      textarea.addEventListener("keydown", (e) => {
        if (e.ctrlKey && e.key === "Enter") {
          e.preventDefault();
          if (!saveBtn.disabled) {
            saveAnswer(q.q_num);
          }
        }
      });
      
      // Bind save changes button click
      saveBtn.addEventListener("click", () => {
        saveAnswer(q.q_num);
      });
      
      // Bind tab clicks to switch coachings
      card.querySelectorAll(".inst-tab-btn").forEach(btn => {
        btn.addEventListener("click", (e) => {
          e.preventDefault();
          const targetCoaching = btn.dataset.inst;
          switchCoachingTab(targetCoaching, q.q_num);
        });
      });
      
      // Initialize preview rendering and height synchronization after rendering
      setTimeout(() => {
        updatePreview(q.q_num);
        autoResize(q.q_num);
      }, 50);
    });
    
    // Optional: Smoothly scroll to the target question card after loading
    if (scrollToQNum !== null) {
      setTimeout(() => {
        const card = document.getElementById(`editor-card-${scrollToQNum}`);
        if (card) {
          card.scrollIntoView({ behavior: "smooth", block: "center" });
          card.style.transition = "outline 0.3s";
          card.style.outline = "2px solid var(--accent-purple)";
          setTimeout(() => {
            card.style.outline = "none";
          }, 1500);
        }
      }, 200);
    }
    
  } catch (error) {
    loading.style.display = "none";
    statusCount.textContent = "❌ Failed to load questions.";
    console.error(error);
  }
}

// ==========================================================================
// Interactive Actions (Resizing, Previews)
// ==========================================================================
window.autoResize = function(qNum) {
  const textarea = document.getElementById(`textarea-${qNum}`);
  if (textarea) {
    textarea.style.height = "auto";
    textarea.style.height = textarea.scrollHeight + "px";
  }
};

window.updatePreview = function(qNum) {
  const textarea = document.getElementById(`textarea-${qNum}`);
  const previewDiv = document.getElementById(`preview-${qNum}`);
  if (!textarea || !previewDiv) return;
  
  let text = textarea.value;
  const folderName = getFolderName(currentCoaching);
  const gsPaperFolder = `../solved paper`;
  
  // Rewrite relative image references in Markdown or raw HTML
  text = text.replace(/!\[(.*?)\]\((?:images\/|([^)]+?)\/images\/)(.*?)\)/g, (match, alt, folder, imgName) => {
    const targetFolder = folder ? folder : folderName;
    return `![${alt}](${gsPaperFolder}/${targetFolder}/images/${imgName})`;
  });
  
  text = text.replace(/src=["'](?:images\/|([^"']+?)\/images\/)(.*?)["']/g, (match, folder, imgName) => {
    const targetFolder = folder ? folder : folderName;
    return `src="${gsPaperFolder}/${targetFolder}/images/${imgName}"`;
  });
  
  let html = "";
  try {
    if (window.marked && typeof window.marked.parse === "function") {
      html = window.marked.parse(text);
    } else if (typeof window.marked === "function") {
      html = window.marked(text);
    } else {
      html = basicMarkdownParser(text);
    }
  } catch (e) {
    console.error("Markdown parsing error, using fallback:", e);
    html = basicMarkdownParser(text);
  }
  
  previewDiv.innerHTML = html;
};

function basicMarkdownParser(md) {
  if (!md) return "";
  let html = md.trim();
  html = html.replace(/^###\s+(.*?)$/gm, '<h3>$1</h3>');
  html = html.replace(/^##\s+(.*?)$/gm, '<h2>$1</h2>');
  html = html.replace(/^#\s+(.*?)$/gm, '<h1>$1</h1>');
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/^\-\s+(.*?)$/gm, '<li>$1</li>');
  html = html.replace(/^\*\s+(.*?)$/gm, '<li>$1</li>');
  html = html.replace(/(<li>.*?<\/li>\n?)+/g, '<ul>$&</ul>');
  html = html.replace(/^---$/gm, '<hr>');
  html = html.replace(/^>\s+(.*?)$/gm, '<blockquote>$1</blockquote>');
  html = html.split('\n\n').map(p => {
    if (!p.trim().startsWith('<h') && !p.trim().startsWith('<ul') && !p.trim().startsWith('<block') && !p.trim().startsWith('<hr')) {
      return `<p>${p.trim().replace(/\n/g, '<br>')}</p>`;
    }
    return p.trim();
  }).join('\n');
  return html;
}

// ==========================================================================
// Save Answer back to Local Markdown File
// ==========================================================================
window.saveAnswer = async function(qNum) {
  const textarea = document.getElementById(`textarea-${qNum}`);
  const saveBtn = document.getElementById(`save-btn-${qNum}`);
  const statusBadge = document.getElementById(`status-${qNum}`);
  
  if (!textarea || !saveBtn || !statusBadge) return;
  
  saveBtn.disabled = true;
  statusBadge.className = "save-status-badge saving";
  statusBadge.textContent = "⏳ Saving...";
  
  const payload = {
    coaching: currentCoaching,
    subject: currentSubject,
    q_num: qNum,
    new_answer: textarea.value
  };
  
  try {
    const res = await fetch(`${API_BASE}/save-answer`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });
    
    const data = await res.json();
    
    if (data.status === "success") {
      // Update our in-memory question record
      const question = questionsList.find(q => q.q_num === qNum);
      if (question) {
        question.answer = textarea.value;
      }
      
      statusBadge.className = "save-status-badge success";
      statusBadge.textContent = "✓ Saved";
      
      updatePreview(qNum);
      autoResize(qNum);
      
      // Reset save button and status class back to clean after 3 seconds
      setTimeout(() => {
        statusBadge.className = "save-status-badge clean";
        statusBadge.textContent = "✓ Saved";
        saveBtn.disabled = true;
      }, 3000);
      
    } else {
      statusBadge.className = "save-status-badge error";
      statusBadge.textContent = "❌ Error";
      saveBtn.disabled = false;
      alert(`Save failed: ${data.error || "failed to save"}`);
    }
  } catch (error) {
    statusBadge.className = "save-status-badge error";
    statusBadge.textContent = "❌ Network Error";
    saveBtn.disabled = false;
    console.error(error);
  }
};

// ==========================================================================
// Coaching Switching Tabs (Quick Navigation)
// ==========================================================================
window.switchCoachingTab = async function(coachingKey, targetQNum) {
  // Check if there are any unsaved changes on the page before switching files
  const unsavedCount = document.querySelectorAll(".save-status-badge.unsaved").length;
  if (unsavedCount > 0) {
    const confirmSwitch = confirm("You have unsaved changes on this page. Are you sure you want to switch files? Unsaved changes will be lost.");
    if (!confirmSwitch) return;
  }
  
  const coachingSelect = document.getElementById("coaching-select");
  if (coachingSelect) {
    coachingSelect.value = coachingKey;
    currentCoaching = coachingKey;
    
    // Save to localStorage
    localStorage.setItem("editor_coaching", currentCoaching);
    
    // Reload database file and scroll to target question card
    await loadQuestions(targetQNum);
  }
};
