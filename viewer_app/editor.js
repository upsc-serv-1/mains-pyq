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
  initLayoutToggle();
});

window.toggleLayoutMode = function() {
  const grid = document.getElementById("editor-grid");
  const toggleBtn = document.getElementById("toggle-layout-btn");
  if (!grid || !toggleBtn) return;
  
  const isNowTwoCol = grid.classList.toggle("two-column-mode");
  if (isNowTwoCol) {
    localStorage.setItem("editor_layout_mode", "two-column");
    toggleBtn.innerHTML = "✏️ Switch to 1-Column Editor";
  } else {
    localStorage.setItem("editor_layout_mode", "one-column");
    toggleBtn.innerHTML = "📖 Switch to 2-Column Preview";
  }
};

function initLayoutToggle() {
  const toggleBtn = document.getElementById("toggle-layout-btn");
  const grid = document.getElementById("editor-grid");
  if (!toggleBtn || !grid) return;
  
  // Load initial state
  const isTwoCol = localStorage.getItem("editor_layout_mode") === "two-column";
  if (isTwoCol) {
    grid.classList.add("two-column-mode");
    toggleBtn.innerHTML = "✏️ Switch to 1-Column Editor";
  } else {
    grid.classList.remove("two-column-mode");
    toggleBtn.innerHTML = "📖 Switch to 2-Column Preview";
  }
}

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
  if (!coaching) return "pwonlyias";
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

