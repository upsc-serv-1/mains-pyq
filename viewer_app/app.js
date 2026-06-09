// ==========================================================================
// State Management
// ==========================================================================
let activePaper = 1; // Default to GS 1
let activeDataset = [];
let filteredDataset = [];
let activeCoaching = "Civilsdaily"; // Default primary coaching
let coachingCache = {}; // Cache of fetched coaching files
let currentLoadSession = 0; // Session ID to prevent race conditions

let currentFilters = {
  search: "",
  year: "all",
  subject: "all"
};

let currentSort = "id-asc";

// List of coaching institutes in order
const COACHING_INSTITUTES = ["Civilsdaily", "Drishti IAS", "PWOnlyIAS", "Rau IAS", "Superkalam", "Unacademy"];

// Map institute names to folder names used for images
const FOLDER_MAP = {
  "Civilsdaily": "civilsdaily",
  "Drishti IAS": "drishti ias",
  "PWOnlyIAS": "pwonlyias",
  "Rau IAS": "rau ias",
  "Superkalam": "superkalam",
  "Unacademy": "unacademy"
};

// ==========================================================================
// Init App
// ==========================================================================
document.addEventListener("DOMContentLoaded", () => {
  initEventListeners();
  loadPaper(1);
});

// ==========================================================================
// Event Listeners & UI Binding
// ==========================================================================
function initEventListeners() {
  // Paper Selection Buttons
  document.querySelectorAll(".paper-btn").forEach(btn => {
    btn.addEventListener("click", (e) => {
      const btnEl = e.currentTarget;
      document.querySelectorAll(".paper-btn").forEach(b => b.classList.remove("active"));
      btnEl.classList.add("active");
      
      const paperNum = parseInt(btnEl.dataset.paper);
      loadPaper(paperNum);
    });
  });

  // Search Input
  const searchInput = document.getElementById("search-input");
  const clearSearch = document.getElementById("clear-search");
  
  searchInput.addEventListener("input", (e) => {
    currentFilters.search = e.target.value.trim().toLowerCase();
    
    if (currentFilters.search.length > 0) {
      clearSearch.style.display = "block";
    } else {
      clearSearch.style.display = "none";
    }
    
    applyFiltersAndRender();
  });

  clearSearch.addEventListener("click", () => {
    searchInput.value = "";
    currentFilters.search = "";
    clearSearch.style.display = "none";
    applyFiltersAndRender();
  });

  // Coaching Select Dropdown
  const coachingSelect = document.getElementById("coaching-select");
  if (coachingSelect) {
    coachingSelect.innerHTML = COACHING_INSTITUTES.map(inst => 
      `<option value="${inst}">${inst}</option>`
    ).join("");
    coachingSelect.value = activeCoaching;
    coachingSelect.addEventListener("change", (e) => {
      activeCoaching = e.target.value;
      loadPaper(activePaper);
    });
  }

  // Sorting
  document.getElementById("sort-select").addEventListener("change", (e) => {
    currentSort = e.target.value;
    applyFiltersAndRender();
  });
}

// Clean and tokenize question text for matching
function cleanAndTokenize(text) {
  text = text.toLowerCase();
  text = text.replace(/^(?:q\d+\.?|que\.?|question\s*\d+\.?|answer\s*in\s*\d+\s*words|marks?|words?|\d+\s*marks?|\d+\s*words?)\s*/g, '');
  text = text.replace(/[^a-z0-9\s]/g, '');
  const words = text.split(/\s+/);
  const stopWords = new Set(['the', 'and', 'of', 'to', 'in', 'is', 'that', 'it', 'on', 'with', 'as', 'for', 'was', 'were']);
  const tokens = new Set();
  words.forEach(w => {
    if (w && !stopWords.has(w)) {
      tokens.add(w);
    }
  });
  return tokens;
}

// Compute Jaccard Similarity
function jaccardSimilarity(set1, set2) {
  if (set1.size === 0 || set2.size === 0) return 0.0;
  let intersectionSize = 0;
  set1.forEach(val => {
    if (set2.has(val)) {
      intersectionSize++;
    }
  });
  const unionSize = set1.size + set2.size - intersectionSize;
  return intersectionSize / unionSize;
}