function cleanStatementDisplay(text) {
  if (!text) return "";
  let clean = text.replace(/\*\*Question ID:\s*[^*]+\*\*/gi, "");
  clean = clean.replace(/Question ID:\s*[a-zA-Z0-9_-]+/gi, "");
  clean = clean.replace(/\[\d+\s*(?:words?|wards?),\s*\d+\s*marks?\]\.?/gi, "");
  clean = clean.replace(/\[\d+\s*marks?,\s*\d+\s*(?:words?|wards?)\]\.?/gi, "");
  clean = clean.replace(/\[\d+\s*(?:words?|wards?|marks?)\]\.?/gi, "");
  clean = clean.replace(/\*\*/g, "");
  clean = clean.replace(/\*/g, "");
  return clean.trim();
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
            <h3 class="q-statement">${cleanStatementDisplay(q.statement)}</h3>
          </div>
          <div style="display: flex; align-items: center; gap: 8px;">
            <div class="save-status-badge clean" id="status-${q.q_num}">✓ Saved</div>
            <button class="edit-card-btn" id="edit-card-btn-${q.q_num}" style="background: var(--bg-primary); border: 1px solid var(--border-color); border-radius: 6px; padding: 4px 8px; font-size: 11px; font-weight: 600; cursor: pointer; color: var(--text-secondary); display: flex; align-items: center; gap: 4px; transition: all 0.2s;">
              ✏️ Edit
            </button>
          </div>
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
                
                <!-- Left Pane: Edit Area / Compare Preview -->
                <div class="editor-pane" id="left-pane-${q.q_num}">
                  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                      <span class="pane-label" id="left-label-${q.q_num}">Edit Markdown</span>
                      <select id="left-compare-select-${q.q_num}" class="editor-select" style="padding: 4px 8px; font-size: 11px; font-weight: 600; display: none; height: auto; margin: 0; border-radius: 6px;">
                        ${COACHING_LIST.map(inst => {
                          const instKey = inst.toLowerCase();
                          const selected = currentCoaching.toLowerCase() === instKey ? "selected" : "";
                          return `<option value="${instKey}" ${selected}>${inst}</option>`;
                        }).join("")}
                      </select>
                    </div>
                    <button class="toggle-compare-btn" id="toggle-compare-btn-${q.q_num}" style="background: var(--bg-primary); border: 1px solid var(--border-color); border-radius: 6px; padding: 4px 8px; font-size: 11px; font-weight: 600; cursor: pointer; color: var(--text-secondary); display: flex; align-items: center; gap: 4px; transition: all 0.2s;">
                      👁️ Hide Editor (Compare Mode)
                    </button>
                  </div>
                  <textarea class="editor-textarea" id="textarea-${q.q_num}" placeholder="Paste or type answer markdown here...">${q.answer}</textarea>
                  <div class="editor-preview-viewport markdown-body" id="preview-left-${q.q_num}" style="display: none;"></div>
                </div>
                
                <!-- Right Pane: Rendered Preview -->
                <div class="editor-pane" id="right-pane-${q.q_num}">
                  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; height: 25px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                      <span class="pane-label" id="right-label-${q.q_num}">Live Preview (Website View)</span>
                      <select id="right-compare-select-${q.q_num}" class="editor-select" style="padding: 4px 8px; font-size: 11px; font-weight: 600; display: none; height: auto; margin: 0; border-radius: 6px;">
                        ${COACHING_LIST.map(inst => {
                          const instKey = inst.toLowerCase();
                          let selected = "";
                          if (currentCoaching.toLowerCase() === "pwonlyias") {
                            if (instKey === "drishti ias") selected = "selected";
                          } else {
                            if (instKey === "pwonlyias") selected = "selected";
                          }
                          return `<option value="${instKey}" ${selected}>${inst}</option>`;
                        }).join("")}
                      </select>
                    </div>
                  </div>
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
      
      // Bind local edit card button click
      const editCardBtn = card.querySelector(`#edit-card-btn-${q.q_num}`);
      if (editCardBtn) {
        editCardBtn.addEventListener("click", (e) => {
          e.preventDefault();
          const qCard = document.getElementById(`editor-card-${q.q_num}`);
          if (qCard) {
            const isEditing = qCard.classList.toggle("individual-edit-mode");
            editCardBtn.innerHTML = isEditing ? "👁️ Preview" : "✏️ Edit";
            if (isEditing) {
              setTimeout(() => {
                autoResize(q.q_num);
              }, 50);
            }
          }
        });
      }

      // Bind compare mode event listeners
      const toggleCompareBtn = card.querySelector(`#toggle-compare-btn-${q.q_num}`);
      if (toggleCompareBtn) {
        toggleCompareBtn.addEventListener("click", (e) => {
          e.preventDefault();
          toggleCompareMode(q.q_num);
        });
      }

      const leftCompareSelect = card.querySelector(`#left-compare-select-${q.q_num}`);
      if (leftCompareSelect) {
        leftCompareSelect.addEventListener("change", () => {
          updateCompareView(q.q_num);
        });
      }

      const rightCompareSelect = card.querySelector(`#right-compare-select-${q.q_num}`);
      if (rightCompareSelect) {
        rightCompareSelect.addEventListener("change", () => {
          updateCompareView(q.q_num);
        });
      }

      // Initialize preview rendering and height synchronization after rendering
      setTimeout(() => {
        autoResize(q.q_num);
        updatePreview(q.q_num);
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

function cleanAnswerHeaders(text) {
  if (!text) return "";
  text = text.trim();
  while (true) {
    const prev = text;
    text = text.replace(/^(?:#+\s*Ans(?:wer)?\s*(?:\*\*Ans(?:wer)?:\*\*)?|\*\*Ans(?:wer)?:\*\*|\*\*Ans(?:wer)?\*\*|Ans(?:wer)?:|Ans(?:wer)?\*\*)\s*/i, '').trim();
    text = text.replace(/^(?:\*\*|\*|)?Question ID:\s*[a-zA-Z0-9_-]+(?:\*\*|\*|)?\s*/i, '').trim();
    text = text.replace(/^(?:---\r?\n|\s+)+/, '').trim();
    if (text === prev) break;
  }
  text = text.replace(/\r?\n#+\s*Ans(?:wer)?(?:\s+\*\*Ans(?:wer)?:\*\*)?\s*(?:\r?\n|$)/gi, '\n');
  text = text.replace(/\r?\n(?:\*\*|\*|)?Ans(?:wer)?:?(?:\*\*|\*|)?\s*(?:\r?\n|$)/gi, '\n');
  return text.trim();
}

window.renderMarkdownToHtml = function(text, coachingName) {
  text = cleanAnswerHeaders(text);
  const folderName = getFolderName(coachingName);
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
    }
  } catch (e) {
    console.error("Marked library failed, falling back to basic parser:", e);
  }
  
  if (!html) {
    html = basicMarkdownParser(text);
  }
  return html;
};

window.fetchCoachingAnswerForCompare = async function(coaching, subject, qNum) {
  const cacheKey = `${coaching.toLowerCase()}_${subject.toLowerCase()}`;
  
  // 1. Try to find in the compiled global JS first! (Fastest and works offline for GS1/GS2/GS3)
  const paperKey = subject.toLowerCase();
  let globalDataSet = null;
  if (paperKey === "gs1") globalDataSet = window.GS1_DATA;
  else if (paperKey === "gs2") globalDataSet = window.GS2_DATA;
  else if (paperKey === "gs3") globalDataSet = window.GS3_DATA;
  
  if (globalDataSet) {
    // Find matching question in global dataset
    const cleanString = (text) => {
      if (!text) return "";
      let cleanText = text.replace(/\*\*Question ID:\s*[a-zA-Z0-9_-]+\*\*/gi, "");
      cleanText = cleanText.replace(/\[?Question ID:\s*[a-zA-Z0-9_-]+\]?/gi, "");
      cleanText = cleanText.replace(/^##\s+Question\s+\d+\s*(?:\([^\)]*\))?\s*/gi, "");
      return cleanText.toLowerCase().replace(/[^a-z0-9]/g, "").substring(0, 100);
    };
    
    // Get statement text of the active question from our loaded questionsList
    const activeQ = questionsList.find(q => q.q_num === qNum);
    if (activeQ) {
      const targetClean = cleanString(activeQ.statement);
      const matchedQ = globalDataSet.find(gq => {
        const gqClean = cleanString(gq.statement);
        return gqClean.includes(targetClean) || targetClean.includes(gqClean);
      });
      
      if (matchedQ) {
        // Find matching key in matchedQ.answers
        const answerKey = Object.keys(matchedQ.answers).find(k => 
          k.toLowerCase() === coaching.toLowerCase() || 
          COACHING_DISPLAY_NAMES[k.toLowerCase()]?.toLowerCase() === coaching.toLowerCase()
        );
        if (answerKey && matchedQ.answers[answerKey]) {
          return matchedQ.answers[answerKey].body || "";
        }
      }
    }
  }
  
  // 2. Fetch from the local API if not found or if it's GS4
  if (!coachingCompareCache[cacheKey]) {
    try {
      const url = `${API_BASE}/get-questions?coaching=${encodeURIComponent(coaching)}&subject=${encodeURIComponent(subject)}`;
      const res = await fetch(url);
      const data = await res.json();
      coachingCompareCache[cacheKey] = data.questions || [];
    } catch (e) {
      console.error(`Failed to fetch compare answers for ${coaching} ${subject}`, e);
      coachingCompareCache[cacheKey] = [];
    }
  }
  
  const q = coachingCompareCache[cacheKey].find(item => item.q_num === qNum);
  return q ? q.answer : "*(No answer found for this coaching institute)*";
};

window.updateCompareView = async function(qNum) {
  const leftSelect = document.getElementById(`left-compare-select-${qNum}`);
  const rightSelect = document.getElementById(`right-compare-select-${qNum}`);
  const leftPreview = document.getElementById(`preview-left-${qNum}`);
  const rightPreview = document.getElementById(`preview-${qNum}`);
  const textarea = document.getElementById(`textarea-${qNum}`);
  
  if (!leftSelect || !rightSelect || !leftPreview || !rightPreview) return;
  
  const leftCoaching = leftSelect.value;
  const rightCoaching = rightSelect.value;
  
  // Render left preview
  if (leftCoaching === currentCoaching.toLowerCase()) {
    leftPreview.innerHTML = renderMarkdownToHtml(textarea.value, currentCoaching);
  } else {
    leftPreview.innerHTML = `<div style="padding: 20px; text-align: center; color: var(--text-muted);">⏳ Loading left preview...</div>`;
    const text = await fetchCoachingAnswerForCompare(leftCoaching, currentSubject, qNum);
    leftPreview.innerHTML = renderMarkdownToHtml(text, leftCoaching);
  }
  
  // Render right preview
  if (rightCoaching === currentCoaching.toLowerCase()) {
    rightPreview.innerHTML = renderMarkdownToHtml(textarea.value, currentCoaching);
  } else {
    rightPreview.innerHTML = `<div style="padding: 20px; text-align: center; color: var(--text-muted);">⏳ Loading right preview...</div>`;
    const text = await fetchCoachingAnswerForCompare(rightCoaching, currentSubject, qNum);
    rightPreview.innerHTML = renderMarkdownToHtml(text, rightCoaching);
  }
};

window.toggleCompareMode = function(qNum) {
  const textarea = document.getElementById(`textarea-${qNum}`);
  const leftPreview = document.getElementById(`preview-left-${qNum}`);
  const leftSelect = document.getElementById(`left-compare-select-${qNum}`);
  const rightSelect = document.getElementById(`right-compare-select-${qNum}`);
  const leftLabel = document.getElementById(`left-label-${qNum}`);
  const rightLabel = document.getElementById(`right-label-${qNum}`);
  const btn = document.getElementById(`toggle-compare-btn-${qNum}`);
  
  if (!textarea || !leftPreview || !leftSelect || !rightSelect || !btn) return;
  
  const isEditing = textarea.style.display !== "none";
  if (isEditing) {
    // Switch to Compare Mode
    textarea.style.display = "none";
    leftPreview.style.display = "block";
    leftSelect.style.display = "inline-block";
    rightSelect.style.display = "inline-block";
    leftLabel.textContent = "Compare:";
    rightLabel.textContent = "Compare:";
    btn.innerHTML = "✏️ Show Editor";
    btn.style.backgroundColor = "rgba(124, 58, 237, 0.08)";
    btn.style.borderColor = "var(--accent-purple)";
    btn.style.color = "var(--accent-purple)";
    updateCompareView(qNum);
  } else {
    // Switch to Edit Mode
    textarea.style.display = "block";
    leftPreview.style.display = "none";
    leftSelect.style.display = "none";
    rightSelect.style.display = "none";
    leftLabel.textContent = "Edit Markdown";
    rightLabel.textContent = "Live Preview (Website View)";
    btn.innerHTML = "👁️ Hide Editor (Compare Mode)";
    btn.style.backgroundColor = "var(--bg-secondary)";
    btn.style.borderColor = "var(--border-color)";
    btn.style.color = "var(--text-secondary)";
    updatePreview(qNum);
  }
};

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
  
  // If in compare mode, do not overwrite the preview with textarea contents
  const leftPreview = document.getElementById(`preview-left-${qNum}`);
  const isCompare = leftPreview && leftPreview.style.display !== "none";
  if (isCompare) {
    updateCompareView(qNum);
    return;
  }
  
  previewDiv.innerHTML = renderMarkdownToHtml(textarea.value, currentCoaching);
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
      
      // If in two-column mode, automatically exit individual edit mode on successful save
      const qCard = document.getElementById(`editor-card-${qNum}`);
      const editCardBtn = document.getElementById(`edit-card-btn-${qNum}`);
      const grid = document.getElementById("editor-grid");
      if (qCard && grid && grid.classList.contains("two-column-mode")) {
        qCard.classList.remove("individual-edit-mode");
        if (editCardBtn) editCardBtn.innerHTML = "✏️ Edit";
      }
      
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