// Parse syllabus formatted questions
function parseSyllabusMarkdown(content) {
  const lines = content.split(/\r?\n/);
  const questions = [];
  
  let i = 0;
  while (i < lines.length) {
    const line = lines[i].trim();
    if (line.match(/^Q\d+\./)) {
      const statement = line;
      const metadataLines = [];
      i++;
      while (i < lines.length) {
        const nextLine = lines[i].trim();
        if (!nextLine) {
          i++;
          continue;
        }
        if (nextLine.startsWith('[')) {
          metadataLines.push(nextLine);
          i++;
        } else {
          break;
        }
      }
      
      const metadata = metadataLines.join(" ");
      const qidMatch = statement.match(/^(Q\d+)\./);
      const qid = qidMatch ? qidMatch[1] : "Unknown";
      
      const yearMatch = metadata.match(/\[Year:\s*(\d{4})\]/i);
      const year = yearMatch ? yearMatch[1] : "Unknown";
      
      const subjectMatch = metadata.match(/\[Subject:\s*([^\]]+)\]/i);
      const subject = subjectMatch ? subjectMatch[1].trim() : "Unknown";
      
      const marksMatch = metadata.match(/\[Marks:\s*([^\]]+)\]/i);
      const marks = marksMatch ? marksMatch[1].trim() : "N/A";
      
      questions.push({
        id: qid,
        statement: statement,
        year: year,
        subject: subject,
        marks: marks,
        metadata: metadata,
        answers: {}
      });
    } else {
      i++;
    }
  }
  return questions;
}

// Parse raw coaching solved papers
function parseCoachingMarkdown(content) {
  const blocks = content.split(/\r?\n\s*(?:(?:-\s*){3,}|(?:\*\s*){3,})\r?\n/);
  const parsedQs = [];
  
  blocks.forEach(block => {
    const blockStrip = block.trim();
    if (!blockStrip) return;
    if (blockStrip.startsWith("# ") || blockStrip.includes("This file contains")) return;
    
    const lines = blockStrip.split('\n');
    const headerLine = lines[0].trim();
    
    const yearMatch = headerLine.match(/\(Year:\s*(\d{4})/i);
    const year = yearMatch ? yearMatch[1] : null;
    
    const qidMatch = blockStrip.match(/Question ID:\s*([a-zA-Z0-9_-]+)/i);
    const qid = qidMatch ? qidMatch[1] : "Unknown";
    
    // 1. Try to extract from the header line first
    let questionText = "";
    const headerMatch = headerLine.match(/^##\s+Question\s+\d+\s*\([^)]+\)\s*(.+)$/i);
    if (headerMatch) {
      let headerQ = headerMatch[1].trim();
      headerQ = headerQ.replace(/^\*\*+|\*\*+$|^\*+|\*+$/g, '').trim();
      if (headerQ.length > 5) {
        questionText = headerQ;
      }
    }
    
    // 2. Fallback to bold matches in the body
    if (!questionText) {
      const boldMatches = [];
      const boldRegex = /\*\*([^*]+)\*\*/g;
      let match;
      while ((match = boldRegex.exec(blockStrip)) !== null) {
        const mClean = match[1].trim();
        if (mClean.startsWith("Question ID:") || mClean.toLowerCase().startsWith("answer") || mClean === "Answer" || mClean === "Answer:") {
          continue;
        }
        if (mClean.length > 20) {
          boldMatches.push(mClean);
        }
      }
      
      questionText = boldMatches[0] || "";
      if (!questionText) {
        for (let j = 1; j < Math.min(lines.length, 5); j++) {
          const lineVal = lines[j].trim();
          if (lineVal.startsWith("**") && lineVal.endsWith("**")) {
            questionText = lineVal.replace(/\*\*/g, "");
            break;
          }
        }
      }
    }
    
    const answerSplit = blockStrip.split(/###\s*Answer(?:\s+\*\*Answer:\*\*)?/i);
    let answer = answerSplit.slice(1).join("### Answer").trim();
    
    answer = answer.replace(/\[Question ID:.*?\]/gi, '').trim();
    answer = answer.replace(/\r?\n---+\s*$/, '').trim();
    
    parsedQs.push({
      qid: qid,
      year: year,
      originalText: questionText.trim(),
      answer: answer,
      tokens: cleanAndTokenize(questionText)
    });
  });
  
  return parsedQs;
}


// Clean answer block headers
function cleanAnswerHeaders(text) {
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

// Map and align coaching answers with syllabus questions
function alignCoachingAnswers(syllabusQs, coachingData, instName) {
  syllabusQs.forEach(sq => {
    const cleanStatement = sq.statement.replace(/^Q\d+\.\s*/, '').trim();
    const targetTokens = cleanAndTokenize(cleanStatement);
    const year = sq.year;
    
    const sameYearQs = coachingData.filter(cq => cq.year === year);
    let bestMatch = null;
    let bestSim = 0.0;
    
    sameYearQs.forEach(cq => {
      const sim = jaccardSimilarity(targetTokens, cq.tokens);
      if (sim > bestSim) {
        bestSim = sim;
        bestMatch = cq;
      }
    });
    
    if (!(bestMatch && bestSim > 0.35)) {
      let bestMatchAny = null;
      let bestSimAny = 0.0;
      coachingData.forEach(cq => {
        const sim = jaccardSimilarity(targetTokens, cq.tokens);
        if (sim > bestSimAny) {
          bestSimAny = sim;
          bestMatchAny = cq;
        }
      });
      if (bestMatchAny && bestSimAny > 0.35) {
        bestMatch = bestMatchAny;
      }
    }
    
    if (bestMatch) {
      const folderName = FOLDER_MAP[instName] || instName.toLowerCase();
      let ansBody = bestMatch.answer;
      
      ansBody = ansBody.replace(/(?<!\/)images\//g, `${folderName}/images/`);
      ansBody = cleanAnswerHeaders(ansBody);
      
      let srcQuestion = bestMatch.originalText;
      srcQuestion = srcQuestion.replace(/(?<!\/)images\//g, `${folderName}/images/`);
      
      sq.answers[instName] = {
        source: srcQuestion,
        body: ansBody
      };
    }
  });
}

// ==========================================================================
// Dynamic Loader, Alignment & Background Processing
// ==========================================================================
async function getOrFetchCoachingData(paperNum, coachingName) {
  const cacheKey = `${paperNum}_${coachingName.toLowerCase().replace(/ /g, "_")}`;
  if (coachingCache[cacheKey]) {
    return coachingCache[cacheKey];
  }
  
  const suffix = coachingName.toLowerCase().replace(/ /g, "_");
  const fileUrl = `../solved paper/gs${paperNum}/gs${paperNum}_${suffix}.md`;
  
  try {
    const res = await fetch(fileUrl);
    if (!res.ok) {
      console.warn(`Could not load file for ${coachingName}: ${fileUrl}`);
      coachingCache[cacheKey] = [];
      return [];
    }
    const text = await res.text();
    const parsedData = parseCoachingMarkdown(text);
    coachingCache[cacheKey] = parsedData;
    return parsedData;
  } catch (err) {
    console.error(`Error fetching/parsing coaching file for ${coachingName}:`, err);
    coachingCache[cacheKey] = [];
    return [];
  }
}

function findMetadataForStatement(statement, paperNum) {
  let staticData = [];
  if (paperNum === 1) staticData = window.GS1_DATA || [];
  else if (paperNum === 2) staticData = window.GS2_DATA || [];
  else if (paperNum === 3) staticData = window.GS3_DATA || [];
  
  if (!staticData || staticData.length === 0) {
    return {
      subject: "General Studies",
      metadata: ""
    };
  }
  
  const targetTokens = cleanAndTokenize(statement);
  let bestMatch = null;
  let bestSim = 0.0;
  
  staticData.forEach(sq => {
    const cleanSqStmt = sq.statement.replace(/^Q\d+\.\s*/, '').trim();
    const sqTokens = cleanAndTokenize(cleanSqStmt);
    const sim = jaccardSimilarity(targetTokens, sqTokens);
    if (sim > bestSim) {
      bestSim = sim;
      bestMatch = sq;
    }
  });
  
  if (bestMatch && bestSim > 0.35) {
    return {
      subject: bestMatch.subject || "General Studies",
      metadata: bestMatch.metadata || ""
    };
  }
  
  return {
    subject: "General Studies",
    metadata: ""
  };
}

async function fetchPrimaryPaper(paperNum, coaching) {
  const suffix = coaching.toLowerCase().replace(/ /g, "_");
  const fileUrl = `../solved paper/gs${paperNum}/gs${paperNum}_${suffix}.md`;
  
  const res = await fetch(fileUrl);
  if (!res.ok) {
    throw new Error(`Failed to load coaching file: ${fileUrl}`);
  }
  const text = await res.text();
  const coachingData = parseCoachingMarkdown(text);
  
  // Cache the primary coaching data
  const cacheKey = `${paperNum}_${suffix}`;
  coachingCache[cacheKey] = coachingData;
  
  const primaryQs = coachingData.map((q, idx) => {
    // Extract marks if available in the text
    const marksMatch = q.originalText.match(/\[Marks:\s*([^\]]+)\]/i);
    const marks = marksMatch ? marksMatch[1].trim() : "N/A";
    
    // Clean statement text of bracketed metadata
    let cleanStmt = q.originalText
      .replace(/\[Year:\s*[^\]]+\]/gi, '')
      .replace(/\[Marks:\s*[^\]]+\]/gi, '')
      .replace(/\[Group:\s*[^\]]+\]/gi, '')
      .replace(/\[Exam:\s*[^\]]+\]/gi, '')
      .replace(/\[Stage:\s*[^\]]+\]/gi, '')
      .replace(/\[Paper:\s*[^\]]+\]/gi, '')
      .trim();
    
    if (!cleanStmt && q.statement) {
      cleanStmt = q.statement;
    }
    
    const enriched = findMetadataForStatement(cleanStmt, paperNum);
    
    const answers = {};
    answers[coaching] = {
      source: q.originalText,
      body: q.answer
    };
    
    return {
      id: `Q${idx + 1}`,
      statement: cleanStmt,
      year: q.year || "Unknown",
      subject: enriched.subject,
      marks: marks,
      metadata: enriched.metadata || `[Year: ${q.year || "Unknown"}] [Marks: ${marks}]`,
      answers: answers
    };
  });
  
  return primaryQs;
}

function alignSingleCoachingQuestion(q, targetData, instName) {
  const targetTokens = cleanAndTokenize(q.statement);
  const year = q.year;
  
  const sameYearQs = targetData.filter(cq => cq.year === year);
  let bestMatch = null;
  let bestSim = 0.0;
  
  sameYearQs.forEach(cq => {
    const sim = jaccardSimilarity(targetTokens, cq.tokens);
    if (sim > bestSim) {
      bestSim = sim;
      bestMatch = cq;
    }
  });
  
  if (!(bestMatch && bestSim > 0.35)) {
    let bestMatchAny = null;
    let bestSimAny = 0.0;
    targetData.forEach(cq => {
      const sim = jaccardSimilarity(targetTokens, cq.tokens);
      if (sim > bestSimAny) {
        bestSimAny = sim;
        bestMatchAny = cq;
      }
    });
    if (bestMatchAny && bestSimAny > 0.35) {
      bestMatch = bestMatchAny;
    }
  }
  
  if (bestMatch) {
    const folderName = FOLDER_MAP[instName] || instName.toLowerCase();
    let ansBody = bestMatch.answer;
    
    ansBody = ansBody.replace(/(?<!\/)images\//g, `${folderName}/images/`);
    ansBody = cleanAnswerHeaders(ansBody);
    
    let srcQuestion = bestMatch.originalText;
    srcQuestion = srcQuestion.replace(/(?<!\/)images\//g, `${folderName}/images/`);
    
    q.answers[instName] = {
      source: srcQuestion,
      body: ansBody
    };
  }
}

async function loadOtherCoachingsInBackground(paperNum, session) {
  const otherCoachings = COACHING_INSTITUTES.filter(inst => inst !== activeCoaching);
  
  for (const inst of otherCoachings) {
    if (session !== currentLoadSession) return;
    
    try {
      const targetData = await getOrFetchCoachingData(paperNum, inst);
      if (session !== currentLoadSession) return;
      
      activeDataset.forEach(q => {
        if (!q.answers[inst]) {
          alignSingleCoachingQuestion(q, targetData, inst);
        }
      });
      
      updateExpandedCardTabs(inst);
    } catch (err) {
      console.warn(`Error loading background coaching ${inst}:`, err);
    }
  }
}

function updateExpandedCardTabs(instName) {
  document.querySelectorAll(`.inst-tab-btn[data-inst="${instName}"]`).forEach(btn => {
    const card = btn.closest(".q-card");
    if (!card) return;
    
    const qid = card.id.replace("card-", "");
    const q = activeDataset.find(item => item.id === qid);
    if (q && q.answers[instName]) {
      btn.classList.remove("missing");
      btn.classList.add("present");
      const badge = btn.querySelector(".tab-badge");
      if (badge) badge.textContent = "✓";
    }
  });
}

// ==========================================================================
// Load Paper Dataset
// ==========================================================================
async function loadPaper(paperNum) {
  activePaper = paperNum;
  const session = ++currentLoadSession;
  
  // Show loading indicator in the feed
  const feed = document.getElementById("questions-feed");
  if (feed) {
    feed.innerHTML = `
      <div class="loading-state">
        <span class="spinner"></span>
        <p>Loading questions directly from ${activeCoaching} solved paper...</p>
      </div>
    `;
  }
  
  let title = "", desc = "";
  if (paperNum === 1) {
    title = "General Studies I (GS-1)";
    desc = "Master solved compilation containing syllabus-mapped questions spanning History, Geography, and Society.";
  } else if (paperNum === 2) {
    title = "General Studies II (GS-2)";
    desc = "Master solved compilation containing syllabus-mapped questions spanning Polity, Governance, Social Justice, and International Relations.";
  } else if (paperNum === 3) {
    title = "General Studies III (GS-3)";
    desc = "Master solved compilation containing syllabus-mapped questions spanning Economy, Agriculture, Science, Environment, and Security.";
  }
  updateHeader(title, desc);
  
  let loadedSuccessfully = false;
  if (location.protocol.startsWith("http")) {
    try {
      activeDataset = await fetchPrimaryPaper(paperNum, activeCoaching);
      loadedSuccessfully = true;
      console.log(`Dynamically loaded ${activeDataset.length} questions for ${activeCoaching} from raw Markdown file.`);
      
      // Load other coachings' papers in the background
      loadOtherCoachingsInBackground(paperNum, session);
    } catch (e) {
      console.error("Dynamic load failed, falling back to static JS data:", e);
    }
  }
  
  if (!loadedSuccessfully) {
    if (paperNum === 1) {
      activeDataset = window.GS1_DATA || [];
    } else if (paperNum === 2) {
      activeDataset = window.GS2_DATA || [];
    } else if (paperNum === 3) {
      activeDataset = window.GS3_DATA || [];
    }
  }
  
  // Reset active filters
  currentFilters.search = "";
  currentFilters.year = "all";
  currentFilters.subject = "all";
  
  const searchInput = document.getElementById("search-input");
  if (searchInput) searchInput.value = "";
  const clearSearch = document.getElementById("clear-search");
  if (clearSearch) clearSearch.style.display = "none";
  
  // Rebuild filter chips
  buildYearChips();
  buildSubjectChips();
  
  // Update sidebar total
  const totalCountEl = document.getElementById("total-questions-count");
  if (totalCountEl) totalCountEl.textContent = activeDataset.length;
  const answeredCountEl = document.getElementById("answered-questions-count");
  if (answeredCountEl) answeredCountEl.textContent = COACHING_INSTITUTES.length;
  
  // Apply filtering and render
  applyFiltersAndRender();
}

function updateHeader(title, desc) {
  document.getElementById("active-paper-header").textContent = title;
  document.getElementById("active-paper-desc").textContent = desc;
}

// ==========================================================================
// Build Dynamic Filters
// ==========================================================================
function buildYearChips() {
  const yearsSet = new Set();
  activeDataset.forEach(q => {
    if (q.year && q.year !== "Unknown") {
      yearsSet.add(q.year);
    }
  });
  
  const sortedYears = Array.from(yearsSet).sort((a, b) => b - a); // Newest first
  
  const container = document.getElementById("year-chips");
  container.innerHTML = `<button class="chip active" data-year="all">All Years</button>`;
  
  sortedYears.forEach(year => {
    const btn = document.createElement("button");
    btn.className = "chip";
    btn.dataset.year = year;
    btn.textContent = year;
    
    btn.addEventListener("click", () => {
      container.querySelectorAll(".chip").forEach(c => c.classList.remove("active"));
      btn.classList.add("active");
      currentFilters.year = year;
      applyFiltersAndRender();
    });
    
    container.appendChild(btn);
  });
  
  // Make "All Years" button clickable
  container.querySelector("[data-year='all']").addEventListener("click", (e) => {
    container.querySelectorAll(".chip").forEach(c => c.classList.remove("active"));
    e.target.classList.add("active");
    currentFilters.year = "all";
    applyFiltersAndRender();
  });
}

function buildSubjectChips() {
  const subjectsSet = new Set();
  activeDataset.forEach(q => {
    if (q.subject && q.subject !== "Unknown") {
      subjectsSet.add(q.subject.toUpperCase());
    }
  });
  
  const sortedSubjects = Array.from(subjectsSet).sort();
  
  const container = document.getElementById("subject-chips");
  container.innerHTML = `<button class="chip active" data-subject="all">All Subjects</button>`;
  
  sortedSubjects.forEach(subject => {
    const btn = document.createElement("button");
    btn.className = "chip";
    btn.dataset.subject = subject.toLowerCase();
    btn.textContent = subject.charAt(0).toUpperCase() + subject.slice(1).toLowerCase();
    
    btn.addEventListener("click", () => {
      container.querySelectorAll(".chip").forEach(c => c.classList.remove("active"));
      btn.classList.add("active");
      currentFilters.subject = subject.toLowerCase();
      applyFiltersAndRender();
    });
    
    container.appendChild(btn);
  });
  
  // Make "All Subjects" button clickable
  container.querySelector("[data-subject='all']").addEventListener("click", (e) => {
    container.querySelectorAll(".chip").forEach(c => c.classList.remove("active"));
    e.target.classList.add("active");
    currentFilters.subject = "all";
    applyFiltersAndRender();
  });
}

// ==========================================================================
// Filter and Sort Engine
// ==========================================================================
function applyFiltersAndRender() {
  filteredDataset = activeDataset.filter(q => {
    // 1. Year Filter
    if (currentFilters.year !== "all" && q.year !== currentFilters.year) {
      return false;
    }
    
    // 2. Subject Filter
    if (currentFilters.subject !== "all" && q.subject.toLowerCase() !== currentFilters.subject) {
      return false;
    }
    
    // 3. Search Filter
    if (currentFilters.search.length > 0) {
      const qText = q.statement.toLowerCase();
      const qMeta = q.metadata.toLowerCase();
      const matchesText = qText.includes(currentFilters.search) || qMeta.includes(currentFilters.search);
      
      // Also check inside answers if text matches
      let matchesAnswer = false;
      for (const inst in q.answers) {
        if (q.answers[inst].body.toLowerCase().includes(currentFilters.search)) {
          matchesAnswer = true;
          break;
        }
      }
      
      return matchesText || matchesAnswer;
    }
    
    return true;
  });
  
  // Sort Dataset
  sortDataset();
  
  // Render
  renderFeed();
  renderSubjectStats();
}

function sortDataset() {
  filteredDataset.sort((a, b) => {
    const idA = parseInt(a.id.replace("Q", "")) || 0;
    const idB = parseInt(b.id.replace("Q", "")) || 0;
    
    const yearA = parseInt(a.year) || 0;
    const yearB = parseInt(b.year) || 0;
    
    if (currentSort === "id-asc") {
      return idA - idB;
    } else if (currentSort === "year-desc") {
      if (yearA !== yearB) return yearB - yearA;
      return idA - idB;
    } else if (currentSort === "year-asc") {
      if (yearA !== yearB) return yearA - yearB;
      return idA - idB;
    }
    return 0;
  });
}

// ==========================================================================
// Render KPI Stats Pill bar
// ==========================================================================
function renderSubjectStats() {
  const container = document.getElementById("subject-stats-bar");
  
  // Calculate counts by subject in CURRENT filtered set
  const counts = {};
  filteredDataset.forEach(q => {
    counts[q.subject] = (counts[q.subject] || 0) + 1;
  });
  
  container.innerHTML = "";
  
  const subjects = Object.keys(counts).sort();
  subjects.forEach(subj => {
    const pill = document.createElement("div");
    pill.className = "stat-pill";
    if (currentFilters.subject === subj.toLowerCase()) {
      pill.classList.add("active");
    }
    
    pill.innerHTML = `
      <span class="stat-pill-num">${counts[subj]}</span>
      <span class="stat-pill-label" title="${subj}">${subj}</span>
    `;
    
    pill.addEventListener("click", () => {
      // Toggle subject filter
      const newSubject = currentFilters.subject === subj.toLowerCase() ? "all" : subj.toLowerCase();
      currentFilters.subject = newSubject;
      
      // Update chips UI
      const chipsContainer = document.getElementById("subject-chips");
      chipsContainer.querySelectorAll(".chip").forEach(c => {
        c.classList.remove("active");
        if (c.dataset.subject === newSubject) {
          c.classList.add("active");
        }
      });
      
      applyFiltersAndRender();
    });
    
    container.appendChild(pill);
  });
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
// Render Feed
// ==========================================================================
function renderFeed() {
  const feed = document.getElementById("questions-feed");
  const countText = document.getElementById("results-count-text");
  
  // Update count text
  countText.textContent = `Showing ${filteredDataset.length} of ${activeDataset.length} questions`;
  
  if (filteredDataset.length === 0) {
    feed.innerHTML = `
      <div class="no-results-state">
        <p>✕ No questions match your search filters.</p>
        <p style="font-size: 12px; margin-top: 8px;">Try clearing search keywords or choosing different subject/year chips.</p>
      </div>
    `;
    return;
  }
  
  feed.innerHTML = "";
  
  filteredDataset.forEach(q => {
    const card = document.createElement("article");
    card.className = "q-card";
    card.id = `card-${q.id}`;
    
    // Header collapsed view html
    const headerHtml = `
      <div class="q-card-header">
        <div class="q-card-header-main">
          <div class="q-badge-row">
            <span class="q-id">${q.id}</span>
            <span class="q-year">${q.year}</span>
            <span class="q-subject">${q.subject}</span>
            <span class="q-marks">${q.marks} Marks</span>
          </div>
          <h3 class="q-statement">${cleanStatementDisplay(q.statement)}</h3>
        </div>
        <div class="arrow-icon">▼</div>
      </div>
    `;
    
    // Content expanded view template
    const contentHtml = `
      <div class="q-card-content">
        <div class="expanded-inner">
          
          <!-- Detailed Taxonomy Metadata Box -->
          <div class="metadata-details-box">
            <div class="meta-tags-grid">
              ${renderMetadataItem("Syllabus Point (L3)", getMetaTag(q.metadata, "Subject"))}
              ${renderMetadataItem("Section Group (L4)", getMetaTag(q.metadata, "Section Group"))}
              ${renderMetadataItem("Microtopic (L5)", getMetaTag(q.metadata, "Microtopic"))}
              ${renderMetadataItem("Subtopic (L6)", getMetaTag(q.metadata, "Subtopic"))}
              ${renderMetadataItem("Macrotag", getMetaTag(q.metadata, "Macrotag"))}
              ${renderMetadataItem("Microtag", getMetaTag(q.metadata, "Microtag"))}
            </div>
          </div>
          
          <!-- Institute Answer View Tabs -->
          <div class="answer-tabs-wrapper">
            <div class="answer-tabs-header">Choose Solved Answer from Coaching Institute</div>
            
            <div class="institute-tabs">
              ${COACHING_INSTITUTES.map(inst => {
                const isPresent = !!q.answers[inst];
                const statusClass = isPresent ? "present" : "missing";
                const badge = isPresent ? "✓" : "✕";
                return `
                  <button class="inst-tab-btn ${statusClass}" data-inst="${inst}">
                    <span class="tab-badge">${badge}</span>
                    <span>${inst}</span>
                  </button>
                `;
              }).join("")}
            </div>
            
            <!-- Dynamic Answer Display Viewport -->
            <div class="answer-viewport" id="viewport-${q.id}">
              <div style="color: var(--text-muted); font-size: 13px; text-align: center; padding: 20px;">
                Select a coaching institute above to display their solved answer.
              </div>
            </div>
          </div>
          
        </div>
      </div>
    `;
    
    card.innerHTML = headerHtml + contentHtml;
    feed.appendChild(card);
    
    // Bind toggle expand/collapse behavior
    const cardHeader = card.querySelector(".q-card-header");
    cardHeader.addEventListener("click", () => {
      const isExpanded = card.classList.contains("expanded");
      
      // Collapse all other cards first (optional, but cleaner experience)
      document.querySelectorAll(".q-card.expanded").forEach(c => {
        if (c.id !== card.id) {
          c.classList.remove("expanded");
          const cContent = c.querySelector(".q-card-content");
          cContent.style.maxHeight = null;
        }
      });
      
      const content = card.querySelector(".q-card-content");
      if (isExpanded) {
        card.classList.remove("expanded");
        content.style.maxHeight = null;
      } else {
        card.classList.add("expanded");
        // Compute scrollHeight dynamically
        content.style.maxHeight = content.scrollHeight + "px";
        
        // Auto-select the first present institute tab
        const firstPresentBtn = card.querySelector(".inst-tab-btn.present");
        if (firstPresentBtn) {
          firstPresentBtn.click();
        } else {
          // If none are present, select the first button
          const firstBtn = card.querySelector(".inst-tab-btn");
          if (firstBtn) firstBtn.click();
        }
        
        // Smoothly scroll the card into view, accounting for layout shifts
        setTimeout(() => {
          const mainContent = document.querySelector(".main-content");
          if (mainContent) {
            const cardRect = card.getBoundingClientRect();
            const mainRect = mainContent.getBoundingClientRect();
            const targetScrollTop = mainContent.scrollTop + cardRect.top - mainRect.top - 20;
            mainContent.scrollTo({
              top: targetScrollTop,
              behavior: "smooth"
            });
          }
        }, 150);
      }
    });
    
    // Bind click listeners to institute tabs
    card.querySelectorAll(".inst-tab-btn").forEach(btn => {
      btn.addEventListener("click", (e) => {
        e.stopPropagation(); // Avoid triggering card header collapse
        
        // Remove active state from all tabs in this card
        card.querySelectorAll(".inst-tab-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        
        const instName = btn.dataset.inst;
        renderAnswer(q, instName);
      });
    });
  });
}

// ==========================================================================
// Helper functions for Rendering Details
// ==========================================================================
function renderMetadataItem(label, val) {
  if (!val) return "";
  return `
    <div class="meta-tag-item">
      <span class="meta-tag-label">${label}:</span>
      <span class="meta-tag-val">${val}</span>
    </div>
  `;
}

function getMetaTag(metadataString, tagKey) {
  // Finds [tagKey: text] inside the string
  const regex = new RegExp(`\\[${tagKey}:\\s*([^\\]]+)\\]`, "i");
  const match = metadataString.match(regex);
  return match ? match[1].strip ? match[1].strip() : match[1] : "";
}

// Helper to strip brackets
if (typeof String.prototype.strip === "undefined") {
  String.prototype.strip = function() {
    return this.replace(/^\s+|\s+$/g, '');
  };
}

// ==========================================================================
// Render Answer Content
// ==========================================================================
async function renderAnswer(q, instName) {
  const viewport = document.getElementById(`viewport-${q.id}`);
  
  let ansData = q.answers[instName];
  if (!ansData) {
    // Show a loading indicator in the viewport
    viewport.innerHTML = `
      <div style="color: var(--text-muted); font-size: 13px; text-align: center; padding: 20px;">
        <span class="spinner" style="display: inline-block; width: 16px; height: 16px; border: 2px solid var(--border-color); border-top-color: var(--accent-color); border-radius: 50%; animation: spin 1s linear infinite; margin-right: 8px; vertical-align: middle;"></span>
        Loading and aligning ${instName} answer...
      </div>
    `;
    
    try {
      const targetData = await getOrFetchCoachingData(activePaper, instName);
      alignSingleCoachingQuestion(q, targetData, instName);
      ansData = q.answers[instName];
    } catch (err) {
      console.error(`Error on-demand aligning for ${instName}:`, err);
    }
  }
  
  if (!ansData) {
    // Missing Answer layout
    viewport.innerHTML = `
      <div class="missing-alert">
        <span class="alert-icon">⚠️</span>
        <h4>No Solved Answer Available</h4>
        <p>Coaching institute <strong>${instName}</strong> does not have an answer compiled for this question.</p>
      </div>
    `;
    return;
  }
  
  // Format body text
  let bodyText = ansData.body;
  
  // Image path rewriting logic:
  // e.g. superkalam/images/foo.png -> ../solved paper/gs1/superkalam/images/foo.png
  const folderName = FOLDER_MAP[instName] || instName.toLowerCase();
  
  // Match relative image references in Markdown or raw HTML e.g. src="images/... " or src="folder/images/... "
  // We want to rewrite them to point to: ../solved paper/folder/images/...
  const gsPaperFolder = `../solved paper`;
  
  // Rewrite raw markdown image patterns: ![alt](images/foo.png) or ![alt](superkalam/images/foo.png)
  bodyText = bodyText.replace(/!\[(.*?)\]\((?:images\/|([^)]+?)\/images\/)(.*?)\)/g, (match, alt, folder, imgName) => {
    const targetFolder = folder ? folder : folderName;
    return `![${alt}](${gsPaperFolder}/${targetFolder}/images/${imgName})`;
  });
  
  // Rewrite HTML img src patterns: src="images/foo.png" or src="superkalam/images/foo.png"
  bodyText = bodyText.replace(/src=["'](?:images\/|([^"']+?)\/images\/)(.*?)["']/g, (match, folder, imgName) => {
    const targetFolder = folder ? folder : folderName;
    return `src="${gsPaperFolder}/${targetFolder}/images/${imgName}"`;
  });
  
  // Check if Marked library is available for beautiful rendering
  let renderedHtml = "";
  try {
    if (window.marked && typeof window.marked.parse === "function") {
      renderedHtml = window.marked.parse(bodyText);
    } else if (typeof window.marked === "function") {
      renderedHtml = window.marked(bodyText);
    } else {
      renderedHtml = basicMarkdownParser(bodyText);
    }
  } catch (e) {
    console.error("Markdown parsing error in app, using fallback:", e);
    renderedHtml = basicMarkdownParser(bodyText);
  }
  
  const sourceHtml = ansData.source ? `
    <div class="answer-meta">
      <strong>Source Question Match:</strong> ${ansData.source.replace(/\*\*Question ID:\s*[a-zA-Z0-9_-]+\*\*/gi, "").replace(/\[?Question ID:\s*[a-zA-Z0-9_-]+\]?/gi, "").trim()}
    </div>
  ` : "";
  
  viewport.innerHTML = `
    <div class="answer-container">
      ${sourceHtml}
      <div class="markdown-body">
        ${renderedHtml}
      </div>
    </div>
  `;
  
  // Readjust card height if opened, since content expanded dynamically
  const card = document.getElementById(`card-${q.id}`);
  const contentBox = card.querySelector(".q-card-content");
  if (card.classList.contains("expanded")) {
    contentBox.style.maxHeight = contentBox.scrollHeight + "px";
  }
}

// ==========================================================================
// Basic Regex Markdown Parser (Fallback)
// ==========================================================================
function basicMarkdownParser(md) {
  let html = md.trim();
  
  // Headers
  html = html.replace(/^###\s+(.*?)$/gm, '<h3>$1</h3>');
  html = html.replace(/^##\s+(.*?)$/gm, '<h2>$1</h2>');
  html = html.replace(/^#\s+(.*?)$/gm, '<h1>$1</h1>');
  
  // Bold
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  
  // Bullet lists
  html = html.replace(/^\-\s+(.*?)$/gm, '<li>$1</li>');
  html = html.replace(/^\*\s+(.*?)$/gm, '<li>$1</li>');
  // Wrap list items in <ul>
  html = html.replace(/(<li>.*?<\/li>\n?)+/g, '<ul>$&</ul>');
  
  // Horizontal Rule
  html = html.replace(/^---$/gm, '<hr>');
  
  // Blockquotes
  html = html.replace(/^>\s+(.*?)$/gm, '<blockquote>$1</blockquote>');
  
  // Newlines to paragraphs
  html = html.split('\n\n').map(p => {
    if (!p.trim().startsWith('<h') && !p.trim().startsWith('<ul') && !p.trim().startsWith('<block') && !p.trim().startsWith('<hr')) {
      return `<p>${p.trim().replace(/\n/g, '<br>')}</p>`;
    }
    return p.trim();
  }).join('\n');
  
  return html;
}
