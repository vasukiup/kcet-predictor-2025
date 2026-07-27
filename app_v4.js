/* =======================================================
   Copyright (c) 2026 Vasuki Upadhya. All rights reserved.
   Author: Vasuki Upadhya (vasuki.upadhya@gmail.com)
   Application: KEA Seat Matrix & Prediction Portal
   ======================================================= */

const ANNEXURE_LABELS = {
  A: 'Government',
  B: 'Govt Aided',
  C: 'Private',
  D: 'Minority',
  M: 'Public University',
  O: 'Pvt University',
  P: 'Deemed Univ.',
  Z: 'Govt (Higher Fees)',
  E: 'New Intake (Govt/Pvt)',
  V: 'New Intake (Univ)'
};

const ANNEXURE_ICONS = {
  A: '🏛️',
  B: '🤝',
  C: '🏢',
  D: '⭐',
  M: '🎓',
  O: '🌍',
  P: '🎖️',
  Z: '🏛️',
  E: '✨',
  V: '⚡'
};

const CHART_COLORS = [
  '#4f8ef7', '#a855f7', '#f97316', '#22c55e',
  '#14b8a6', '#ec4899', '#eab308', '#06b6d4',
  '#8b5cf6', '#f43f5e', '#84cc16', '#fb923c'
];

// ─────────────────────────────
// State
// State
// ─────────────────────────────
let allData = null;
let cache2024 = null;
let cache2025 = null;
let cache2026 = null;
let filtered = [];
let displayCount = 30;
let currentTab = 'colleges';
let sortMode = 'name';
let viewMode = 'grid';
let filters = { search: '', annexure: 'all', district: '', course: '', minSeats: 0 };

// Predefined groups for Institutions
const INSTITUTION_GROUPS = {
  rvgroup: {
    name: "RV Group of Institutions",
    patterns: ["rv college", "r v college", "rv institute", "r v institute", "rv university", "rv arch"],
    colleges: []
  },
  bmsgroup: {
    name: "BMS Group of Institutions",
    patterns: ["bms college", "b m s college", "bms institute", "b m s institute", "bms school"],
    colleges: []
  },
  pesgroup: {
    name: "PES Group of Institutions",
    patterns: ["pes university", "p e s university", "pes college", "p e s college", "pes institute", "p e s institute"],
    colleges: []
  },
  dsgroup: {
    name: "Dayananda Sagar Group",
    patterns: ["dayananda sagar", "dayanandasagar", "dsce", "dsatm", "dsu"],
    colleges: []
  }
};

function getCollegeGroup(name) {
  const lower = name.toLowerCase();
  for (const [groupId, group] of Object.entries(INSTITUTION_GROUPS)) {
    if (group.patterns.some(p => lower.includes(p))) {
      return groupId;
    }
  }
  return null;
}

let currentUser = null;
let pendingIntakeRequests = []; // Stores intake requests from institutions
let systemAnnouncements = ["⚠️ KEA Seat Matrix & Prediction Portal is online for candidate counselling validation."];
let authorityLogs = [`[System] Console initialized. Ready for operations.`];
let studentOptionsList = []; // Student option entry priority sheet
try {
  studentOptionsList = JSON.parse(localStorage.getItem('kcet_student_options')) || [];
} catch(e) {
  studentOptionsList = [];
}
let kcetSessions = [];
let currentSessionId = '';
let superuserPerspective = 'student'; // 'student', 'institution', 'authority', 'counsellor'
let superuserGroup = 'rvgroup';

// ─────────────────────────────
// Boot
// ─────────────────────────────
async function loadYearData(year) {
  try {
    const resFilters = await fetch(`/api/filters?year=${year}`);
    const filtersData = await resFilters.json();

    const resColleges = await fetch(`/api/colleges?year=${year}&limit=1000`);
    const collegesData = await resColleges.json();

    allData = {
      year: year,
      colleges: collegesData.colleges,
      all_courses: filtersData.courses,
      districts: filtersData.districts,
      types: filtersData.types,
      stats: {
        total_kea_seats: collegesData.total_seats,
        by_annexure: {
          'A': { kea_seats: 0 },
          'B': { kea_seats: 0 },
          'C': { kea_seats: 0 },
          'D': { kea_seats: 0 },
          'M': { kea_seats: 0 },
          'O': { kea_seats: 0 },
          'P': { kea_seats: 0 },
          'Z': { kea_seats: 0 }
        }
      }
    };

    // Preserve exact KEA seat numbers from source JSON file
    allData.colleges.forEach(col => {
      let colKea = 0;
      if (col.courses && Array.isArray(col.courses)) {
        col.courses.forEach(c => {
          const keaSeats = (c.total_kea_seats !== undefined && c.total_kea_seats !== null) 
            ? c.total_kea_seats 
            : ((c.kea_rk || 0) + (c.kea_hk || 0) + (c.kea_spl || 0) + (c.kea_ph || 0));
          c.total_kea_seats = keaSeats;
          colKea += keaSeats;
        });
      }
      if (!col.total_kea_seats) {
        col.total_kea_seats = colKea;
      }
    });

    // Re-calculate statistics dynamically to ensure accuracy across dashboards/summary cards
    let totalKea = 0;
    allData.colleges.forEach(col => {
      totalKea += col.total_kea_seats;
    });
    allData.stats.total_kea_seats = totalKea;

    // Re-calculate by_annexure KEA seats
    if (allData.stats && allData.stats.by_annexure) {
      for (const ann in allData.stats.by_annexure) {
        let annKea = 0;
        allData.colleges.filter(c => c.annexure === ann).forEach(col => {
          annKea += col.total_kea_seats;
        });
        allData.stats.by_annexure[ann].kea_seats = annKea;
      }
    }

    // Cache the loaded year data
    if (year === '2024') cache2024 = allData;
    else if (year === '2026') cache2026 = allData;
    else cache2025 = allData;

    populateFilters();
    updateHeaderStats();
    applyFilters();
    renderStats();
    renderTotals('ALL');
    updateDownloadDropdown(year);

    // Update document subtitle
    const subtitleEl = document.getElementById('brand-subtitle');
    if (subtitleEl) {
      subtitleEl.textContent = `Engineering Admissions ${year}`;
    }

    // Load and render YoY comparison asynchronously
    triggerYoYStatsLoad(year);

  } catch (e) {
    console.error('Failed to load data:', e);
    document.getElementById('colleges-grid').innerHTML =
      `<div class="empty-state"><div class="empty-state-icon">⚠️</div>
       <div class="empty-state-text">Could not load KCET Portal APIs.<br>Make sure the backend service is running.</div></div>`;
  }
}

function triggerYoYStatsLoad(activeYear) {
  if (activeYear === '2026') cache2026 = allData;
  else if (activeYear === '2024') cache2024 = allData;
  else cache2025 = allData;

  const loadCache = (year, callback) => {
    if (year === '2026' && cache2026) return callback();
    if (year === '2025' && cache2025) return callback();
    if (year === '2024' && cache2024) return callback();

    fetch(`/api/colleges?year=${year}&limit=1000`)
      .then(r => r.json())
      .then(collegesData => {
        const data = {
          year: year,
          colleges: collegesData.colleges,
          stats: {
            total_kea_seats: collegesData.total_seats
          }
        };
        data.colleges.forEach(col => {
          let colKea = 0;
          col.courses.forEach(c => {
            const keaSeats = (c.total_kea_seats !== undefined && c.total_kea_seats !== null) 
              ? c.total_kea_seats 
              : ((c.kea_rk || 0) + (c.kea_hk || 0) + (c.kea_spl || 0) + (c.kea_ph || 0));
            c.total_kea_seats = keaSeats;
            colKea += keaSeats;
          });
          if (!col.total_kea_seats) {
            col.total_kea_seats = colKea;
          }
        });

        if (year === '2026') cache2026 = data;
        else if (year === '2024') cache2024 = data;
        else cache2025 = data;
        
        callback();
      })
      .catch(err => {
        console.error(`Error loading comparison year ${year}:`, err);
        callback();
      });
  };

  let targetYear = '2025';
  if (activeYear === '2025') targetYear = '2024';
  else if (activeYear === '2024') targetYear = '2025';

  loadCache(targetYear, () => {
    loadCache(activeYear, () => {
      renderYoYStats();
    });
  });
}

function getCourseBranch(name) {
  const n = name.toUpperCase();
  if (n.includes('COMPUTER') || n.includes('INFORMATION SCIENCE') || n.includes('INFO.SCIENCE') || n.includes('AI') || n.includes('DATA SCIENCE') || n.includes('CYBER') || n.includes('IOT')) {
    return 'Computer Science & IT';
  }
  if (n.includes('ELECTRONICS') || n.includes('ELECTRICAL') || n.includes('TELECOMMUNICATION') || n.includes('INSTRUMENTATION') || n.includes('VLSI')) {
    return 'Electronics & Electrical';
  }
  if (n.includes('MECHANICAL') || n.includes('AERONAUTICAL') || n.includes('MECHATRONICS') || n.includes('AEROSPACE') || n.includes('AUTOMOBILE') || n.includes('ROBOTIC')) {
    return 'Mechanical & Aerospace';
  }
  if (n.includes('CIVIL') || n.includes('CHEMICAL') || n.includes('ENVIRONMENTAL')) {
    return 'Civil & Chemical';
  }
  return 'Other Branches';
}
function getCleanCollegeName(name) {
  if (!name) return '';
  let n = name.toLowerCase();
  
  // 1. Remove parenthesized text (like "(autonomous)", "(formerly...)", "(e003)")
  n = n.replace(/\(.*?\)/g, ' ');
  
  // 2. Fix common spelling variations and typos
  n = n.replace(/univeristy/g, 'university');
  n = n.replace(/uniersity/g, 'university');
  n = n.replace(/visveswaraya/g, 'visvesvaraya');
  n = n.replace(/visveswariah/g, 'visvesvaraya');
  n = n.replace(/visvesvariah/g, 'visvesvaraya');
  n = n.replace(/visvesvar/g, 'visvesvaraya');
  n = n.replace(/achitecture/g, 'architecture');
  n = n.replace(/architchure/g, 'architecture');
  n = n.replace(/institutute/g, 'institute');
  
  // 3. Normalize abbreviations
  n = n.replace(/engineering/g, 'engg');
  n = n.replace(/technology/g, 'tech');
  n = n.replace(/institute/g, 'inst');
  n = n.replace(/school/g, 'sch');
  
  // 4. Remove specific address descriptors and campus locations
  const addressTerms = [
    'kottar chowki', 'boloor village', 'doddakalisandra', 'chandapura', 'yelahanka',
    'white field', 'whitefield', 'k r puram', 'kr puram', 'bg nagara', 'jnanabharathi campus',
    'hunasamaranahalli', 'electronic city campus', 'electronic city', 'chagalatti',
    'devanahalli', 'mallohalli', 'doddaballapur', 'karur village', 'davangere',
    'basavanagudi', 'kengeri', 'uthrahalli road', 'chikkaballapur', 'chintamani',
    'mysore', 'mysuru', 'mangalore', 'mangaluru', 'belgaum', 'belagavi', 'hubli',
    'tumkur', 'nippani', 'bagalkote', 'bagalkot', 'gulbarga', 'mandya', 'hassan',
    'moodabidri', 'bangalore', 'bengaluru', 'gitam'
  ];
  for (const term of addressTerms) {
    n = n.replace(new RegExp('\\b' + term + '\\b', 'g'), ' ');
  }

  // 5. Remove non-alphanumeric characters
  n = n.replace(/[^a-z0-9]/g, ' ');
  
  // 6. Join single letters (e.g. "s j m" -> "sjm", "m s" -> "ms")
  while (/\b([a-z])\s+([a-z])\b/.test(n)) {
    n = n.replace(/\b([a-z])\s+([a-z])\b/g, '$1$2');
  }
  
  // 7. Clean up whitespace
  n = n.replace(/\s+/g, ' ').trim();
  
  // 8. Name Equivalents Mapping
  const equivalents = {
    "anuvartik mirji bharatesh inst of tech": "bharatesh inst of tech",
    "vs ms somashekhar r kothiwale inst of tech": "vs ms inst of tech",
    "gandhi inst of tech and management off campus": "gandhi inst of tech and management gitam off campus"
  };
  if (equivalents[n]) {
    return equivalents[n];
  }
  
  return n;
}

function renderYoYStats() {
  const selectedYear = document.getElementById('year-select')?.value || '2025';
  let activeCache, prevCache;
  let activeYearText, prevYearText;

  if (selectedYear === '2026') {
    if (!cache2026 || !cache2025) return;
    activeCache = cache2026;
    prevCache = cache2025;
    activeYearText = '2026';
    prevYearText = '2025';
  } else if (selectedYear === '2024') {
    if (!cache2024 || !cache2025) return;
    activeCache = cache2024;
    prevCache = cache2025;
    activeYearText = '2024';
    prevYearText = '2025';
  } else {
    if (!cache2025 || !cache2024) return;
    activeCache = cache2025;
    prevCache = cache2024;
    activeYearText = '2025';
    prevYearText = '2024';
  }

  const seats2024 = prevCache.stats.total_seats;
  const seats2025 = activeCache.stats.total_seats;
  const kea2024 = prevCache.stats.total_kea_seats;
  const kea2025 = activeCache.stats.total_kea_seats;
  const colleges2024 = prevCache.stats.total_colleges;
  const colleges2025 = activeCache.stats.total_colleges;

  const elSeats24 = document.getElementById('yoy-seats-2024');
  const elSeats25 = document.getElementById('yoy-seats-2025');
  const elKea24 = document.getElementById('yoy-kea-2024');
  const elKea25 = document.getElementById('yoy-kea-2025');
  const elCol24 = document.getElementById('yoy-colleges-2024');
  const elCol25 = document.getElementById('yoy-colleges-2025');

  if (elSeats24) elSeats24.textContent = seats2024.toLocaleString();
  if (elSeats25) elSeats25.textContent = seats2025.toLocaleString();
  if (elKea24) elKea24.textContent = kea2024.toLocaleString();
  if (elKea25) elKea25.textContent = kea2025.toLocaleString();
  if (elCol24) elCol24.textContent = colleges2024.toLocaleString();
  if (elCol25) elCol25.textContent = colleges2025.toLocaleString();

  const maxSeats = Math.max(seats2024, seats2025) || 1;
  const maxKea = Math.max(kea2024, kea2025) || 1;
  const maxColleges = Math.max(colleges2024, colleges2025) || 1;

  const barSeats24 = document.getElementById('yoy-bar-seats-2024');
  const barSeats25 = document.getElementById('yoy-bar-seats-2025');
  const barKea24 = document.getElementById('yoy-bar-kea-2024');
  const barKea25 = document.getElementById('yoy-bar-kea-2025');
  const barCol24 = document.getElementById('yoy-bar-colleges-2024');
  const barCol25 = document.getElementById('yoy-bar-colleges-2025');

  if (barSeats24) barSeats24.style.width = `${(seats2024 / maxSeats) * 100}%`;
  if (barSeats25) barSeats25.style.width = `${(seats2025 / maxSeats) * 100}%`;
  if (barKea24) barKea24.style.width = `${(kea2024 / maxKea) * 100}%`;
  if (barKea25) barKea25.style.width = `${(kea2025 / maxKea) * 100}%`;
  if (barCol24) barCol24.style.width = `${(colleges2024 / maxColleges) * 100}%`;
  if (barCol25) barCol25.style.width = `${(colleges2025 / maxColleges) * 100}%`;

  // Update dynamic year labels in the DOM
  const mainTitleEl = document.getElementById('yoy-main-title');
  if (mainTitleEl) {
    mainTitleEl.textContent = `Year-on-Year Comparison (${prevYearText} vs ${activeYearText})`;
  }
  const branchTitleEl = document.getElementById('yoy-branch-title');
  if (branchTitleEl) {
    branchTitleEl.textContent = `YoY Course Branch Seat Distribution (${prevYearText} vs ${activeYearText})`;
  }
  document.querySelectorAll('.yoy-prev-year-label').forEach(el => el.textContent = prevYearText);
  document.querySelectorAll('.yoy-active-year-label').forEach(el => el.textContent = activeYearText);
  
  const addedHeaderEl = document.querySelector('.yoy-added-header');
  if (addedHeaderEl) addedHeaderEl.innerHTML = `➕ Added in ${activeYearText}:`;
  const removedHeaderEl = document.querySelector('.yoy-removed-header');
  if (removedHeaderEl) removedHeaderEl.innerHTML = `➖ Removed in ${activeYearText}:`;
  const addedCourseHeaderEl = document.querySelector('.yoy-added-course-header');
  if (addedCourseHeaderEl) addedCourseHeaderEl.innerHTML = `🆕 Added in ${activeYearText}:`;
  const removedCourseHeaderEl = document.querySelector('.yoy-removed-course-header');
  if (removedCourseHeaderEl) removedCourseHeaderEl.innerHTML = `🚫 Removed in ${activeYearText}:`;

  // YoY Course Branch Seat Distribution
  const branches = ['Computer Science & IT', 'Electronics & Electrical', 'Mechanical & Aerospace', 'Civil & Chemical', 'Other Branches'];
  const branchSeats24 = { 'Computer Science & IT': 0, 'Electronics & Electrical': 0, 'Mechanical & Aerospace': 0, 'Civil & Chemical': 0, 'Other Branches': 0 };
  const branchSeats25 = { 'Computer Science & IT': 0, 'Electronics & Electrical': 0, 'Mechanical & Aerospace': 0, 'Civil & Chemical': 0, 'Other Branches': 0 };

  prevCache.colleges.forEach(col => {
    col.courses.forEach(c => {
      const b = getCourseBranch(c.course_name);
      branchSeats24[b] += c.total_intake || 0;
    });
  });

  activeCache.colleges.forEach(col => {
    col.courses.forEach(c => {
      const b = getCourseBranch(c.course_name);
      branchSeats25[b] += c.total_intake || 0;
    });
  });

  const getBranchIcon = (b) => {
    if (b.includes('Computer')) return '💻';
    if (b.includes('Electronics')) return '⚡';
    if (b.includes('Mechanical')) return '⚙️';
    if (b.includes('Civil')) return '🏢';
    return '🌱';
  };

  const branchHtml = branches.map(b => {
    const val24 = branchSeats24[b];
    const val25 = branchSeats25[b];
    const maxVal = Math.max(val24, val25) || 1;
    const pct24 = Math.round((val24 / maxVal) * 100);
    const pct25 = Math.round((val25 / maxVal) * 100);
    const change = val25 - val24;
    const changePct = val24 ? Math.round((change / val24) * 100) : 0;
    const changeBadge = change >= 0 
      ? `<span style="color:var(--green); font-weight:700;">▲ +${changePct}% (+${change.toLocaleString()} seats)</span>`
      : `<span style="color:var(--pink); font-weight:700;">▼ ${changePct}% (${change.toLocaleString()} seats)</span>`;

    return `
      <div style="margin-bottom: 20px; border-bottom: 1px solid rgba(255,255,255,0.02); padding-bottom: 12px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
          <span style="font-weight:600; color:var(--text); font-size:13px;">${getBranchIcon(b)} ${b}</span>
          <span style="font-size:11px;">${changeBadge}</span>
        </div>
        <div style="display:flex; flex-direction:column; gap:6px;">
          <div style="display:flex; align-items:center; gap:8px;">
            <span style="font-size:10px; width:30px; color:var(--text-muted);">${prevYearText}</span>
            <div style="flex:1; height:6px; background:rgba(255,255,255,0.05); border-radius:3px; overflow:hidden;">
              <div style="background:#6b7799; height:100%; width:${pct24}%;"></div>
            </div>
            <span style="font-size:11px; width:50px; text-align:right; color:var(--text-muted); font-weight:600;">${val24.toLocaleString()}</span>
          </div>
          <div style="display:flex; align-items:center; gap:8px;">
            <span style="font-size:10px; width:30px; color:var(--blue);">${activeYearText}</span>
            <div style="flex:1; height:6px; background:rgba(255,255,255,0.05); border-radius:3px; overflow:hidden;">
              <div style="background:var(--blue); height:100%; width:${pct25}%;"></div>
            </div>
            <span style="font-size:11px; width:50px; text-align:right; color:var(--blue); font-weight:600;">${val25.toLocaleString()}</span>
          </div>
        </div>
      </div>
    `;
  }).join('');

  const elBranch = document.getElementById('yoy-branch-distribution');
  if (elBranch) elBranch.innerHTML = branchHtml;

  // YoY Cutoff Popularity Shifts
  const shifts = [];
  activeCache.colleges.forEach(col => {
    if (!col.kea_code) return;
    const col24 = prevCache.colleges.find(c24 => c24.kea_code === col.kea_code);
    if (!col24) return;
    
    col.courses.forEach(c25 => {
      const cut25 = parseInt(c25.round1_cutoff?.GM);
      if (!cut25 || cut25 > 50000) return;
      
      const stdTarget = c25.course_name.toUpperCase().replace(/[^A-Z0-9]/g, '');
      const c24 = col24.courses.find(cx => cx.course_name.toUpperCase().replace(/[^A-Z0-9]/g, '') === stdTarget);
      if (!c24) return;
      
      const cut24 = parseInt(c24.round1_cutoff?.GM);
      if (!cut24) return;
      
      const change = cut25 - cut24;
      const changePct = Math.round((change / cut24) * 100);
      
      shifts.push({
        collegeName: col.college_name,
        courseName: c25.course_name,
        cut24,
        cut25,
        changePct
      });
    });
  });

  const rising = [...shifts].sort((a, b) => a.changePct - b.changePct).slice(0, 5);
  const cooling = [...shifts].sort((a, b) => b.changePct - a.changePct).slice(0, 5);

  const renderShiftItem = (item, isRising) => {
    const badgeColor = isRising ? 'var(--pink)' : 'var(--green)';
    const arrow = isRising ? '▲' : '▼';
    const absPct = Math.abs(item.changePct);
    const label = isRising ? 'tougher' : 'easier';
    
    return `
      <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:12px; border-bottom:1px solid rgba(255,255,255,0.02); padding-bottom:8px;">
        <div style="max-width:70%;">
          <div style="font-size:12px; font-weight:700; color:var(--text); white-space:nowrap; overflow:hidden; text-overflow:ellipsis;" title="${item.collegeName}">${item.collegeName}</div>
          <div style="font-size:10px; color:var(--text-muted);">${item.courseName}</div>
          <div style="font-size:10px; color:var(--text-muted); margin-top:2px;">Cutoff: ${item.cut24.toLocaleString()} (${prevYearText.slice(-2)}) ➔ ${item.cut25.toLocaleString()} (${activeYearText.slice(-2)})</div>
        </div>
        <span style="font-size:11px; font-weight:700; color:${badgeColor}; white-space:nowrap; background:rgba(255,255,255,0.02); border: 1px solid var(--border); padding:2px 8px; border-radius:12px;">
          ${arrow} ${absPct}% ${label}
        </span>
      </div>
    `;
  };

  const elRising = document.getElementById('popularity-shifts-rising');
  if (elRising) elRising.innerHTML = rising.map(item => renderShiftItem(item, true)).join('');

  const elCooling = document.getElementById('popularity-shifts-cooling');
  if (elCooling) elCooling.innerHTML = cooling.map(item => renderShiftItem(item, false)).join('');

  // YoY Structural Shifts - Colleges Added/Removed
  const clean24Names = new Set(prevCache.colleges.map(c => getCleanCollegeName(c.college_name)));
  const clean25Names = new Set(activeCache.colleges.map(c => getCleanCollegeName(c.college_name)));

  const addedColleges = activeCache.colleges.filter(c => !clean24Names.has(getCleanCollegeName(c.college_name)));
  const removedColleges = prevCache.colleges.filter(c => !clean25Names.has(getCleanCollegeName(c.college_name)));

  const addedColHtml = addedColleges.length > 0 
    ? addedColleges.map(col => {
        const codeDisplay = col.kea_code ? `<strong>${col.kea_code}</strong> - ` : '';
        return `
          <div style="font-size:11px; color:var(--text); padding:4px 6px; background:rgba(74,222,128,0.05); border-radius:6px; border:1px solid rgba(74,222,128,0.1); white-space:nowrap; overflow:hidden; text-overflow:ellipsis;" title="${col.college_name}">
            🟢 ${codeDisplay}${col.college_name}
          </div>
        `;
      }).join('')
    : '<div style="font-size:11px; color:var(--text-muted);">None detected</div>';

  const removedColHtml = removedColleges.length > 0
    ? removedColleges.map(col => {
        const codeDisplay = col.kea_code ? `<strong>${col.kea_code}</strong> - ` : '';
        return `
          <div style="font-size:11px; color:var(--text); padding:4px 6px; background:rgba(244,63,94,0.05); border-radius:6px; border:1px solid rgba(244,63,94,0.1); white-space:nowrap; overflow:hidden; text-overflow:ellipsis;" title="${col.college_name}">
            🔴 ${codeDisplay}${col.college_name}
          </div>
        `;
      }).join('')
    : '<div style="font-size:11px; color:var(--text-muted);">None detected</div>';

  const elColAdded = document.getElementById('colleges-added-list');
  const elColRemoved = document.getElementById('colleges-removed-list');
  if (elColAdded) elColAdded.innerHTML = addedColHtml;
  if (elColRemoved) elColRemoved.innerHTML = removedColHtml;

  // YoY Structural Shifts - Courses Added/Removed
  const courses24Clean = new Set(prevCache.colleges.flatMap(col => col.courses.map(c => c.course_name.toUpperCase().trim())));
  const courses25Clean = new Set(activeCache.colleges.flatMap(col => col.courses.map(c => c.course_name.toUpperCase().trim())));

  const addedCourses = [...courses25Clean].filter(x => !courses24Clean.has(x));
  const removedCourses = [...courses24Clean].filter(x => !courses25Clean.has(x));

  const addedCoursesHtml = addedCourses.length > 0
    ? addedCourses.map(c => `
        <div style="font-size:11px; color:var(--text); padding:3px 6px; background:rgba(74,222,128,0.02); border-radius:4px; border:1px solid rgba(255,255,255,0.02); white-space:nowrap; overflow:hidden; text-overflow:ellipsis;" title="${c}">
          ✨ ${c}
        </div>
      `).join('')
    : '<div style="font-size:11px; color:var(--text-muted);">None detected</div>';

  const removedCoursesHtml = removedCourses.length > 0
    ? removedCourses.map(c => `
        <div style="font-size:11px; color:var(--text-muted); padding:3px 6px; background:rgba(255,255,255,0.01); border-radius:4px; border:1px solid rgba(255,255,255,0.02); white-space:nowrap; overflow:hidden; text-overflow:ellipsis;" title="${c}">
          🚫 ${c}
        </div>
      `).join('')
    : '<div style="font-size:11px; color:var(--text-muted);">None detected</div>';

  const elCoursesAdded = document.getElementById('courses-added-list');
  const elCoursesRemoved = document.getElementById('courses-removed-list');
  if (elCoursesAdded) elCoursesAdded.innerHTML = addedCoursesHtml;
  if (elCoursesRemoved) elCoursesRemoved.innerHTML = removedCoursesHtml;

  // YoY Structural Shifts - Tuition Fee changes
  const parseFeeString = (str) => {
    if (!str) return 0;
    const clean = str.replace(/[^0-9]/g, '');
    return parseInt(clean) || 0;
  };

  const feeChanges = [];
  activeCache.colleges.forEach(col => {
    if (!col.kea_code) return;
    const col24 = prevCache.colleges.find(c24 => c24.kea_code === col.kea_code);
    if (!col24) return;
    
    col.courses.forEach(c25 => {
      if ((c25.total_kea_seats || 0) === 0) return;
      const stdTarget = c25.course_name.toUpperCase().replace(/[^A-Z0-9]/g, '');
      const c24 = col24.courses.find(cx => cx.course_name.toUpperCase().replace(/[^A-Z0-9]/g, '') === stdTarget);
      if (!c24) return;
      
      const fee24Str = getCourseFee(col24, c24.course_name, c24.total_kea_seats);
      const fee25Str = getCourseFee(col, c25.course_name, c25.total_kea_seats);
      
      const fee24 = parseFeeString(fee24Str);
      const fee25 = parseFeeString(fee25Str);
      
      if (!fee24 || !fee25 || fee24 === fee25) return;
      
      const change = fee25 - fee24;
      feeChanges.push({
        collegeName: col.college_name,
        courseName: c25.course_name,
        fee24,
        fee25,
        change
      });
    });
  });

  const topHikes = [...feeChanges].sort((a, b) => b.change - a.change).slice(0, 5);

  const hikesHtml = topHikes.length > 0
    ? topHikes.map(item => `
        <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:10px; border-bottom:1px solid rgba(255,255,255,0.02); padding-bottom:6px;">
          <div style="max-width:70%;">
            <div style="font-size:11px; font-weight:700; color:var(--text); white-space:nowrap; overflow:hidden; text-overflow:ellipsis;" title="${item.collegeName}">${item.collegeName}</div>
            <div style="font-size:10px; color:var(--text-muted);">${item.courseName}</div>
            <div style="font-size:9px; color:var(--text-muted);">₹${item.fee24.toLocaleString()} ➔ ₹${item.fee25.toLocaleString()}</div>
          </div>
          <span style="font-size:10px; font-weight:700; color:var(--pink); white-space:nowrap;">
            +₹${item.change.toLocaleString()}
          </span>
        </div>
      `).join('')
    : '<div style="font-size:11px; color:var(--text-muted); text-align:center; padding:12px;">No tuition fee changes detected</div>';

  const elFees = document.getElementById('fee-changes-list');
  if (elFees) elFees.innerHTML = hikesHtml;

  // YoY Branch Popularity Index
  const elIndex = document.getElementById('popularity-branch-index');
  if (elIndex) {
    const branchKeys = ['CS', 'EC', 'EE', 'ME', 'CE', 'AD'];
    const branchLabels = {
      'CS': 'Computer Science & IS',
      'EC': 'Electronics (ECE)',
      'EE': 'Electrical (EEE)',
      'ME': 'Mechanical Engg',
      'CE': 'Civil Engg',
      'AD': 'AI, ML & Data Science'
    };

    const calculateBranchAverage = (cache, branchCode) => {
      let sum = 0;
      let count = 0;
      cache.colleges.forEach(col => {
        col.courses.forEach(c => {
          if (matchesBranch(c.course_name, branchCode)) {
            const cut = parseInt(c.round1_cutoff?.GM);
            if (cut && cut < 120000) { // Limit to competitive ranges to avoid skew
              sum += cut;
              count++;
            }
          }
        });
      });
      return count > 0 ? sum / count : null;
    };

    const indexData = [];
    branchKeys.forEach(key => {
      const avgActive = calculateBranchAverage(activeCache, key);
      const avgPrev = calculateBranchAverage(prevCache, key);

      if (avgActive && avgPrev) {
        const pctShift = ((avgActive - avgPrev) / avgPrev) * 100;
        indexData.push({
          key,
          label: branchLabels[key],
          avgActive,
          avgPrev,
          pctShift
        });
      }
    });

    elIndex.innerHTML = indexData.map(item => {
      const isRising = item.pctShift < 0;
      const arrow = isRising ? '▲' : '▼';
      const absPct = Math.abs(item.pctShift).toFixed(1);
      const badgeColor = isRising ? '#f43f5e' : '#22c55e';
      const badgeBg = isRising ? 'rgba(244,63,94,0.1)' : 'rgba(34,197,94,0.1)';
      const directionLabel = isRising ? 'Rising Demand' : 'Cooling Demand';

      return `
        <div style="background:rgba(255,255,255,0.01); border:1px solid var(--border); padding:16px; border-radius:12px; display:flex; flex-direction:column; gap:8px;">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <strong style="font-size:12px; color:var(--text);">${item.label}</strong>
            <span style="font-size:9px; font-weight:700; padding:2px 6px; border-radius:4px; background:${badgeBg}; color:${badgeColor}; border:1px solid rgba(255,255,255,0.02);">${arrow} ${absPct}% ${directionLabel}</span>
          </div>
          <div style="display:flex; justify-content:space-between; font-size:10px; color:var(--text-muted); margin-top:4px;">
            <span>Avg Cutoff (${prevYearText.slice(-2)}): <strong>${Math.round(item.avgPrev).toLocaleString()}</strong></span>
            <span>Avg Cutoff (${activeYearText.slice(-2)}): <strong style="color:var(--text);">${Math.round(item.avgActive).toLocaleString()}</strong></span>
          </div>
          <div style="height:6px; background:rgba(255,255,255,0.05); border-radius:3px; overflow:hidden; margin-top:4px;">
            <div style="height:100%; width:${Math.min(100, Math.max(10, (120000 - item.avgActive) / 1200))}%; background:var(--blue);"></div>
          </div>
        </div>
      `;
    }).join('');
  }

  // Update header text dynamically
  const elBranchTitle = document.getElementById('yoy-popularity-branch-title');
  if (elBranchTitle) {
    elBranchTitle.textContent = `Predictive YoY Branch Popularity Trends (${prevYearText} vs ${activeYearText})`;
  }
}

async function init() {
  try {
    await loadYearData('2026');
    bindEvents();
    initAssistant();
    initAuth();
    initializeSessions();
  } catch (err) {
    console.error("Initialization error:", err);
  }

  // Bind Year Selector Event
  const yearSelect = document.getElementById('year-select');
  if (yearSelect) {
    yearSelect.addEventListener('change', async (e) => {
      const selectedYear = e.target.value;
      
      // Reset sidebar filters first
      filters = { search: '', annexure: 'all', district: '', course: '', minSeats: 0 };
      const searchInput = document.getElementById('search-input');
      if (searchInput) searchInput.value = '';
      const distFilter = document.getElementById('district-filter');
      if (distFilter) distFilter.value = '';
      const courseFilter = document.getElementById('course-filter');
      if (courseFilter) courseFilter.value = '';
      const affFilter = document.getElementById('affiliation-filter');
      if (affFilter) affFilter.value = '';
      const naacFilter = document.getElementById('naac-filter');
      if (naacFilter) naacFilter.value = '';
      const nbaFilter = document.getElementById('nba-filter');
      if (nbaFilter) nbaFilter.value = '';
      const salarySlider = document.getElementById('min-salary');
      const salarySliderVal = document.getElementById('min-salary-val');
      if (salarySlider && salarySliderVal) {
        salarySlider.value = 0;
        salarySliderVal.textContent = '0 LPA+';
      }
      const hostelSlider = document.getElementById('max-hostel');
      const hostelSliderVal = document.getElementById('max-hostel-val');
      if (hostelSlider && hostelSliderVal) {
        hostelSlider.value = 150000;
        hostelSliderVal.textContent = 'Any Fee';
      }
      const slider = document.getElementById('min-seats');
      if (slider) slider.value = 0;
      const sliderVal = document.getElementById('min-seats-val');
      if (sliderVal) sliderVal.textContent = '0+';
      document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
      const allChip = document.querySelector('[data-annexure="all"]');
      if (allChip) allChip.classList.add('active');

      await loadYearData(selectedYear);
    });
  }
}

// ─────────────────────────────
// Populate filter dropdowns
// ─────────────────────────────
function populateFilters() {
  const sortedCourses = [...(allData.all_courses || [])].sort((a, b) => a.localeCompare(b));

  const distSel = document.getElementById('district-filter');
  distSel.innerHTML = '<option value="">All Districts</option>';
  (allData.districts || []).forEach(d => {
    const opt = document.createElement('option');
    opt.value = d; opt.textContent = d;
    distSel.appendChild(opt);
  });

  const courseSel = document.getElementById('course-filter');
  courseSel.innerHTML = '<option value="">All Courses</option>';
  sortedCourses.forEach(c => {
    const opt = document.createElement('option');
    opt.value = c; opt.textContent = c;
    courseSel.appendChild(opt);
  });

  const predCourseSel = document.getElementById('pred-course');
  if (predCourseSel) {
    predCourseSel.innerHTML = '<option value="">All Courses</option>';
    sortedCourses.forEach(c => {
      const opt = document.createElement('option');
      opt.value = c; opt.textContent = c;
      predCourseSel.appendChild(opt);
    });
  }

  // Populate download tab filters
  const downDistSel = document.getElementById('download-district-select');
  if (downDistSel) {
    downDistSel.innerHTML = '<option value="">All Districts</option>';
    (allData.districts || []).forEach(d => {
      const opt = document.createElement('option');
      opt.value = d; opt.textContent = d;
      downDistSel.appendChild(opt);
    });
  }

  const downCourseSel = document.getElementById('download-course-select');
  if (downCourseSel) {
    downCourseSel.innerHTML = '<option value="">All Courses</option>';
    sortedCourses.forEach(c => {
      const opt = document.createElement('option');
      opt.value = c; opt.textContent = c;
      downCourseSel.appendChild(opt);
    });
  }

  // Populate Comparison, Fee Calculator & Download College Dropdowns
  const sortedColleges = [...(allData.colleges || [])].sort((a, b) => a.college_name.localeCompare(b.college_name));
  const downCollegeSel = document.getElementById('download-college-select');
  if (downCollegeSel) {
    downCollegeSel.innerHTML = '<option value="">All Colleges (Individual Matrix)</option>';
    sortedColleges.forEach(col => {
      const opt = document.createElement('option');
      const codeStr = col.kea_code ? `(${col.kea_code}) ` : '';
      opt.value = col.college_number || col.kea_code;
      opt.textContent = `${codeStr}${col.college_name}`;
      downCollegeSel.appendChild(opt);
    });
  }
  const compareCols = ['compare-col-1', 'compare-col-2', 'compare-col-3', 'calc-fee-college'];
  compareCols.forEach((id, index) => {
    const sel = document.getElementById(id);
    if (sel) {
      const defaultText = index === 0 ? '-- Choose College 1 --' : 
                          (index === 1 ? '-- Choose College 2 (Optional) --' : 
                          (index === 2 ? '-- Choose College 3 (Optional) --' : '-- Choose College --'));
      sel.innerHTML = `<option value="">${defaultText}</option>`;
      sortedColleges.forEach(col => {
        const opt = document.createElement('option');
        opt.value = col.kea_code;
        opt.textContent = `${col.kea_code || '---'} - ${col.college_name}`;
        sel.appendChild(opt);
      });
    }
  });
}

// ─────────────────────────────
// Header stats
// ─────────────────────────────
function updateHeaderStats() {
  const s = allData.stats;
  animateNum('hs-colleges', s.total_colleges);
  animateNum('hs-seats', s.total_seats, true);
  animateNum('hs-kea', s.total_kea_seats, true);
  animateNum('hs-courses', s.total_courses);
}

function animateNum(id, target, abbrev = false) {
  const el = document.getElementById(id);
  if (!el) return;
  let start = 0;
  const dur = 800;
  const startTime = performance.now();
  const tick = (now) => {
    const p = Math.min((now - startTime) / dur, 1);
    const val = Math.round(easeOut(p) * target);
    el.textContent = abbrev ? formatNum(val) : val.toLocaleString();
    if (p < 1) requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
}

function easeOut(t) { return 1 - Math.pow(1 - t, 3); }

function formatNum(n) {
  if (n >= 100000) return (n / 100000).toFixed(1) + 'L';
  if (n >= 1000) return (n / 1000).toFixed(1) + 'K';
  return n.toLocaleString();
}

function initAuth() {
  const overlay = document.getElementById('auth-overlay');
  const profileChip = document.getElementById('user-profile-chip');
  const roleBadge = document.getElementById('user-role-badge');
  const nameDisplay = document.getElementById('user-display-name');
  const logoutBtn = document.getElementById('logout-btn');

  // Load from local storage
  const savedUser = localStorage.getItem('kcet_user');
  if (savedUser) {
    currentUser = JSON.parse(savedUser);
    overlay.style.display = 'none';
    applyUserRole();
  } else {
    overlay.style.display = 'flex';
  }

  // Role switching
  document.querySelectorAll('.auth-role-tab').forEach(tab => {
    tab.addEventListener('click', (e) => {
      if (e) e.preventDefault();
      document.querySelectorAll('.auth-role-tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.auth-form').forEach(f => f.classList.remove('active'));
      tab.classList.add('active');
      const role = tab.getAttribute('data-role');
      console.log('Switching auth view to role:', role);
      const formEl = document.getElementById(`auth-form-${role}`);
      if (formEl) {
        formEl.classList.add('active');
      } else {
        console.error(`Auth form Element auth-form-${role} not found!`);
      }
    });
  });

  // Submit Student
  document.getElementById('btn-submit-student').addEventListener('click', () => {
    const name = document.getElementById('reg-name').value.trim();
    const email = document.getElementById('reg-email').value.trim();
    const password = document.getElementById('reg-password').value;
    const rank = parseInt(document.getElementById('reg-rank').value);
    const category = document.getElementById('reg-category').value;
    const region = document.getElementById('reg-region').value;

    if (!name || !email || !password || !rank) {
      alert("Please fill in all registration fields.");
      return;
    }

    currentUser = { role: 'student', name, email, rank, category, region };
    localStorage.setItem('kcet_user', JSON.stringify(currentUser));
    
    // Log registration in PostgreSQL
    fetch('/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: name, email: email, role: 'student' })
    }).catch(err => console.error('Reg log error:', err));

    overlay.style.display = 'none';
    applyUserRole();
  });

  // Submit Institution
  document.getElementById('btn-submit-institution').addEventListener('click', () => {
    const groupVal = document.getElementById('inst-group').value.trim().toLowerCase();
    const password = document.getElementById('inst-password').value;
    const errorEl = document.getElementById('inst-error');

    const validGroups = {
      'rvgroup': 'RV Group of Institutions',
      'bmsgroup': 'BMS Group of Institutions',
      'pesgroup': 'PES Group of Institutions',
      'dsgroup': 'Dayananda Sagar Group'
    };

    if (validGroups[groupVal] && password === 'kcet2025') {
      errorEl.style.display = 'none';
      currentUser = { role: 'institution', name: validGroups[groupVal], institutionGroup: groupVal };
      localStorage.setItem('kcet_user', JSON.stringify(currentUser));
      
      // Log login event
      fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: validGroups[groupVal], role: 'institution' })
      }).catch(err => console.error(err));

      overlay.style.display = 'none';
      applyUserRole();
    } else {
      errorEl.style.display = 'block';
    }
  });

  // Submit Authority
  document.getElementById('btn-submit-authority').addEventListener('click', () => {
    const authId = document.getElementById('auth-id').value.trim();
    const password = document.getElementById('auth-password').value;
    const errorEl = document.getElementById('auth-error');

    if (authId === 'authority' && password === 'kcet2025') {
      errorEl.style.display = 'none';
      currentUser = { role: 'authority', name: "KEA Admin Console" };
      localStorage.setItem('kcet_user', JSON.stringify(currentUser));

      // Log login event
      fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: "KEA Admin Console", role: 'authority' })
      }).catch(err => console.error(err));

      overlay.style.display = 'none';
      applyUserRole();
    } else {
      errorEl.style.display = 'block';
    }
  });

  // Submit Counsellor
  document.getElementById('btn-submit-counsellor').addEventListener('click', () => {
    const cid = document.getElementById('counsellor-id').value.trim();
    const cpwd = document.getElementById('counsellor-password').value;
    const errorEl = document.getElementById('counsellor-error');

    if ((cid === 'counsellor' || cid === 'mentor') && cpwd === 'kcet2025') {
      errorEl.style.display = 'none';
      const saved = localStorage.getItem('kcet_user');
      if (saved) {
        try {
          const parsed = JSON.parse(saved);
          if (parsed.role === 'counsellor') {
            currentUser = parsed;
          }
        } catch(e) {}
      }
      if (!currentUser || currentUser.role !== 'counsellor') {
        currentUser = {
          role: 'counsellor',
          name: "Professional Advisor",
          students: [
            { id: 'cs1', name: "Aditi Rao", rank: 4200, category: "3BG", optionList: [] },
            { id: 'cs2', name: "Roshan Kumar", rank: 12500, category: "GM", optionList: [] },
            { id: 'cs3', name: "Basavaraj S", rank: 28000, category: "2AR", optionList: [] }
          ],
          activeStudentId: 'cs1'
        };
      }
      localStorage.setItem('kcet_user', JSON.stringify(currentUser));

      // Log login event
      fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: currentUser.name, role: 'counsellor' })
      }).catch(err => console.error(err));

      overlay.style.display = 'none';
      applyUserRole();
    } else {
      errorEl.style.display = 'block';
    }
  });

  // Submit Super User
  document.getElementById('btn-submit-superuser').addEventListener('click', () => {
    const suid = document.getElementById('su-id').value.trim();
    const supwd = document.getElementById('su-password').value;
    const errorEl = document.getElementById('su-error');

    if (suid === 'superuser' && supwd === 'kcet2025') {
      errorEl.style.display = 'none';
      currentUser = { role: 'superuser', name: "Global Admin" };
      localStorage.setItem('kcet_user', JSON.stringify(currentUser));

      // Log login event
      fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: "Global Admin", role: 'superuser' })
      }).catch(err => console.error(err));

      overlay.style.display = 'none';
      applyUserRole();
    } else {
      errorEl.style.display = 'block';
    }
  });

  // Logout
  logoutBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    localStorage.removeItem('kcet_user');
    currentUser = null;
    overlay.style.display = 'flex';
    applyUserRole();
  });

  // Bind Student Profile updates in sidebar
  const profileRank = document.getElementById('profile-rank');
  const profileCat = document.getElementById('profile-category');
  
  if (profileRank) {
    profileRank.addEventListener('change', () => {
      const val = parseInt(profileRank.value);
      if (val > 0 && currentUser && currentUser.role === 'student') {
        currentUser.rank = val;
        localStorage.setItem('kcet_user', JSON.stringify(currentUser));
        
        // Sync to Predictor Tab
        const prRank = document.getElementById('pred-rank');
        if (prRank) prRank.value = val;
        
        if (studentOptionsList.length > 0) {
          studentOptionsList.forEach(opt => {
            opt.chanceClass = getChanceClass(opt.cutoff, currentUser.rank);
          });
          renderOptionEntryList();
        }

        // Sync header displays or modal calculations
        applyFilters();
      }
    });
  }

  if (profileCat) {
    profileCat.addEventListener('change', () => {
      const val = profileCat.value;
      if (val && currentUser && currentUser.role === 'student') {
        currentUser.category = val;
        localStorage.setItem('kcet_user', JSON.stringify(currentUser));
        
        // Sync to Predictor Tab
        const prCat = document.getElementById('pred-category');
        if (prCat) prCat.value = val;
        
        if (studentOptionsList.length > 0) {
          studentOptionsList.forEach(opt => {
            const col = allData.colleges.find(c => c.college_number == opt.collegeNum);
            if (col) {
              const course = col.courses.find(cr => cr.course_name === opt.courseName);
              if (course) {
                const newCutoff = getCourseCutoff(course, currentUser.category);
                if (!isNaN(newCutoff)) opt.cutoff = newCutoff;
              }
            }
            opt.chanceClass = getChanceClass(opt.cutoff, currentUser.rank);
          });
          renderOptionEntryList();
        }

        applyFilters();
      }
    });
  }

  // Bind Institution form change request button
  const submitChangeBtn = document.getElementById('btn-inst-submit-change');
  if (submitChangeBtn) {
    submitChangeBtn.addEventListener('click', () => {
      if (!currentUser || currentUser.role !== 'institution') return;
      const colNum = document.getElementById('inst-edit-college').value;
      const colText = document.getElementById('inst-edit-college').options[document.getElementById('inst-edit-college').selectedIndex].text;
      const courseName = document.getElementById('inst-edit-course').value;
      
      const intake = parseInt(document.getElementById('inst-edit-intake').value);
      const kea = parseInt(document.getElementById('inst-edit-kea').value);
      const comedk = parseInt(document.getElementById('inst-edit-comedk').value);
      const mgmt = parseInt(document.getElementById('inst-edit-mgmt').value);
      const fee = parseInt(document.getElementById('inst-edit-fee').value);

      if (isNaN(intake) || isNaN(kea) || isNaN(comedk) || isNaN(mgmt) || isNaN(fee)) {
        alert("Please enter valid seat and fee numbers.");
        return;
      }

      const collegeObj = allData.colleges.find(c => c.college_number == colNum);
      const reqId = Date.now();
      const newRequest = {
        id: reqId,
        group: currentUser.institutionGroup,
        collegeNum: colNum,
        collegeName: colText,
        keaCode: collegeObj ? collegeObj.kea_code : 'N/A',
        courseName: courseName,
        intake: intake,
        kea: kea,
        comedk: comedk,
        mgmt: mgmt,
        fee: fee,
        status: 'Pending'
      };

      pendingIntakeRequests.push(newRequest);
      alert(`Seat modification request for ${courseName} at ${colText} submitted to KCET Authority!`);
      
      renderInstitutionHistory();
      
      // Log in system logs
      const time = new Date().toLocaleTimeString();
      authorityLogs.push(`[${time}] REQUEST: ${colText} requested Intake to ${intake}, Fee to ₹${fee.toLocaleString()} for ${courseName}`);
    });
  }

  // Bind Authority announcement publish button
  const publishBtn = document.getElementById('btn-auth-publish');
  if (publishBtn) {
    publishBtn.addEventListener('click', () => {
      const input = document.getElementById('auth-announcement-input');
      const txt = input.value.trim();
      if (txt) {
        systemAnnouncements.push(txt);
        input.value = '';
        alert("Announcement published successfully!");
        
        // Log in system logs
        const time = new Date().toLocaleTimeString();
        authorityLogs.push(`[${time}] ANNOUNCEMENT: Published "${txt}"`);
        
        // Refresh alert display
        applyUserRole();
      }
    });
  }

  // Bind Clear Logs
  const clearBtn = document.getElementById('btn-clear-logs');
  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      authorityLogs = [`[System] Console cleared.`];
      renderAuthorityDashboard();
    });
  }

  // Bind Downloads
  const downloadInstCsv = document.getElementById('btn-inst-download-csv');
  if (downloadInstCsv) {
    downloadInstCsv.addEventListener('click', () => downloadInstitutionData('csv'));
  }
  const downloadInstJson = document.getElementById('btn-inst-download-json');
  if (downloadInstJson) {
    downloadInstJson.addEventListener('click', () => downloadInstitutionData('json'));
  }
  const downloadAuthCsv = document.getElementById('btn-auth-download-consolidated');
  if (downloadAuthCsv) {
    downloadAuthCsv.addEventListener('click', () => downloadAuthorityData('csv'));
  }
  const downloadAuthAudit = document.getElementById('btn-auth-download-audit');
  if (downloadAuthAudit) {
    downloadAuthAudit.addEventListener('click', () => downloadAuthorityData('txt'));
  }

  // Bind Option Entry priority builder events
  bindOptionEntryEvents();
  
  // Bind Counsellor Portfolio and Super User controller events
  bindCounsellorAndSuperUserEvents();

  // Bind Advanced Data Download Tab events
  bindDownloadTabEvents();
}

function setupInstitutionGroupColleges() {
  if (!allData || !currentUser) return;
  const isSuper = (currentUser.role === 'superuser' && superuserPerspective === 'institution');
  if (currentUser.role !== 'institution' && !isSuper) return;

  const groupId = isSuper ? superuserGroup : currentUser.institutionGroup;
  if (!groupId || !INSTITUTION_GROUPS[groupId]) return;

  const group = INSTITUTION_GROUPS[groupId];
  group.colleges = allData.colleges.filter(c => {
    const clean = getCleanCollegeName(c.college_name);
    return group.patterns.some(p => clean.includes(p));
  });
}

function renderInstitutionDashboard() {
  if (!currentUser) return;
  const isSuper = (currentUser.role === 'superuser' && superuserPerspective === 'institution');
  if (currentUser.role !== 'institution' && !isSuper) return;

  const groupId = isSuper ? superuserGroup : currentUser.institutionGroup;
  const group = INSTITUTION_GROUPS[groupId];
  if (!group) return;

  // 1. Calculate Group Stats
  const colleges = allData.colleges.filter(c => {
    const clean = getCleanCollegeName(c.college_name);
    return group.patterns.some(p => clean.includes(p));
  });

  let totalIntake = 0, totalKea = 0, totalComedk = 0, totalMgmt = 0;
  colleges.forEach(col => {
    col.courses.forEach(c => {
      totalIntake += c.total_intake || 0;
      totalKea    += c.total_kea_seats || 0;
      totalComedk += c.cat2_seats || 0;
      totalMgmt   += c.cat3_seats || 0;
    });
  });

  const cardsHtml = `
    <div class="summary-card" style="background:var(--bg-card); border:1px solid var(--border); padding:16px; border-radius:12px; display:flex; flex-direction:column; gap:6px;">
      <span style="font-size:11px; color:var(--text-muted); font-weight:600; text-transform:uppercase; letter-spacing:0.05em;">Group Colleges</span>
      <span style="font-size:24px; font-weight:800; font-family:var(--font-display); color:var(--text);">${colleges.length}</span>
    </div>
    <div class="summary-card" style="background:var(--bg-card); border:1px solid var(--border); padding:16px; border-radius:12px; display:flex; flex-direction:column; gap:6px;">
      <span style="font-size:11px; color:var(--text-muted); font-weight:600; text-transform:uppercase; letter-spacing:0.05em;">Total Group Intake</span>
      <span style="font-size:24px; font-weight:800; font-family:var(--font-display); color:var(--blue);">${totalIntake.toLocaleString()}</span>
    </div>
    <div class="summary-card" style="background:var(--bg-card); border:1px solid var(--border); padding:16px; border-radius:12px; display:flex; flex-direction:column; gap:6px;">
      <span style="font-size:11px; color:var(--text-muted); font-weight:600; text-transform:uppercase; letter-spacing:0.05em;">KEA Seats</span>
      <span style="font-size:24px; font-weight:800; font-family:var(--font-display); color:var(--green);">${totalKea.toLocaleString()}</span>
    </div>
    <div class="summary-card" style="background:var(--bg-card); border:1px solid var(--border); padding:16px; border-radius:12px; display:flex; flex-direction:column; gap:6px;">
      <span style="font-size:11px; color:var(--text-muted); font-weight:600; text-transform:uppercase; letter-spacing:0.05em;">COMEDK vs Mgmt</span>
      <span style="font-size:16px; font-weight:800; font-family:var(--font-display); color:var(--purple); display:flex; gap:10px; align-items:center; height:100%;">
        🎓 ${totalComedk.toLocaleString()} <span style="font-size:10px; color:var(--text-muted); font-weight:500;">vs</span> 💼 ${totalMgmt.toLocaleString()}
      </span>
    </div>
  `;
  document.getElementById('inst-summary-cards').innerHTML = cardsHtml;

  // 2. Populate College Dropdown
  const colSelect = document.getElementById('inst-edit-college');
  colSelect.innerHTML = colleges.map(c => `<option value="${c.college_number}">${c.college_name}</option>`).join('');

  // Course update listener
  const updateCoursesDropdown = () => {
    const colNum = colSelect.value;
    const college = colleges.find(c => c.college_number == colNum);
    const courseSelect = document.getElementById('inst-edit-course');
    if (college) {
      courseSelect.innerHTML = college.courses.map(c => `<option value="${escHtml(c.course_name)}">${c.course_name}</option>`).join('');
      updateSeatInputs();
    }
  };

  const updateSeatInputs = () => {
    const colNum = colSelect.value;
    const courseName = document.getElementById('inst-edit-course').value;
    const college = colleges.find(c => c.college_number == colNum);
    if (college) {
      const course = college.courses.find(c => c.course_name === courseName);
      if (course) {
        document.getElementById('inst-edit-intake').value = course.total_intake || 0;
        document.getElementById('inst-edit-kea').value = course.total_kea_seats || 0;
        document.getElementById('inst-edit-comedk').value = course.cat2_seats || 0;
        document.getElementById('inst-edit-mgmt').value = course.cat3_seats || 0;
        document.getElementById('inst-edit-fee').value = getSeatFees(college).rows[0]?.year1?.replace(/[^0-9]/g, '') || 120000;
      }
    }
  };

  colSelect.onchange = updateCoursesDropdown;
  document.getElementById('inst-edit-course').onchange = updateSeatInputs;

  updateCoursesDropdown();
  renderInstitutionHistory();
}

function renderInstitutionHistory() {
  const container = document.getElementById('inst-requests-history');
  if (pendingIntakeRequests.length === 0) {
    container.innerHTML = `<div style="font-size:12px; color:var(--text-muted); text-align:center; padding:20px 0;">No changes submitted in this session.</div>`;
    return;
  }

  const groupRequests = pendingIntakeRequests.filter(r => r.group === currentUser.institutionGroup);
  if (groupRequests.length === 0) {
    container.innerHTML = `<div style="font-size:12px; color:var(--text-muted); text-align:center; padding:20px 0;">No changes submitted in this session.</div>`;
    return;
  }

  container.innerHTML = groupRequests.map(r => {
    let statusBadge = '';
    if (r.status === 'Pending') statusBadge = '<span style="color:var(--purple); font-weight:700;">⏳ PENDING</span>';
    else if (r.status === 'Approved') statusBadge = '<span style="color:var(--green); font-weight:700;">🟢 APPROVED</span>';
    else statusBadge = '<span style="color:var(--pink); font-weight:700;">🔴 REJECTED</span>';

    return `
      <div style="background:rgba(255,255,255,0.02); border:1px solid var(--border); padding:10px 12px; border-radius:8px; display:flex; flex-direction:column; gap:4px; font-size:11px;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <strong style="color:var(--text); text-overflow:ellipsis; overflow:hidden; white-space:nowrap; max-width:180px;">${r.collegeName}</strong>
          ${statusBadge}
        </div>
        <div style="color:var(--text-muted); font-size:10px;">Course: ${r.courseName}</div>
        <div style="color:var(--text-muted); margin-top:2px;">Requested: Intake ${r.intake} | KEA ${r.kea} | COMEDK ${r.comedk} | Mgmt ${r.mgmt} | Fee ₹${r.fee.toLocaleString()}</div>
      </div>
    `;
  }).join('');
}

function renderAuthorityDashboard() {
  if (currentUser.role !== 'authority') return;

  // 1. Populate Approvals Queue
  const tbody = document.getElementById('authority-pending-tbody');
  const pending = pendingIntakeRequests.filter(r => r.status === 'Pending');

  if (pending.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="5" style="text-align:center; color:var(--text-muted); padding:30px;">No pending seat change requests from colleges.</td>
      </tr>
    `;
  } else {
    tbody.innerHTML = pending.map(r => `
      <tr>
        <td><strong>${r.collegeName}</strong><br><small style="color:var(--text-muted)">Code: ${r.keaCode || 'N/A'}</small></td>
        <td>${r.courseName}</td>
        <td>Intake & Fee matrix</td>
        <td>
          Intake: <strong>${r.intake}</strong> (KEA: ${r.kea}, COMEDK: ${r.comedk}, Mgmt: ${r.mgmt})<br>
          Proposed Fee: <strong>₹${r.fee.toLocaleString()}</strong>
        </td>
        <td style="text-align:center;">
          <div style="display:flex; gap:6px; justify-content:center;">
            <button class="auth-submit-btn" onclick="approveRequest(${r.id})" style="margin:0; padding:6px 12px; font-size:11px; background:var(--green); border-radius:4px;">Approve</button>
            <button class="auth-submit-btn" onclick="rejectRequest(${r.id})" style="margin:0; padding:6px 12px; font-size:11px; background:var(--pink); border-radius:4px;">Reject</button>
          </div>
        </td>
      </tr>
    `).join('');
  }

  // 2. Render Audit Logs
  const logEl = document.getElementById('auth-audit-logs');
  logEl.textContent = authorityLogs.join('\n');
  logEl.scrollTop = logEl.scrollHeight;

  // 3. Fetch and Render Live Database Activity Log & Summary metrics
  fetch('/api/admin/activities')
    .then(res => res.json())
    .then(data => {
      // Set registered counts
      const studentsCount = data.registrations.student || 0;
      const advisorsCount = data.registrations.counsellor || 0;
      document.getElementById('stat-students-count').textContent = studentsCount;
      document.getElementById('stat-advisors-count').textContent = advisorsCount;

      // Set action counts
      document.getElementById('stat-predictions-count').textContent = data.action_stats.PREDICTION || 0;
      document.getElementById('stat-downloads-count').textContent = data.action_stats.DOWNLOAD || 0;
      document.getElementById('stat-compare-count').textContent = data.action_stats.COMPARE || 0;

      // Render timeline list
      const timelineEl = document.getElementById('admin-activity-timeline');
      if (data.recent_logs && data.recent_logs.length > 0) {
        timelineEl.innerHTML = data.recent_logs.map(log => {
          let badgeColor = 'var(--text-muted)';
          if (log.action === 'REGISTER') badgeColor = 'var(--blue)';
          else if (log.action === 'LOGIN') badgeColor = 'var(--teal)';
          else if (log.action === 'PREDICTION') badgeColor = 'var(--green)';
          else if (log.action === 'OPTION_OPTIMIZE') badgeColor = 'rgba(168, 85, 247, 0.85)';
          else if (log.action === 'DOWNLOAD') badgeColor = 'var(--orange)';
          else if (log.action === 'COMPARE') badgeColor = 'var(--pink)';

          return `
            <div style="margin-bottom:8px; border-bottom:1px solid rgba(255,255,255,0.03); padding-bottom:6px; display:flex; align-items:flex-start; gap:8px;">
              <span style="background:${badgeColor}; color:#fff; padding:2px 6px; border-radius:4px; font-size:9px; font-weight:700; text-transform:uppercase; margin-top:2px;">${log.action}</span>
              <div style="flex:1;">
                <div style="display:flex; justify-content:space-between; margin-bottom:2px;">
                  <strong>${log.username}</strong>
                  <span style="color:var(--text-muted); font-size:10px;">${log.time_str} (${log.ip_address})</span>
                </div>
                <div style="color:var(--text-muted); font-size:10px; word-break:break-all;">${log.details || 'No details provided.'}</div>
              </div>
            </div>
          `;
        }).join('');
      } else {
        timelineEl.innerHTML = `<div style="color:var(--text-muted); text-align:center; padding:20px;">No user activities logged yet.</div>`;
      }
    })
    .catch(err => console.error("Error fetching authority metrics:", err));
}

function approveRequest(id) {
  const req = pendingIntakeRequests.find(r => r.id === id);
  if (req) {
    req.status = 'Approved';
    
    // Update raw seat matrix data in-memory
    const college = allData.colleges.find(c => c.college_number == req.collegeNum);
    if (college) {
      const course = college.courses.find(c => c.course_name === req.courseName);
      if (course) {
        course.total_intake = req.intake;
        course.total_kea_seats = req.kea;
        course.cat2_seats = req.comedk;
        course.cat3_seats = req.mgmt;
        
        // Update fees locally
        if (college.courses_fee) {
          college.courses_fee[req.courseName] = req.fee;
        } else {
          college.courses_fee = { [req.courseName]: req.fee };
        }
      }
    }

    const time = new Date().toLocaleTimeString();
    authorityLogs.push(`[${time}] APPROVED: ${req.collegeName} (${req.courseName}) intake set to ${req.intake}, fee set to ₹${req.fee.toLocaleString()}`);
    
    renderAuthorityDashboard();
    applyFilters();
  }
}

function rejectRequest(id) {
  const req = pendingIntakeRequests.find(r => r.id === id);
  if (req) {
    req.status = 'Rejected';
    const time = new Date().toLocaleTimeString();
    authorityLogs.push(`[${time}] REJECTED: ${req.collegeName} (${req.courseName}) seat modification request`);
    
    renderAuthorityDashboard();
  }
}

function downloadInstitutionData(format) {
  if (!currentUser || currentUser.role !== 'institution') return;
  const groupId = currentUser.institutionGroup;
  const group = INSTITUTION_GROUPS[groupId];
  if (!group) return;

  const groupColleges = allData.colleges.filter(c => {
    const clean = getCleanCollegeName(c.college_name);
    return group.patterns.some(p => clean.includes(p));
  });

  if (format === 'csv') {
    let csv = "College Code,College Name,Course Name,Total Intake,KEA Seats,COMEDK Seats,Management Seats\n";
    groupColleges.forEach(col => {
      col.courses.forEach(c => {
        csv += `"${col.kea_code || ''}","${col.college_name}","${c.course_name}",${c.total_intake || 0},${c.total_kea_seats || 0},${c.cat2_seats || 0},${c.cat3_seats || 0}\n`;
      });
    });
    triggerFileDownload(csv, `${groupId}_seat_matrix.csv`, "text/csv");
  } else if (format === 'json') {
    const jsonStr = JSON.stringify(groupColleges, null, 2);
    triggerFileDownload(jsonStr, `${groupId}_seat_matrix.json`, "application/json");
  }
}

function downloadAuthorityData(format) {
  if (!currentUser || currentUser.role !== 'authority') return;

  if (format === 'csv') {
    let csv = "College Code,College Name,District,Annexure,Course Name,Total Intake,KEA Seats,COMEDK Seats,Management Seats\n";
    allData.colleges.forEach(col => {
      col.courses.forEach(c => {
        csv += `"${col.kea_code || ''}","${col.college_name}","${col.district || ''}","${col.annexure || ''}","${c.course_name}",${c.total_intake || 0},${c.total_kea_seats || 0},${c.cat2_seats || 0},${c.cat3_seats || 0}\n`;
      });
    });
    triggerFileDownload(csv, "kcet_consolidated_seat_matrix_2025.csv", "text/csv");
  } else if (format === 'txt') {
    const logStr = authorityLogs.join("\n");
    triggerFileDownload(logStr, "authority_audit_logs.txt", "text/plain");
  }
}

function triggerFileDownload(content, filename, contentType) {
  // Log download action in PostgreSQL
  fetch('/api/log', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      username: currentUser ? currentUser.name : 'guest',
      action: 'DOWNLOAD',
      details: `Downloaded file: ${filename} (${contentType})`
    })
  }).catch(err => console.error(err));

  const blob = new Blob([content], { type: contentType });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

// Make helper functions globally accessible for inline actions
window.approveRequest = approveRequest;
window.rejectRequest = rejectRequest;

function applyUserRole() {
  const profileChip = document.getElementById('user-profile-chip');
  const roleBadge = document.getElementById('user-role-badge');
  const nameDisplay = document.getElementById('user-display-name');
  const studentProfileSection = document.getElementById('student-profile-section');
  const counsellorPortfolioSection = document.getElementById('counsellor-portfolio-section');
  const tabInst = document.getElementById('tab-institution');
  const tabAuth = document.getElementById('tab-authority');
  const tabOption = document.getElementById('tab-option-entry');
  const superuserBar = document.getElementById('superuser-view-bar');
  const scrollingWrap = document.getElementById('scrolling-announcements-wrap');

  // Toggle scrolling alerts bar
  if (scrollingWrap) {
    scrollingWrap.style.display = systemAnnouncements.length > 0 ? 'flex' : 'none';
    const textEl = document.getElementById('scrolling-announcements-text');
    if (textEl) textEl.textContent = systemAnnouncements.join(" | ");
  }

  if (!currentUser) {
    if (profileChip) profileChip.style.display = 'none';
    if (studentProfileSection) studentProfileSection.style.display = 'none';
    if (counsellorPortfolioSection) counsellorPortfolioSection.style.display = 'none';
    if (tabInst) tabInst.style.display = 'none';
    if (tabAuth) tabAuth.style.display = 'none';
    if (tabOption) tabOption.style.display = 'block';
    if (superuserBar) superuserBar.style.display = 'none';
    return;
  }

  // Display user profile status
  if (profileChip) {
    profileChip.style.display = 'flex';
    nameDisplay.textContent = currentUser.name;
    roleBadge.textContent = currentUser.role;
    if (currentUser.role === 'student') {
      roleBadge.style.background = 'var(--blue)';
    } else if (currentUser.role === 'institution') {
      roleBadge.style.background = 'var(--teal)';
    } else if (currentUser.role === 'counsellor') {
      roleBadge.style.background = 'rgba(168, 85, 247, 0.85)'; // Purple for advisor
    } else if (currentUser.role === 'superuser') {
      roleBadge.style.background = 'var(--pink)'; // Pink for superuser
    } else {
      roleBadge.style.background = 'var(--pink)';
    }
  }

  // Superuser Bar visibility
  if (superuserBar) {
    superuserBar.style.display = currentUser.role === 'superuser' ? 'flex' : 'none';
  }

  // Determine effective perspective/role
  const effectiveRole = currentUser.role === 'superuser' ? superuserPerspective : currentUser.role;

  // Show/Hide downloads tab based on eligibility
  const tabDownloads = document.getElementById('tab-downloads');
  if (tabDownloads) {
    tabDownloads.style.display = 'block';
  }

  // Render dashboard elements based on effective role
  if (effectiveRole === 'student') {
    if (studentProfileSection) {
      studentProfileSection.style.display = 'block';
      document.getElementById('profile-rank').value = currentUser.rank || 5000;
      document.getElementById('profile-category').value = currentUser.category || 'GM';
    }
    if (counsellorPortfolioSection) counsellorPortfolioSection.style.display = 'none';
    if (tabInst) tabInst.style.display = 'none';
    if (tabAuth) tabAuth.style.display = 'none';
    if (tabOption) tabOption.style.display = 'block';

    // Sync to Predictor Tab
    const prRank = document.getElementById('pred-rank');
    const prCat = document.getElementById('pred-category');
    if (prRank) prRank.value = currentUser.rank || 5000;
    if (prCat) prCat.value = currentUser.category || 'GM';

  } else if (effectiveRole === 'counsellor') {
    if (studentProfileSection) studentProfileSection.style.display = 'none';
    if (counsellorPortfolioSection) counsellorPortfolioSection.style.display = 'block';
    if (tabInst) tabInst.style.display = 'none';
    if (tabAuth) tabAuth.style.display = 'none';
    if (tabOption) tabOption.style.display = 'block';

    renderCounsellorPortfolio();

  } else if (effectiveRole === 'institution') {
    if (studentProfileSection) studentProfileSection.style.display = 'none';
    if (counsellorPortfolioSection) counsellorPortfolioSection.style.display = 'none';
    if (tabInst) tabInst.style.display = 'block';
    if (tabAuth) tabAuth.style.display = 'none';
    if (tabOption) tabOption.style.display = 'block';

    setupInstitutionGroupColleges();
    renderInstitutionDashboard();

  } else if (effectiveRole === 'authority') {
    if (studentProfileSection) studentProfileSection.style.display = 'none';
    if (counsellorPortfolioSection) counsellorPortfolioSection.style.display = 'none';
    if (tabInst) tabInst.style.display = 'none';
    if (tabAuth) tabAuth.style.display = 'block';
    if (tabOption) tabOption.style.display = 'block';

    renderAuthorityDashboard();
  }

  // Update download live preview if eligible
  if (effectiveRole !== 'student') {
    updateDownloadPreview();
  }

  // Go to Colleges tab by default on role change
  const collegesTab = document.getElementById('tab-colleges');
  if (collegesTab) collegesTab.click();

  // Apply filtering
  applyFilters();
  setupViewportSimulator();
}

// ─────────────────────────────────────────────────────
// Option Entry List Priority Builder
// ─────────────────────────────────────────────────────
const OPTION_BRANCH_MAP = {
  CS: ["computer science", "cse", "information science", "ise", "artificial intelligence", "data science", "aiml", "cyber security", "software", "computer technology"],
  EC: ["electronics", "ece", "telecommunication", "communication", "tele-communication"],
  EE: ["electrical", "eee"],
  ME: ["mechanical", "me", "automobile"],
  CE: ["civil"],
  AD: ["artificial intelligence", "data science", "aiml", "machine learning"]
};

function getActiveStudentProfile() {
  const sidebarRank = parseInt(document.getElementById('pred-rank')?.value || document.getElementById('profile-rank')?.value || 5000);
  const sidebarCat = document.getElementById('pred-category')?.value || document.getElementById('profile-category')?.value || 'GM';

  if (!currentUser) return { rank: sidebarRank, category: sidebarCat };
  if (currentUser.role === 'counsellor') {
    const activeStudent = currentUser.students.find(s => s.id === currentUser.activeStudentId);
    if (activeStudent) {
      return { rank: activeStudent.rank, category: activeStudent.category };
    }
  }
  return { rank: currentUser.rank || sidebarRank, category: currentUser.category || sidebarCat };
}

function getChanceClass(cutoff, studentRank) {
  if (!cutoff || cutoff === 999999) return 'dream';
  if (studentRank <= cutoff * 0.9) return 'safety';
  if (studentRank > cutoff * 1.15) return 'dream';
  return 'target';
}

function initializeSessions() {
  try {
    kcetSessions = JSON.parse(localStorage.getItem('kcet_sessions_list')) || [];
    currentSessionId = localStorage.getItem('kcet_current_session_id') || '';
  } catch(e) {
    kcetSessions = [];
    currentSessionId = '';
  }

  // If no sessions exist, seed with a default Guest profile
  if (kcetSessions.length === 0) {
    const defaultSession = {
      id: 'session_' + Date.now(),
      name: 'Default Guest Profile',
      rank: 5000,
      category: 'GM',
      options: studentOptionsList || []
    };
    kcetSessions.push(defaultSession);
    currentSessionId = defaultSession.id;
    saveSessionsList();
  }

  // Ensure current session id is valid, else fallback to first
  const exists = kcetSessions.some(s => s.id === currentSessionId);
  if (!exists) {
    currentSessionId = kcetSessions[0].id;
    localStorage.setItem('kcet_current_session_id', currentSessionId);
  }

  renderSessionDropdown();
  loadActiveSessionData();
}

function saveSessionsList() {
  localStorage.setItem('kcet_sessions_list', JSON.stringify(kcetSessions));
  localStorage.setItem('kcet_current_session_id', currentSessionId);
}

function renderSessionDropdown() {
  const select = document.getElementById('session-select');
  if (!select) return;

  select.innerHTML = kcetSessions.map(s => 
    `<option value="${s.id}" ${s.id === currentSessionId ? 'selected' : ''}>${escHtml(s.name)} (Rank: ${s.rank.toLocaleString()} - ${s.category})</option>`
  ).join('');
}

function loadActiveSessionData() {
  const activeSession = kcetSessions.find(s => s.id === currentSessionId);
  if (!activeSession) return;

  // Sync priority list
  studentOptionsList = activeSession.options || [];

  // Sync sidebar predictor inputs
  const prRank = document.getElementById('pred-rank');
  const prCat = document.getElementById('pred-category');
  if (prRank) prRank.value = activeSession.rank;
  if (prCat) prCat.value = activeSession.category;

  // Run updates
  renderOptionEntryList();
  if (typeof applyFilters === 'function') {
    applyFilters();
  }
}

function syncCurrentSessionState() {
  const activeSession = kcetSessions.find(s => s.id === currentSessionId);
  if (!activeSession) return;

  const prRank = parseInt(document.getElementById('pred-rank')?.value || 5000);
  const prCat = document.getElementById('pred-category')?.value || 'GM';

  activeSession.rank = prRank;
  activeSession.category = prCat;
  activeSession.options = studentOptionsList;

  saveSessionsList();
  renderSessionDropdown();
}

function createNewSession() {
  const name = prompt("Enter Student/Candidate Name:", "Student " + (kcetSessions.length + 1));
  if (!name) return;

  const { rank: studentRank, category: studentCategory } = getActiveStudentProfile();

  const newSession = {
    id: 'session_' + Date.now(),
    name: name,
    rank: studentRank,
    category: studentCategory,
    options: []
  };

  kcetSessions.push(newSession);
  currentSessionId = newSession.id;

  saveSessionsList();
  renderSessionDropdown();
  loadActiveSessionData();
  alert(`Created and switched to student session: "${name}"`);
}

function deleteCurrentSession() {
  if (kcetSessions.length <= 1) {
    alert("Cannot delete the only student session profile!");
    return;
  }

  const activeSession = kcetSessions.find(s => s.id === currentSessionId);
  if (!activeSession) return;

  if (confirm(`Are you sure you want to delete session profile: "${activeSession.name}"?`)) {
    kcetSessions = kcetSessions.filter(s => s.id !== currentSessionId);
    currentSessionId = kcetSessions[0].id;

    saveSessionsList();
    renderSessionDropdown();
    loadActiveSessionData();
  }
}

function saveCounsellorOptions() {
  if (currentUser && currentUser.role === 'counsellor') {
    const activeStudent = currentUser.students.find(s => s.id === currentUser.activeStudentId);
    if (activeStudent) {
      activeStudent.optionList = studentOptionsList;
      localStorage.setItem('kcet_user', JSON.stringify(currentUser));
    }
  } else {
    localStorage.setItem('kcet_student_options', JSON.stringify(studentOptionsList));
  }
  
  // Sync back to our Student Session manager state
  syncCurrentSessionState();
}

function renderCounsellorPortfolio() {
  const select = document.getElementById('counsellor-student-select');
  if (!select || !currentUser || currentUser.role !== 'counsellor') return;

  const activeId = currentUser.activeStudentId || '';
  select.innerHTML = currentUser.students.map(s => 
    `<option value="${s.id}" ${s.id === activeId ? 'selected' : ''}>${s.name} (Rank: ${s.rank.toLocaleString()} - ${s.category})</option>`
  ).join('');

  // Update active student details in sidebar/predictor
  const activeStudent = currentUser.students.find(s => s.id === activeId);
  if (activeStudent) {
    // Populate optionList
    studentOptionsList = activeStudent.optionList || [];
    renderOptionEntryList();

    // Sync Rank & Category to Rank Predictor Tab
    const prRank = document.getElementById('pred-rank');
    const prCat = document.getElementById('pred-category');
    if (prRank) prRank.value = activeStudent.rank;
    if (prCat) prCat.value = activeStudent.category;
  }
}

function bindCounsellorAndSuperUserEvents() {
  // 1. Counsellor portfolio active student selection change
  const select = document.getElementById('counsellor-student-select');
  if (select) {
    select.addEventListener('change', () => {
      if (!currentUser || currentUser.role !== 'counsellor') return;
      currentUser.activeStudentId = select.value;
      localStorage.setItem('kcet_user', JSON.stringify(currentUser));
      
      const activeStudent = currentUser.students.find(s => s.id === select.value);
      if (activeStudent) {
        studentOptionsList = activeStudent.optionList || [];
        renderOptionEntryList();
      }
      applyFilters();
    });
  }

  // 2. Toggle collapse add student form
  const toggleBtn = document.getElementById('btn-toggle-add-portfolio-student');
  const formDiv = document.getElementById('counsellor-add-student-form');
  if (toggleBtn && formDiv) {
    toggleBtn.addEventListener('click', () => {
      formDiv.style.display = formDiv.style.display === 'none' ? 'block' : 'none';
      toggleBtn.textContent = formDiv.style.display === 'none' ? '➖ Close Add Form' : '➕ Add Student to Portfolio';
    });
  }

  // 3. Submit add student to portfolio
  const submitAddBtn = document.getElementById('btn-submit-add-portfolio-student');
  if (submitAddBtn) {
    submitAddBtn.addEventListener('click', () => {
      if (!currentUser || currentUser.role !== 'counsellor') return;
      const name = document.getElementById('cs-add-name').value.trim();
      const rank = parseInt(document.getElementById('cs-add-rank').value);
      const category = document.getElementById('cs-add-category').value;

      if (!name || isNaN(rank) || rank <= 0) {
        alert("Please enter a valid student name and rank.");
        return;
      }

      const newStudent = {
        id: 'cs_' + Date.now(),
        name: name,
        rank: rank,
        category: category,
        optionList: []
      };

      currentUser.students.push(newStudent);
      currentUser.activeStudentId = newStudent.id;
      localStorage.setItem('kcet_user', JSON.stringify(currentUser));

      // Reset form
      document.getElementById('cs-add-name').value = '';
      document.getElementById('cs-add-rank').value = '';
      formDiv.style.display = 'none';
      if (toggleBtn) toggleBtn.textContent = '➕ Add Student to Portfolio';

      alert(`Successfully added ${name} to your mentoring portfolio!`);
      applyUserRole();
    });
  }

  // 4. Super User Perspective switches
  document.querySelectorAll('#su-perspective-buttons button').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('#su-perspective-buttons button').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      superuserPerspective = btn.dataset.view;

      // Show/Hide group select for institution view
      const groupWrap = document.getElementById('su-group-selector-wrap');
      if (groupWrap) {
        groupWrap.style.display = superuserPerspective === 'institution' ? 'flex' : 'none';
      }

      applyUserRole();
    });
  });

  // 5. Super User Group Selector
  const suGroupSelect = document.getElementById('su-group-select');
  if (suGroupSelect) {
    suGroupSelect.addEventListener('change', () => {
      superuserGroup = suGroupSelect.value;
      if (currentUser && currentUser.role === 'superuser' && superuserPerspective === 'institution') {
        setupInstitutionGroupColleges();
        renderInstitutionDashboard();
        applyFilters();
      }
    });
  }
}

function matchesBranch(courseName, branchCode) {
  const lower = courseName.toLowerCase();
  const patterns = OPTION_BRANCH_MAP[branchCode] || [];
  return patterns.some(p => lower.includes(p));
}

function getCourseCutoff(course, category) {
  const r1 = course.round1_cutoff ? parseInt(course.round1_cutoff[category]) : NaN;
  const r2 = course.round2_cutoff ? parseInt(course.round2_cutoff[category]) : NaN;
  const r3 = course.round3_cutoff ? parseInt(course.round3_cutoff[category]) : NaN;
  return r3 || r2 || r1 || NaN;
}

function generateSeedPriorities() {
  const effectiveRole = currentUser ? (currentUser.role === 'superuser' ? superuserPerspective : currentUser.role) : 'student';
  if (currentUser && effectiveRole !== 'student' && effectiveRole !== 'counsellor') return;

  // 1. Get Selected Branch Prefixes
  const activeBranchChips = document.querySelectorAll('#option-branch-chips .chip.active');
  const selectedBranches = Array.from(activeBranchChips).map(c => c.dataset.branch);

  // 2. Get Selected Locations
  const activeLocChips = document.querySelectorAll('#option-location-chips .chip.active');
  const selectedLocs = Array.from(activeLocChips).map(c => c.dataset.dist);

  if (selectedBranches.length === 0) {
    alert("Please select at least one branch interest.");
    return;
  }

  const { rank: studentRank, category: studentCategory } = getActiveStudentProfile();

  // 3. Find Matches
  const matches = [];
  allData.colleges.forEach(col => {
    // Filter location
    const colDist = (col.district || '').toUpperCase();
    const matchesLoc = selectedLocs.length === 0 || selectedLocs.some(l => colDist.includes(l));
    if (!matchesLoc) return;

    col.courses.forEach(c => {
      // Filter branch
      const matchesBranchCheck = selectedBranches.some(b => matchesBranch(c.course_name, b));
      if (!matchesBranchCheck) return;

      const cutoff = getCourseCutoff(c, studentCategory);
      if (isNaN(cutoff)) return; // Ignore if no cutoff data

      // Determine chance classification
      let chanceClass = 'safety';
      if (cutoff < studentRank) chanceClass = 'dream';
      else if (cutoff >= studentRank && cutoff <= studentRank * 1.25) chanceClass = 'target';

      matches.push({
        id: col.college_number + '_' + c.course_name,
        collegeNum: col.college_number,
        collegeName: col.college_name,
        keaCode: col.kea_code,
        courseName: c.course_name,
        cutoff: cutoff,
        chanceClass: chanceClass
      });
    });
  });

  // Sort strictly by cutoff rank ascending (highest quality/hardest to get first)
  matches.sort((a, b) => a.cutoff - b.cutoff);

  // Take top 100 matching priority options to keep it clean and performant
  studentOptionsList = matches.slice(0, 100);
  
  saveCounsellorOptions();

  alert(`Successfully generated ${studentOptionsList.length} options matching your profile rank & preferences!`);
  renderOptionEntryList();
}

function renderOptionEntryList() {
  const tbody = document.getElementById('option-entry-tbody');
  if (!tbody) return;

  const { rank: studentRank, category: studentCategory } = getActiveStudentProfile();

  if (studentOptionsList.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="5" style="text-align:center; color:var(--text-muted); padding:40px;">Your priority list is empty. Set your branch/location preferences above and click Generate, or add custom options manually.</td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = studentOptionsList.map((opt, index) => {
    const priority = index + 1;
    
    // Dynamic feasibility recalculation
    let cutoff = opt.cutoff;
    let chanceClass = opt.chanceClass;
    if (allData && allData.colleges) {
      const collegeObj = allData.colleges.find(col => col.college_number == opt.collegeNum || col.kea_code == opt.keaCode);
      if (collegeObj) {
        const courseObj = collegeObj.courses.find(c => c.course_name === opt.courseName);
        if (courseObj) {
          cutoff = getCourseCutoff(courseObj, studentCategory) || 999999;
          chanceClass = getChanceClass(cutoff, studentRank);
          // Sync back to object
          opt.cutoff = cutoff;
          opt.chanceClass = chanceClass;
        }
      }
    }

    let badgeHtml = '';
    if (chanceClass === 'dream') {
      badgeHtml = '<span class="chance-badge chance-dream">Dream</span>';
    } else if (chanceClass === 'target') {
      badgeHtml = '<span class="chance-badge chance-target">Target</span>';
    } else {
      badgeHtml = '<span class="chance-badge chance-safety">Safety</span>';
    }

    // Disable UP button if first item, disable DOWN button if last item
    const upDisabled = priority === 1 ? 'disabled style="opacity:0.3; cursor:not-allowed;"' : '';
    const downDisabled = priority === studentOptionsList.length ? 'disabled style="opacity:0.3; cursor:not-allowed;"' : '';

    return `
      <tr id="priority-row-${priority}">
        <td class="priority-row-num">${priority}</td>
        <td>
          <div style="font-weight:600; color:var(--text);">${opt.collegeName}</div>
          <small style="color:var(--text-muted)">KEA Code: <span class="kea-code-badge" style="padding:1px 6px; font-size:9px;">${opt.keaCode || 'N/A'}</span></small>
        </td>
        <td><strong>${opt.courseName}</strong><br><small style="color:var(--text-muted)">Cutoff Rank: ${opt.cutoff.toLocaleString()}</small></td>
        <td style="text-align:center;">${badgeHtml}</td>
        <td>
          <div style="display:flex; gap:6px; justify-content:center;">
            <button class="reorder-btn" onclick="movePriorityOption(${index}, -1)" ${upDisabled} title="Move Up">▲</button>
            <button class="reorder-btn" onclick="movePriorityOption(${index}, 1)" ${downDisabled} title="Move Down">▼</button>
            <button class="reorder-btn" onclick="deletePriorityOption(${index})" title="Delete" style="color:var(--pink); border-color:rgba(244,63,94,0.2);">🗑️</button>
          </div>
        </td>
      </tr>
    `;
  }).join('');

  auditStudentOptionsList();
}

function auditStudentOptionsList() {
  const container = document.getElementById('options-audit-container');
  const badge = document.getElementById('options-audit-badge');
  const budget = document.getElementById('options-audit-budget');
  const warningsList = document.getElementById('options-audit-warnings');
  
  if (!container || !badge || !budget || !warningsList) return;

  if (studentOptionsList.length === 0) {
    container.style.display = 'none';
    return;
  }

  container.style.display = 'flex';
  const { rank: studentRank, category: studentCategory } = getActiveStudentProfile();

  const warnings = [];
  let totalFee = 0;
  let safetyCount = 0;

  const parseFeeVal = (str) => {
    if (!str) return 0;
    const clean = str.replace(/[^0-9]/g, '');
    return parseInt(clean) || 0;
  };

  // 1. Fee calculations & safety count
  studentOptionsList.forEach((opt) => {
    if (allData && allData.colleges) {
      const collegeObj = allData.colleges.find(col => col.college_number == opt.collegeNum || col.kea_code == opt.keaCode);
      if (collegeObj) {
        const courseObj = collegeObj.courses.find(c => c.course_name === opt.courseName);
        if (courseObj) {
          const cutoff = getCourseCutoff(courseObj, studentCategory) || 999999;
          const chanceClass = getChanceClass(cutoff, studentRank);
          opt.cutoff = cutoff;
          opt.chanceClass = chanceClass;

          // Fee calculations
          const feeStr = getCourseFee(collegeObj, opt.courseName, courseObj.total_kea_seats);
          const feeVal = parseFeeVal(feeStr);
          totalFee += feeVal;

          if (chanceClass === 'safety') {
            safetyCount++;
          }
        }
      }
    }
  });

  // 2. Check for out-of-order cutoff ranks (the main KEA algorithm sequence rule)
  for (let i = 1; i < studentOptionsList.length; i++) {
    const prev = studentOptionsList[i - 1];
    const curr = studentOptionsList[i];

    if (prev.cutoff && curr.cutoff && curr.cutoff < prev.cutoff * 0.85) {
      warnings.push({
        type: 'out-of-order',
        text: `⚠️ <strong>Out of Order:</strong> Option ${i+1} (${curr.courseName} at ${curr.collegeName}) has a tougher cutoff (<strong>${curr.cutoff.toLocaleString()}</strong>) than Option ${i} (${prev.courseName} at ${prev.collegeName}, Cutoff: <strong>${prev.cutoff.toLocaleString()}</strong>). Under KEA's allocation, Option ${i} will always prevent Option ${i+1} from being considered.`
      });
    }
  }

  // 3. Safety Check
  if (safetyCount === 0) {
    warnings.push({
      type: 'high-risk',
      text: `❌ <strong>High Risk:</strong> You have <strong>0 safety options</strong> in your choices list. If you do not meet the cutoffs for your Dream/Target options, you will not receive any allotment. Consider adding options with cutoff ranks higher than <strong>${Math.round(studentRank * 1.15).toLocaleString()}</strong>.`
    });
  } else if (safetyCount < 3) {
    warnings.push({
      type: 'low-safety',
      text: `⚠️ <strong>Low Safety Margin:</strong> You only have <strong>${safetyCount} safety options</strong>. It is highly recommended to add at least 3 safety options to prevent blank allotments.`
    });
  }

  // Update budget display
  budget.textContent = `Annual Fee Budget: ₹${totalFee.toLocaleString()}`;

  // Update badge status
  if (warnings.length === 0) {
    badge.textContent = '✅ Sequence Optimal';
    badge.style.background = 'rgba(34,197,94,0.15)';
    badge.style.color = '#22c55e';
    warningsList.innerHTML = `<div style="font-size:11px; color:#22c55e; padding:8px 12px; background:rgba(34,197,94,0.05); border-radius:6px; border:1px solid rgba(34,197,94,0.1);">All checks passed! Your options sheet matches KEA choice entry strategies perfectly.</div>`;
  } else {
    const hasError = warnings.some(w => w.type === 'high-risk');
    badge.textContent = hasError ? '❌ Strategic Flaws Found' : '⚠️ Warnings Found';
    badge.style.background = hasError ? 'rgba(244,63,94,0.15)' : 'rgba(234,179,8,0.15)';
    badge.style.color = hasError ? '#f43f5e' : '#eab308';

    warningsList.innerHTML = warnings.map(w => `
      <div style="font-size:11px; color:var(--text); padding:8px 12px; background:rgba(255,255,255,0.02); border-radius:6px; border:1px solid var(--border); display:flex; flex-direction:column; gap:4px;">
        <div>${w.text}</div>
      </div>
    `).join('');
  }
}

function optimizeStudentOptionsList() {
  if (studentOptionsList.length === 0) return;

  studentOptionsList.sort((a, b) => {
    const cutA = a.cutoff || 999999;
    const cutB = b.cutoff || 999999;
    return cutA - cutB;
  });

  // Log option optimization in PostgreSQL
  fetch('/api/log', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      username: currentUser ? currentUser.name : 'guest',
      action: 'OPTION_OPTIMIZE',
      details: `Optimized sequence of ${studentOptionsList.length} choices`
    })
  }).catch(err => console.error(err));

  saveCounsellorOptions();
  renderOptionEntryList();
}

function movePriorityOption(index, direction) {
  const newIndex = index + direction;
  if (newIndex < 0 || newIndex >= studentOptionsList.length) return;

  // Swap elements
  const temp = studentOptionsList[index];
  studentOptionsList[index] = studentOptionsList[newIndex];
  studentOptionsList[newIndex] = temp;

  saveCounsellorOptions();
  renderOptionEntryList();

  // Highlight swapped rows for visual confirmation
  const row1 = document.getElementById(`priority-row-${index + 1}`);
  const row2 = document.getElementById(`priority-row-${newIndex + 1}`);
  if (row1) row1.classList.add('priority-row-highlight');
  if (row2) row2.classList.add('priority-row-highlight');
}

function deletePriorityOption(index) {
  studentOptionsList.splice(index, 1);
  saveCounsellorOptions();
  renderOptionEntryList();
}

window.movePriorityOption = movePriorityOption;
window.deletePriorityOption = deletePriorityOption;

function bindOptionEntryEvents() {
  // 1. Branch chips toggles
  document.querySelectorAll('#option-branch-chips .chip').forEach(chip => {
    chip.addEventListener('click', () => {
      chip.classList.toggle('active');
    });
  });

  // 2. Location chips toggles
  document.querySelectorAll('#option-location-chips .chip').forEach(chip => {
    chip.addEventListener('click', () => {
      chip.classList.toggle('active');
    });
  });

  // 3. Generate button
  const genBtn = document.getElementById('btn-generate-options');
  if (genBtn) {
    genBtn.addEventListener('click', generateSeedPriorities);
  }

  // 4. Clear priorities
  const clearBtn = document.getElementById('btn-clear-options');
  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      if (confirm("Are you sure you want to clear your prioritized option entry sheet?")) {
        studentOptionsList = [];
        saveCounsellorOptions();
        renderOptionEntryList();
      }
    });
  }

  // Print priorities
  const printBtn = document.getElementById('btn-print-options');
  if (printBtn) {
    printBtn.addEventListener('click', () => {
      if (studentOptionsList.length === 0) {
        alert("Your priority option list is empty!");
        return;
      }
      
      const printWindow = window.open('', '_blank');
      const rowsHtml = studentOptionsList.map((opt, index) => `
        <tr>
          <td style="text-align:center; padding:8px; border:1px solid #ddd;">${index + 1}</td>
          <td style="padding:8px; border:1px solid #ddd;"><strong>${opt.collegeName}</strong></td>
          <td style="text-align:center; padding:8px; border:1px solid #ddd;"><code style="background:#f5f5f5; padding:2px 6px; border-radius:4px;">${opt.keaCode || 'N/A'}</code></td>
          <td style="padding:8px; border:1px solid #ddd;">${opt.courseName}</td>
          <td style="text-align:center; padding:8px; border:1px solid #ddd; text-transform:uppercase; font-weight:700; color:${opt.chanceClass === 'dream' ? '#f43f5e' : opt.chanceClass === 'target' ? '#eab308' : '#22c55e'}">${opt.chanceClass}</td>
        </tr>
      `).join('');

      printWindow.document.write(`
        <html>
          <head>
            <title>KEA KCET Priority Choice Checklist</title>
            <style>
              body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; padding: 20px; color: #333; }
              h1 { font-size: 20px; margin-bottom: 5px; text-align: center; }
              p { font-size: 12px; margin-bottom: 20px; text-align: center; color: #666; }
              table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 12px; }
              th { background: #f0f0f0; padding: 10px; border: 1px solid #ddd; font-weight: 700; }
              footer { margin-top: 30px; text-align: center; font-size: 10px; color: #999; border-top: 1px solid #eee; padding-top: 10px; }
            </style>
          </head>
          <body>
            <h1>KEA KCET Priority Choice Checklist</h1>
            <p>Generated on ${new Date().toLocaleDateString()} - Keep this form handy during your official choice entry.</p>
            <table>
              <thead>
                <tr>
                  <th style="width:80px;">Option No</th>
                  <th>College Name</th>
                  <th style="width:100px;">KEA Code</th>
                  <th>Course / Branch</th>
                  <th style="width:120px;">Feasibility Chance</th>
                </tr>
              </thead>
              <tbody>
                ${rowsHtml}
              </tbody>
            </table>
            <footer>Generated via KCET Seat Matrix & Predictor Portal</footer>
            <script>
              window.onload = function() {
                window.print();
                window.close();
              }
            </script>
          </body>
        </html>
      `);
      printWindow.document.close();
    });
  }

  // 5. Export priorities
  const exportBtn = document.getElementById('btn-export-options');
  if (exportBtn) {
    exportBtn.addEventListener('click', () => {
      if (studentOptionsList.length === 0) {
        alert("Your priority option list is empty!");
        return;
      }
      let csv = "Priority Index,KEA Code,College Name,Course Name,Cutoff Rank,Category Chance\n";
      studentOptionsList.forEach((opt, index) => {
        csv += `${index+1},"${opt.keaCode || ''}","${opt.collegeName}","${opt.courseName}",${opt.cutoff},"${opt.chanceClass.toUpperCase()}"\n`;
      });
      triggerFileDownload(csv, "my_kcet_prioritized_options.csv", "text/csv");
    });
  }

  // 6. Autocomplete custom search-and-add options
  const searchInput = document.getElementById('option-search-input');
  const searchResults = document.getElementById('option-search-results');
  const searchCourseSelect = document.getElementById('option-search-course');
  const addOptionBtn = document.getElementById('btn-add-searched-option');

  let selectedCollegeForAdd = null;

  if (searchInput) {
    searchInput.addEventListener('input', () => {
      const q = searchInput.value.toLowerCase().trim();
      if (!q) {
        searchResults.style.display = 'none';
        return;
      }

      // Filter matches
      const matches = allData.colleges.filter(c => 
        c.college_name.toLowerCase().includes(q) || 
        (c.kea_code || '').toLowerCase().includes(q)
      ).slice(0, 8);

      if (matches.length === 0) {
        searchResults.innerHTML = `<div style="padding:10px; font-size:12px; color:var(--text-muted); text-align:center;">No colleges found.</div>`;
      } else {
        searchResults.innerHTML = matches.map(c => `
          <div class="option-search-item" data-id="${c.college_number}">
            <strong>${c.college_name}</strong> <span style="font-size:10px; color:var(--blue); font-weight:700; margin-left:6px;">${c.kea_code || ''}</span>
          </div>
        `).join('');
      }

      searchResults.style.display = 'block';

      // Bind search items
      const bindSearchResults = () => {
        document.querySelectorAll('.option-search-item').forEach(item => {
          item.addEventListener('click', () => {
            const colId = item.dataset.id;
            selectedCollegeForAdd = allData.colleges.find(c => c.college_number == colId);
            
            if (selectedCollegeForAdd) {
              searchInput.value = selectedCollegeForAdd.college_name;
              searchResults.style.display = 'none';
              
              // Populate courses select dropdown
              searchCourseSelect.disabled = false;
              searchCourseSelect.innerHTML = `<option value="">Choose Course...</option>` + 
                selectedCollegeForAdd.courses.map(c => `<option value="${escHtml(c.course_name)}">${c.course_name}</option>`).join('');
            }
          });
        });
      };
      bindSearchResults();
    });

    // Close dropdown on click outside
    document.addEventListener('click', (e) => {
      if (searchInput && !searchInput.contains(e.target) && !searchResults.contains(e.target)) {
        searchResults.style.display = 'none';
      }
    });
  }

  if (searchCourseSelect) {
    searchCourseSelect.addEventListener('change', () => {
      const activeVal = searchCourseSelect.value;
      if (activeVal && selectedCollegeForAdd) {
        addOptionBtn.disabled = false;
      } else {
        addOptionBtn.disabled = true;
      }
    });
  }

  if (addOptionBtn) {
    addOptionBtn.addEventListener('click', () => {
      if (!selectedCollegeForAdd) return;
      const courseName = searchCourseSelect.value;
      const courseObj = selectedCollegeForAdd.courses.find(c => c.course_name === courseName);
      if (!courseObj) return;

      const { rank: studentRank, category: studentCategory } = getActiveStudentProfile();
      const cutoff = getCourseCutoff(courseObj, studentCategory) || 999999;

      let chanceClass = 'safety';
      if (cutoff < studentRank) chanceClass = 'dream';
      else if (cutoff >= studentRank && cutoff <= studentRank * 1.25) chanceClass = 'target';

      const newOpt = {
        id: selectedCollegeForAdd.college_number + '_' + courseName,
        collegeNum: selectedCollegeForAdd.college_number,
        collegeName: selectedCollegeForAdd.college_name,
        keaCode: selectedCollegeForAdd.kea_code,
        courseName: courseName,
        cutoff: cutoff,
        chanceClass: chanceClass
      };

      // Check for duplicate
      if (studentOptionsList.some(o => o.id === newOpt.id)) {
        alert("This option is already in your priority list!");
        return;
      }

      studentOptionsList.push(newOpt);
      saveCounsellorOptions();
      renderOptionEntryList();

      // Reset
      searchInput.value = '';
      searchCourseSelect.disabled = true;
      searchCourseSelect.innerHTML = `<option value="">Choose Course...</option>`;
      addOptionBtn.disabled = true;
      selectedCollegeForAdd = null;
    });
  }

  // 7. Optimize Priorities
  const optimizeBtn = document.getElementById('btn-optimize-options');
  if (optimizeBtn) {
    optimizeBtn.addEventListener('click', optimizeStudentOptionsList);
  }

  // 8. Counselor/Student Session Management
  const sessionSelect = document.getElementById('session-select');
  if (sessionSelect) {
    sessionSelect.addEventListener('change', (e) => {
      currentSessionId = e.target.value;
      localStorage.setItem('kcet_current_session_id', currentSessionId);
      loadActiveSessionData();
    });
  }

  const createSessionBtn = document.getElementById('btn-session-create');
  if (createSessionBtn) {
    createSessionBtn.addEventListener('click', createNewSession);
  }

  const deleteSessionBtn = document.getElementById('btn-session-delete');
  if (deleteSessionBtn) {
    deleteSessionBtn.addEventListener('click', deleteCurrentSession);
  }

  // Sidebar rank/category listeners to sync dynamic session changes
  const sidebarRankInput = document.getElementById('pred-rank');
  const sidebarCatSelect = document.getElementById('pred-category');
  if (sidebarRankInput) {
    sidebarRankInput.addEventListener('change', () => {
      syncCurrentSessionState();
      renderOptionEntryList();
    });
    sidebarRankInput.addEventListener('input', () => {
      syncCurrentSessionState();
      renderOptionEntryList();
    });
  }
  if (sidebarCatSelect) {
    sidebarCatSelect.addEventListener('change', () => {
      syncCurrentSessionState();
      renderOptionEntryList();
    });
  }
}

// ─────────────────────────────
// Filtering
// ─────────────────────────────
function applyFilters() {
  const sidebar = document.querySelector('.sidebar');
  const mobileOverlay = document.getElementById('mobile-drawer-overlay');
  if (sidebar && sidebar.classList.contains('open')) {
    sidebar.classList.remove('open');
    if (mobileOverlay) mobileOverlay.style.display = 'none';
  }

  const { search, annexure, district, course, minSeats } = filters;
  const q = search.toLowerCase().trim();
  const affiliationVal = document.getElementById('affiliation-filter')?.value || '';
  const naacVal = document.getElementById('naac-filter')?.value || '';
  const nbaVal = document.getElementById('nba-filter')?.value || '';
  const minSalaryVal = parseFloat(document.getElementById('min-salary')?.value || 0);
  const maxHostelVal = parseInt(document.getElementById('max-hostel')?.value || 150000);

  let baseColleges = allData.colleges;
  const isInst = (currentUser && currentUser.role === 'institution');
  const isSuperInst = (currentUser && currentUser.role === 'superuser' && superuserPerspective === 'institution');
  if (isInst || isSuperInst) {
    const groupId = isSuperInst ? superuserGroup : currentUser.institutionGroup;
    if (groupId && INSTITUTION_GROUPS[groupId]) {
      const groupColleges = INSTITUTION_GROUPS[groupId].colleges;
      const groupCleanNames = new Set(groupColleges.map(col => getCleanCollegeName(col.college_name)));
      baseColleges = allData.colleges.filter(col => groupCleanNames.has(getCleanCollegeName(col.college_name)));
    }
  }

  filtered = baseColleges.filter(c => {
    if (c.annexure === 'E' || c.annexure === 'V') return false;
    if (annexure !== 'all' && c.annexure !== annexure) return false;
    if (district && c.district !== district) return false;
    if (course) {
      const has = c.courses.some(cr => cr.course_name === course);
      if (!has) return false;
    }
    if (minSeats > 0 && (c.total_intake || 0) < minSeats) return false;
    if (affiliationVal) {
      if (affiliationVal === 'Autonomous') {
        if (!c.affiliation || !c.affiliation.includes('Autonomous')) return false;
      } else if (affiliationVal === 'Private University') {
        if (!c.affiliation || !c.affiliation.includes('Private University')) return false;
      } else if (affiliationVal === 'State University') {
        if (!c.affiliation || !c.affiliation.includes('State University')) return false;
      } else if (affiliationVal === 'VTU Affiliated (Government)') {
        if (!c.affiliation || !c.affiliation.includes('VTU Affiliated (Government)')) return false;
      } else if (affiliationVal === 'VTU Affiliated') {
        if (!c.affiliation || c.affiliation !== 'VTU Affiliated') return false;
      }
    }
    if (naacVal) {
      if (!c.naac_grade) return false;
      if (naacVal === 'A++' && c.naac_grade !== 'A++') return false;
      if (naacVal === 'A+') {
        if (c.naac_grade !== 'A++' && c.naac_grade !== 'A+') return false;
      }
      if (naacVal === 'A') {
        if (c.naac_grade !== 'A++' && c.naac_grade !== 'A+' && c.naac_grade !== 'A') return false;
      }
      if (naacVal === 'B++') {
        if (c.naac_grade === 'B' || c.naac_grade === 'C') return false;
      }
    }
    if (nbaVal) {
      const isAcc = !!c.nba_accredited;
      if (nbaVal === 'Accredited' && !isAcc) return false;
      if (nbaVal === 'Not Accredited' && isAcc) return false;
    }
    if (minSalaryVal > 0) {
      if (!c.placement_stats || (c.placement_stats.avg_package_lpa || 0) < minSalaryVal) return false;
    }
    if (maxHostelVal < 150000) {
      if (!c.hostel_details || (c.hostel_details.annual_hostel_fees || 0) > maxHostelVal) return false;
    }
    if (q) {
      const nameMatch = c.college_name.toLowerCase().includes(q);
      const addrMatch = (c.address || '').toLowerCase().includes(q);
      const distMatch = (c.district || '').toLowerCase().includes(q);
      const codeMatch = (c.kea_code || '').toLowerCase().includes(q);
      if (!nameMatch && !addrMatch && !distMatch && !codeMatch) return false;
    }
    return true;
  });

  sortFiltered();
  displayCount = 30;
  renderColleges();
  updateSidebarStats();
  renderCourseTable();

  // Update totals tab
  const activeBtn = document.querySelector('.totals-ann-btn.active');
  const activeAnnFilter = activeBtn ? activeBtn.dataset.ann : 'ALL';
  renderTotals(activeAnnFilter);
}

function sortFiltered() {
  if (sortMode === 'name') {
    filtered.sort((a, b) => a.college_name.localeCompare(b.college_name));
  } else if (sortMode === 'seats-desc') {
    filtered.sort((a, b) => (b.total_intake || 0) - (a.total_intake || 0));
  } else if (sortMode === 'kea-desc') {
    filtered.sort((a, b) => (b.total_kea_seats || 0) - (a.total_kea_seats || 0));
  } else if (sortMode === 'district') {
    filtered.sort((a, b) => (a.district || '').localeCompare(b.district || ''));
  }
}

function updateSidebarStats() {
  const totalSeats = filtered.reduce((s, c) => s + (c.total_intake || 0), 0);
  document.getElementById('ss-count').textContent = `${filtered.length.toLocaleString()} colleges`;
  document.getElementById('ss-seats').textContent = `${totalSeats.toLocaleString()} total seats`;
}

// ─────────────────────────────
// Render Colleges
// ─────────────────────────────
function renderColleges() {
  const grid = document.getElementById('colleges-grid');
  const toShow = filtered.slice(0, displayCount);

  if (filtered.length === 0) {
    grid.innerHTML = `<div class="empty-state" style="grid-column:1/-1">
      <div class="empty-state-icon">🔍</div>
      <div class="empty-state-text">No colleges match your filters.<br><small style="color:#4a5a7a">Try adjusting the search or filters.</small></div>
    </div>`;
    document.getElementById('load-more-wrap').style.display = 'none';
    return;
  }

  grid.innerHTML = toShow.map((c, i) => renderCollegeCard(c, i)).join('');

  // Load more button
  const lmw = document.getElementById('load-more-wrap');
  const lmb = document.getElementById('load-more-btn');
  if (displayCount >= filtered.length) {
    lmw.style.display = 'none';
  } else {
    lmw.style.display = 'flex';
    lmb.textContent = `Load More Colleges (${filtered.length - displayCount} remaining)`;
  }

  // Bind card clicks using unique college_number lookup
  grid.querySelectorAll('.college-card').forEach(el => {
    el.addEventListener('click', () => {
      const colNum = el.dataset.collegeNumber;
      const collegeObj = allData.colleges.find(c => c.college_number == colNum);
      if (collegeObj) openModal(collegeObj);
    });
  });
}

function renderCollegeCard(college, index) {
  const ann = college.annexure || 'C';
  const annLabel = ANNEXURE_LABELS[ann] || ann;

  const totalIntake = college.total_intake || college.courses.reduce((s, c) => s + (c.total_intake || 0), 0);
  const totalKea = college.total_kea_seats || college.courses.reduce((s, c) => s + (c.total_kea_seats || 0), 0);
  const totalComedk = college.courses.reduce((s, c) => s + (c.cat2_seats || 0), 0);
  const totalMgmt = college.courses.reduce((s, c) => s + (c.cat3_seats || 0), 0);

  const courseNames = [...new Set(college.courses.map(c => c.course_name))];
  const shownCourses = courseNames.slice(0, 3);
  const moreCourses = courseNames.length - 3;

  const courseTagsHtml = shownCourses.map(name =>
    `<span class="course-tag">${abbrCourseName(name)}</span>`
  ).join('') + (moreCourses > 0 ? `<span class="course-tag more">+${moreCourses} more</span>` : '');

  const seatsHtml = `
    <div class="seat-pill total">
      <span class="seat-pill-val">${totalIntake.toLocaleString()}</span>
      <span class="seat-pill-lbl">Total</span>
    </div>
    <div class="seat-pill kea">
      <span class="seat-pill-val">${totalKea.toLocaleString()}</span>
      <span class="seat-pill-lbl">KEA</span>
    </div>
    ${totalComedk > 0 ? `<div class="seat-pill comedk">
      <span class="seat-pill-val">${totalComedk.toLocaleString()}</span>
      <span class="seat-pill-lbl">COMEDK</span>
    </div>` : ''}
    ${totalMgmt > 0 ? `<div class="seat-pill mgmt">
      <span class="seat-pill-val">${totalMgmt.toLocaleString()}</span>
      <span class="seat-pill-lbl">Mgmt</span>
    </div>` : ''}
  `;

  const estBadg = college.established_year ? `<span class="meta-badge" style="background:rgba(255,255,255,0.04); color:var(--text-muted); padding:2px 6px; border-radius:4px; font-size:10px; font-weight:600; display:inline-flex; align-items:center; gap:3px; border:1px solid var(--border);">📅 Est. ${college.established_year}</span>` : '';
  const affBadg = college.affiliation ? `<span class="meta-badge" style="background:rgba(59,130,246,0.06); color:var(--blue); padding:2px 6px; border-radius:4px; font-size:10px; font-weight:600; display:inline-flex; align-items:center; gap:3px; border:1px solid rgba(59,130,246,0.15);">🎓 ${college.affiliation}</span>` : '';
  const nirfBadg = college.nirf_ranking ? `<span class="meta-badge" style="background:rgba(234,179,8,0.06); color:#eab308; padding:2px 6px; border-radius:4px; font-size:10px; font-weight:700; display:inline-flex; align-items:center; gap:3px; border:1px solid rgba(234,179,8,0.15);">🏆 NIRF #${college.nirf_ranking}</span>` : '';
  const naacBadg = college.naac_grade ? `<span class="meta-badge" style="background:rgba(168,85,247,0.06); color:#a855f7; padding:2px 6px; border-radius:4px; font-size:10px; font-weight:700; display:inline-flex; align-items:center; gap:3px; border:1px solid rgba(168,85,247,0.15);">🎖️ NAAC ${college.naac_grade}</span>` : '';
  const nbaBadg = college.nba_accredited ? `<span class="meta-badge" style="background:rgba(20,184,166,0.06); color:#14b8a6; padding:2px 6px; border-radius:4px; font-size:10px; font-weight:700; display:inline-flex; align-items:center; gap:3px; border:1px solid rgba(20,184,166,0.15);">🛡️ NBA</span>` : '';
  const placementInfo = college.placement_stats ? `<span class="meta-badge" style="background:rgba(34,197,94,0.06); color:#22c55e; padding:2px 6px; border-radius:4px; font-size:10px; font-weight:700; display:inline-flex; align-items:center; gap:3px; border:1px solid rgba(34,197,94,0.15);">💼 Avg: ${college.placement_stats.avg_package_lpa} LPA</span>` : '';
  const hostelInfo = college.hostel_details ? `<span class="meta-badge" style="background:rgba(249,115,22,0.06); color:#f97316; padding:2px 6px; border-radius:4px; font-size:10px; font-weight:700; display:inline-flex; align-items:center; gap:3px; border:1px solid rgba(249,115,22,0.15);">🏠 Hostel: ₹${Math.round(college.hostel_details.annual_hostel_fees/1000)}k/yr</span>` : '';

  return `
    <div class="college-card" style="animation-delay:${Math.min(index * 0.03, 0.3)}s" data-index="${index}" data-college-number="${college.college_number}">
      <div class="card-top">
        <div class="card-badge badge-${ann}">${ANNEXURE_ICONS[ann]}</div>
        <div class="card-info">
          <div class="card-name">${college.kea_code ? `<span class="kea-code-badge">${college.kea_code}</span> ` : ''}${escHtml(college.college_name)}</div>
          <div class="card-location">
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
               <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/>
               <circle cx="12" cy="9" r="2.5"/>
            </svg>
            ${escHtml(college.district || 'Karnataka')}
          </div>
          <div style="display:flex; flex-wrap:wrap; gap:4px; margin-top:6px;">
            ${estBadg}
            ${affBadg}
            ${nirfBadg}
            ${naacBadg}
            ${nbaBadg}
            ${placementInfo}
            ${hostelInfo}
          </div>
        </div>
        <span class="card-type-pill pill-${ann}">${annLabel}</span>
      </div>
      <div class="card-seats">${seatsHtml}</div>
      <div class="card-courses">${courseTagsHtml}</div>
    </div>
  `;
}

// ─────────────────────────────
// Course Table
// ─────────────────────────────
function renderCourseTable() {
  const tbody = document.getElementById('courses-tbody');
  // Build course stats from filtered colleges
  const courseMap = {};
  filtered.forEach(college => {
    college.courses.forEach(c => {
      const name = c.course_name;
      if (!courseMap[name]) courseMap[name] = { total: 0, kea: 0, colleges: new Set() };
      courseMap[name].total += c.total_intake || 0;
      courseMap[name].kea += c.total_kea_seats || 0;
      courseMap[name].colleges.add(college.college_name);
    });
  });

  const rows = Object.entries(courseMap)
    .map(([name, s]) => ({ name, ...s, colleges: s.colleges.size }))
    .sort((a, b) => b.total - a.total);

  const maxTotal = rows[0]?.total || 1;

  tbody.innerHTML = rows.map(row => {
    const pct = row.total > 0 ? Math.round((row.kea / row.total) * 100) : 0;
    const pctClass = pct >= 60 ? 'pct-high' : pct >= 40 ? 'pct-mid' : 'pct-low';
    const barWidth = Math.round((row.total / maxTotal) * 100);
    return `<tr>
      <td>${row.name}</td>
      <td>${row.colleges}</td>
      <td>${row.total.toLocaleString()}</td>
      <td>${row.kea.toLocaleString()}</td>
      <td><span class="kea-pct-badge ${pctClass}">${pct}%</span></td>
      <td>
        <div class="mini-bar-wrap">
          <div class="mini-bar-bg"><div class="mini-bar-fill" style="width:${barWidth}%"></div></div>
          <div class="mini-bar-lbl">${row.total.toLocaleString()} seats</div>
        </div>
      </td>
    </tr>`;
  }).join('');
}

// ─────────────────────────────
// Statistics Charts
// ─────────────────────────────
function renderStats() {
  renderDonutChart();
  renderDistrictBarChart();
  renderCourseBarChart();
  renderQuotaDistributionChart();
  renderSunburstChart();
  renderSankeyChart();
}

function renderQuotaDistributionChart() {
  let totalKea = 0;
  let totalComedk = 0;
  let totalMgmt = 0;

  filtered.forEach(col => {
    col.courses.forEach(c => {
      totalKea += (c.total_kea_seats || 0);
      totalComedk += (c.cat2_seats || 0);
      totalMgmt += (c.cat3_seats || 0);
    });
  });

  const grandTotal = totalKea + totalComedk + totalMgmt || 1;

  const keaPct = ((totalKea / grandTotal) * 100).toFixed(1);
  const comedkPct = ((totalComedk / grandTotal) * 100).toFixed(1);
  const mgmtPct = ((totalMgmt / grandTotal) * 100).toFixed(1);

  const barKea = document.getElementById('quota-bar-kea');
  const barComedk = document.getElementById('quota-bar-comedk');
  const barMgmt = document.getElementById('quota-bar-mgmt');

  if (barKea) barKea.style.width = `${keaPct}%`;
  if (barComedk) barComedk.style.width = `${comedkPct}%`;
  if (barMgmt) barMgmt.style.width = `${mgmtPct}%`;

  const valKea = document.getElementById('quota-val-kea');
  const valComedk = document.getElementById('quota-val-comedk');
  const valMgmt = document.getElementById('quota-val-mgmt');

  if (valKea) valKea.innerHTML = `${totalKea.toLocaleString()}<span style="font-size: 11px; font-weight: normal; color: var(--text-muted);"> (${keaPct}%)</span>`;
  if (valComedk) valComedk.innerHTML = `${totalComedk.toLocaleString()}<span style="font-size: 11px; font-weight: normal; color: var(--text-muted);"> (${comedkPct}%)</span>`;
  if (valMgmt) valMgmt.innerHTML = `${totalMgmt.toLocaleString()}<span style="font-size: 11px; font-weight: normal; color: var(--text-muted);"> (${mgmtPct}%)</span>`;
}

function renderDonutChart() {
  const annCounts = {};
  filtered.forEach(c => {
    let colSeats = 0;
    c.courses.forEach(cr => { colSeats += cr.total_intake || 0; });
    annCounts[c.annexure] = (annCounts[c.annexure] || 0) + colSeats;
  });

  const items = Object.entries(ANNEXURE_LABELS).map(([k, label], i) => ({
    label: label,
    value: annCounts[k] || 0,
    color: CHART_COLORS[i % CHART_COLORS.length]
  })).filter(item => item.value > 0);

  const total = items.reduce((s, i) => s + i.value, 0);
  if (total === 0) {
    const wrap = document.getElementById('donut-svg-wrap');
    if (wrap) wrap.innerHTML = `<div style="font-size:12px; color:var(--text-muted); text-align:center; padding:50px 0;">No seat data.</div>`;
    return;
  }

  // SVG donut
  const size = 180, cx = 90, cy = 90, r = 70, strokeW = 24;
  let offset = -90;
  const arcs = items.map(item => {
    const pct = item.value / total;
    const angle = pct * 360;
    const startAngle = offset;
    offset += angle;
    return { ...item, pct, startAngle, endAngle: offset };
  });

  const pathD = (startA, endA, r, cx, cy) => {
    const s = polarToCart(cx, cy, r, startA);
    const e = polarToCart(cx, cy, r, endA);
    const largeArc = (endA - startA) > 180 ? 1 : 0;
    return `M ${cx} ${cy} L ${s.x} ${s.y} A ${r} ${r} 0 ${largeArc} 1 ${e.x} ${e.y} Z`;
  };

  const svgPaths = arcs.map(a => `
    <path d="${pathD(a.startAngle, a.endAngle, r, cx, cy)}"
          fill="${a.color}" opacity="0.9"
          style="transform-origin:${cx}px ${cy}px; transition:transform 0.2s"
          onmouseenter="this.style.transform='scale(1.04)'"
          onmouseleave="this.style.transform='scale(1)'"
    >
      <title>${a.label}: ${a.value.toLocaleString()} seats (${Math.round(a.pct*100)}%)</title>
    </path>
  `).join('');

  const svg = `<svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
    ${svgPaths}
    <circle cx="${cx}" cy="${cy}" r="40" fill="var(--bg-card)"/>
  </svg>`;

  const wrap = document.getElementById('donut-svg-wrap');
  if (wrap) wrap.innerHTML = svg;

  // Legends
  const legends = items.map(a => `
    <div class="legend-item" style="display:flex; align-items:center; gap:8px; font-size:11px; margin-bottom:4px;">
      <span style="width:10px; height:10px; border-radius:50%; background:${a.color}; display:inline-block;"></span>
      <span style="color:var(--text); font-weight:500;">${a.label}:</span>
      <span style="color:var(--text-muted);">${a.value.toLocaleString()} (${Math.round((a.value/total)*100)}%)</span>
    </div>
  `).join('');
  const legWrap = document.getElementById('donut-legends');
  if (legWrap) legWrap.innerHTML = legends;
}

function classifyCourseStream(courseName) {
  const name = courseName.toLowerCase();
  if (name.includes("computer science") || name.includes("cse") || name.includes("information science") || name.includes("ise") || name.includes("information technology") || name.includes("software engineering")) {
    return "IT & Software";
  } else if (name.includes("electronics") || name.includes("ece") || name.includes("electrical") || name.includes("eee") || name.includes("telecommunication") || name.includes("communication")) {
    return "Electronics & Electrical";
  } else if (name.includes("artificial intelligence") || name.includes("data science") || name.includes("cyber security") || name.includes("machine learning") || name.includes("aiml") || name.includes("robotics") || name.includes("iot") || name.includes("cloud computing") || name.includes("internet of things")) {
    return "Allied & Emerging Tech";
  } else {
    return "Core Engineering";
  }
}

function renderSunburstChart() {
  const wrap = document.getElementById('sunburst-svg-wrap');
  const legWrap = document.getElementById('sunburst-legends');
  if (!wrap || !legWrap) return;

  // Stream mapping config
  const STREAM_COLORS = {
    "IT & Software": "#3b82f6", // var(--blue)
    "Electronics & Electrical": "#a855f7", // Purple
    "Allied & Emerging Tech": "#14b8a6", // Teal
    "Core Engineering": "#f97316" // Orange
  };

  // 1. Aggregate hierarchical data
  const streamData = {};
  let totalIntake = 0;

  filtered.forEach(c => {
    c.courses.forEach(cr => {
      const intake = cr.total_intake || 0;
      if (intake <= 0) return;

      const courseName = cr.course_name;
      const stream = classifyCourseStream(courseName);
      totalIntake += intake;

      if (!streamData[stream]) {
        streamData[stream] = { seats: 0, branches: {} };
      }
      streamData[stream].seats += intake;
      streamData[stream].branches[courseName] = (streamData[stream].branches[courseName] || 0) + intake;
    });
  });

  if (totalIntake === 0) {
    wrap.innerHTML = `<div style="font-size:12px; color:var(--text-muted); text-align:center; padding:50px 0;">No seat data.</div>`;
    legWrap.innerHTML = "";
    return;
  }

  // Convert to sorted lists
  const hierarchy = Object.entries(streamData).map(([streamName, data]) => {
    const sortedBranches = Object.entries(data.branches).map(([name, seats]) => ({
      name,
      seats,
      pct: seats / totalIntake
    })).sort((a, b) => b.seats - a.seats);

    return {
      name: streamName,
      seats: data.seats,
      pct: data.seats / totalIntake,
      color: STREAM_COLORS[streamName] || "#94a3b8",
      branches: sortedBranches
    };
  }).sort((a, b) => b.seats - a.seats);

  // 2. Generate SVG arc paths
  const cx = 160, cy = 160;
  const r1_in = 45, r1_out = 80;
  const r2_in = 83, r2_out = 125;

  let currentAngle = 0;
  const sectors1 = []; // Inner stream category arcs
  const sectors2 = []; // Outer course branch arcs

  const makeArcPath = (cx, cy, rIn, rOut, startAngle, endAngle) => {
    const radStart = ((startAngle - 90) * Math.PI) / 180;
    const radEnd = ((endAngle - 90) * Math.PI) / 180;
    
    const x1_out = cx + rOut * Math.cos(radStart);
    const y1_out = cy + rOut * Math.sin(radStart);
    const x2_out = cx + rOut * Math.cos(radEnd);
    const y2_out = cy + rOut * Math.sin(radEnd);
    
    const x1_in = cx + rIn * Math.cos(radEnd);
    const y1_in = cy + rIn * Math.sin(radEnd);
    const x2_in = cx + rIn * Math.cos(radStart);
    const y2_in = cy + rIn * Math.sin(radStart);
    
    const largeArc = (endAngle - startAngle) > 180 ? 1 : 0;
    
    return `M ${x1_out} ${y1_out} A ${rOut} ${rOut} 0 ${largeArc} 1 ${x2_out} ${y2_out} L ${x1_in} ${y1_in} A ${rIn} ${rIn} 0 ${largeArc} 0 ${x2_in} ${y2_in} Z`;
  };

  hierarchy.forEach(stream => {
    const streamAngle = stream.pct * 360;
    const startStreamAngle = currentAngle;
    const endStreamAngle = currentAngle + streamAngle;

    sectors1.push({
      name: stream.name,
      seats: stream.seats,
      pct: stream.pct,
      color: stream.color,
      path: makeArcPath(cx, cy, r1_in, r1_out, startStreamAngle, endStreamAngle),
      id: `sb-stream-${stream.name.replace(/\s+/g, '-')}`
    });

    let outerAngle = startStreamAngle;
    stream.branches.forEach((branch, idx) => {
      const branchPctOfTotal = branch.pct;
      const branchAngle = branchPctOfTotal * 360;
      const startBranchAngle = outerAngle;
      const endBranchAngle = outerAngle + branchAngle;
      outerAngle += branchAngle;

      sectors2.push({
        name: branch.name,
        parentName: stream.name,
        seats: branch.seats,
        pct: branchPctOfTotal,
        color: stream.color,
        opacity: 0.55 + (idx % 4) * 0.15, // Lightness/opacity variation
        path: makeArcPath(cx, cy, r2_in, r2_out, startBranchAngle, endBranchAngle)
      });
    });

    currentAngle = endStreamAngle;
  });

  // Render SVG
  const innerPathsHtml = sectors1.map(s => `
    <path class="sunburst-sector sunburst-inner" d="${s.path}" fill="${s.color}" opacity="0.9" id="${s.id}" data-name="${s.name}" data-seats="${s.seats}" data-pct="${Math.round(s.pct * 100)}%"></path>
  `).join('');

  const outerPathsHtml = sectors2.map(s => `
    <path class="sunburst-sector sunburst-outer" d="${s.path}" fill="${s.color}" opacity="${s.opacity}" data-parent="${s.parentName}" data-name="${s.name}" data-seats="${s.seats}" data-pct="${(s.pct * 100).toFixed(1)}%"></path>
  `).join('');

  wrap.innerHTML = `
    <svg width="320" height="320" viewBox="0 0 320 320" style="position:relative; z-index:2;">
      ${innerPathsHtml}
      ${outerPathsHtml}
      <circle cx="${cx}" cy="${cy}" r="40" fill="var(--bg-card2)"></circle>
    </svg>
    <div id="sunburst-center-card" style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 76px; height: 76px; border-radius: 50%; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; pointer-events: none; z-index: 10;">
      <div id="sb-center-title" style="font-size: 8px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 2px;">Admissions</div>
      <div id="sb-center-seats" style="font-size: 11px; font-weight: 800; color: var(--text); line-height: 1.1;">Hover<br>Sectors</div>
    </div>
  `;

  // Render legends grouped by streams
  const legendHtml = hierarchy.map(stream => {
    const branchesLegend = stream.branches.slice(0, 5).map(b => `
      <div style="display:flex; justify-content:space-between; align-items:center; font-size:10px; color:var(--text-muted); margin-left:14px; padding:2px 0;">
        <span>• ${b.name}</span>
        <span style="font-weight:600; color:var(--text);">${b.seats.toLocaleString()}</span>
      </div>
    `).join('');

    return `
      <div style="background:rgba(255,255,255,0.01); border:1px solid var(--border); border-radius:8px; padding:10px; margin-bottom:8px;">
        <div style="display:flex; align-items:center; gap:8px; font-size:11px; font-weight:700; color:var(--text); margin-bottom:6px;">
          <span style="width:10px; height:10px; border-radius:50%; background:${stream.color}; display:inline-block;"></span>
          <span>${stream.name}</span>
          <span style="margin-left:auto; color:var(--text-muted); font-size:10px;">${stream.seats.toLocaleString()} (${Math.round(stream.pct * 100)}%)</span>
        </div>
        ${branchesLegend}
        ${stream.branches.length > 5 ? `<div style="font-size:9px; color:var(--text-faint); margin-left:14px; margin-top:2px;">+ ${stream.branches.length - 5} more branches</div>` : ''}
      </div>
    `;
  }).join('');
  
  legWrap.innerHTML = legendHtml;

  // 3. Add Hover interactive highlights
  const sectors = wrap.querySelectorAll('.sunburst-sector');
  const centerTitle = wrap.querySelector('#sb-center-title');
  const centerSeats = wrap.querySelector('#sb-center-seats');

  sectors.forEach(sec => {
    sec.addEventListener('mouseenter', () => {
      // Fade out others
      sectors.forEach(s => {
        if (s !== sec) {
          s.style.opacity = '0.15';
        } else {
          s.style.opacity = '1';
        }
      });

      const name = sec.getAttribute('data-name');
      const seats = parseInt(sec.getAttribute('data-seats')).toLocaleString();
      const pct = sec.getAttribute('data-pct');
      const isParent = sec.classList.contains('sunburst-inner');

      if (isParent) {
        centerTitle.textContent = name;
        centerTitle.style.color = sec.getAttribute('fill');
        centerSeats.innerHTML = `<span style="font-size:12px; font-weight:800;">${seats}</span><br><span style="font-size:9px; color:var(--text-muted);">${pct}</span>`;
      } else {
        const parent = sec.getAttribute('data-parent');
        centerTitle.textContent = name;
        centerTitle.style.color = sec.getAttribute('fill');
        centerSeats.innerHTML = `<span style="font-size:12px; font-weight:800;">${seats}</span><br><span style="font-size:9px; color:var(--text-muted);">${pct}</span>`;
      }
    });

    sec.addEventListener('mouseleave', () => {
      // Restore opacities
      sectors1.forEach(s => {
        const el = wrap.querySelector(`#${s.id}`);
        if (el) el.style.opacity = '0.9';
      });
      sectors2.forEach((s, idx) => {
        const el = wrap.querySelectorAll('.sunburst-outer')[idx];
        if (el) el.style.opacity = s.opacity.toString();
      });

      centerTitle.textContent = "Admissions";
      centerTitle.style.color = "var(--text-muted)";
      centerSeats.innerHTML = `Hover<br>Sectors`;
    });
  });
}

function renderSankeyChart() {
  const wrap = document.getElementById('sankey-svg-wrap');
  const tooltipPanel = document.getElementById('sankey-tooltip-panel');
  if (!wrap) return;

  // 1. Calculate flows and seats dynamically from active filtered dataset
  let totalKeaSeats = 0;
  
  // Reservation totals
  let resGeneral = 0;
  let resRural = 0;
  let resKannada = 0;
  let resHk = 0;

  // Stream totals
  const streamSeats = {
    "IT & Software": 0,
    "Electronics & Electrical": 0,
    "Allied & Emerging Tech": 0,
    "Core Engineering": 0
  };

  // Flow details: Reservation Category -> Stream Category
  const flowMatrix = {
    "General Quota": { "IT & Software": 0, "Electronics & Electrical": 0, "Allied & Emerging Tech": 0, "Core Engineering": 0 },
    "Rural Quota": { "IT & Software": 0, "Electronics & Electrical": 0, "Allied & Emerging Tech": 0, "Core Engineering": 0 },
    "Kannada Medium": { "IT & Software": 0, "Electronics & Electrical": 0, "Allied & Emerging Tech": 0, "Core Engineering": 0 },
    "HK Local Quota": { "IT & Software": 0, "Electronics & Electrical": 0, "Allied & Emerging Tech": 0, "Core Engineering": 0 }
  };

  filtered.forEach(c => {
    c.courses.forEach(cr => {
      const seats = cr.total_kea_seats || 0;
      if (seats <= 0) return;

      totalKeaSeats += seats;

      // Classify branch stream
      const stream = classifyCourseStream(cr.course_name);
      streamSeats[stream] += seats;

      // Reservation splits
      const g = seats * 0.60;
      const r = seats * 0.25;
      const k = seats * 0.05;
      const h = seats * 0.10;

      resGeneral += g;
      resRural += r;
      resKannada += k;
      resHk += h;

      // Accumulate flows
      flowMatrix["General Quota"][stream] += g;
      flowMatrix["Rural Quota"][stream] += r;
      flowMatrix["Kannada Medium"][stream] += k;
      flowMatrix["HK Local Quota"][stream] += h;
    });
  });

  if (totalKeaSeats === 0) {
    wrap.innerHTML = `<div style="font-size:12px; color:var(--text-muted); text-align:center; padding:50px 0;">No KEA seats found.</div>`;
    return;
  }

  // 2. Compute Nodes Heights & Y Coordinates (D3-like Proportional Scaler)
  const svgW = 540, svgH = 340;
  const colX = [30, 240, 450];
  const nodeW = 16;
  const nodePadding = 18;
  const heightBudget = 250;
  const scale = heightBudget / totalKeaSeats;

  // Nodes definition
  const nodes = {
    col0: [
      { name: "KEA Seat Pool", seats: totalKeaSeats, color: "var(--text-muted)", id: "n-kea" }
    ],
    col1: [
      { name: "General Quota", seats: resGeneral, color: "#3b82f6", id: "n-res-gen" }, // Blue
      { name: "Rural Quota", seats: resRural, color: "#14b8a6", id: "n-res-rur" }, // Teal
      { name: "HK Local Quota", seats: resHk, color: "#f97316", id: "n-res-hk" }, // Orange
      { name: "Kannada Medium", seats: resKannada, color: "#a855f7", id: "n-res-kan" } // Purple
    ],
    col2: [
      { name: "IT & Software", seats: streamSeats["IT & Software"], color: "#3b82f6", id: "n-str-it" },
      { name: "Electronics & Electrical", seats: streamSeats["Electronics & Electrical"], color: "#a855f7", id: "n-str-ec" },
      { name: "Allied & Emerging Tech", seats: streamSeats["Allied & Emerging Tech"], color: "#14b8a6", id: "n-str-al" },
      { name: "Core Engineering", seats: streamSeats["Core Engineering"], color: "#f97316", id: "n-str-co" }
    ]
  };

  // Helper to compute node Ys (centered vertically)
  const computeYs = (colNodes) => {
    const totalHeight = colNodes.reduce((acc, n) => acc + (n.seats * scale), 0) + (colNodes.length - 1) * nodePadding;
    let startY = 40 + (heightBudget - totalHeight) / 2;
    colNodes.forEach(n => {
      n.x = 0; // Set later based on column
      n.y = startY;
      n.h = n.seats * scale;
      n.nextOutY = startY;
      n.nextInY = startY;
      startY += n.h + nodePadding;
    });
  };

  computeYs(nodes.col0);
  computeYs(nodes.col1);
  computeYs(nodes.col2);

  // Set X coordinates
  nodes.col0[0].x = colX[0];
  nodes.col1.forEach(n => n.x = colX[1]);
  nodes.col2.forEach(n => n.x = colX[2]);

  // Nodes rendering markup
  const allNodes = [...nodes.col0, ...nodes.col1, ...nodes.col2];
  const nodesHtml = allNodes.map(n => `
    <rect class="sankey-node" id="${n.id}" x="${n.x}" y="${n.y}" width="${nodeW}" height="${n.h}" fill="${n.color}" opacity="0.85">
      <title>${n.name}: ${Math.round(n.seats).toLocaleString()} seats</title>
    </rect>
    <text x="${n.x + (n.x === colX[2] ? -8 : nodeW + 8)}" y="${n.y + n.h/2 + 4}"
          fill="var(--text)" font-size="10" font-weight="700"
          text-anchor="${n.x === colX[2] ? 'end' : 'start'}"
          style="pointer-events:none; font-family:'Space Grotesk', sans-serif;"
    >
      ${n.name}
    </text>
  `).join('');

  // 3. Generate Link ribbons paths (Sequential Stack drawing)
  const links = [];

  const makeSankeyPath = (x0, y0, x1, y1, width) => {
    const dx = (x1 - x0) * 0.45;
    const topCurve = `M ${x0} ${y0} C ${x0 + dx} ${y0}, ${x1 - dx} ${y1}, ${x1} ${y1}`;
    const rightEdge = `L ${x1} ${y1 + width}`;
    const bottomCurve = `C ${x1 - dx} ${y1 + width}, ${x0 + dx} ${y0 + width}, ${x0} ${y0 + width}`;
    return `${topCurve} ${rightEdge} ${bottomCurve} Z`;
  };

  // Link Flow Stage 1: KEA Pool -> Reservation categories
  nodes.col1.forEach(resNode => {
    const flowSeats = resNode.seats;
    if (flowSeats <= 0) return;
    const h = flowSeats * scale;

    const sourceNode = nodes.col0[0];

    links.push({
      path: makeSankeyPath(sourceNode.x + nodeW, sourceNode.nextOutY, resNode.x, resNode.nextInY, h),
      sourceId: sourceNode.id,
      targetId: resNode.id,
      seats: flowSeats,
      color: resNode.color,
      label: `KEA Pool ➔ ${resNode.name}: ${Math.round(flowSeats).toLocaleString()} seats`
    });

    sourceNode.nextOutY += h;
    resNode.nextInY += h;
  });

  // Link Flow Stage 2: Reservation categories -> Streams
  nodes.col1.forEach(resNode => {
    nodes.col2.forEach(strNode => {
      const flowSeats = flowMatrix[resNode.name]?.[strNode.name] || 0;
      if (flowSeats <= 0) return;
      const h = flowSeats * scale;

      links.push({
        path: makeSankeyPath(resNode.x + nodeW, resNode.nextOutY, strNode.x, strNode.nextInY, h),
        sourceId: resNode.id,
        targetId: strNode.id,
        seats: flowSeats,
        color: resNode.color,
        label: `${resNode.name} ➔ ${strNode.name}: ${Math.round(flowSeats).toLocaleString()} seats`
      });

      resNode.nextOutY += h;
      strNode.nextInY += h;
    });
  });

  // Links rendering markup with Linear Gradients
  const gradientsHtml = links.map((l, i) => `
    <linearGradient id="sankey-grad-${i}" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="${l.color}" stop-opacity="0.25" />
      <stop offset="100%" stop-color="${l.color}" stop-opacity="0.1" />
    </linearGradient>
  `).join('');

  const linksHtml = links.map((l, i) => `
    <path class="sankey-link" d="${l.path}" fill="url(#sankey-grad-${i})" data-src="${l.sourceId}" data-tgt="${l.targetId}" data-seats="${Math.round(l.seats)}" data-lbl="${l.label}">
      <title>${l.label}</title>
    </path>
  `).join('');

  wrap.innerHTML = `
    <svg width="${svgW}" height="${svgH}" viewBox="0 0 ${svgW} ${svgH}" style="position:relative; max-width: 100%;">
      <defs>${gradientsHtml}</defs>
      <g>${linksHtml}</g>
      <g>${nodesHtml}</g>
    </svg>
  `;

  // 4. Hook up Hover interactions
  const allSvgLinks = wrap.querySelectorAll('.sankey-link');
  const allSvgNodes = wrap.querySelectorAll('.sankey-node');

  allSvgLinks.forEach(link => {
    link.addEventListener('mouseenter', () => {
      allSvgLinks.forEach(l => {
        if (l !== link) {
          l.style.opacity = '0.08';
        } else {
          l.style.opacity = '1';
        }
      });
      if (tooltipPanel) {
        tooltipPanel.innerHTML = `📊 ${link.getAttribute('data-lbl')} (${Math.round((parseInt(link.getAttribute('data-seats')) / totalKeaSeats) * 100)}% of KEA total)`;
        tooltipPanel.style.color = "var(--blue)";
      }
    });

    link.addEventListener('mouseleave', () => {
      allSvgLinks.forEach(l => l.style.opacity = '');
      if (tooltipPanel) {
        tooltipPanel.textContent = "Hover links or nodes to inspect flow volumes";
        tooltipPanel.style.color = "";
      }
    });
  });

  allSvgNodes.forEach(node => {
    node.addEventListener('mouseenter', () => {
      const nid = node.getAttribute('id');
      const nname = allNodes.find(n => n.id === nid)?.name || '';
      const nseats = allNodes.find(n => n.id === nid)?.seats || 0;
      
      allSvgLinks.forEach(l => {
        const src = l.getAttribute('data-src');
        const tgt = l.getAttribute('data-tgt');
        if (src === nid || tgt === nid) {
          l.style.opacity = '1';
        } else {
          l.style.opacity = '0.08';
        }
      });

      if (tooltipPanel) {
        tooltipPanel.innerHTML = `🏢 <strong>${nname}</strong>: ${Math.round(nseats).toLocaleString()} seats (${Math.round((nseats / totalKeaSeats) * 100)}% of total)`;
        tooltipPanel.style.color = node.getAttribute('fill');
      }
    });

    node.addEventListener('mouseleave', () => {
      allSvgLinks.forEach(l => l.style.opacity = '');
      if (tooltipPanel) {
        tooltipPanel.textContent = "Hover links or nodes to inspect flow volumes";
        tooltipPanel.style.color = "";
      }
    });
  });
}

function polarToCart(cx, cy, r, angle) {
  const rad = (angle * Math.PI) / 180;
  return { x: cx + r * Math.cos(rad), y: cx + r * Math.sin(rad) };
}

function renderDistrictBarChart() {
  const distCounts = {};
  filtered.forEach(c => {
    let colSeats = 0;
    c.courses.forEach(cr => { colSeats += cr.total_intake || 0; });
    const dist = c.district || 'Other';
    distCounts[dist] = (distCounts[dist] || 0) + colSeats;
  });

  const rows = Object.entries(distCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 12);
  const maxVal = rows[0]?.[1] || 1;

  const html = rows.map(([dist, total], i) => {
    const w = Math.round((total / maxVal) * 100);
    const color = CHART_COLORS[i % CHART_COLORS.length];
    return `<div class="bar-item">
      <div class="bar-label">${dist}</div>
      <div class="bar-bg">
        <div class="bar-fill" style="width:${w}%; background:${color};"></div>
      </div>
      <div class="bar-val">${total.toLocaleString()}</div>
    </div>`;
  }).join('');

  document.getElementById('bar-district').innerHTML = html;
}

// ─────────────────────────────
function getYoYCutoffData(currentYear, keaCode, courseName) {
  if (!keaCode) return null;
  let otherYearCache = null;
  if (currentYear === '2026') otherYearCache = cache2025;
  else if (currentYear === '2025') otherYearCache = cache2024;
  else otherYearCache = cache2025;
  
  if (!otherYearCache) return null;
  
  const otherCol = otherYearCache.colleges.find(col => col.kea_code === keaCode);
  if (!otherCol) return null;
  
  const stdTarget = courseName.toUpperCase().replace(/[^A-Z0-9]/g, '');
  const otherCourse = otherCol.courses.find(c => {
    const stdC = c.course_name.toUpperCase().replace(/[^A-Z0-9]/g, '');
    return stdC === stdTarget;
  });
  if (!otherCourse) return null;
  
  return {
    r1: otherCourse.round1_cutoff || {},
    r2: otherCourse.round2_cutoff || {},
    r3: otherCourse.round3_cutoff || {}
  };
}

function renderCourseBarChart() {
  const courseCounts = {};
  filtered.forEach(c => {
    c.courses.forEach(cr => {
      courseCounts[cr.course_name] = (courseCounts[cr.course_name] || 0) + (cr.total_intake || 0);
    });
  });

  const rows = Object.entries(courseCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 15);
  const maxVal = rows[0]?.[1] || 1;

  const html = rows.map(([name, total], i) => {
    const w = Math.round((total / maxVal) * 100);
    const color = CHART_COLORS[i % CHART_COLORS.length];
    return `<div class="bar-item horizontal">
      <div class="bar-label" title="${name}">${name}</div>
      <div class="bar-bg">
        <div class="bar-fill" style="width:${w}%; background:${color}; display:flex; align-items:center;">
        </div>
      </div>
      <div class="bar-val">${total.toLocaleString()}</div>
    </div>`;
  }).join('');

  document.getElementById('bar-courses').innerHTML = html;
}

function computeSubcategorySeatSplit(c) {
  const keaTot = parseInt(c.total_kea_seats) || 0;
  const hkTot = parseInt(c.kea_hk) || 0;
  const rkTot = parseInt(c.kea_rk) || Math.max(0, keaTot - hkTot);
  const ph = parseInt(c.kea_ph) || 0;
  const snq = parseInt(c.snq_5pct || c.over_above_5pct) || 0;

  const pcts = {
    'GM': 0.50, 'SC': 0.17, 'ST': 0.07, '1': 0.04,
    '2A': 0.15, '2B': 0.04, '3A': 0.04, '3B': 0.05
  };

  const rkSplit = {};
  let urbSum = 0, rurSum = 0, kmSum = 0;
  for (const [cat, pct] of Object.entries(pcts)) {
    const catSeats = rkTot * pct;
    const gVal = maxZero(Math.round(catSeats * 0.66));
    const rVal = maxZero(Math.round(catSeats * 0.24));
    const kVal = maxZero(Math.round(catSeats * 0.10));
    rkSplit[`${cat}G`] = gVal;
    rkSplit[`${cat}R`] = rVal;
    rkSplit[`${cat}K`] = kVal;
    urbSum += gVal;
    rurSum += rVal;
    kmSum += kVal;
  }

  const hkSplit = {};
  let hkSum = 0;
  for (const [cat, pct] of Object.entries(pcts)) {
    const val = hkTot > 0 ? maxZero(Math.round(hkTot * pct)) : 0;
    hkSplit[`${cat}H`] = val;
    hkSum += val;
  }

  return { rkSplit, hkSplit, rkTot, hkTot, snq, ph, urbSum, rurSum, kmSum, hkSum };
}

function maxZero(val) {
  return isNaN(val) || val < 0 ? 0 : val;
}

// ─────────────────────────────
// Modal
// ─────────────────────────────
function openModal(college) {
  const ann = college.annexure || 'C';
  const annLabel = ANNEXURE_LABELS[ann] || ann;

  const plStats = college.placement_stats || { avg_package_lpa: '—', highest_package_lpa: '—', placement_rate_pct: '—', top_recruiters: [] };
  const hDetails = college.hostel_details || { hostel_type: '—', annual_hostel_fees: 0, hostel_capacity: '—', has_mess_included: false };
  const lDetails = college.location_details || { distance_from_bus_stand_km: '—', nearest_railway_station: '—', campus_area_acres: '—' };

  const totalIntake = college.total_intake || college.courses.reduce((s, c) => s + (c.total_intake || 0), 0);
  const totalKea = college.total_kea_seats || college.courses.reduce((s, c) => s + (c.total_kea_seats || 0), 0);
  const totalComedk = college.courses.reduce((s, c) => s + (c.cat2_seats || 0), 0);
  const totalMgmt = college.courses.reduce((s, c) => s + (c.cat3_seats || 0), 0);
  const totalSnq = college.courses.reduce((s, c) => s + (parseInt(c.snq_5pct || c.over_above_5pct) || 0), 0);

  const comEdkBox = totalComedk > 0 ? `
    <div class="modal-seat-box comedk">
      <div class="msb-val">${totalComedk.toLocaleString()}</div>
      <div class="msb-lbl">COMEDK</div>
    </div>` : '';

  const mgmtBox = totalMgmt > 0 ? `
    <div class="modal-seat-box mgmt">
      <div class="msb-val">${totalMgmt.toLocaleString()}</div>
      <div class="msb-lbl">Management</div>
    </div>` : '';

  const snqBox = totalSnq > 0 ? `
    <div class="modal-seat-box snq" style="background: rgba(34, 197, 94, 0.1); border-color: rgba(34, 197, 94, 0.2);">
      <div class="msb-val" style="color: #22c55e;">${totalSnq.toLocaleString()}</div>
      <div class="msb-lbl" style="color: #22c55e;">SNQ (5%)</div>
    </div>` : '';

  // Get default category from predictor if available, else default to GM
  const predCatEl = document.getElementById('pred-category');
  const defaultCat = predCatEl ? predCatEl.value : 'GM';

  // Quota Advantage Calculator
  let quotaAdvantageHtml = '';
  if (defaultCat !== 'GM') {
    let totalGM = 0, totalRes = 0, count = 0;
    college.courses.forEach(c => {
      const gmCut = parseInt(c.round1_cutoff?.GM);
      const resCut = parseInt(c.round1_cutoff?.[defaultCat]);
      if (gmCut && resCut) {
        totalGM += gmCut;
        totalRes += resCut;
        count++;
      }
    });
    if (count > 0) {
      const avgDiff = Math.round((totalRes - totalGM) / count);
      if (avgDiff > 0) {
        quotaAdvantageHtml = `
          <div class="quota-adv-card" style="background:var(--bg-card); border: 1px dashed var(--blue); padding:12px 16px; border-radius:12px; font-size:12px; margin-top:20px; display:flex; align-items:center; gap:8px; line-height:1.4;">
            <span style="font-size:16px;">💡</span>
            <span>Your <strong>${defaultCat}</strong> category gives you an average cutoff advantage of <strong style="color:var(--blue);">+${avgDiff.toLocaleString()} ranks</strong> compared to General Merit (GM) at this college!</span>
          </div>
        `;
      }
    }
  }

  const hasComDk = college.courses.some(c => c.cat2_seats > 0);
  const hasMgmt = college.courses.some(c => c.cat3_seats > 0);
  const hasSnq = college.courses.some(c => (c.snq_5pct || c.over_above_5pct || 0) > 0);
  const hasPh = college.courses.some(c => (c.kea_ph || 0) > 0);
  const hasSpl = college.courses.some(c => (c.kea_spl || 0) > 0);
  const hasHk = college.courses.some(c => (c.kea_hk || 0) > 0);
  const hasRk = college.courses.some(c => (c.kea_rk || 0) > 0);

  const modalOverlay = document.getElementById('modal-overlay');
  const modalContent = document.getElementById('modal-content');

  const courseRows = college.courses.map((c, idx) => {
    const comEdkCol = hasComDk ? `<td class="td-comedk">${parseInt(c.cat2_seats) || 0}</td>` : '';
    const mgmtCol = hasMgmt ? `<td class="td-mgmt">${parseInt(c.cat3_seats) || 0}</td>` : '';
    const snqCol = hasSnq ? `<td class="td-snq" style="color:#22c55e; font-weight:600;">${parseInt(c.snq_5pct || c.over_above_5pct) || 0}</td>` : '';
    const phCol = hasPh ? `<td class="td-ph">${parseInt(c.kea_ph) || 0}</td>` : '';
    const splCol = hasSpl ? `<td class="td-spl">${parseInt(c.kea_spl) || 0}</td>` : '';
    const hkCol = hasHk ? `<td class="td-hk">${parseInt(c.kea_hk) || 0}</td>` : '';
    const rkCol = hasRk ? `<td class="td-rk">${parseInt(c.kea_rk) || 0}</td>` : '';
    
    const r1_cutoffs = c.round1_cutoff || {};
    const r1_cutoff_val = r1_cutoffs[defaultCat];
    let initialCutoffR1 = r1_cutoff_val ? parseInt(r1_cutoff_val).toLocaleString() : '—';

    const r2_cutoffs = c.round2_cutoff || {};
    const r2_cutoff_val = r2_cutoffs[defaultCat];
    let initialCutoffR2 = r2_cutoff_val ? parseInt(r2_cutoff_val).toLocaleString() : '—';

    const r3_cutoffs = c.round3_cutoff || {};
    const r3_cutoff_val = r3_cutoffs[defaultCat];
    let initialCutoffR3 = r3_cutoff_val ? parseInt(r3_cutoff_val).toLocaleString() : '—';

    // YoY Cutoff comparison logic
    const activeYear = allData.year || '2025';
    const yoyData = getYoYCutoffData(activeYear, college.kea_code, c.course_name);

    const enrichCutoff = (currentValStr, otherCutoffsRound) => {
      if (!currentValStr || !otherCutoffsRound || !otherCutoffsRound[defaultCat]) return currentValStr ? parseInt(currentValStr).toLocaleString() : '—';
      const currentVal = parseInt(currentValStr);
      const otherVal = parseInt(otherCutoffsRound[defaultCat]);
      if (!otherVal || !currentVal) return currentValStr ? parseInt(currentValStr).toLocaleString() : '—';
      
      let changePercent = 0;
      if (activeYear === '2025') {
        const change = currentVal - otherVal;
        changePercent = Math.round((change / otherVal) * 100);
      } else {
        const change = otherVal - currentVal;
        changePercent = Math.round((change / currentVal) * 100);
      }
      
      let displayStr = currentVal.toLocaleString();
      if (changePercent < 0) {
        displayStr += `<br><span style="color:var(--pink); font-size:9px; font-weight:600; white-space:nowrap;" title="YoY Shift: ${otherVal.toLocaleString()} in other year">🔥 ${Math.abs(changePercent)}% tougher</span>`;
      } else if (changePercent > 0) {
        displayStr += `<br><span style="color:var(--green); font-size:9px; font-weight:600; white-space:nowrap;" title="YoY Shift: ${otherVal.toLocaleString()} in other year">📉 -${changePercent}% easier</span>`;
      }
      return displayStr;
    };

    initialCutoffR1 = enrichCutoff(r1_cutoff_val, yoyData?.r1);
    initialCutoffR2 = enrichCutoff(r2_cutoff_val, yoyData?.r2);
    const feeVal = getCourseFee(college, c.course_name, c.total_kea_seats);
    const sub = computeSubcategorySeatSplit(c);

    return `
      <tr class="course-main-row" data-course-idx="${idx}">
        <td class="course-name-cell" style="cursor:pointer;" title="Click to expand full sub-category matrix">
          <span class="drawer-toggle-icon" id="toggle-icon-${idx}" style="display:inline-block; transition:transform 0.2s; font-size:10px; margin-right:4px; color:var(--blue);">▶</span>
          <strong>${escHtml(c.course_name)}</strong>
          <button class="btn-add-option-inline" data-course-idx="${idx}" style="margin-left:8px; padding:2px 6px; font-size:9px; font-weight:700; background:rgba(34,197,94,0.1); border:1px solid rgba(34,197,94,0.2); color:#22c55e; border-radius:4px; cursor:pointer; font-family:var(--font); display:inline-flex; align-items:center; gap:2px; vertical-align:middle; transition:background 0.2s;" title="Add this course to your Option Entry priority sheet">➕ Add</button>
        </td>
        <td class="td-total">${c.total_intake || 0}</td>
        <td class="td-kea">${c.total_kea_seats || 0}</td>
        ${comEdkCol}
        ${mgmtCol}
        ${snqCol}
        ${phCol}
        ${splCol}
        ${hkCol}
        ${rkCol}
        <td>${feeVal}</td>
        <td class="td-cutoff-r1" data-course-idx="${idx}" style="color:var(--blue); text-align:right; font-family:var(--font-display); font-weight:700; line-height:1.2; padding:6px 8px;">${initialCutoffR1}</td>
        <td class="td-cutoff-r2" data-course-idx="${idx}" style="color:var(--purple); text-align:right; font-family:var(--font-display); font-weight:700; line-height:1.2; padding:6px 8px;">${initialCutoffR2}</td>
        <td class="td-cutoff-r3" data-course-idx="${idx}" style="color:var(--pink); text-align:right; font-family:var(--font-display); font-weight:700; line-height:1.2; padding:6px 8px;">${initialCutoffR3}</td>
      </tr>
      <tr class="course-drawer-row" id="drawer-row-${idx}" style="display:none; background:var(--bg-elevated, #1a233b);">
        <td colspan="15" style="padding:16px 20px; border-bottom:2px solid var(--blue);">
          <div style="display:grid; grid-template-columns: 2fr 1fr; gap:20px; align-items:start; flex-wrap:wrap;">
            <!-- Left side: Seats breakdown & cutoffs -->
            <div>
              <div style="font-size:12px; font-weight:700; color:var(--text); margin-bottom:8px;">📊 Detailed Sub-Category Breakdown for <em>${escHtml(c.course_name)}</em></div>
              <div style="display:flex; flex-wrap:wrap; gap:8px; margin-bottom:10px;">
                <span style="padding:4px 10px; border-radius:6px; background:rgba(59,130,246,0.15); color:var(--blue); font-size:11px; font-weight:600;">Rest of Karnataka (RK): ${c.kea_rk || 0} seats</span>
                <span style="padding:4px 10px; border-radius:6px; background:rgba(168,85,247,0.15); color:var(--purple); font-size:11px; font-weight:600;">Hyderabad Karnataka (371-J): ${c.kea_hk || 0} seats</span>
                <span style="padding:4px 10px; border-radius:6px; background:rgba(34,197,94,0.15); color:#22c55e; font-size:11px; font-weight:600;">Supernumerary (SNQ 5%): ${c.snq_5pct || c.over_above_5pct || 0} seats</span>
                ${c.sports ? `<span style="padding:4px 10px; border-radius:6px; background:rgba(234,179,8,0.15); color:#eab308; font-size:11px; font-weight:600;">🏅 Sports: ${c.sports}</span>` : ''}
                ${c.ncc ? `<span style="padding:4px 10px; border-radius:6px; background:rgba(234,179,8,0.15); color:#eab308; font-size:11px; font-weight:600;">🎖️ NCC: ${c.ncc}</span>` : ''}
                ${c.sct_guides ? `<span style="padding:4px 10px; border-radius:6px; background:rgba(234,179,8,0.15); color:#eab308; font-size:11px; font-weight:600;">⚜️ Scouts & Guides: ${c.sct_guides}</span>` : ''}
                ${c.defence ? `<span style="padding:4px 10px; border-radius:6px; background:rgba(234,179,8,0.15); color:#eab308; font-size:11px; font-weight:600;">🛡️ Defence: ${c.defence}</span>` : ''}
                ${c.ex_defence ? `<span style="padding:4px 10px; border-radius:6px; background:rgba(234,179,8,0.15); color:#eab308; font-size:11px; font-weight:600;">🎗️ Ex-Defence: ${c.ex_defence}</span>` : ''}
                ${c.capf ? `<span style="padding:4px 10px; border-radius:6px; background:rgba(234,179,8,0.15); color:#eab308; font-size:11px; font-weight:600;">👮 CAPF: ${c.capf}</span>` : ''}
                ${c.kea_ph ? `<span style="padding:4px 10px; border-radius:6px; background:rgba(234,179,8,0.15); color:#eab308; font-size:11px; font-weight:600;">♿ PH: ${c.kea_ph}</span>` : ''}
              </div>

              <div style="font-size:11px; font-weight:700; color:var(--text-muted); margin-top:12px; margin-bottom:6px;">📋 Sub-Category Seat Allocation Matrix (PDF Layout):</div>
              <table class="modal-courses-table" style="font-size:11px; background:var(--bg-card); border-radius:8px; overflow:hidden; margin-bottom:14px;">
                <thead>
                  <tr style="background:rgba(255,255,255,0.04);">
                    <th>Quota / Reservation</th>
                    <th style="text-align:center;">GM</th>
                    <th style="text-align:center;">SC</th>
                    <th style="text-align:center;">ST</th>
                    <th style="text-align:center;">Cat-1</th>
                    <th style="text-align:center;">2A</th>
                    <th style="text-align:center;">2B</th>
                    <th style="text-align:center;">3A</th>
                    <th style="text-align:center;">3B</th>
                    <th style="text-align:right;">Sub-Total</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td><strong>Urban / General (G)</strong></td>
                    <td style="text-align:center;">${sub.rkSplit['GMG']}</td>
                    <td style="text-align:center;">${sub.rkSplit['SCG']}</td>
                    <td style="text-align:center;">${sub.rkSplit['STG']}</td>
                    <td style="text-align:center;">${sub.rkSplit['1G']}</td>
                    <td style="text-align:center;">${sub.rkSplit['2AG']}</td>
                    <td style="text-align:center;">${sub.rkSplit['2BG']}</td>
                    <td style="text-align:center;">${sub.rkSplit['3AG']}</td>
                    <td style="text-align:center;">${sub.rkSplit['3BG']}</td>
                    <td style="text-align:right; font-weight:bold; color:var(--blue);">${sub.urbSum}</td>
                  </tr>
                  <tr>
                    <td><strong>Rural Quota (R)</strong></td>
                    <td style="text-align:center;">${sub.rkSplit['GMR']}</td>
                    <td style="text-align:center;">${sub.rkSplit['SCR']}</td>
                    <td style="text-align:center;">${sub.rkSplit['STR']}</td>
                    <td style="text-align:center;">${sub.rkSplit['1R']}</td>
                    <td style="text-align:center;">${sub.rkSplit['2AR']}</td>
                    <td style="text-align:center;">${sub.rkSplit['2BR']}</td>
                    <td style="text-align:center;">${sub.rkSplit['3AR']}</td>
                    <td style="text-align:center;">${sub.rkSplit['3BR']}</td>
                    <td style="text-align:right; font-weight:bold; color:var(--blue);">${sub.rurSum}</td>
                  </tr>
                  <tr>
                    <td><strong>Kannada Medium (K)</strong></td>
                    <td style="text-align:center;">${sub.rkSplit['GMK']}</td>
                    <td style="text-align:center;">${sub.rkSplit['SCK']}</td>
                    <td style="text-align:center;">${sub.rkSplit['STK']}</td>
                    <td style="text-align:center;">${sub.rkSplit['1K']}</td>
                    <td style="text-align:center;">${sub.rkSplit['2AK']}</td>
                    <td style="text-align:center;">${sub.rkSplit['2BK']}</td>
                    <td style="text-align:center;">${sub.rkSplit['3AK']}</td>
                    <td style="text-align:center;">${sub.rkSplit['3BK']}</td>
                    <td style="text-align:right; font-weight:bold; color:var(--blue);">${sub.kmSum}</td>
                  </tr>
                  ${sub.hkTot > 0 ? `
                    <tr style="background:rgba(168,85,247,0.05);">
                      <td><strong style="color:var(--purple);">HK 371-J Local (H)</strong></td>
                      <td style="text-align:center;">${sub.hkSplit['GMH']}</td>
                      <td style="text-align:center;">${sub.hkSplit['SCH']}</td>
                      <td style="text-align:center;">${sub.hkSplit['STH']}</td>
                      <td style="text-align:center;">${sub.hkSplit['1H']}</td>
                      <td style="text-align:center;">${sub.hkSplit['2AH']}</td>
                      <td style="text-align:center;">${sub.hkSplit['2BH']}</td>
                      <td style="text-align:center;">${sub.hkSplit['3AH']}</td>
                      <td style="text-align:center;">${sub.hkSplit['3BH']}</td>
                      <td style="text-align:right; font-weight:bold; color:var(--purple);">${sub.hkTot}</td>
                    </tr>
                  ` : ''}
                </tbody>
              </table>

              ${c.round1_cutoff ? `
                <div style="font-size:11px; font-weight:600; color:var(--text-muted); margin-bottom:6px;">Round 1 Cut-off Ranks by Category:</div>
                <div style="display:grid; grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); gap:6px; font-size:11px;">
                  ${Object.entries(c.round1_cutoff).map(([catKey, val]) => `
                    <div style="background:var(--bg-card); padding:5px 8px; border-radius:6px; border:1px solid var(--border); display:flex; justify-content:space-between;">
                      <span style="font-weight:600;">${catKey}:</span>
                      <span style="color:var(--blue); font-weight:700;">${parseInt(val).toLocaleString()}</span>
                    </div>
                  `).join('')}
                </div>
              ` : ''}
            </div>

            <!-- Right side: Course Placement Profile -->
            <div style="background:rgba(255,255,255,0.015); border:1px solid var(--border); padding:16px; border-radius:12px; display:flex; flex-direction:column; gap:12px; position:sticky; top:10px;">
              <div style="font-size:12px; font-weight:700; color:var(--text); margin-bottom:4px; display:flex; align-items:center; gap:6px; border-bottom:1px solid var(--border); padding-bottom:8px;">
                <span>💼</span> ${abbrCourseName(c.course_name)} Placement Profile
              </div>
              
              <div style="display:flex; flex-direction:column; gap:10px; font-size:11px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                  <span style="color:var(--text-faint);">Average Salary:</span>
                  <strong style="color:var(--green); font-size:13px; font-family:var(--font-display);">${c.course_placements?.avg_package_lpa || '—'} LPA</strong>
                </div>
                <div style="display:flex; justify-content:space-between; align-items:center;">
                  <span style="color:var(--text-faint);">Highest Salary:</span>
                  <strong style="color:var(--green); font-size:13px; font-family:var(--font-display);">${c.course_placements?.max_package_lpa || '—'} LPA</strong>
                </div>
                <div style="display:flex; justify-content:space-between; align-items:center;">
                  <span style="color:var(--text-faint);">Minimum Salary:</span>
                  <strong style="color:var(--text);">${c.course_placements?.min_package_lpa || '—'} LPA</strong>
                </div>
                <div style="display:flex; justify-content:space-between; align-items:center;">
                  <span style="color:var(--text-faint);">Placement Rate:</span>
                  <strong style="color:var(--text);">${c.course_placements?.placement_rate_pct || '—'}%</strong>
                </div>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-top:4px;">
                  <span style="color:var(--text-faint);">Sector Category:</span>
                  <span style="padding:2px 6px; border-radius:4px; font-weight:700; font-size:9px; background:${
                    (c.course_placements?.industry_type || '').includes('Product') ? 'rgba(34,197,94,0.06)' :
                    (c.course_placements?.industry_type || '').includes('VLSI') ? 'rgba(59,130,246,0.06)' : 'rgba(249,115,22,0.06)'
                  }; color:${
                    (c.course_placements?.industry_type || '').includes('Product') ? '#22c55e' :
                    (c.course_placements?.industry_type || '').includes('VLSI') ? 'var(--blue)' : '#f97316'
                  }; border:1px solid ${
                    (c.course_placements?.industry_type || '').includes('Product') ? 'rgba(34,197,94,0.15)' :
                    (c.course_placements?.industry_type || '').includes('VLSI') ? 'rgba(59,130,246,0.15)' : 'rgba(249,115,22,0.15)'
                  };">${c.course_placements?.industry_type || '—'}</span>
                </div>

                ${c.course_placements?.top_recruiters && c.course_placements.top_recruiters.length > 0 ? `
                  <div style="margin-top:8px; border-top:1px solid var(--border); padding-top:8px;">
                    <div style="font-size:9px; color:var(--text-faint); margin-bottom:4px; text-transform:uppercase;">Top Recruiters:</div>
                    <div style="display:flex; flex-wrap:wrap; gap:4px;">
                      ${c.course_placements.top_recruiters.map(r => `<span style="font-size:9px; background:rgba(255,255,255,0.04); border:1px solid var(--border); padding:2px 5px; border-radius:4px;">${r}</span>`).join('')}
                    </div>
                  </div>
                ` : ''}
              </div>
            </div>
          </div>
        </td>
      </tr>
    `;
  }).join('');

  // Course-level category totals calculation
  const totalIntakeSum = college.total_intake || college.courses.reduce((acc, c) => acc + (c.total_intake || 0), 0);
  const totalKeaSum = college.total_kea_seats || college.courses.reduce((acc, c) => acc + (c.total_kea_seats || 0), 0);
  const totalComEdkSum = college.courses.reduce((acc, c) => acc + (parseInt(c.cat2_seats) || 0), 0);
  const totalMgmtSum = college.courses.reduce((acc, c) => acc + (parseInt(c.cat3_seats) || 0), 0);
  const totalSnqSum = college.courses.reduce((acc, c) => acc + (parseInt(c.snq_5pct || c.over_above_5pct) || 0), 0);
  const totalPhSum = college.courses.reduce((acc, c) => acc + (parseInt(c.kea_ph) || 0), 0);
  const totalSplSum = college.courses.reduce((acc, c) => acc + (parseInt(c.kea_spl) || 0), 0);
  const totalHkSum = college.courses.reduce((acc, c) => acc + (parseInt(c.kea_hk) || 0), 0);
  const totalRkSum = college.courses.reduce((acc, c) => acc + (parseInt(c.kea_rk) || 0), 0);

  // Fee calculation
  const feeInfo = getSeatFees(college);
  const feeRows = feeInfo.rows.map(r => `
    <tr>
      <td>${r.seatType}</td>
      <td>${r.year1}</td>
      <td>${r.subsequent}</td>
      <td>${r.note}</td>
    </tr>
  `).join('');

  let disclaimerHtml = '';
  if (feeInfo.type === 'options') {
    disclaimerHtml = `
      <div class="fee-disclaimer">
        ℹ️ Private & Deemed institutions operate under consensual agreements offering Option A or Option B. An additional "Other Fee" up to ₹20,000/- per annum can be collected by KEA during admission.
      </div>`;
  } else if (feeInfo.hasConcession) {
    disclaimerHtml = `
      <div class="fee-disclaimer concession-info">
        🎉 Note: A 50% concession applies to tuition fees for Civil (CE), Mechanical (ME), Textile (TX), Silk (ST), and Automobile (AT) courses in government colleges where admission is low, reducing the fee to ₹28,450/- (1st Year).
      </div>`;
  }

  // Category fee table generation
  const categoryFees = getCategoryFeesList(college);
  const concessionCourses = ['civil', 'mechanical', 'textile', 'silk', 'automobile'];
  const hasConcession = college.courses.some(c => 
    concessionCourses.some(cc => c.course_name.toLowerCase().includes(cc))
  );
  const type = college.college_type || '';
  const isGovt = type.includes('Government / VTU Constituent');

  let categoryFeeRows = '';
  categoryFees.forEach(row => {
    categoryFeeRows += `
      <tr>
        <td><strong>${row.category}</strong></td>
        <td>${row.year1}</td>
        <td>${row.subsequent}</td>
        ${isGovt && hasConcession ? `<td>${row.concession_year1 || '—'}</td>` : ''}
        <td>${row.note}</td>
      </tr>
    `;
  });

  const categoryTableHead = `
    <thead>
      <tr>
        <th>Category & Income Limit</th>
        <th>1st Year Fee</th>
        <th>Subsequent Years</th>
        ${isGovt && hasConcession ? '<th>Concession Fee (1st Yr)</th>' : ''}
        <th>Eligibility / Detail</th>
      </tr>
    </thead>
  `;

  const categories = [
    'GM', 'GMK', 'GMR', '1G', '1K', '1R', '2AG', '2AK', '2AR', '2BG', '2BK', '2BR', '3AG', '3AK', '3AR', '3BG', '3BK', '3BR', 'SCG', 'SCK', 'SCR', 'STG', 'STK', 'STR',
    'GMH', 'GMKH', 'GMRH', '1H', '1KH', '1RH', '2AH', '2AKH', '2ARH', '2BH', '2BKH', '2BRH', '3AH', '3AKH', '3ARH', '3BH', '3BKH', '3BRH', 'SCH', 'SCKH', 'SCRH', 'STH', 'STKH', 'STRH'
  ];
  const optionsHtml = categories
    .map(cat => `<option value="${cat}" ${cat === defaultCat ? 'selected' : ''}>${cat}</option>`)
    .join('');

  const ageSpan = college.established_year ? `<span style="font-size:12px; font-weight:600; color:var(--text-muted); background:rgba(255,255,255,0.03); border:1px solid var(--border); padding:4px 10px; border-radius:6px; display:inline-flex; align-items:center; gap:4px;">📅 Established: <strong>${college.established_year}</strong> (${new Date().getFullYear() - college.established_year} years old)</span>` : '';
  const affSpan = college.affiliation ? `<span style="font-size:12px; font-weight:600; color:var(--blue); background:rgba(59,130,246,0.06); border:1px solid rgba(59,130,246,0.15); padding:4px 10px; border-radius:6px; display:inline-flex; align-items:center; gap:4px;">🎓 Affiliation: <strong>${college.affiliation}</strong></span>` : '';
  const nirfSpan = college.nirf_ranking ? `<span style="font-size:12px; font-weight:700; color:#eab308; background:rgba(234,179,8,0.06); border:1px solid rgba(234,179,8,0.15); padding:4px 10px; border-radius:6px; display:inline-flex; align-items:center; gap:4px;">🏆 NIRF Rank: <strong>#${college.nirf_ranking} (Engg 2025)</strong></span>` : '';
  const naacSpan = college.naac_grade ? `<span style="font-size:12px; font-weight:700; color:#a855f7; background:rgba(168,85,247,0.06); border:1px solid rgba(168,85,247,0.15); padding:4px 10px; border-radius:6px; display:inline-flex; align-items:center; gap:4px;">🎖️ NAAC Grade: <strong>${college.naac_grade}</strong></span>` : '';
  const nbaSpan = `<span style="font-size:12px; font-weight:700; color:${college.nba_accredited ? '#14b8a6' : 'var(--text-muted)'}; background:${college.nba_accredited ? 'rgba(20,184,166,0.06)' : 'rgba(255,255,255,0.02)'}; border:1px solid ${college.nba_accredited ? 'rgba(20,184,166,0.15)' : 'var(--border)'}; padding:4px 10px; border-radius:6px; display:inline-flex; align-items:center; gap:4px;">🛡️ NBA: <strong>${college.nba_accredited ? 'Accredited' : 'Not Accredited / Candidate'}</strong></span>`;

  document.getElementById('modal-content').innerHTML = `
    <div class="modal-header">
      <div class="modal-badge-row">
        <span class="card-type-pill pill-${ann}">${ANNEXURE_ICONS[ann]} ${annLabel}</span>
        <span class="card-location" style="color:var(--text-muted); font-size:13px">
          📍 ${escHtml(college.district || 'Karnataka')}
        </span>
        <button id="modal-compare-btn" style="margin-left:auto; padding: 6px 12px; font-size:11px; font-weight:700; background:var(--blue); color:#fff; border:none; border-radius:6px; cursor:pointer; font-family:var(--font); display:flex; align-items:center; gap:4px; transition:background 0.2s;">⚖️ Add to Compare</button>
      </div>
      <div class="modal-title">${college.kea_code ? `<span class="kea-code-badge large">${college.kea_code}</span> ` : ''}${escHtml(college.college_name)}</div>
      <div class="modal-address">📌 ${escHtml(college.address || 'Karnataka')}</div>
      <div style="display:flex; flex-wrap:wrap; gap:8px; margin-top:12px; margin-bottom:4px;">
        ${ageSpan}
        ${affSpan}
        ${nirfSpan}
        ${naacSpan}
        ${nbaSpan}
      </div>
    </div>

    <div class="modal-seats-row">
      <div class="modal-seat-box total">
        <div class="msb-val">${totalIntake.toLocaleString()}</div>
        <div class="msb-lbl">Total Intake</div>
      </div>
      <div class="modal-seat-box kea">
        <div class="msb-val">${totalKea.toLocaleString()}</div>
        <div class="msb-lbl">KEA Seats</div>
      </div>
      ${comEdkBox}
      ${mgmtBox}
      ${snqBox}
    </div>

    ${quotaAdvantageHtml}

    <div class="modal-cutoff-filter-row" style="display:flex; justify-content:space-between; align-items:center; margin-top:24px; margin-bottom:12px; flex-wrap:wrap; gap:8px;">
      <div class="modal-courses-title" style="margin:0;">Course-wise Seat Breakdown & Cut-offs</div>
      <div style="display:flex; align-items:center; gap:8px;">
        <label style="font-size:11px; font-weight:600; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.05em;">Cut-off Category:</label>
        <select id="modal-cutoff-category" class="select-filter" style="margin:0; padding:4px 8px; font-size:12px; background:var(--bg-card); border-color:var(--border); color:var(--text); border-radius:var(--radius-sm); width:auto;">
          ${optionsHtml}
        </select>
      </div>
    </div>

    <div class="table-container" style="overflow-x:auto; margin-bottom:24px;">
      <table class="modal-courses-table">
        <thead>
          <tr>
            <th>Course</th>
            <th>Total</th>
            <th>KEA</th>
            ${hasComDk ? '<th>COMEDK</th>' : ''}
            ${hasMgmt ? '<th>Mgmt</th>' : ''}
            ${hasSnq ? '<th>SNQ</th>' : ''}
            ${hasPh ? '<th>PH</th>' : ''}
            ${hasSpl ? '<th>SPL</th>' : ''}
            ${hasHk ? '<th>HK</th>' : ''}
            ${hasRk ? '<th>RK</th>' : ''}
            <th>Fee (1st Yr)</th>
            <th style="color:var(--blue); text-align:right;">R1 Cut-off</th>
            <th style="color:var(--purple); text-align:right;">R2 Cut-off</th>
            <th style="color:var(--pink); text-align:right;">R3 Cut-off</th>
          </tr>
        </thead>
        <tbody>${courseRows}</tbody>
        <tfoot>
          <tr style="border-top:2px solid var(--border); font-weight:bold; background:rgba(255,255,255,0.02);">
            <td><strong>Total</strong></td>
            <td class="td-total"><strong>${totalIntakeSum.toLocaleString()}</strong></td>
            <td class="td-kea"><strong>${totalKeaSum.toLocaleString()}</strong></td>
            ${hasComDk ? `<td class="td-comedk"><strong>${totalComEdkSum.toLocaleString()}</strong></td>` : ''}
            ${hasMgmt ? `<td class="td-mgmt"><strong>${totalMgmtSum.toLocaleString()}</strong></td>` : ''}
            ${hasSnq ? `<td class="td-snq" style="color:#22c55e;"><strong>${totalSnqSum.toLocaleString()}</strong></td>` : ''}
            ${hasPh ? `<td class="td-ph"><strong>${totalPhSum.toLocaleString()}</strong></td>` : ''}
            ${hasSpl ? `<td class="td-spl"><strong>${totalSplSum.toLocaleString()}</strong></td>` : ''}
            ${hasHk ? `<td class="td-hk"><strong>${totalHkSum.toLocaleString()}</strong></td>` : ''}
            ${hasRk ? `<td class="td-rk"><strong>${totalRkSum.toLocaleString()}</strong></td>` : ''}
            <td>—</td>
            <td style="text-align:right;">—</td>
            <td style="text-align:right;">—</td>
            <td style="text-align:right;">—</td>
          </tr>
        </tfoot>
      </table>
    </div>

    <div class="modal-courses-title" style="margin-top:24px">💰 Fee Structure (per Annum)</div>
    <div class="table-container" style="overflow-x:auto; margin-bottom:16px;">
      <table class="modal-courses-table fee-table">
        <thead>
          <tr>
            <th>Seat Type</th>
            <th>1st Year Fee</th>
            <th>Subsequent Years</th>
            <th>Note</th>
          </tr>
        </thead>
        <tbody>${feeRows}</tbody>
      </table>
    </div>
    ${disclaimerHtml}

    <div class="modal-courses-title" style="margin-top:24px">👥 KEA Quota Category-wise Fees & Concessions</div>
    <div class="table-container" style="overflow-x:auto; margin-bottom:16px;">
      <table class="modal-courses-table fee-table category-fee-table">
        ${categoryTableHead}
        <tbody>${categoryFeeRows}</tbody>
      </table>
    </div>

    <div class="modal-courses-title" style="margin-top:24px">🔍 Interactive Fee Estimator</div>
    <div class="fee-calculator-box" style="background: rgba(255,255,255,0.02); border: 1px solid var(--border); border-radius: var(--radius); padding: 18px; margin-bottom: 8px;">
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px;">
        <div>
          <label class="msb-lbl" style="display:block; margin-bottom:6px; font-size:10px; color:var(--text-faint);">Your Category & Income Limit</label>
          <select id="calc-category" class="select-filter" style="width:100%; margin:0; padding:8px; background:var(--bg-card); border-color:var(--border); border-radius:var(--radius-sm); color:var(--text);">
            <option value="GM">General Merit (GM) / OBC (Income > 10L)</option>
            <option value="OBC_LOW">OBC (2A, 2B, 3A, 3B) (Income ≤ 10 Lakhs)</option>
            <option value="CAT1">Category-1 (Income ≤ 2.5 Lakhs)</option>
            <option value="SCST_LOW">SC / ST (Income ≤ 10 Lakhs)</option>
            <option value="SCST_HIGH">SC / ST (Income > 10 Lakhs)</option>
            <option value="SNQ">SNQ Quota Seat</option>
          </select>
        </div>
        <div>
          <label class="msb-lbl" style="display:block; margin-bottom:6px; font-size:10px; color:var(--text-faint);">Course Type</label>
          <select id="calc-course-type" class="select-filter" style="width:100%; margin:0; padding:8px; background:var(--bg-card); border-color:var(--border); border-radius:var(--radius-sm); color:var(--text);">
            <option value="regular">Regular Course</option>
            ${feeInfo.hasConcession ? '<option value="concession">Concession Course (Mech/Civil/Textile/Silk/Auto)</option>' : ''}
          </select>
        </div>
      </div>
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; border-top:1px solid var(--border); padding-top:16px; margin-top:8px;">
        <div style="background: rgba(255,255,255,0.01); border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 12px; text-align: center;">
          <div style="font-size:11px; font-weight:600; color:var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px;">1st Year Fee</div>
          <div id="calc-fee-year1" style="font-size:20px; font-weight:800; color:var(--green); font-family:var(--font-display);">₹44,200</div>
        </div>
        <div style="background: rgba(255,255,255,0.01); border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 12px; text-align: center;">
          <div style="font-size:11px; font-weight:600; color:var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px;">Subsequent Years Fee</div>
          <div id="calc-fee-subsequent" style="font-size:20px; font-weight:800; color:var(--green); font-family:var(--font-display);">₹42,200</div>
        </div>
      </div>
      <div id="calc-note" style="font-size:11px; color:var(--text-faint); margin-top: 8px; text-align: center;">Based on KEA Quota rules</div>
    </div>

    <!-- Placements & Campus Life -->
    <div class="modal-courses-title" style="margin-top:24px">💼 Placements & Campus Life</div>
    <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap:16px; margin-bottom:16px;">
      <!-- Placements Card -->
      <div style="background: rgba(255,255,255,0.01); border: 1px solid var(--border); border-radius: var(--radius); padding:16px;">
        <div style="font-size:12px; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.05em; margin-bottom:12px; display:flex; align-items:center; gap:6px;">
          <span>📈</span> Placement Highlights
        </div>
        <div style="display:flex; flex-direction:column; gap:10px;">
          <div style="display:flex; justify-content:space-between; font-size:12px;">
            <span style="color:var(--text-faint);">Average Salary Package:</span>
            <strong style="color:var(--green); font-size:13px;">${plStats.avg_package_lpa} LPA</strong>
          </div>
          <div style="display:flex; justify-content:space-between; font-size:12px;">
            <span style="color:var(--text-faint);">Highest Salary Package:</span>
            <strong style="color:var(--green); font-size:13px;">${plStats.highest_package_lpa} LPA</strong>
          </div>
          <div style="display:flex; justify-content:space-between; font-size:12px;">
            <span style="color:var(--text-faint);">Placement Percentage:</span>
            <strong>${plStats.placement_rate_pct}%</strong>
          </div>
          ${plStats.top_recruiters && plStats.top_recruiters.length > 0 ? `
            <div style="margin-top:6px;">
              <div style="font-size:10px; color:var(--text-faint); margin-bottom:4px; text-transform:uppercase;">Top Recruiters:</div>
              <div style="display:flex; flex-wrap:wrap; gap:4px;">
                ${plStats.top_recruiters.map(r => `<span style="font-size:10px; background:rgba(255,255,255,0.04); border:1px solid var(--border); padding:2px 6px; border-radius:4px;">${r}</span>`).join('')}
              </div>
            </div>
          ` : ''}
        </div>
      </div>

      <!-- Hostel & Boarding Card -->
      <div style="background: rgba(255,255,255,0.01); border: 1px solid var(--border); border-radius: var(--radius); padding:16px;">
        <div style="font-size:12px; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.05em; margin-bottom:12px; display:flex; align-items:center; gap:6px;">
          <span>🏠</span> Hostel & Boarding Details
        </div>
        <div style="display:flex; flex-direction:column; gap:10px;">
          <div style="display:flex; justify-content:space-between; font-size:12px;">
            <span style="color:var(--text-faint);">Hostel Availability:</span>
            <strong>${hDetails.hostel_type}</strong>
          </div>
          <div style="display:flex; justify-content:space-between; font-size:12px;">
            <span style="color:var(--text-faint);">Annual Hostel Fees:</span>
            <strong style="color:#f97316; font-size:13px;">${hDetails.annual_hostel_fees > 0 ? `₹${hDetails.annual_hostel_fees.toLocaleString()}/-` : '—'}</strong>
          </div>
          <div style="display:flex; justify-content:space-between; font-size:12px;">
            <span style="color:var(--text-faint);">Capacity:</span>
            <strong>${hDetails.hostel_capacity} students</strong>
          </div>
          <div style="display:flex; justify-content:space-between; font-size:12px;">
            <span style="color:var(--text-faint);">Mess Charge & Food:</span>
            <strong>${hDetails.has_mess_included ? 'Included in Fees (Veg/Non-Veg)' : 'Separate Charges'}</strong>
          </div>
        </div>
      </div>

      <!-- Location & Transit Card -->
      <div style="background: rgba(255,255,255,0.01); border: 1px solid var(--border); border-radius: var(--radius); padding:16px;">
        <div style="font-size:12px; font-weight:700; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.05em; margin-bottom:12px; display:flex; align-items:center; gap:6px;">
          <span>📍</span> Geolocation & Transit
        </div>
        <div style="display:flex; flex-direction:column; gap:10px;">
          <div style="display:flex; justify-content:space-between; font-size:12px;">
            <span style="color:var(--text-faint);">Distance to Bus Stand:</span>
            <strong>${lDetails.distance_from_bus_stand_km} km</strong>
          </div>
          <div style="display:flex; justify-content:space-between; font-size:12px;">
            <span style="color:var(--text-faint);">Nearest Railway Station:</span>
            <strong>${lDetails.nearest_railway_station}</strong>
          </div>
          <div style="display:flex; justify-content:space-between; font-size:12px;">
            <span style="color:var(--text-faint);">Campus Size (Acres):</span>
            <strong>${lDetails.campus_area_acres} Acres</strong>
          </div>
        </div>
      </div>
    </div>
  `;

  document.getElementById('modal-overlay').classList.add('open');
  document.body.style.overflow = 'hidden';

  // Attach event listeners for fee estimator
  const catSel = document.getElementById('calc-category');
  const courseSel = document.getElementById('calc-course-type');
  const feeYear1 = document.getElementById('calc-fee-year1');
  const feeSubseq = document.getElementById('calc-fee-subsequent');
  const feeNote = document.getElementById('calc-note');
  
  function updateEstimation() {
    const category = catSel.value;
    const courseType = courseSel.value;
    const details = getCategoryFeeDetails(college, category, courseType);
    feeYear1.innerHTML = details.year1;
    feeSubseq.innerHTML = details.subsequent;
    feeNote.textContent = details.note + " (KEA Quota)";
  }
  
  if (catSel && courseSel && feeYear1 && feeSubseq) {
    catSel.addEventListener('change', updateEstimation);
    courseSel.addEventListener('change', updateEstimation);
    updateEstimation(); // Initial run
  }

  // Attach event listener for cutoff category selector
  const cutoffSel = document.getElementById('modal-cutoff-category');
  if (cutoffSel) {
    cutoffSel.addEventListener('change', () => {
      const selectedCat = cutoffSel.value;
      document.querySelectorAll('.td-cutoff-r1').forEach(td => {
        const idx = parseInt(td.dataset.courseIdx);
        const course = college.courses[idx];
        const cutoffs = course.round1_cutoff || {};
        const val = cutoffs[selectedCat];
        td.textContent = val ? parseInt(val).toLocaleString() : '—';
      });
      document.querySelectorAll('.td-cutoff-r2').forEach(td => {
        const idx = parseInt(td.dataset.courseIdx);
        const course = college.courses[idx];
        const cutoffs = course.round2_cutoff || {};
        const val = cutoffs[selectedCat];
        td.textContent = val ? parseInt(val).toLocaleString() : '—';
      });
      document.querySelectorAll('.td-cutoff-r3').forEach(td => {
        const idx = parseInt(td.dataset.courseIdx);
        const course = college.courses[idx];
        const cutoffs = course.round3_cutoff || {};
        const val = cutoffs[selectedCat];
        td.textContent = val ? parseInt(val).toLocaleString() : '—';
      });
    });
  }

  // Inline course drawer accordion toggle listener
  modalContent.querySelectorAll('.course-main-row').forEach(row => {
    row.addEventListener('click', (e) => {
      if (e.target.closest('.subcat-clickable') || e.target.closest('.btn-add-option-inline')) return;
      const idx = row.dataset.courseIdx;
      const drawer = document.getElementById(`drawer-row-${idx}`);
      const icon = document.getElementById(`toggle-icon-${idx}`);
      if (drawer) {
        const isOpen = drawer.style.display !== 'none';
        drawer.style.display = isOpen ? 'none' : 'table-row';
        if (icon) icon.style.transform = isOpen ? 'rotate(0deg)' : 'rotate(90deg)';
      }
    });
  });

  // Inline add option listener
  modalContent.querySelectorAll('.btn-add-option-inline').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const idx = parseInt(btn.dataset.courseIdx);
      const courseObj = college.courses[idx];
      
      const { rank: studentRank, category: studentCategory } = getActiveStudentProfile();
      const cutoff = getCourseCutoff(courseObj, studentCategory) || 999999;

      const chanceClass = getChanceClass(cutoff, studentRank);

      const newOpt = {
        id: college.college_number + '_' + courseObj.course_name,
        collegeNum: college.college_number,
        collegeName: college.college_name,
        keaCode: college.kea_code,
        courseName: courseObj.course_name,
        cutoff: cutoff,
        chanceClass: chanceClass
      };

      // Check for duplicate
      if (studentOptionsList.some(o => o.id === newOpt.id)) {
        alert("This option is already in your priority list!");
        return;
      }

      studentOptionsList.push(newOpt);
      saveCounsellorOptions();
      renderOptionEntryList();

      // Inline feedback
      const originalText = btn.innerHTML;
      btn.innerHTML = '✔ Added';
      btn.style.background = 'rgba(34,197,94,0.2)';
      btn.style.color = '#22c55e';
      setTimeout(() => {
        btn.innerHTML = originalText;
        btn.style.background = 'rgba(34,197,94,0.1)';
      }, 1500);
    });
  });

  // Compare button event listener
  const compBtn = document.getElementById('modal-compare-btn');
  if (compBtn) {
    compBtn.addEventListener('click', () => {
      if (!college.kea_code) {
        alert("This college does not have a valid KEA code for comparison.");
        return;
      }
      
      const s1 = document.getElementById('compare-col-1');
      const s2 = document.getElementById('compare-col-2');
      const s3 = document.getElementById('compare-col-3');
      
      if (s1.value === college.kea_code || s2.value === college.kea_code || s3.value === college.kea_code) {
        alert("This college is already in the comparison list!");
        return;
      }
      
      if (!s1.value) {
        s1.value = college.kea_code;
      } else if (!s2.value) {
        s2.value = college.kea_code;
      } else if (!s3.value) {
        s3.value = college.kea_code;
      } else {
        alert("All 3 comparison slots are full! Please clear one in the Compare tab first.");
        return;
      }
      
      updateComparisonMatrix();
      closeModal();
      
      // Switch tab to Compare
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(tc => tc.classList.remove('active'));
      const tabComp = document.getElementById('tab-compare');
      if (tabComp) tabComp.classList.add('active');
      currentTab = 'compare';
      const contentComp = document.getElementById('tab-content-compare');
      if (contentComp) contentComp.classList.add('active');
    });
  }
}

function closeModal() {
  document.getElementById('modal-overlay').classList.remove('open');
  document.body.style.overflow = '';
}

function getCourseFee(college, courseName, keaSeats) {
  const type = college.college_type || '';
  const selectedYear = document.getElementById('year-select')?.value || '2025';
  
  if (selectedYear === '2026') {
    if (type.includes('Government / VTU Constituent')) {
      const concessionCourses = ['civil', 'mechanical', 'textile', 'silk', 'automobile'];
      const isConcession = concessionCourses.some(cc => courseName.toLowerCase().includes(cc));
      return isConcession ? '₹33,600' : '₹47,100';
    }
    if (type.includes('Government Aided')) {
      return '₹47,100';
    }
    if (type.includes('Public University')) {
      return '₹56,500';
    }
    if (type.includes('Government (Higher Fees)')) {
      return '₹1,10,320';
    }
    return '₹1,10,320';
  }
  
  if (type.includes('Government / VTU Constituent')) {
    const concessionCourses = ['civil', 'mechanical', 'textile', 'silk', 'automobile'];
    const isConcession = concessionCourses.some(cc => courseName.toLowerCase().includes(cc));
    return isConcession ? '₹28,450' : '₹44,200';
  }
  if (type.includes('Government Aided')) {
    return '₹44,200';
  }
  if (type.includes('Public University')) {
    return '₹49,600';
  }
  if (type.includes('Government (Higher Fees)')) {
    return '₹1,02,410';
  }
  return '₹1,12,410';
}

function getSeatFees(college) {
  const type = college.college_type || '';
  const selectedYear = document.getElementById('year-select')?.value || '2025';
  const result = {
    type: 'standard',
    hasConcession: false,
    rows: []
  };

  if (selectedYear === '2026') {
    if (type.includes('Government / VTU Constituent Colleges') || type.includes('Government Engineering Colleges') || type.includes('Government')) {
      const concessionCourses = ['civil', 'mechanical', 'textile', 'silk', 'automobile'];
      const hasConcession = college.courses.some(c => 
        concessionCourses.some(cc => c.course_name.toLowerCase().includes(cc))
      );
      result.type = 'standard';
      result.hasConcession = hasConcession;
      result.rows.push({
        seatType: 'KEA General Quota',
        year1: '₹47,100',
        subsequent: '₹45,100',
        note: 'Includes ₹12,320 VTU fee and ₹10,000 other fees.'
      });
      if (hasConcession) {
        result.rows.push({
          seatType: 'KEA Concession Quota',
          year1: '₹33,600',
          subsequent: '₹32,320',
          note: 'Applies to Civil, Mechanical, Textile, Silk, Automobile.'
        });
      }
      result.rows.push({
        seatType: 'SNQ (Supernumerary Quota)',
        year1: '₹22,320',
        subsequent: '₹22,320',
        note: 'Tuition fee waived. Pays VTU and other fees.'
      });
    } else if (type.includes('Government Aided Private Colleges') || type.includes('Aided Courses')) {
      result.type = 'standard';
      result.rows.push({
        seatType: 'KEA General (Aided Courses)',
        year1: '₹47,100',
        subsequent: '₹45,100',
        note: 'Includes ₹12,320 VTU fee and ₹10,000 other fees.'
      });
      result.rows.push({
        seatType: 'SNQ (Supernumerary Quota)',
        year1: '₹22,320',
        subsequent: '₹22,320',
        note: 'Tuition fee waived. Pays VTU and other fees.'
      });
    } else if (type.includes('Public University') || type.includes('University of Visvesvaraya')) {
      result.type = 'uvce';
      result.rows.push({
        seatType: 'KEA General Quota',
        year1: '₹56,500',
        subsequent: '₹54,500',
        note: 'Under autonomous IIT-like status.'
      });
      result.rows.push({
        seatType: 'SNQ (Supernumerary Quota)',
        year1: '₹22,320',
        subsequent: '₹22,320',
        note: 'Tuition fee waived. Pays university and other fees.'
      });
    } else if (type.includes('Government (Higher Fees)')) {
      result.type = 'higher';
      result.rows.push({
        seatType: 'KEA General Quota',
        year1: '₹1,10,320',
        subsequent: '₹1,10,320',
        note: 'Applied to specific VTU constituent seats.'
      });
      result.rows.push({
        seatType: 'SNQ (Supernumerary Quota)',
        year1: '₹22,320',
        subsequent: '₹22,320',
        note: 'Tuition fee waived. Pays university and other fees.'
      });
    } else {
      result.type = 'options';
      result.rows = [
        {
          seatType: 'KEA General (Option A)',
          year1: '₹1,10,320',
          subsequent: '₹1,10,320',
          note: 'Consensual Agreement Option A. Includes ₹22,320 other fees.'
        },
        {
          seatType: 'KEA General (Option B)',
          year1: '₹1,20,320',
          subsequent: '₹1,20,320',
          note: 'Consensual Agreement Option B. Includes ₹22,320 other fees.'
        },
        {
          seatType: 'COMEDK (Option A)',
          year1: '₹2,15,000',
          subsequent: '₹2,15,000',
          note: 'Charged if the college chooses ₹1,10,320 for KEA.'
        },
        {
          seatType: 'COMEDK (Option B)',
          year1: '₹3,02,000',
          subsequent: '₹3,02,000',
          note: 'Charged if the college chooses ₹1,20,320 for KEA.'
        },
        {
          seatType: 'SNQ (Supernumerary Quota)',
          year1: '₹32,320',
          subsequent: '₹32,320',
          note: 'Tuition fee waived. Pays university and other fees.'
        }
      ];
    }
  } else if (selectedYear === '2024') {
    if (type.includes('Government / VTU Constituent Colleges') || type.includes('Government Engineering Colleges') || type.includes('Government')) {
      const concessionCourses = ['civil', 'mechanical', 'textile', 'silk', 'automobile'];
      const hasConcession = college.courses.some(c => 
        concessionCourses.some(cc => c.course_name.toLowerCase().includes(cc))
      );
      result.type = 'standard';
      result.hasConcession = hasConcession;
      result.rows.push({
        seatType: 'KEA General Quota',
        year1: '₹42,866',
        subsequent: '₹41,500',
        note: 'Includes ₹10,610 VTU fee and ₹10,000 other fees.'
      });
      if (hasConcession) {
        result.rows.push({
          seatType: 'KEA Concession Quota',
          year1: '₹31,738',
          subsequent: '₹30,360',
          note: 'Applies to Civil, Mechanical, Textile, Silk, Automobile.'
        });
      }
      result.rows.push({
        seatType: 'SNQ (Supernumerary Quota)',
        year1: '₹21,360',
        subsequent: '₹21,360',
        note: 'Tuition fee waived. Pays VTU and other fees.'
      });
    } else if (type.includes('Government Aided Private Colleges') || type.includes('Aided Courses')) {
      result.type = 'standard';
      result.rows.push({
        seatType: 'KEA General (Aided Courses)',
        year1: '₹42,866',
        subsequent: '₹41,500',
        note: 'Includes ₹10,610 VTU fee and ₹10,000 other fees.'
      });
      result.rows.push({
        seatType: 'SNQ (Supernumerary Quota)',
        year1: '₹21,360',
        subsequent: '₹21,360',
        note: 'Tuition fee waived. Pays VTU and other fees.'
      });
    } else if (type.includes('Public University') || type.includes('University of Visvesvaraya')) {
      result.type = 'uvce';
      result.rows.push({
        seatType: 'KEA General Quota',
        year1: '₹48,000',
        subsequent: '₹46,500',
        note: 'Under autonomous IIT-like status.'
      });
      result.rows.push({
        seatType: 'SNQ (Supernumerary Quota)',
        year1: '₹21,360',
        subsequent: '₹21,360',
        note: 'Tuition fee waived. Pays university and other fees.'
      });
    } else {
      result.type = 'options';
      result.rows = [
        {
          seatType: 'KEA General (Type-1 / Option A)',
          year1: '₹1,07,495',
          subsequent: '₹1,07,495',
          note: 'Type-1 fee structure. Includes ₹20,000 other fees.'
        },
        {
          seatType: 'KEA General (Type-2 / Option B)',
          year1: '₹1,15,956',
          subsequent: '₹1,15,956',
          note: 'Type-2 fee structure. Includes ₹20,000 other fees.'
        },
        {
          seatType: 'COMEDK (Type-1 / Option A)',
          year1: '₹2,64,000',
          subsequent: '₹2,64,000',
          note: 'Charged if the college chooses Type-1 fees.'
        },
        {
          seatType: 'COMEDK (Type-2 / Option B)',
          year1: '₹2,01,000',
          subsequent: '₹2,01,000',
          note: 'Charged if the college chooses Type-2 fees.'
        },
        {
          seatType: 'SNQ (Supernumerary Quota)',
          year1: '₹31,360',
          subsequent: '₹31,360',
          note: 'Tuition fee waived. Pays university and other fees.'
        }
      ];
    }
  } else {
    // 2025 Fee structure
    if (type.includes('Government / VTU Constituent Colleges')) {
      const concessionCourses = ['civil', 'mechanical', 'textile', 'silk', 'automobile'];
      const hasConcession = college.courses.some(c => 
        concessionCourses.some(cc => c.course_name.toLowerCase().includes(cc))
      );
      result.type = 'standard';
      result.hasConcession = hasConcession;
      result.rows.push({
        seatType: 'KEA General Quota',
        year1: '₹44,200',
        subsequent: '₹42,200',
        note: 'Includes ₹10,610 VTU fee and ₹10,000 other fees.'
      });
      if (hasConcession) {
        result.rows.push({
          seatType: 'KEA Concession Quota',
          year1: '₹28,450',
          subsequent: '₹26,450',
          note: 'Applies to Civil, Mechanical, Textile, Silk, Automobile.'
        });
      }
      result.rows.push({
        seatType: 'SNQ (Supernumerary Quota)',
        year1: '₹20,610',
        subsequent: '₹20,610',
        note: 'Tuition fee waived. Pays VTU and other fees.'
      });
    } else if (type.includes('Government Aided Private Colleges')) {
      result.type = 'standard';
      result.rows.push({
        seatType: 'KEA General (Aided Courses)',
        year1: '₹44,200',
        subsequent: '₹42,200',
        note: 'Includes ₹10,610 VTU fee and ₹10,000 other fees.'
      });
      result.rows.push({
        seatType: 'SNQ (Supernumerary Quota)',
        year1: '₹20,610',
        subsequent: '₹20,610',
        note: 'Tuition fee waived. Pays VTU and other fees.'
      });
    } else if (type.includes('Public University')) {
      result.type = 'uvce';
      result.rows.push({
        seatType: 'KEA General Quota',
        year1: '₹49,600',
        subsequent: '₹48,250',
        note: 'Under autonomous IIT-like status.'
      });
      result.rows.push({
        seatType: 'SNQ (Supernumerary Quota)',
        year1: '₹20,610',
        subsequent: '₹20,610',
        note: 'Tuition fee waived. Pays university and other fees.'
      });
    } else if (type.includes('Government (Higher Fees)')) {
      result.type = 'higher';
      result.rows.push({
        seatType: 'KEA General Quota',
        year1: '₹1,02,410',
        subsequent: '₹1,02,410',
        note: 'Applied to specific VTU constituent seats.'
      });
      result.rows.push({
        seatType: 'SNQ (Supernumerary Quota)',
        year1: '₹20,610',
        subsequent: '₹20,610',
        note: 'Tuition fee waived. Pays university and other fees.'
      });
    } else {
      result.type = 'options';
      result.rows = [
        {
          seatType: 'KEA General (Option A)',
          year1: '₹1,12,410',
          subsequent: '₹1,12,410',
          note: 'Consensual Agreement Option A. Includes ₹20,000 other fees.'
        },
        {
          seatType: 'KEA General (Option B)',
          year1: '₹1,21,610',
          subsequent: '₹1,21,610',
          note: 'Consensual Agreement Option B. Includes ₹20,000 other fees.'
        },
        {
          seatType: 'COMEDK (Option A)',
          year1: '₹2,81,100',
          subsequent: '₹2,81,100',
          note: 'Charged if the college chooses ₹1,12,410 for KEA.'
        },
        {
          seatType: 'COMEDK (Option B)',
          year1: '₹2,00,000',
          subsequent: '₹2,00,000',
          note: 'Charged if the college chooses ₹1,21,610 for KEA.'
        },
        {
          seatType: 'SNQ (Supernumerary Quota)',
          year1: '₹30,610',
          subsequent: '₹30,610',
          note: 'Tuition fee waived. Pays university and other fees.'
        }
      ];
    }
  }

  return result;
}

// Category details resolver based on KEA_FEES_2025.pdf & provisional fees 2024
function getCategoryFeeDetails(college, category, courseType) {
  const type = college.college_type || '';
  const isConcession = courseType === 'concession';
  const isGovt = type.includes('Government / VTU Constituent');
  const selectedYear = document.getElementById('year-select')?.value || '2025';

  if (selectedYear === '2024') {
    if (type.includes('Government / VTU Constituent Colleges') || type.includes('Government Engineering Colleges') || type.includes('Government Aided Private Colleges') || type.includes('Government')) {
      if (category === 'SCST_LOW') {
        return { year1: '₹750', subsequent: '₹750', note: 'KEA Registration fee only (tuition waived)' };
      }
      if (category === 'CAT1' || category === 'OBC_LOW') {
        return { year1: '₹21,360', subsequent: '₹21,360', note: 'KEA Concession rate (tuition waived)' };
      }
      if (category === 'SNQ') {
        return { year1: '₹21,360', subsequent: '₹21,360', note: 'SNQ Quota (tuition waived)' };
      }
      return {
        year1: isGovt && isConcession ? '₹31,738' : '₹42,866',
        subsequent: isGovt && isConcession ? '₹30,360' : '₹41,500',
        note: 'Standard KEA fee'
      };
    } else if (type.includes('Public University') || type.includes('University of Visvesvaraya')) {
      if (category === 'SCST_LOW') {
        return { year1: '₹750', subsequent: '₹750', note: 'KEA Registration fee only (tuition waived)' };
      }
      if (category === 'CAT1' || category === 'OBC_LOW') {
        return { year1: '₹21,360', subsequent: '₹21,360', note: 'KEA Concession rate' };
      }
      if (category === 'SNQ') {
        return { year1: '₹21,360', subsequent: '₹21,360', note: 'SNQ Quota (tuition waived)' };
      }
      return { year1: '₹48,000', subsequent: '₹46,500', note: 'Standard UVCE fee' };
    } else {
      // Private / Minority / Deemed / Private Univ
      if (category === 'SCST_LOW') {
        return { year1: '₹750', subsequent: '₹750', note: 'KEA Registration fee only (tuition waived)' };
      }
      if (category === 'CAT1' || category === 'OBC_LOW') {
        return {
          year1: 'Type-1: ₹31,360<br>Type-2: ₹31,360',
          subsequent: 'Type-1: ₹31,360<br>Type-2: ₹31,360',
          note: 'KEA Concession rate'
        };
      }
      if (category === 'SNQ') {
        return { year1: '₹31,360', subsequent: '₹31,360', note: 'SNQ Quota (tuition waived)' };
      }
      return {
        year1: 'Type-1: ₹1,07,495<br>Type-2: ₹1,15,956',
        subsequent: 'Type-1: ₹1,07,495<br>Type-2: ₹1,15,956',
        note: 'Standard KEA fee'
      };
    }
  } else {
    // 2025 Category Fees
    if (type.includes('Government / VTU Constituent Colleges') || type.includes('Government Aided Private Colleges')) {
      if (category === 'SCST_LOW') {
        return { year1: '₹0', subsequent: '₹0', note: 'Full waiver at KEA counter' };
      }
      if (category === 'CAT1' || category === 'OBC_LOW') {
        return {
          year1: isGovt && isConcession ? '₹16,950' : '₹23,590',
          subsequent: isGovt && isConcession ? '₹14,950' : '₹21,590',
          note: 'KEA Concession rate (tuition fee waiver)'
        };
      }
      if (category === 'SNQ') {
        return { year1: '₹20,610', subsequent: '₹20,610', note: 'SNQ Quota (tuition waived)' };
      }
      // GM / SCST_HIGH
      return {
        year1: isGovt && isConcession ? '₹28,450' : '₹44,200',
        subsequent: isGovt && isConcession ? '₹26,450' : '₹42,200',
        note: 'Standard KEA fee'
      };
    } else if (type.includes('Public University')) {
      if (category === 'SCST_LOW') {
        return { year1: '₹0', subsequent: '₹0', note: 'Full waiver at KEA counter' };
      }
      if (category === 'CAT1' || category === 'OBC_LOW') {
        return { year1: '₹28,990', subsequent: '₹27,640', note: 'KEA Concession rate' };
      }
      if (category === 'SNQ') {
        return { year1: '₹20,610', subsequent: '₹20,610', note: 'SNQ Quota (tuition waived)' };
      }
      return { year1: '₹49,600', subsequent: '₹48,250', note: 'Standard UVCE fee' };
    } else if (type.includes('Government (Higher Fees)')) {
      if (category === 'SCST_LOW') {
        return { year1: '₹0', subsequent: '₹0', note: 'Full waiver at KEA counter' };
      }
      if (category === 'CAT1' || category === 'OBC_LOW') {
        return { year1: '₹78,820', subsequent: '₹78,820', note: 'KEA Concession rate' };
      }
      if (category === 'SNQ') {
        return { year1: '₹20,610', subsequent: '₹20,610', note: 'SNQ Quota (tuition waived)' };
      }
      return { year1: '₹1,02,410', subsequent: '₹1,02,410', note: 'VTU Constituent Higher fee' };
    } else {
      // Private / Minority / Deemed / Private Univ
      if (category === 'SCST_LOW') {
        return { year1: '₹0', subsequent: '₹0', note: 'Full waiver at KEA counter' };
      }
      if (category === 'CAT1' || category === 'OBC_LOW') {
        return {
          year1: 'Opt A: ₹88,820<br>Opt B: ₹98,020',
          subsequent: 'Opt A: ₹88,820<br>Opt B: ₹98,020',
          note: 'KEA Concession rate'
        };
      }
      if (category === 'SNQ') {
        return { year1: '₹30,610', subsequent: '₹30,610', note: 'SNQ Quota (tuition waived)' };
      }
      return {
        year1: 'Opt A: ₹1,12,410<br>Opt B: ₹1,21,610',
        subsequent: 'Opt A: ₹1,12,410<br>Opt B: ₹1,21,610',
        note: 'Standard KEA fee'
      };
    }
  }
}

// Generate the category list elements
function getCategoryFeesList(college) {
  const categories = [
    { key: 'GM', label: 'General Merit (GM) / OBC (Income > 10L)' },
    { key: 'OBC_LOW', label: 'OBC (2A, 2B, 3A, 3B) (Income ≤ 10 Lakhs)' },
    { key: 'CAT1', label: 'Category-1 (Income ≤ 2.5 Lakhs)' },
    { key: 'SCST_LOW', label: 'SC / ST (Income ≤ 10 Lakhs)' },
    { key: 'SCST_HIGH', label: 'SC / ST (Income > 10 Lakhs)' },
    { key: 'SNQ', label: 'SNQ Quota Seat' }
  ];

  const type = college.college_type || '';
  const list = [];

  categories.forEach(cat => {
    const regular = getCategoryFeeDetails(college, cat.key, 'regular');
    const concession = type.includes('Government / VTU Constituent') 
      ? getCategoryFeeDetails(college, cat.key, 'concession') 
      : null;

    list.push({
      category: cat.label,
      year1: regular.year1,
      subsequent: regular.subsequent,
      concession_year1: concession ? concession.year1 : null,
      note: regular.note
    });
  });

  return list;
}



// ─────────────────────────────
// Event Bindings
// ─────────────────────────────
function bindEvents() {
  // Mobile filter drawer toggles
  const mobileToggle = document.getElementById('mobile-filter-toggle');
  const mobileOverlay = document.getElementById('mobile-drawer-overlay');
  const sidebar = document.querySelector('.sidebar');
  if (mobileToggle && mobileOverlay && sidebar) {
    mobileToggle.addEventListener('click', () => {
      sidebar.classList.add('open');
      mobileOverlay.style.display = 'block';
    });
    mobileOverlay.addEventListener('click', () => {
      sidebar.classList.remove('open');
      mobileOverlay.style.display = 'none';
    });
  }

  // Floating Action Button for Filters
  const filterFab = document.getElementById('mobile-filter-fab');
  if (filterFab && mobileOverlay && sidebar) {
    filterFab.addEventListener('click', () => {
      sidebar.classList.add('open');
      mobileOverlay.style.display = 'block';
    });
  }

  // Mobile Bottom Navigation Bar Buttons
  const mobNavBtns = document.querySelectorAll('.mob-nav-btn');
  mobNavBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetTabName = btn.dataset.tab;
      const targetDesktopTab = document.getElementById(`tab-${targetTabName}`);
      if (targetDesktopTab) {
        targetDesktopTab.click();
      }
    });
  });

  // Search
  const searchInput = document.getElementById('search-input');
  let searchTimeout;
  searchInput.addEventListener('input', () => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      filters.search = searchInput.value;
      applyFilters();
    }, 200);
  });

  // Type chips
  document.getElementById('type-chips').addEventListener('click', e => {
    const chip = e.target.closest('.chip');
    if (!chip) return;
    document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
    chip.classList.add('active');
    filters.annexure = chip.dataset.annexure;
    applyFilters();
  });

  // District filter
  document.getElementById('district-filter').addEventListener('change', e => {
    filters.district = e.target.value;
    applyFilters();
  });

  // Course filter
  document.getElementById('course-filter').addEventListener('change', e => {
    filters.course = e.target.value;
    applyFilters();
  });

  // Affiliation filter
  const affFilter = document.getElementById('affiliation-filter');
  if (affFilter) {
    affFilter.addEventListener('change', () => {
      applyFilters();
    });
  }

  // NAAC filter
  const naacFilter = document.getElementById('naac-filter');
  if (naacFilter) {
    naacFilter.addEventListener('change', () => {
      applyFilters();
    });
  }

  // NBA filter
  const nbaFilter = document.getElementById('nba-filter');
  if (nbaFilter) {
    nbaFilter.addEventListener('change', () => {
      applyFilters();
    });
  }

  // Min seats slider
  const slider = document.getElementById('min-seats');
  const sliderVal = document.getElementById('min-seats-val');
  slider.addEventListener('input', () => {
    filters.minSeats = parseInt(slider.value);
    sliderVal.textContent = filters.minSeats > 0 ? `${filters.minSeats}+` : '0+';
    applyFilters();
  });

  // Min salary slider
  const salarySlider = document.getElementById('min-salary');
  const salarySliderVal = document.getElementById('min-salary-val');
  if (salarySlider && salarySliderVal) {
    salarySlider.addEventListener('input', () => {
      salarySliderVal.textContent = `${salarySlider.value} LPA+`;
      applyFilters();
    });
  }

  // Max hostel slider
  const hostelSlider = document.getElementById('max-hostel');
  const hostelSliderVal = document.getElementById('max-hostel-val');
  if (hostelSlider && hostelSliderVal) {
    hostelSlider.addEventListener('input', () => {
      const val = parseInt(hostelSlider.value);
      hostelSliderVal.textContent = val >= 150000 ? 'Any Fee' : `₹${(val/1000)}k/yr`;
      applyFilters();
    });
  }

  // Reset
  document.getElementById('reset-btn').addEventListener('click', () => {
    filters = { search: '', annexure: 'all', district: '', course: '', minSeats: 0 };
    searchInput.value = '';
    document.getElementById('district-filter').value = '';
    document.getElementById('course-filter').value = '';
    if (affFilter) affFilter.value = '';
    if (naacFilter) naacFilter.value = '';
    if (nbaFilter) nbaFilter.value = '';
    if (salarySlider) {
      salarySlider.value = 0;
      salarySliderVal.textContent = '0 LPA+';
    }
    if (hostelSlider) {
      hostelSlider.value = 150000;
      hostelSliderVal.textContent = 'Any Fee';
    }
    slider.value = 0;
    sliderVal.textContent = '0+';
    document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
    document.querySelector('[data-annexure="all"]').classList.add('active');
    applyFilters();
  });

  // Tabs
  document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(tc => tc.classList.remove('active'));
      tab.classList.add('active');
      currentTab = tab.dataset.tab;
      document.getElementById(`tab-content-${currentTab}`).classList.add('active');
      
      // Sync bottom navigation
      document.querySelectorAll('.mob-nav-btn').forEach(mnb => {
        mnb.classList.remove('active');
        if (mnb.dataset.tab === currentTab) {
          mnb.classList.add('active');
        }
      });
      
      if (currentTab === 'totals') {
        const activeBtn = document.querySelector('.totals-ann-btn.active');
        const activeAnnFilter = activeBtn ? activeBtn.dataset.ann : 'ALL';
        renderTotals(activeAnnFilter);
      } else if (currentTab === 'stats') {
        renderStats();
        renderYoYStats();
      } else if (currentTab === 'institution') {
        renderInstitutionDashboard();
      } else if (currentTab === 'authority') {
        renderAuthorityDashboard();
      } else if (currentTab === 'option-entry') {
        renderOptionEntryList();
      } else if (currentTab === 'downloads') {
        updateDownloadPreview();
      }
    });
  });

  // Sort buttons
  document.querySelectorAll('.sort-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.sort-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      sortMode = btn.dataset.sort;
      applyFilters();
    });
  });

  // View toggle
  document.getElementById('view-grid').addEventListener('click', () => {
    viewMode = 'grid';
    document.getElementById('view-grid').classList.add('active');
    document.getElementById('view-list').classList.remove('active');
    document.getElementById('colleges-grid').classList.remove('list-view');
  });
  document.getElementById('view-list').addEventListener('click', () => {
    viewMode = 'list';
    document.getElementById('view-list').classList.add('active');
    document.getElementById('view-grid').classList.remove('active');
    document.getElementById('colleges-grid').classList.add('list-view');
  });

  // Load more
  document.getElementById('load-more-btn').addEventListener('click', () => {
    displayCount += 30;
    renderColleges();
  });

  // Modal
  document.getElementById('modal-close').addEventListener('click', closeModal);
  document.getElementById('modal-overlay').addEventListener('click', e => {
    if (e.target === document.getElementById('modal-overlay')) closeModal();
  });
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') closeModal();
  });

  // Totals annexure selector
  document.getElementById('totals-annexure-bar').addEventListener('click', e => {
    const btn = e.target.closest('.totals-ann-btn');
    if (!btn) return;
    document.querySelectorAll('.totals-ann-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    renderTotals(btn.dataset.ann);
  });



  // Predictor handlers
  const predBtn = document.getElementById('pred-btn');
  if (predBtn) {
    predBtn.addEventListener('click', runPrediction);
  }

  // Refresh user activities dashboard
  const refreshActivitiesBtn = document.getElementById('btn-refresh-activities');
  if (refreshActivitiesBtn) {
    refreshActivitiesBtn.addEventListener('click', renderAuthorityDashboard);
  }
  const predRankInput = document.getElementById('pred-rank');
  if (predRankInput) {
    predRankInput.addEventListener('keydown', e => {
      if (e.key === 'Enter') runPrediction();
    });
  }

  // College Comparer Bindings
  const comp1 = document.getElementById('compare-col-1');
  const comp2 = document.getElementById('compare-col-2');
  const comp3 = document.getElementById('compare-col-3');
  if (comp1) comp1.addEventListener('change', updateComparisonMatrix);
  if (comp2) comp2.addEventListener('change', updateComparisonMatrix);
  if (comp3) comp3.addEventListener('change', updateComparisonMatrix);

  // Fee Calculator Bindings
  const feeCol = document.getElementById('calc-fee-college');
  const feeQuot = document.getElementById('calc-fee-quota');
  const feeYr = document.getElementById('calc-fee-year');
  if (feeCol) feeCol.addEventListener('change', calculateTuitionFee);
  if (feeQuot) feeQuot.addEventListener('change', calculateTuitionFee);
  if (feeYr) feeYr.addEventListener('change', calculateTuitionFee);
}

// ─────────────────────────────
// Helpers
// ─────────────────────────────
function escHtml(str) {
  return (str || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function titleCase(str) {
  if (!str) return '';
  const exceptions = new Set(['and', 'of', 'in', 'the', 'for', 'with', 'a', 'an', 'to', 'at', 'by', 'or', '&']);
  const specialWords = {
    'vlsi': 'VLSI',
    'iot': 'IoT',
    'devops': 'DevOps',
    'ai': 'AI',
    'ml': 'ML',
    'ds': 'DS',
    'ar/vr': 'AR/VR',
    'pwd': 'PWD'
  };
  
  return str.split(' ').map((w, i) => {
    const cleanWord = w.replace(/[^a-zA-Z]/g, '').toLowerCase();
    
    // Check if it's a special acronym
    if (specialWords[cleanWord]) {
      return w.replace(/[a-zA-Z]+/g, specialWords[cleanWord]);
    }
    
    // Find the first alphabetical character
    let firstLetterIdx = -1;
    for (let j = 0; j < w.length; j++) {
      if (/[a-zA-Z]/.test(w[j])) {
        firstLetterIdx = j;
        break;
      }
    }
    if (firstLetterIdx === -1) return w;
    
    if (i === 0 || !exceptions.has(cleanWord)) {
      return w.slice(0, firstLetterIdx) + w.charAt(firstLetterIdx).toUpperCase() + w.slice(firstLetterIdx + 1).toLowerCase();
    }
    return w.toLowerCase();
  }).join(' ');
}

function abbrCourseName(name) {
  const abbrs = {
    'COMPUTER SCIENCE AND ENGINEERING': 'CSE',
    'ELECTRONICS AND COMMUNICATION ENGINEERING': 'ECE',
    'ELECTRONICS AND COMMUNICATION ENGG': 'ECE',
    'MECHANICAL ENGINEERING': 'Mech',
    'CIVIL ENGINEERING': 'Civil',
    'INFORMATION SCIENCE AND ENGINEERING': 'ISE',
    'ARTIFICIAL INTELLIGENCE AND MACHINE LEARNING': 'AI/ML',
    'ARTIFICIAL INTELLIGENCE AND DATA SCIENCE': 'AI/DS',
    'ELECTRICAL & ELECTRONICS ENGINEERING': 'EEE',
    'COMPUTER SCIENCE AND ENGINEERING (DATA SCIENCE)': 'CSE-DS',
    'BIOTECHNOLOGY': 'BioTech',
    'AUTOMOBILE ENGINEERING': 'Auto',
    'AEROSPACE ENGINEERING': 'Aero',
    'CHEMICAL ENGINEERING': 'Chem',
    'INDUSTRIAL ENGINEERING AND MANAGEMENT': 'IEM',
  };
  return abbrs[name] || (name.length > 20 ? name.slice(0, 18) + '…' : name);
}

// ─────────────────────────────
// Start
// ─────────────────────────────
document.addEventListener('DOMContentLoaded', init);

// ─────────────────────────────────────────────────────
// Seat Totals Tab
// ─────────────────────────────────────────────────────
function renderTotals(annFilter) {
  const colleges = filtered.filter(c =>
    annFilter === 'ALL' ? ['A','B','C','D','M','O','P','Z'].includes(c.annexure) : c.annexure === annFilter
  );

  // Aggregate everything from course level
  let totalIntake = 0, totalKea = 0, totalCat2 = 0, totalCat3 = 0;
  let totalPh = 0, totalSpl = 0, totalHk = 0, totalRk = 0, totalTot = 0, totalOver = 0;

  colleges.forEach(col => {
    col.courses.forEach(c => {
      totalIntake += c.total_intake || 0;
      totalKea    += c.total_kea_seats || 0;
      totalCat2   += c.cat2_seats || 0;
      totalCat3   += c.cat3_seats || 0;
      totalPh     += c.kea_ph || 0;
      totalSpl    += c.kea_spl || 0;
      totalHk     += c.kea_hk || 0;
      totalRk     += c.kea_rk || 0;
      totalTot    += c.kea_tot || 0;
      totalOver   += c.over_above_5pct || 0;
    });
  });

  const numColleges = colleges.length;

  // ── Summary cards ────────────────────────────────────
  const summaryCards = [
    { label: 'Total Colleges',   val: numColleges.toLocaleString(),  icon: '🏫', cls: 'sc-colleges' },
    { label: 'Total Intake',     val: totalIntake.toLocaleString(),  icon: '🪑', cls: 'sc-total'    },
    { label: 'KEA / Govt Seats', val: totalKea.toLocaleString(),     icon: '🏛️', cls: 'sc-kea'     },
    { label: 'COMEDK Seats',     val: totalCat2.toLocaleString(),    icon: '🎓', cls: 'sc-comedk'   },
    { label: 'Management Seats', val: totalCat3.toLocaleString(),    icon: '💼', cls: 'sc-mgmt'     },
    { label: 'KEA%',
      val: totalIntake > 0 ? Math.round((totalKea/totalIntake)*100) + '%' : '—',
      icon: '📊', cls: 'sc-pct' },
  ];

  document.getElementById('totals-summary-row').innerHTML = summaryCards.map(s => `
    <div class="totals-sum-card ${s.cls}">
      <div class="tsc-icon">${s.icon}</div>
      <div class="tsc-val">${s.val}</div>
      <div class="tsc-lbl">${s.label}</div>
    </div>
  `).join('');

  // ── Category breakdown table ─────────────────────────
  const catRows = [
    { cat: 'Total Intake',       desc: 'All seats across all categories',           seats: totalIntake, color: '#4f8ef7' },
    { cat: 'KEA – Govt Quota',   desc: 'CAT-1: Reserved for Govt/KEA merit list',   seats: totalKea,    color: '#22c55e' },
    { cat: '  ↳ PH (5%)',        desc: 'Physically Handicapped reservation',         seats: totalPh,     color: '#86efac', indent: true },
    { cat: '  ↳ SPL Reservation',desc: 'Special category (SC/ST/OBC etc.)',          seats: totalSpl,    color: '#86efac', indent: true },
    { cat: '  ↳ HK Region',      desc: 'Hyderabad-Karnataka region seats',           seats: totalHk,     color: '#67e8f9', indent: true },
    { cat: '  ↳ RK Region',      desc: 'Rest of Karnataka seats',                   seats: totalRk,     color: '#67e8f9', indent: true },
    { cat: '  ↳ TOT HK+RK',      desc: 'HK + RK combined total',                    seats: totalTot,    color: '#a5f3fc', indent: true },
    { cat: '  ↳ Over SNQ (5%)',   desc: 'Supernumerary SNQ seats (over intake)',      seats: totalOver,   color: '#fde68a', indent: true },
    { cat: 'COMEDK (CAT-2)',      desc: 'CAT-2: COMEDK UGET merit seats (30%)',      seats: totalCat2,   color: '#a855f7' },
    { cat: 'Management (CAT-3)', desc: 'CAT-3: NRI/Management seats (25%)',          seats: totalCat3,   color: '#f97316' },
  ];

  const maxCat = totalIntake || 1;
  document.getElementById('totals-cat-tbody').innerHTML = catRows.map(row => {
    const pct  = row.seats > 0 && !row.indent ? Math.round((row.seats / totalIntake) * 100) : '';
    const barW = Math.round((row.seats / maxCat) * 100);
    return `<tr class="${row.indent ? 'sub-row' : ''}">
      <td><strong>${row.cat}</strong></td>
      <td class="td-desc">${row.desc}</td>
      <td class="td-seats">${row.seats.toLocaleString()}</td>
      <td>${pct !== '' ? `<span class="kea-pct-badge pct-mid">${pct}%</span>` : '—'}</td>
      <td>
        <div class="mini-bar-bg" style="width:220px">
          <div class="mini-bar-fill" style="width:${barW}%; background:${row.color}"></div>
        </div>
      </td>
    </tr>`;
  }).join('');

  // ── Annexure-wise breakdown ───────────────────────────
  const annexures = annFilter === 'ALL'
    ? ['A','B','C','D','M','O','P','Z']
    : [annFilter];

  const annLabels = {
    A:'Government / VTU', B:'Govt Aided', C:'Private Unaided',
    D:'Private Minority', M:'Public University (UVCE)',
    O:'Private University', P:'Deemed University', Z:'Government (Higher Fees)',
    E:'New Intake (Govt/Pvt)', V:'New Intake (Univ)'
  };
  const annIcons = { A:'🏛️', B:'🤝', C:'🏢', D:'⭐', M:'🎓', O:'🌍', P:'🎖️', Z:'🏛️', E:'✨', V:'⚡' };

  const annRows = annexures.map(ann => {
    const cols = colleges.filter(c => c.annexure === ann);
    let ai=0, ak=0, a2=0, a3=0;
    cols.forEach(col => col.courses.forEach(c => {
      ai += c.total_intake || 0;
      ak += c.total_kea_seats || 0;
      a2 += c.cat2_seats || 0;
      a3 += c.cat3_seats || 0;
    }));
    const keaPct = ai > 0 ? Math.round((ak/ai)*100) : 0;
    const pctCls = keaPct >= 80 ? 'pct-high' : keaPct >= 40 ? 'pct-mid' : 'pct-low';
    return `<tr>
      <td><strong>Annexure ${ann}</strong></td>
      <td>${annIcons[ann]} ${annLabels[ann] || ann}</td>
      <td>${cols.length}</td>
      <td class="td-seats">${ai.toLocaleString()}</td>
      <td class="td-kea">${ak.toLocaleString()}</td>
      <td class="td-comedk">${a2.toLocaleString()}</td>
      <td class="td-mgmt">${a3.toLocaleString()}</td>
      <td><span class="kea-pct-badge ${pctCls}">${keaPct}%</span></td>
    </tr>`;
  });

  // Grand total row
  const gt2 = totalCat2.toLocaleString();
  const gt3 = totalCat3.toLocaleString();
  const gtPct = totalIntake > 0 ? Math.round((totalKea/totalIntake)*100) : 0;
  annRows.push(`<tr class="total-row">
    <td colspan="2"><strong>GRAND TOTAL</strong></td>
    <td><strong>${numColleges}</strong></td>
    <td class="td-seats"><strong>${totalIntake.toLocaleString()}</strong></td>
    <td class="td-kea"><strong>${totalKea.toLocaleString()}</strong></td>
    <td class="td-comedk"><strong>${gt2}</strong></td>
    <td class="td-mgmt"><strong>${gt3}</strong></td>
    <td><span class="kea-pct-badge pct-high">${gtPct}%</span></td>
  </tr>`);

  document.getElementById('totals-ann-tbody').innerHTML = annRows.join('');

  // ── KEA internal quota breakdown ──────────────────────
  const keaRows = annexures.map(ann => {
    const cols = colleges.filter(c => c.annexure === ann);
    let ph=0,spl=0,hk=0,rk=0,tot=0,over=0;
    cols.forEach(col => col.courses.forEach(c => {
      ph   += c.kea_ph || 0;
      spl  += c.kea_spl || 0;
      hk   += c.kea_hk || 0;
      rk   += c.kea_rk || 0;
      tot  += c.kea_tot || 0;
      over += c.over_above_5pct || 0;
    }));
    return `<tr>
      <td><strong>Annexure ${ann}</strong></td>
      <td>${annIcons[ann]} ${annLabels[ann] || ann}</td>
      <td>${ph.toLocaleString()}</td>
      <td>${spl.toLocaleString()}</td>
      <td class="td-hk">${hk.toLocaleString()}</td>
      <td class="td-rk">${rk.toLocaleString()}</td>
      <td>${tot.toLocaleString()}</td>
      <td>${over.toLocaleString()}</td>
    </tr>`;
  });

  keaRows.push(`<tr class="total-row">
    <td colspan="2"><strong>TOTAL</strong></td>
    <td><strong>${totalPh.toLocaleString()}</strong></td>
    <td><strong>${totalSpl.toLocaleString()}</strong></td>
    <td class="td-hk"><strong>${totalHk.toLocaleString()}</strong></td>
    <td class="td-rk"><strong>${totalRk.toLocaleString()}</strong></td>
    <td><strong>${totalTot.toLocaleString()}</strong></td>
    <td><strong>${totalOver.toLocaleString()}</strong></td>
  </tr>`);

  document.getElementById('totals-kea-tbody').innerHTML = keaRows.join('');
}

// ─────────────────────────────
// Annexure Data Download logic
// ─────────────────────────────
function updateDownloadDropdown(year) {
  const select = document.getElementById('download-ann-select');
  if (!select) return;
  
  const valBefore = select.value;
  
  if (year === '2024') {
    select.innerHTML = `
      <option value="ALL">All Annexures (Combined)</option>
      <option value="A">Annexure A - Government</option>
      <option value="B">Annexure B - Govt Aided</option>
      <option value="C">Annexure C - Private Unaided</option>
      <option value="D">Annexure D - Private Minority</option>
      <option value="M">Annexure M - Public Univ.</option>
      <option value="O">Annexure O - Pvt Univ.</option>
      <option value="P">Annexure P - Deemed Univ.</option>
      <option value="Undefined">Annexure Undefined - Special Category</option>
    `;
  } else {
    select.innerHTML = `
      <option value="ALL">All Annexures (Combined)</option>
      <option value="A">Annexure A - Government</option>
      <option value="B">Annexure B - Govt Aided</option>
      <option value="C">Annexure C - Private Unaided</option>
      <option value="D">Annexure D - Private Minority</option>
      <option value="M">Annexure M - Public Univ.</option>
      <option value="O">Annexure O - Pvt Univ.</option>
      <option value="P">Annexure P - Deemed Univ.</option>
      <option value="Z">Annexure Z - Govt (Higher Fees)</option>
      <option value="E">Annexure E - New Intake (Govt/Pvt)</option>
      <option value="V">Annexure V - New Intake (Univ)</option>
      <option value="Undefined">Annexure Undefined - Special Category</option>
    `;
  }
  
  if ([...select.options].some(o => o.value === valBefore)) {
    select.value = valBefore;
  } else {
    select.value = 'ALL';
  }
}

// ─────────────────────────────
// Annexure Data Download logic
// ─────────────────────────────
function getScopedBaseColleges() {
  if (!currentUser) return [];

  const effectiveRole = currentUser.role === 'superuser' ? superuserPerspective : currentUser.role;

  if (effectiveRole === 'authority') {
    return allData.colleges;
  }

  if (effectiveRole === 'institution') {
    const groupId = currentUser.role === 'superuser' ? superuserGroup : currentUser.institutionGroup;
    if (groupId && INSTITUTION_GROUPS[groupId]) {
      const groupColleges = INSTITUTION_GROUPS[groupId].colleges || [];
      const groupCleanNames = new Set(groupColleges.map(col => getCleanCollegeName(col.college_name)));
      return allData.colleges.filter(col => groupCleanNames.has(getCleanCollegeName(col.college_name)));
    }
    return [];
  }

  if (effectiveRole === 'counsellor') {
    const { rank: studentRank, category: studentCategory } = getActiveStudentProfile();
    // Return colleges with courses that have cutoff data matching the student's category and rank suitability
    return allData.colleges.filter(col => {
      return col.courses.some(c => {
        const cutoff = getCourseCutoff(c, studentCategory);
        return !isNaN(cutoff);
      });
    });
  }

  return [];
}

function updateDownloadPreview() {
  const alertEl = document.getElementById('download-scope-alert');
  if (alertEl) {
    alertEl.innerHTML = `<span>📥 <strong>Data Export Scope:</strong> Select Year, College Group, Individual College, District, or Course filters to export custom CSV/JSON seat matrices and cutoff ranks.</span>`;
    alertEl.style.background = 'rgba(59, 130, 246, 0.1)';
    alertEl.style.borderColor = 'rgba(59, 130, 246, 0.25)';
    alertEl.style.color = 'var(--blue)';
  }

  // Fetch Criteria Filters
  const selectedYear = document.getElementById('download-year-select')?.value || allData.year || '2025';
  const minSeats = parseInt(document.getElementById('download-min-seats')?.value) || 0;
  const district = document.getElementById('download-district-select')?.value || '';
  const course = document.getElementById('download-course-select')?.value || '';
  const selectedGroup = document.getElementById('download-group-select')?.value || '';
  const selectedCollege = document.getElementById('download-college-select')?.value || '';

  // Get selected Annexure checkboxes
  const selectedAnn = Array.from(document.querySelectorAll('#download-annexures-grid input[type="checkbox"]:checked')).map(cb => cb.value);

  const groupAnnexureMap = {
    'GOVT': ['A', 'E', 'Z'],
    'AIDED': ['B'],
    'UNAIDED': ['C'],
    'MINORITY': ['D'],
    'UNIV': ['O', 'P', 'V']
  };

  // Filter the Database by selected year
  let baseColleges = allData.colleges || [];
  if (selectedYear === '2026' && cache2026 && cache2026.colleges) baseColleges = cache2026.colleges;
  else if (selectedYear === '2024' && cache2024 && cache2024.colleges) baseColleges = cache2024.colleges;
  else if (selectedYear === '2025' && cache2025 && cache2025.colleges) baseColleges = cache2025.colleges;

  let collegeMatchCount = 0;
  let courseMatchCount = 0;
  let totalSeatsSum = 0;

  baseColleges.forEach(col => {
    // Group filter check
    if (selectedGroup && groupAnnexureMap[selectedGroup]) {
      if (!groupAnnexureMap[selectedGroup].includes(col.annexure)) return;
    }

    // Specific College filter check
    if (selectedCollege) {
      if (col.college_number != selectedCollege && col.kea_code != selectedCollege) return;
    }

    // Annexure check
    if (col.annexure === 'E' || col.annexure === 'V') {
      if (!selectedAnn.includes(col.annexure)) return;
    } else {
      if (!selectedAnn.includes(col.annexure || 'Undefined')) return;
    }

    // District check
    if (district && col.district !== district) return;

    // Course matches inside college
    const matchingCourses = col.courses.filter(c => {
      if (course && c.course_name !== course) return false;
      if (minSeats > 0 && (c.total_intake || 0) < minSeats) return false;
      return true;
    });

    if (matchingCourses.length > 0) {
      collegeMatchCount++;
      courseMatchCount += matchingCourses.length;
      matchingCourses.forEach(c => {
        totalSeatsSum += (c.total_intake || 0);
      });
    }
  });

  // Update Preview Counters
  const elCol = document.getElementById('download-preview-colleges');
  const elCr = document.getElementById('download-preview-courses');
  const elSt = document.getElementById('download-preview-seats');
  if (elCol) elCol.textContent = collegeMatchCount.toLocaleString();
  if (elCr) elCr.textContent = courseMatchCount.toLocaleString();
  if (elSt) elSt.textContent = totalSeatsSum.toLocaleString();
}

function triggerTabDownload() {
  const selectedYear = document.getElementById('download-year-select')?.value || allData.year || '2025';
  const minSeats = parseInt(document.getElementById('download-min-seats')?.value) || 0;
  const district = document.getElementById('download-district-select')?.value || '';
  const course = document.getElementById('download-course-select')?.value || '';
  const selectedGroup = document.getElementById('download-group-select')?.value || '';
  const selectedCollege = document.getElementById('download-college-select')?.value || '';
  const datasetType = document.querySelector('input[name="download-dataset-type"]:checked')?.value || 'seat_matrix';
  const format = document.querySelector('input[name="download-format"]:checked')?.value || 'csv';

  const selectedAnn = Array.from(document.querySelectorAll('#download-annexures-grid input[type="checkbox"]:checked')).map(cb => cb.value);

  if (selectedAnn.length === 0) {
    alert("Please select at least one Annexure category to download.");
    return;
  }

  const groupAnnexureMap = {
    'GOVT': ['A', 'E', 'Z'],
    'AIDED': ['B'],
    'UNAIDED': ['C'],
    'MINORITY': ['D'],
    'UNIV': ['O', 'P', 'V']
  };

  let baseColleges = allData.colleges || [];
  if (selectedYear === '2026' && cache2026 && cache2026.colleges) baseColleges = cache2026.colleges;
  else if (selectedYear === '2024' && cache2024 && cache2024.colleges) baseColleges = cache2024.colleges;
  else if (selectedYear === '2025' && cache2025 && cache2025.colleges) baseColleges = cache2025.colleges;
  const filteredData = [];

  baseColleges.forEach(col => {
    // Group filter check
    if (selectedGroup && groupAnnexureMap[selectedGroup]) {
      if (!groupAnnexureMap[selectedGroup].includes(col.annexure)) return;
    }

    // Specific College filter check
    if (selectedCollege) {
      if (col.college_number != selectedCollege && col.kea_code != selectedCollege) return;
    }

    // Annexure check
    if (col.annexure === 'E' || col.annexure === 'V') {
      if (!selectedAnn.includes(col.annexure)) return;
    } else {
      if (!selectedAnn.includes(col.annexure || 'Undefined')) return;
    }

    // District check
    if (district && col.district !== district) return;

    // Filter courses
    const matchingCourses = col.courses.filter(c => {
      if (course && c.course_name !== course) return false;
      if (minSeats > 0 && (c.total_intake || 0) < minSeats) return false;
      return true;
    });

    if (matchingCourses.length > 0) {
      filteredData.push({
        ...col,
        courses: matchingCourses
      });
    }
  });

  if (filteredData.length === 0) {
    alert("No records match your selected criteria. Adjust your filters and try again.");
    return;
  }

  // Construct filename
  let filename = datasetType === 'closing_ranks' ? `kcet_${selectedYear}_closing_ranks` : `kcet_${selectedYear}_seat_matrix`;
  if (selectedGroup) filename += `_group_${selectedGroup.toLowerCase()}`;
  if (selectedCollege) filename += `_college_${selectedCollege}`;
  if (district) filename += `_${district.toLowerCase().replace(/ /g, '_')}`;
  if (course) filename += `_${course.toLowerCase().replace(/[^a-z0-9]/g, '_')}`;
  filename += `.${format}`;

  if (format === 'json') {
    const jsonStr = JSON.stringify(filteredData, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/json' });
    triggerDownload(blob, filename);
  } else {
    let headers = [];
    if (datasetType === 'closing_ranks') {
      headers = [
        'College Code', 'College Number', 'College Name', 'Address', 'Annexure', 'College Type', 'District', 'Course Name',
        'Round 1 GM Cutoff', 'Round 1 SC Cutoff', 'Round 1 ST Cutoff', 'Round 1 Cat-1 Cutoff', 'Round 1 2A Cutoff', 'Round 1 2B Cutoff', 'Round 1 3A Cutoff', 'Round 1 3B Cutoff', 'Round 1 GMK Cutoff', 'Round 1 GMR Cutoff', 'Round 1 GMH Cutoff',
        'Round 2 GM Cutoff', 'Round 2 SC Cutoff', 'Round 2 ST Cutoff', 'Round 2 Cat-1 Cutoff', 'Round 2 2A Cutoff', 'Round 2 2B Cutoff', 'Round 2 3A Cutoff', 'Round 2 3B Cutoff',
        'Round 3 GM Cutoff', 'Round 3 SC Cutoff', 'Round 3 ST Cutoff', 'Round 3 Cat-1 Cutoff', 'Round 3 2A Cutoff', 'Round 3 2B Cutoff', 'Round 3 3A Cutoff', 'Round 3 3B Cutoff'
      ];
    } else {
      headers = [
        'College Code', 'College Number', 'College Name', 'Address', 'Annexure', 'College Type', 'District', 'Course Name',
        'Total Intake', 'KEA Seats', 'COMEDK Seats', 'Mgmt Seats', 'Rest of Karnataka (RK)', 'Hyderabad Karnataka (HK 371-J)', 'SNQ Seats (5%)',
        'Sports', 'NCC', 'Scouts & Guides', 'Defence', 'Ex-Defence', 'CAPF', 'PH'
      ];
    }

    const csvRows = [headers.join(',')];

    filteredData.forEach(col => {
      col.courses.forEach(c => {
        let row = [];
        if (datasetType === 'closing_ranks') {
          const r1 = c.round1_cutoff || {};
          const r2 = c.round2_cutoff || {};
          const r3 = c.round3_cutoff || {};
          row = [
            `"${col.kea_code || ''}"`,
            col.college_number || '',
            `"${col.college_name.replace(/"/g, '""')}"`,
            `"${(col.address || '').replace(/"/g, '""')}"`,
            col.annexure || 'N/A',
            `"${col.college_type}"`,
            col.district || '',
            `"${c.course_name}"`,
            r1.GM || '', r1.SC || '', r1.ST || '', r1['1'] || '', r1['2A'] || '', r1['2B'] || '', r1['3A'] || '', r1['3B'] || '', r1.GMK || '', r1.GMR || '', r1.GMH || '',
            r2.GM || '', r2.SC || '', r2.ST || '', r2['1'] || '', r2['2A'] || '', r2['2B'] || '', r2['3A'] || '', r2['3B'] || '',
            r3.GM || '', r3.SC || '', r3.ST || '', r3['1'] || '', r3['2A'] || '', r3['2B'] || '', r3['3A'] || '', r3['3B'] || ''
          ];
        } else {
          row = [
            `"${col.kea_code || ''}"`,
            col.college_number || '',
            `"${col.college_name.replace(/"/g, '""')}"`,
            `"${(col.address || '').replace(/"/g, '""')}"`,
            col.annexure || 'N/A',
            `"${col.college_type}"`,
            col.district || '',
            `"${c.course_name}"`,
            c.total_intake || 0,
            c.total_kea_seats || 0,
            c.cat2_seats || 0,
            c.cat3_seats || 0,
            c.kea_rk || 0,
            c.kea_hk || 0,
            c.snq_5pct || c.over_above_5pct || 0,
            c.sports || 0,
            c.ncc || 0,
            c.sct_guides || 0,
            c.defence || 0,
            c.ex_defence || 0,
            c.capf || 0,
            c.kea_ph || 0
          ];
        }
        csvRows.push(row.join(','));
      });
    });

    const csvContent = '\uFEFF' + csvRows.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    triggerDownload(blob, filename);
  }
}

function bindDownloadTabEvents() {
  const yearSel = document.getElementById('download-year-select');
  const minSeatsInput = document.getElementById('download-min-seats');
  const distSel = document.getElementById('download-district-select');
  const courseSel = document.getElementById('download-course-select');
  const groupSel = document.getElementById('download-group-select');
  const collegeSel = document.getElementById('download-college-select');
  const toggleBtn = document.getElementById('btn-download-toggle-annexures');
  const executeBtn = document.getElementById('btn-execute-download');

  // Change listeners
  [yearSel, minSeatsInput, distSel, courseSel, groupSel, collegeSel].forEach(el => {
    if (el) el.addEventListener('change', updateDownloadPreview);
  });
  if (minSeatsInput) {
    minSeatsInput.addEventListener('input', updateDownloadPreview);
  }

  // Bind checkboxes in grid
  document.querySelectorAll('#download-annexures-grid input[type="checkbox"]').forEach(cb => {
    cb.addEventListener('change', updateDownloadPreview);
  });

  // Toggle all annexures
  if (toggleBtn) {
    toggleBtn.addEventListener('click', () => {
      const checkboxes = document.querySelectorAll('#download-annexures-grid input[type="checkbox"]');
      const allChecked = Array.from(checkboxes).every(cb => cb.checked);
      checkboxes.forEach(cb => cb.checked = !allChecked);
      updateDownloadPreview();
    });
  }

  // Execute download click
  if (executeBtn) {
    executeBtn.addEventListener('click', triggerTabDownload);
  }

  // Sync Year selects
  if (yearSel) {
    yearSel.addEventListener('change', async (e) => {
      const globalYearSelect = document.getElementById('year-select');
      if (globalYearSelect) {
        globalYearSelect.value = e.target.value;
      }
      await loadYearData(e.target.value);
      updateDownloadPreview();
    });
  }
}


function triggerDownload(blob, filename) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.setAttribute('href', url);
  link.setAttribute('download', filename);
  link.style.visibility = 'hidden';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

// ─────────────────────────────────────────────────────
// Rank Predictor Logic
// ─────────────────────────────────────────────────────
function cleanCourseStr(name) {
  if (!name) return '';
  return name.toUpperCase().replace(/[^A-Z0-9]/g, '');
}

function resolveCourseCutoff(college, course, category, selectedRound) {
  const activeYear = allData.year || '2026';
  
  const roundKeyMap = {
    'mock_round1': 'mock_round1_cutoff',
    'round1': 'round1_cutoff',
    'round2': 'round2_cutoff',
    'round3': 'round3_cutoff'
  };

  const targetKey = roundKeyMap[selectedRound] || 'round1_cutoff';

  // 1. Direct match in activeYear (if the exact requested round cutoff is published)
  const directCutoffs = course[targetKey] || {};
  const directVal = directCutoffs[category];
  if (directVal && !isNaN(parseFloat(directVal))) {
    const roundShort = selectedRound === 'mock_round1' ? 'Mock' : (selectedRound === 'round1' ? 'R1' : (selectedRound === 'round2' ? 'R2' : 'R3'));
    return {
      cutoff: parseFloat(directVal),
      sourceYear: activeYear,
      sourceLabel: `${activeYear} ${roundShort}`,
      isFallback: false,
      isEstimated: false
    };
  }

  // 2. If requested round is NOT published in activeYear (e.g. 2026 Round 2 or Round 3),
  // predict using 2026 Round 1 (or Mock) combined with historical progression ratio from 2025/2024!
  const base2026R1Str = (course.round1_cutoff || {})[category] || (course.mock_round1_cutoff || {})[category];
  if (base2026R1Str && !isNaN(parseFloat(base2026R1Str))) {
    const base2026R1 = parseFloat(base2026R1Str);
    
    // Find matching course in 2025 cache
    const prevCache = cache2025 || (activeYear === '2025' ? cache2024 : null);
    let ratio = null;

    if (prevCache && prevCache.colleges) {
      const prevCol = prevCache.colleges.find(c => (c.kea_code && c.kea_code === college.kea_code) || c.college_name === college.college_name);
      if (prevCol && prevCol.courses) {
        const stdTarget = cleanCourseStr(course.course_name);
        const prevCourse = prevCol.courses.find(c => cleanCourseStr(c.course_name) === stdTarget);
        if (prevCourse) {
          const pR1 = parseFloat((prevCourse.round1_cutoff || {})[category]);
          const pTarget = parseFloat((prevCourse[targetKey] || {})[category]);
          if (pR1 && pTarget && pR1 > 0) {
            ratio = pTarget / pR1;
          }
        }
      }
    }

    // Default historical expansion ratios if exact course ratio is unavailable
    if (!ratio) {
      if (selectedRound === 'round2') ratio = 1.12;       // ~12% rank expansion in Round 2
      else if (selectedRound === 'round3') ratio = 1.25;  // ~25% rank expansion in Round 3
      else ratio = 1.0;
    }

    const estCutoff = Math.round(base2026R1 * ratio);
    const pctDiff = Math.round((ratio - 1) * 100);
    const pctSign = pctDiff >= 0 ? `+${pctDiff}%` : `${pctDiff}%`;
    const targetShort = selectedRound === 'round2' ? 'R2' : (selectedRound === 'round3' ? 'R3' : 'R1');

    return {
      cutoff: estCutoff,
      sourceYear: activeYear,
      sourceLabel: `Est. ${activeYear} ${targetShort} (${pctSign})`,
      isFallback: true,
      isEstimated: true
    };
  }

  // 3. Fallback to 2025 dataset directly if activeYear has no published ranks for this course
  const prevCache = cache2025 || cache2024;
  if (prevCache && prevCache.colleges) {
    const prevCol = prevCache.colleges.find(c => (c.kea_code && c.kea_code === college.kea_code) || c.college_name === college.college_name);
    if (prevCol && prevCol.courses) {
      const stdTarget = cleanCourseStr(course.course_name);
      const prevCourse = prevCol.courses.find(c => cleanCourseStr(c.course_name) === stdTarget);
      if (prevCourse) {
        const roundsOrder = [targetKey, 'round3_cutoff', 'round2_cutoff', 'round1_cutoff', 'mock_round1_cutoff'];
        for (const rKey of roundsOrder) {
          const val = (prevCourse[rKey] || {})[category];
          if (val && !isNaN(parseFloat(val))) {
            const rShort = rKey === 'mock_round1_cutoff' ? 'Mock' : (rKey === 'round1_cutoff' ? 'R1' : (rKey === 'round2_cutoff' ? 'R2' : 'R3'));
            return {
              cutoff: parseFloat(val),
              sourceYear: prevCache.year || '2025',
              sourceLabel: `${prevCache.year || '2025'} ${rShort}`,
              isFallback: true,
              isEstimated: false
            };
          }
        }
      }
    }
  }

  return null;
}

function computeCourseYoYTrend(college, courseName, category, selectedRound) {
  const roundKeys = {
    'mock_round1': 'mock_round1_cutoff',
    'round1': 'round1_cutoff',
    'round2': 'round2_cutoff',
    'round3': 'round3_cutoff'
  };
  const targetKey = roundKeys[selectedRound] || 'round1_cutoff';

  let val2026 = null;
  let val2025 = null;
  let val2024 = null;

  // Resolve 2026
  if (cache2026 && cache2026.colleges) {
    const colObj = cache2026.colleges.find(c => (c.kea_code && c.kea_code === college.kea_code) || c.college_name === college.college_name);
    if (colObj && colObj.courses) {
      const crObj = colObj.courses.find(c => c.course_name === courseName);
      if (crObj && crObj[targetKey]) {
        val2026 = parseFloat(crObj[targetKey][category]);
      }
    }
  } else if (allData && allData.year === '2026') {
    const colObj = allData.colleges.find(c => (c.kea_code && c.kea_code === college.kea_code) || c.college_name === college.college_name);
    if (colObj && colObj.courses) {
      const crObj = colObj.courses.find(c => c.course_name === courseName);
      if (crObj && crObj[targetKey]) {
        val2026 = parseFloat(crObj[targetKey][category]);
      }
    }
  }

  // Resolve 2025
  if (cache2025 && cache2025.colleges) {
    const colObj = cache2025.colleges.find(c => (c.kea_code && c.kea_code === college.kea_code) || c.college_name === college.college_name);
    if (colObj && colObj.courses) {
      const crObj = colObj.courses.find(c => c.course_name === courseName);
      if (crObj && crObj[targetKey]) {
        val2025 = parseFloat(crObj[targetKey][category]);
      }
    }
  } else if (allData && allData.year === '2025') {
    const colObj = allData.colleges.find(c => (c.kea_code && c.kea_code === college.kea_code) || c.college_name === college.college_name);
    if (colObj && colObj.courses) {
      const crObj = colObj.courses.find(c => c.course_name === courseName);
      if (crObj && crObj[targetKey]) {
        val2025 = parseFloat(crObj[targetKey][category]);
      }
    }
  }

  // Resolve 2024
  if (cache2024 && cache2024.colleges) {
    const colObj = cache2024.colleges.find(c => (c.kea_code && c.kea_code === college.kea_code) || c.college_name === college.college_name);
    if (colObj && colObj.courses) {
      const crObj = colObj.courses.find(c => c.course_name === courseName);
      if (crObj && crObj[targetKey]) {
        val2024 = parseFloat(crObj[targetKey][category]);
      }
    }
  } else if (allData && allData.year === '2024') {
    const colObj = allData.colleges.find(c => (c.kea_code && c.kea_code === college.kea_code) || c.college_name === college.college_name);
    if (colObj && colObj.courses) {
      const crObj = colObj.courses.find(c => c.course_name === courseName);
      if (crObj && crObj[targetKey]) {
        val2024 = parseFloat(crObj[targetKey][category]);
      }
    }
  }

  // Compute shift
  let pctShift = 0;
  let hasShift = false;
  if (val2026 && val2025 && !isNaN(val2026) && !isNaN(val2025) && val2025 > 0) {
    pctShift = ((val2026 - val2025) / val2025) * 100;
    hasShift = true;
  } else if (val2025 && val2024 && !isNaN(val2025) && !isNaN(val2024) && val2024 > 0) {
    pctShift = ((val2025 - val2024) / val2024) * 100;
    hasShift = true;
  }

  if (!hasShift || Math.abs(pctShift) < 1) {
    return {
      label: '➡️ Stable',
      color: 'var(--text-muted)',
      bg: 'rgba(255,255,255,0.03)',
      pct: 0
    };
  }

  if (pctShift < 0) {
    return {
      label: `🔥 Tightening (-${Math.abs(Math.round(pctShift))}%)`,
      color: '#f43f5e',
      bg: 'rgba(244,63,94,0.1)',
      pct: pctShift
    };
  } else {
    return {
      label: `📉 Easing (+${Math.round(pctShift)}%)`,
      color: '#22c55e',
      bg: 'rgba(34,197,94,0.1)',
      pct: pctShift
    };
  }
}

function runPrediction() {
  const rankInput = document.getElementById('pred-rank');
  const catSel = document.getElementById('pred-category');
  const roundSel = document.getElementById('pred-round');
  const courseSel = document.getElementById('pred-course');
  
  const userRank = parseInt(rankInput.value);
  if (isNaN(userRank) || userRank <= 0) {
    alert("Please enter a valid rank.");
    return;
  }
  
  const category = catSel.value;
  const selectedRound = roundSel ? roundSel.value : 'round1';
  const preferredCourse = courseSel.value;

  // Log prediction event to backend PostgreSQL
  fetch('/api/log', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      username: currentUser ? currentUser.name : 'guest',
      action: 'PREDICTION',
      details: `Rank: ${userRank}, Category: ${category}, Round: ${selectedRound}, Course: ${preferredCourse || 'All'}`
    })
  }).catch(err => console.error(err));
  
  const results = [];
  const seen = new Set();
  
  allData.colleges.forEach(college => {
    college.courses.forEach(course => {
      // Filter by course name if selected
      if (preferredCourse && course.course_name !== preferredCourse) {
        return;
      }
      
      const cutoffInfo = resolveCourseCutoff(college, course, category, selectedRound);
      if (!cutoffInfo) return; // No cutoff found across current and previous year datasets
      
      const cutoff = cutoffInfo.cutoff;
      
      // Deduplicate identical combinations of college, course, and cutoff
      const key = `${college.college_number}_${course.course_name}_${cutoff}`;
      if (seen.has(key)) return;
      seen.add(key);
      
      const diff = cutoff - userRank;
      
      // Filter out low chance
      if (diff < -3000) return;
      
      let chance = 'Borderline';
      let chanceClass = 'badge-borderline';
      
      if (diff >= 5000) {
        chance = 'Very High';
        chanceClass = 'badge-very-high';
      } else if (diff >= 0) {
        chance = 'High';
        chanceClass = 'badge-high';
      }
      
      const trend = computeCourseYoYTrend(college, course.course_name, category, selectedRound);
      
      results.push({
        college,
        courseName: course.course_name,
        cutoff: cutoff,
        diff: diff,
        chance: chance,
        chanceClass: chanceClass,
        sourceLabel: cutoffInfo.sourceLabel,
        isFallback: cutoffInfo.isFallback,
        isEstimated: cutoffInfo.isEstimated,
        trend: trend
      });
    });
  });
  
  // Sort results by cutoff ascending (most competitive first)
  results.sort((a, b) => a.cutoff - b.cutoff);
  
  renderPredictionResults(results, selectedRound);
}

function renderPredictionResults(results, selectedRound) {
  const tbody = document.getElementById('pred-tbody');
  const title = document.getElementById('pred-results-title');
  const wrap = document.getElementById('pred-results-wrap');
  const emptyState = document.getElementById('pred-empty-state');
  const header = document.getElementById('pred-cutoff-header');
  
  if (header) {
    header.textContent = 'Cutoff Rank & Basis';
  }
  
  if (results.length === 0) {
    tbody.innerHTML = '';
    title.style.display = 'none';
    wrap.style.display = 'none';
    emptyState.style.display = 'block';
    emptyState.innerHTML = `
      <div class="empty-state-icon">🔮</div>
      <div class="empty-state-text">No matches found.<br><small style="color:#6b7799">Try entering a different rank or category.</small></div>
    `;
    return;
  }
  
  emptyState.style.display = 'none';
  title.style.display = 'block';
  wrap.style.display = 'block';
  
  tbody.innerHTML = results.map((res, index) => {
    const col = res.college;
    const diffText = res.diff >= 0 ? `+${res.diff.toLocaleString()}` : res.diff.toLocaleString();
    const diffClass = res.diff >= 0 ? 'text-green' : 'text-orange';
    
    let badgeColor = 'var(--blue)';
    let badgeBg = 'rgba(59,130,246,0.15)';
    if (res.isEstimated) {
      badgeColor = '#f59e0b';
      badgeBg = 'rgba(245,158,11,0.15)';
    } else if (res.isFallback) {
      badgeColor = 'var(--purple)';
      badgeBg = 'rgba(168,85,247,0.15)';
    }
    
    return `<tr class="pred-row" data-college-number="${col.college_number}" style="cursor:pointer; transition:background 0.2s;">
      <td><span class="card-type-pill pill-${col.annexure}" style="font-size:11px; padding: 2px 6px;">${col.kea_code || col.college_number}</span></td>
      <td><strong>${escHtml(col.college_name)}</strong><br><small style="color:var(--text-muted)">📍 ${escHtml(col.district)}</small></td>
      <td>${res.courseName}</td>
      <td style="font-family:var(--font-display); font-weight:700; text-align:right; line-height:1.3;">
        ${res.cutoff.toLocaleString()}<br>
        <span style="font-size:10px; font-weight:600; padding:2px 6px; border-radius:4px; background:${badgeBg}; color:${badgeColor}; display:inline-block; margin-top:2px;">${res.sourceLabel}</span>
      </td>
      <td class="${diffClass}" style="font-family:var(--font-display); font-weight:700; text-align:right;">${diffText}</td>
      <td style="text-align:center;"><span class="badge-chance ${res.chanceClass}">${res.chance}</span></td>
      <td style="text-align:center;"><span style="font-size:10px; font-weight:700; padding:4px 8px; border-radius:6px; background:${res.trend.bg}; color:${res.trend.color}; border:1px solid rgba(255,255,255,0.03); white-space:nowrap;">${res.trend.label}</span></td>
    </tr>`;
  }).join('');
  
  // Attach event listener for row clicks
  tbody.querySelectorAll('.pred-row').forEach(row => {
    row.addEventListener('click', () => {
      const colNum = row.dataset.collegeNumber;
      const collegeObj = allData.colleges.find(c => c.college_number == colNum);
      if (collegeObj) {
        openModal(collegeObj);
      }
    });
  });
}

// ─────────────────────────────────────────────────────
// Q&A Assistant Logic
// ─────────────────────────────────────────────────────
function initAssistant() {
  const sendBtn = document.getElementById('assistant-send-btn');
  const inputEl = document.getElementById('assistant-input');
  const suggestionsBox = document.getElementById('assistant-suggestions');

  if (sendBtn && inputEl) {
    sendBtn.addEventListener('click', () => {
      runAssistantQuery(inputEl.value);
    });

    inputEl.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        runAssistantQuery(inputEl.value);
      }
    });
  }

  if (suggestionsBox) {
    suggestionsBox.addEventListener('click', (e) => {
      const chip = e.target.closest('.chip');
      if (!chip) return;
      const queryText = chip.dataset.query || chip.textContent;
      if (inputEl) {
        inputEl.value = queryText;
        runAssistantQuery(queryText);
      }
    });
  }
}

function runAssistantQuery(query) {
  const q = query.trim();
  if (!q) return;

  const container = document.getElementById('assistant-response-container');
  const userText = document.getElementById('assistant-user-text');
  const textResponse = document.getElementById('assistant-text-response');
  const resultsWrapper = document.getElementById('assistant-results-wrapper');

  if (!container || !userText || !textResponse || !resultsWrapper) return;

  // Show container
  container.style.display = 'block';
  
  // Set user query text
  userText.textContent = q;

  // Clear previous response and show typing indicator
  textResponse.innerHTML = `
    <div class="typing-indicator">
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
    </div>
  `;
  resultsWrapper.innerHTML = '';

  // Scroll response container into view smoothly
  container.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

  // Simulate typing delay for premium UX
  setTimeout(() => {
    try {
      const analysis = parseAssistantQuery(q);
      const response = generateAssistantResponse(analysis);
      
      // Render text response
      textResponse.innerHTML = formatMarkdown(response.text);

      // Render HTML results (cards or table)
      resultsWrapper.innerHTML = response.html || '';

      // Bind click events on cards inside assistant results
      resultsWrapper.querySelectorAll('.college-card').forEach(card => {
        card.addEventListener('click', () => {
          const colNum = card.dataset.collegeNumber;
          const collegeObj = allData.colleges.find(c => c.college_number == colNum);
          if (collegeObj) {
            openModal(collegeObj);
          }
        });
      });

      // Bind click events on table rows
      resultsWrapper.querySelectorAll('.assistant-row-click').forEach(row => {
        row.addEventListener('click', () => {
          const colNum = row.dataset.collegeNumber;
          const collegeObj = allData.colleges.find(c => c.college_number == colNum);
          if (collegeObj) {
            openModal(collegeObj);
          }
        });
      });

    } catch (err) {
      console.error(err);
      textResponse.innerHTML = `<span style="color:#ef4444;">⚠️ Sorry, I encountered an error processing your query. Please try again.</span>`;
    }
  }, 450);
}

function parseAssistantQuery(queryStr) {
  let norm = queryStr.toLowerCase();
  
  // Remove periods from acronyms (e.g. c.s.e. -> cse, c.s -> cs)
  norm = norm.replace(/\./g, '');
  
  // Remove other punctuation
  norm = norm.replace(/[?,!]/g, '');
  
  // Normalize spacing in common acronyms (e.g. c s e -> cse, i s e -> ise, e c e -> ece, e e e -> eee, c s -> cs)
  norm = norm.replace(/\b(c)\s+(s)\s+(e)\b/g, 'cse');
  norm = norm.replace(/\b(i)\s+(s)\s+(e)\b/g, 'ise');
  norm = norm.replace(/\b(e)\s+(c)\s+(e)\b/g, 'ece');
  norm = norm.replace(/\b(e)\s+(e)\s+(e)\b/g, 'eee');
  norm = norm.replace(/\b(c)\s+(s)\b/g, 'cs');
  norm = norm.replace(/\b(i)\s+(s)\b/g, 'is');
  norm = norm.replace(/\b(e)\s+(e)\b/g, 'ee');
  norm = norm.replace(/\b(d)\s+(s)\b/g, 'ds');
  norm = norm.replace(/\b(b)\s+(t)\b/g, 'bt');
  norm = norm.replace(/\b(a)\s+(e)\b/g, 'ae');
  norm = norm.replace(/\b(t)\s+(c)\b/g, 'tc');

  // Replace multiple spaces with a single space
  norm = norm.replace(/\s+/g, ' ').trim();
  
  // 1. Extract Rank
  let rank = null;
  const kMatch = norm.match(/\b(\d+(?:\.\d+)?)\s*k\b/);
  if (kMatch) {
    rank = Math.round(parseFloat(kMatch[1]) * 1000);
  } else {
    const numMatch = norm.match(/\b\d{3,6}\b/);
    if (numMatch) {
      rank = parseInt(numMatch[0]);
    }
  }

  // 2. Extract Category
  let category = null;
  const catRegex = /\b(gmk|gmr|gm|1g|1k|1r|2ag|2ak|2ar|2bg|2bk|2br|3ag|3ak|3ar|3bg|3bk|3br|scg|sck|scr|stg|stk|str)\b/i;
  const catMatch = norm.match(catRegex);
  if (catMatch) {
    category = catMatch[1].toUpperCase();
  }

  // 3. Extract District
  let district = null;
  const districtAliases = {
    'bangalore': 'Bangalore', 'bengaluru': 'Bangalore',
    'mysore': 'Mysore', 'mysuru': 'Mysore',
    'mangalore': 'Mangalore', 'mangaluru': 'Mangalore',
    'belgaum': 'Belgaum', 'belagavi': 'Belgaum',
    'gulbarga': 'Gulbarga', 'kalaburagi': 'Gulbarga',
    'shimoga': 'Shimoga', 'shivamogga': 'Shimoga',
    'tumkur': 'Tumkur', 'tumakuru': 'Tumkur',
    'hubli': 'Dharwad', 'dharwad': 'Dharwad', 'hubballi': 'Dharwad',
    'hassan': 'Hassan', 'udupi': 'Udupi', 'karwar': 'Karwar',
    'davanagere': 'Davanagere', 'bellary': 'Bellary', 'ballari': 'Bellary',
    'mandya': 'Mandya', 'kolar': 'Kolar', 'chickballapur': 'Chickballapur',
    'chamarajanagar': 'Chamarajanagar', 'bidar': 'Bidar', 'raichur': 'Raichur',
    'koppal': 'Koppal', 'gadag': 'Gadag', 'haveri': 'Haveri',
    'bagalkot': 'Bagalkot', 'bijapur': 'Bijapur', 'vijayapura': 'Bijapur',
    'chitradurga': 'Chitradurga', 'chikmagalur': 'Chikmagalur', 'kodagu': 'Kodagu',
    'coorg': 'Kodagu', 'yadgir': 'Yadgir', 'ramanagara': 'Ramanagara'
  };
  
  for (const alias in districtAliases) {
    if (norm.includes(alias)) {
      district = districtAliases[alias];
      break;
    }
  }

  // 4. Extract College Type
  let collegeType = null;
  if (norm.includes('government') || norm.includes('govt')) {
    collegeType = 'govt';
  } else if (norm.includes('aided')) {
    collegeType = 'aided';
  } else if (norm.includes('private')) {
    collegeType = 'private';
  } else if (norm.includes('university') || norm.includes('universities')) {
    collegeType = 'university';
  }

  // 5. Extract Course
  let courseName = null;
  const courseAbbrMap = {
    'cse': 'Computer Science and Engineering',
    'computer science': 'Computer Science and Engineering',
    'comp sci': 'Computer Science and Engineering',
    'cs': 'Computer Science and Engineering',
    
    'ece': 'Electronics and Communication Engineering',
    'electronics': 'Electronics and Communication Engineering',
    
    'ise': 'Information Science and Engineering',
    'information science': 'Information Science and Engineering',
    'info sci': 'Information Science and Engineering',
    
    'eee': 'Electrical and Electronics Engineering',
    'ee': 'Electrical and Electronics Engineering',
    'electrical': 'Electrical and Electronics Engineering',
    
    'tc': 'Telecommunication Engineering',
    'telecom': 'Telecommunication Engineering',
    'bt': 'Bio-Technology',
    'ae': 'Aerospace Engineering',
    
    'mech': 'Mechanical Engineering',
    'mechanical': 'Mechanical Engineering',
    
    'civil': 'Civil Engineering',
    
    'aiml': 'Artificial Intelligence and Machine Learning',
    'ai & ml': 'Artificial Intelligence and Machine Learning',
    'ai and ml': 'Artificial Intelligence and Machine Learning',
    'ai/ml': 'Artificial Intelligence and Machine Learning',
    
    'aids': 'Artificial Intelligence and Data Science',
    'ai & ds': 'Artificial Intelligence and Data Science',
    'ai and ds': 'Artificial Intelligence and Data Science',
    'ai/ds': 'Artificial Intelligence and Data Science',
    
    'data science': 'Data Science',
    'ds': 'Data Science',
    
    'vlsi': 'VLSI',
    'biotech': 'Biotechnology',
    'biotechnology': 'Biotechnology',
    'aero': 'Aerospace Engineering',
    'aerospace': 'Aerospace Engineering',
    'chemical': 'Chemical Engineering',
    'chem': 'Chemical Engineering'
  };

  let longestMatchLen = 0;
  for (const phrase in courseAbbrMap) {
    let hasMatch = false;
    if (phrase.length <= 3) {
      const escPhrase = phrase.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
      hasMatch = new RegExp('\\b' + escPhrase + '\\b', 'i').test(norm);
    } else {
      hasMatch = norm.includes(phrase);
    }

    if (hasMatch && phrase.length > longestMatchLen) {
      courseName = courseAbbrMap[phrase];
      longestMatchLen = phrase.length;
    }
  }

  if (!courseName && allData.all_courses) {
    for (const cName of allData.all_courses) {
      if (norm.includes(cName.toLowerCase())) {
        courseName = cName;
        break;
      }
    }
  }

  // 6. Extract College
  let colleges = [];
  const collegeAcronyms = {
    'rv': 'R.V. College of Engineering',
    'rvce': 'R.V. College of Engineering',
    'bms': 'B.M.S. College of Engineering',
    'bmsce': 'B.M.S. College of Engineering',
    'bmsit': 'B.M.S. Institute of Technology',
    'pes': 'PES University',
    'pesu': 'PES University',
    'msrit': 'M.S. Ramaiah Institute of Technology',
    'ramaiah': 'M.S. Ramaiah Institute of Technology',
    'uvce': 'University Visvesvaraya College of Engineering',
    'bit': 'Bangalore Institute of Technology',
    'dsce': 'Dayananda Sagar College of Engineering',
    'dayananda sagar': 'Dayananda Sagar',
    'sit': 'Siddaganga Institute of Technology',
    'siddaganga': 'Siddaganga',
    'nie': 'National Institute of Engineering',
    'sjbit': 'SJB Institute of Technology',
    'sjb': 'SJB Institute of Technology',
    'mvj': 'MVJ College of Engineering',
    'nmit': 'Nitte Meenakshi Institute of Technology'
  };

  let matchedAcronym = false;
  for (const acr in collegeAcronyms) {
    if (new RegExp('\\b' + acr + '\\b', 'i').test(norm)) {
      const colName = collegeAcronyms[acr];
      const found = allData.colleges.filter(c => c.college_name.toLowerCase().includes(colName.toLowerCase()));
      if (found.length > 0) {
        colleges = found;
        matchedAcronym = true;
        break;
      }
    }
  }

  if (colleges.length === 0) {
    const queryWords = norm.split(/\s+/).filter(w => w.length > 3 && !['college', 'engineering', 'institute', 'technology', 'aided', 'private', 'minority', 'government', 'university', 'what', 'show', 'fees', 'seat', 'seats', 'rank', 'with', 'from', 'offering', 'in', 'near'].includes(w));
    
    const scoredColleges = allData.colleges.map(c => {
      let score = 0;
      const cNameNorm = c.college_name.toLowerCase();
      queryWords.forEach(w => {
        if (cNameNorm.includes(w)) {
          score += w.length;
        }
      });
      return { college: c, score };
    }).filter(sc => sc.score > 0);

    if (scoredColleges.length > 0) {
      scoredColleges.sort((a, b) => b.score - a.score);
      const maxScore = scoredColleges[0].score;
      colleges = scoredColleges.filter(sc => sc.score === maxScore).map(sc => sc.college);
    }
  }

  // 7. Detect Intent
  let intent = 'SEARCH';
  if (norm.includes('fee') || norm.includes('fees') || norm.includes('cost') || norm.includes('charge') || norm.includes('rupees') || norm.includes('price') || norm.includes('how much')) {
    intent = 'FEE_INQUIRY';
  } else if (norm.includes('seat') || norm.includes('seats') || norm.includes('intake') || norm.includes('capacity') || norm.includes('matrix')) {
    intent = 'SEAT_INQUIRY';
  } else if (rank !== null || norm.includes('chance') || norm.includes('predict') || norm.includes('admission') || norm.includes('allotment') || norm.includes('get a seat') || norm.includes('cutoff')) {
    intent = 'PREDICT';
  }

  return {
    query: queryStr,
    rank,
    category: category || 'GM',
    categorySpecified: !!category,
    district,
    collegeType,
    courseName,
    colleges,
    intent
  };
}

function getCutoffForCategory(courseObj, category) {
  const r3 = courseObj.round3_cutoff && courseObj.round3_cutoff[category];
  if (r3) return { cutoff: parseFloat(r3), round: 'Round 3' };
  
  const r2 = courseObj.round2_cutoff && courseObj.round2_cutoff[category];
  if (r2) return { cutoff: parseFloat(r2), round: 'Round 2' };
  
  const r1 = courseObj.round1_cutoff && courseObj.round1_cutoff[category];
  if (r1) return { cutoff: parseFloat(r1), round: 'Round 1' };
  
  return null;
}

function generateAssistantResponse(analysis) {
  const category = analysis.category;
  const rank = analysis.rank;
  const courseName = analysis.courseName;
  const colleges = analysis.colleges;
  const district = analysis.district;
  const collegeType = analysis.collegeType;
  const intent = analysis.intent;

  let text = '';
  let html = '';

  const filterCollegesList = (list) => {
    return list.filter(c => {
      if (district && c.district !== district) return false;
      if (collegeType) {
        const type = c.college_type.toLowerCase();
        if (collegeType === 'govt' && !type.includes('government') && !type.includes('vtu')) return false;
        if (collegeType === 'aided' && !type.includes('aided')) return false;
        if (collegeType === 'private' && !type.includes('private')) return false;
        if (collegeType === 'university' && !type.includes('university') && !type.includes('constituent')) return false;
      }
      return true;
    });
  };

  // Case 1: PREDICT (Cutoff & Admission Chances)
  if (intent === 'PREDICT') {
    if (rank === null) {
      text = `I detected you are asking for cutoffs or admission predictions. Could you please specify your **UGCET Rank**? For example: *'Can I get CSE at RV College with rank 5000?'*`;
      return { text, html };
    }

    const targetCategory = category || 'GM';

    // Subcase 1.1: Specific College and Course
    if (colleges.length === 1 && courseName) {
      const college = colleges[0];
      const course = college.courses.find(c => c.course_name.toLowerCase().includes(courseName.toLowerCase()) || courseName.toLowerCase().includes(c.course_name.toLowerCase()));
      
      if (!course) {
        text = `**${college.college_name}** does not offer a course matching **${courseName}**. Click one of these courses to search cutoffs:`;
        html = `<div style="display:flex; flex-wrap:wrap; gap:8px; margin-top:10px;">` + 
          college.courses.map(c => `<span class="chip active" style="margin:0; background:rgba(255,255,255,0.03); border:1px solid var(--border); color:var(--text-muted); font-size:11px; padding:6px 12px; font-weight:500;" onclick="window.setAssistantInputAndAsk('Can I get ${c.course_name} at ${college.college_name} with rank ${rank} in ${targetCategory}?')">${abbrCourseName(c.course_name)}</span>`).join('') + 
          `</div>`;
        return { text, html };
      }

      const cutoffInfo = getCutoffForCategory(course, targetCategory);
      
      if (!cutoffInfo) {
        text = `At **${college.college_name}**, there is no cutoff rank recorded for **${course.course_name}** under category **${targetCategory}**. This usually means no seats were allotted to this category in 2025.`;
        return { text, html };
      }

      const cutoff = cutoffInfo.cutoff;
      const roundUsed = cutoffInfo.round;

      const diff = cutoff - rank;
      let chance = 'Low';
      let chanceClass = 'badge-borderline';
      let explanation = '';

      if (diff >= 5000) {
        chance = 'Very High';
        chanceClass = 'badge-very-high';
        explanation = `Your rank (**${rank.toLocaleString()}**) is significantly better than the ${roundUsed} cutoff of **${cutoff.toLocaleString()}** (by **+${diff.toLocaleString()}** ranks). You are highly likely to get admitted here.`;
      } else if (diff >= 0) {
        chance = 'High';
        chanceClass = 'badge-high';
        explanation = `Your rank (**${rank.toLocaleString()}**) is better than the ${roundUsed} cutoff of **${cutoff.toLocaleString()}** (by **+${diff.toLocaleString()}** ranks). You have a very good chance of getting this seat.`;
      } else if (diff >= -3000) {
        chance = 'Borderline';
        chanceClass = 'badge-borderline';
        explanation = `Your rank (**${rank.toLocaleString()}**) is slightly worse than the ${roundUsed} cutoff of **${cutoff.toLocaleString()}** (by **${diff.toLocaleString()}** ranks). You might stand a chance in final or casual vacancy rounds, but it's borderline.`;
      } else {
        chance = 'Low';
        chanceClass = 'style-low';
        explanation = `Your rank (**${rank.toLocaleString()}**) is significantly behind the ${roundUsed} cutoff of **${cutoff.toLocaleString()}** (by **${diff.toLocaleString()}** ranks). It is unlikely you will get this seat under category ${targetCategory}.`;
      }

      text = `Here is your admission chance for **${course.course_name}** at **${college.college_name}** under category **${targetCategory}**:\n\n` +
             `• **Category**: ${targetCategory}\n` +
             `• **${roundUsed} Cutoff**: **${cutoff.toLocaleString()}**\n` +
             `• **Your Rank**: **${rank.toLocaleString()}**\n` +
             `• **Chances**: **${chance}**\n\n` +
             explanation;

      html = `<div style="margin-top:16px;">` + renderCollegeCard(college, 0) + `</div>`;
      return { text, html };
    }

    // Subcase 1.2: Specific College (List all courses cutoff and user chances)
    if (colleges.length === 1 && !courseName) {
      const college = colleges[0];
      text = `Here are the cutoff ranks and your admission chances for all courses at **${college.college_name}** for category **${targetCategory}** with your rank of **${rank.toLocaleString()}**:`;
      
      const courseRows = college.courses.map(c => {
        const cutoffInfo = getCutoffForCategory(c, targetCategory);
        if (!cutoffInfo) {
          return `<tr>
            <td><strong>${c.course_name}</strong></td>
            <td style="text-align:right; color:var(--text-muted);">—</td>
            <td style="text-align:right; color:var(--text-muted);">—</td>
            <td style="text-align:center;"><span class="badge-chance" style="background:rgba(255,255,255,0.03); color:var(--text-muted); border:1px solid var(--border);">No Cutoff</span></td>
          </tr>`;
        }
        const cutoff = cutoffInfo.cutoff;
        
        const diff = cutoff - rank;
        const diffText = diff >= 0 ? `+${diff.toLocaleString()}` : diff.toLocaleString();
        const diffClass = diff >= 0 ? 'text-green' : 'text-orange';
        
        let chance = 'Low';
        let chanceClass = 'badge-borderline';
        if (diff >= 5000) { chance = 'Very High'; chanceClass = 'badge-very-high'; }
        else if (diff >= 0) { chance = 'High'; chanceClass = 'badge-high'; }
        else if (diff >= -3000) { chance = 'Borderline'; chanceClass = 'badge-borderline'; }
        else { chance = 'Low'; chanceClass = 'style-low'; }

        return `<tr>
          <td><strong>${c.course_name}</strong></td>
          <td style="font-family:var(--font-display); font-weight:700; text-align:right;">${cutoff.toLocaleString()}</td>
          <td class="${diffClass}" style="font-family:var(--font-display); font-weight:700; text-align:right;">${diffText}</td>
          <td style="text-align:center;"><span class="badge-chance ${chanceClass}">${chance}</span></td>
        </tr>`;
      }).join('');

      html = `
        <div class="table-container" style="overflow-x:auto; margin-top:16px; border:1px solid var(--border); border-radius:10px;">
          <table class="modal-courses-table" style="width:100%;">
            <thead>
              <tr style="border-bottom:1px solid var(--border);">
                <th style="text-align:left;">Course Name</th>
                <th style="text-align:right;">Cutoff (R3)</th>
                <th style="text-align:right;">Diff</th>
                <th style="text-align:center;">Chance</th>
              </tr>
            </thead>
            <tbody>
              ${courseRows}
            </tbody>
          </table>
        </div>
        <div style="margin-top:16px;">` + renderCollegeCard(college, 0) + `</div>
      `;
      return { text, html };
    }

    // Subcase 1.3: Specific Course or general (List colleges sorted by cutoff showing chances)
    let filteredColleges = allData.colleges;
    if (courseName) {
      filteredColleges = filteredColleges.filter(col => col.courses.some(c => c.course_name.toLowerCase().includes(courseName.toLowerCase()) || courseName.toLowerCase().includes(c.course_name.toLowerCase())));
    }
    filteredColleges = filterCollegesList(filteredColleges);

    if (filteredColleges.length === 0) {
      text = `No colleges found offering **${courseName || 'any course'}** matching your criteria.`;
      return { text, html };
    }

    const matchingResults = [];
    const seenCol = new Set();
    
    filteredColleges.forEach(college => {
      college.courses.forEach(c => {
        if (courseName && !(c.course_name.toLowerCase().includes(courseName.toLowerCase()) || courseName.toLowerCase().includes(c.course_name.toLowerCase()))) return;
        
        const cutoffInfo = getCutoffForCategory(c, targetCategory);
        if (!cutoffInfo) return;
        const cutoff = cutoffInfo.cutoff;
        
        const key = `${college.college_number}_${c.course_name}`;
        if (seenCol.has(key)) return;
        seenCol.add(key);
        
        const diff = cutoff - rank;
        if (diff < -3000) return;
        
        let chance = 'Borderline';
        let chanceClass = 'badge-borderline';
        if (diff >= 5000) { chance = 'Very High'; chanceClass = 'badge-very-high'; }
        else if (diff >= 0) { chance = 'High'; chanceClass = 'badge-high'; }
        
        matchingResults.push({
          college,
          courseName: c.course_name,
          cutoff,
          diff,
          chance,
          chanceClass
        });
      });
    });

    matchingResults.sort((a, b) => a.cutoff - b.cutoff);

    if (matchingResults.length === 0) {
      text = `Based on your rank of **${rank.toLocaleString()}** under category **${targetCategory}**, I couldn't find colleges offering **${courseName || 'this course'}** where your rank is within the cutoff margin. You may want to consider a different category, location, or course.`;
      return { text, html };
    }

    const countToShow = Math.min(matchingResults.length, 10);
    const displayedResults = matchingResults.slice(0, countToShow);

    text = `Based on your rank of **${rank.toLocaleString()}** under category **${targetCategory}**, here are the top **${countToShow}** colleges offering **${courseName || 'Engineering'}** where you have a **High** or **Borderline** chance of admission (ordered by competitive cutoff ranks):`;

    const tableRows = displayedResults.map(res => {
      const col = res.college;
      const diffText = res.diff >= 0 ? `+${res.diff.toLocaleString()}` : res.diff.toLocaleString();
      const diffClass = res.diff >= 0 ? 'text-green' : 'text-orange';
      
      return `<tr class="pred-row assistant-row-click" data-college-number="${col.college_number}" style="cursor:pointer; transition:background 0.2s;">
        <td><span class="card-type-pill pill-${col.annexure}" style="font-size:11px; padding: 2px 6px;">${col.kea_code || col.college_number}</span></td>
        <td><strong>${col.college_name}</strong><br><small style="color:var(--text-muted)">📍 ${col.district}</small></td>
        <td>${abbrCourseName(res.courseName)}</td>
        <td style="font-family:var(--font-display); font-weight:700; text-align:right;">${res.cutoff.toLocaleString()}</td>
        <td class="${diffClass}" style="font-family:var(--font-display); font-weight:700; text-align:right;">${diffText}</td>
        <td style="text-align:center;"><span class="badge-chance ${res.chanceClass}">${res.chance}</span></td>
      </tr>`;
    }).join('');

    html = `
      <div class="table-container" style="overflow-x:auto; margin-top:16px; border:1px solid var(--border); border-radius:10px;">
        <table class="modal-courses-table" style="width:100%;">
          <thead>
            <tr style="border-bottom:1px solid var(--border);">
              <th style="text-align:left;">Code</th>
              <th style="text-align:left;">College</th>
              <th style="text-align:left;">Course</th>
              <th style="text-align:right;">Cutoff</th>
              <th style="text-align:right;">Diff</th>
              <th style="text-align:center;">Chance</th>
            </tr>
          </thead>
          <tbody>
            ${tableRows}
          </tbody>
        </table>
      </div>
      <div style="font-size:11px; color:var(--text-muted); margin-top:8px;">💡 Clicking any row in the table will open the college detail modal.</div>
    `;

    return { text, html };
  }

  // Case 2: SEAT_INQUIRY (Seat Count / Matrix)
  if (intent === 'SEAT_INQUIRY') {
    if (colleges.length === 1) {
      const college = colleges[0];
      
      if (courseName) {
        const course = college.courses.find(c => c.course_name.toLowerCase().includes(courseName.toLowerCase()) || courseName.toLowerCase().includes(c.course_name.toLowerCase()));
        if (!course) {
          text = `**${college.college_name}** does not offer **${courseName}**.`;
          return { text, html };
        }
        
        text = `Here is the seat matrix for **${course.course_name}** at **${college.college_name}**:\n\n` +
               `• **Total Intake**: **${(course.total_intake || 0).toLocaleString()}** seats\n` +
               `• **KEA / Govt Seats**: **${(course.total_kea_seats || 0).toLocaleString()}** seats\n` +
               `  - Hyderabad-Karnataka (HK): ${(course.kea_hk || 0).toLocaleString()} seats\n` +
               `  - Rest of Karnataka (RK): ${(course.kea_rk || 0).toLocaleString()} seats\n` +
               `  - Special Quotas: ${(course.kea_spl || 0).toLocaleString()} seats\n` +
               `  - PH Quota: ${(course.kea_ph || 0).toLocaleString()} seats\n` +
               `• **COMEDK Seats**: **${(course.cat2_seats || 0).toLocaleString()}** seats\n` +
               `• **Management Seats**: **${(course.cat3_seats || 0).toLocaleString()}** seats\n` +
               `• **Supernumerary SNQ Seats**: **${(course.over_above_5pct || 0).toLocaleString()}** seats`;

        html = `<div style="margin-top:16px;">` + renderCollegeCard(college, 0) + `</div>`;
        return { text, html };
      } else {
        let totalIntake = 0, totalKea = 0, totalComedk = 0, totalMgmt = 0;
        college.courses.forEach(c => {
          totalIntake += c.total_intake || 0;
          totalKea += c.total_kea_seats || 0;
          totalComedk += c.cat2_seats || 0;
          totalMgmt += c.cat3_seats || 0;
        });

        text = `**${college.college_name}** offers **${college.courses.length}** courses with a total intake of **${totalIntake.toLocaleString()}** seats. Under KEA/Govt quota, there are **${totalKea.toLocaleString()}** seats. Here is the course-wise seat matrix:`;

        const hasComDk = college.courses.some(c => (c.cat2_seats || 0) > 0);
        const hasMgmt = college.courses.some(c => (c.cat3_seats || 0) > 0);

        const courseRows = college.courses.map(c => {
          const comedkCol = hasComDk ? `<td style="text-align:right; color:var(--purple);">${(c.cat2_seats || 0).toLocaleString()}</td>` : '';
          const mgmtCol = hasMgmt ? `<td style="text-align:right; color:var(--orange);">${(c.cat3_seats || 0).toLocaleString()}</td>` : '';
          const feeVal = getCourseFee(college, c.course_name, c.total_kea_seats);
          return `
            <tr>
              <td><strong>${c.course_name}</strong></td>
              <td style="text-align:right;">${(c.total_intake || 0).toLocaleString()}</td>
              <td style="text-align:right; color:var(--green); font-weight:600;">${(c.total_kea_seats || 0).toLocaleString()}</td>
              ${comedkCol}
              ${mgmtCol}
              <td style="text-align:right;">${feeVal}</td>
            </tr>
          `;
        }).join('');

        html = `
          <div class="table-container" style="overflow-x:auto; margin-top:16px; border:1px solid var(--border); border-radius:10px;">
            <table class="modal-courses-table" style="width:100%;">
              <thead>
                <tr style="border-bottom:1px solid var(--border);">
                  <th style="text-align:left;">Course Name</th>
                  <th style="text-align:right;">Total</th>
                  <th style="text-align:right; color:var(--green);">KEA</th>
                  ${hasComDk ? '<th style="text-align:right; color:var(--purple);">COMEDK</th>' : ''}
                  ${hasMgmt ? '<th style="text-align:right; color:var(--orange);">Mgmt</th>' : ''}
                  <th style="text-align:right;">KEA Fee</th>
                </tr>
              </thead>
              <tbody>
                ${courseRows}
              </tbody>
            </table>
          </div>
          <div style="margin-top:16px;">` + renderCollegeCard(college, 0) + `</div>
        `;
        return { text, html };
      }
    }

    let filteredColleges = allData.colleges;
    if (courseName) {
      filteredColleges = filteredColleges.filter(col => col.courses.some(c => c.course_name.toLowerCase().includes(courseName.toLowerCase()) || courseName.toLowerCase().includes(c.course_name.toLowerCase())));
    }
    filteredColleges = filterCollegesList(filteredColleges);

    let sumIntake = 0, sumKea = 0, sumComedk = 0, sumMgmt = 0;
    filteredColleges.forEach(col => {
      col.courses.forEach(c => {
        if (courseName && !(c.course_name.toLowerCase().includes(courseName.toLowerCase()) || courseName.toLowerCase().includes(c.course_name.toLowerCase()))) return;
        sumIntake += c.total_intake || 0;
        sumKea += c.total_kea_seats || 0;
        sumComedk += c.cat2_seats || 0;
        sumMgmt += c.cat3_seats || 0;
      });
    });

    const filterDesc = [];
    if (collegeType) filterDesc.push(`**${collegeType.toUpperCase()}**`);
    if (district) filterDesc.push(`in **${district}**`);
    const filterDescStr = filterDesc.length > 0 ? ' ' + filterDesc.join(' ') : '';

    text = `Across **${filteredColleges.length}** colleges${filterDescStr} offering **${courseName || 'Engineering'}**, here are the total seat statistics:\n\n` +
           `• **Total Intake**: **${sumIntake.toLocaleString()}** seats\n` +
           `• **KEA Govt Quota**: **${sumKea.toLocaleString()}** seats\n` +
           `• **COMEDK Quota**: **${sumComedk.toLocaleString()}** seats\n` +
           `• **Management Quota**: **${sumMgmt.toLocaleString()}** seats`;

    const topColleges = filteredColleges.slice(0, 6);
    html = `
      <div style="font-weight:600; font-size:12px; color:var(--text-muted); margin:16px 0 10px; text-transform:uppercase; letter-spacing:0.05em;">Matching Colleges (showing top ${topColleges.length} of ${filteredColleges.length}):</div>
      <div class="colleges-grid" style="display:grid; grid-template-columns:repeat(auto-fill, minmax(280px, 1fr)); gap:16px;">
        ${topColleges.map((c, i) => renderCollegeCard(c, i)).join('')}
      </div>
    `;
    return { text, html };
  }

  // Case 3: FEE_INQUIRY (Fee Details)
  if (intent === 'FEE_INQUIRY') {
    if (colleges.length === 1) {
      const college = colleges[0];
      const feeInfo = getSeatFees(college);

      text = `Here is the annual fee structure for **${college.college_name}** (College Type: *${college.college_type}*):\n\n` +
             `Private/Deemed colleges may charge Option A or Option B fees depending on consensual agreements. An additional "Other Fee" up to ₹20,000/- per annum can be collected by KEA.`;

      const feeRows = feeInfo.rows.map(r => `
        <tr>
          <td><strong>${r.seatType}</strong></td>
          <td style="text-align:right; font-family:var(--font-display); font-weight:700; color:var(--green);">${r.year1}</td>
          <td style="text-align:right; font-family:var(--font-display); font-weight:700; color:var(--green);">${r.subsequent}</td>
          <td style="font-size:11px; color:var(--text-muted); padding-left:12px; text-align:left;">${r.note}</td>
        </tr>
      `).join('');

      html = `
        <div class="table-container" style="overflow-x:auto; margin-top:16px; border:1px solid var(--border); border-radius:10px;">
          <table class="modal-courses-table fee-table" style="width:100%;">
            <thead>
              <tr style="border-bottom:1px solid var(--border);">
                <th style="text-align:left;">Quota Type</th>
                <th style="text-align:right;">1st Year</th>
                <th style="text-align:right;">Subsequent</th>
                <th style="text-align:left; padding-left:12px;">Details</th>
              </tr>
            </thead>
            <tbody>
              ${feeRows}
            </tbody>
          </table>
        </div>
        <div style="margin-top:16px;">` + renderCollegeCard(college, 0) + `</div>
      `;
      return { text, html };
    }

    text = `Here is the general annual fee structure for engineering colleges in Karnataka for 2025 (as per KEA guidelines):\n\n` +
           `• **Government & VTU constituent colleges**:\n` +
           `  - General Quota: **₹44,200** (1st Year) / **₹42,200** (subsequent years).\n` +
           `  - Concession rate (CE/ME/TX/ST/AT courses): **₹28,450** (1st Year) / **₹26,450** (subsequent years).\n` +
           `  - SNQ quota: **₹20,610** per year.\n\n` +
           `• **Private Aided colleges**:\n` +
           `  - General Quota (Aided course): **₹44,200** (1st Year) / **₹42,200** (subsequent years).\n` +
           `  - SNQ quota: **₹20,610** per year.\n\n` +
           `• **Public Universities (e.g. UVCE)**:\n` +
           `  - General Quota: **₹49,600** (1st Year) / **₹48,250** (subsequent years).\n` +
           `  - SNQ quota: **₹20,610** per year.\n\n` +
           `• **Private Unaided / Minority / Deemed / Private Universities**:\n` +
           `  - Option A KEA Quota: **₹1,12,410** per year.\n` +
           `  - Option B KEA Quota: **₹1,21,610** per year.\n` +
           `  - COMEDK Quota: **₹2,81,100** or **₹2,00,000** per year.\n` +
           `  - SNQ quota: **₹30,610** per year.`;

    html = `
      <div style="background:rgba(255,255,255,0.02); border:1px solid var(--border); padding:16px; border-radius:10px; margin-top:16px; font-size:13px;">
        ℹ️ Private institutions operate under consensual agreements. An additional "Other Fee" up to ₹20,000/- per annum can be collected by KEA during admission.
      </div>
    `;
    return { text, html };
  }

  // Case 4: SEARCH (College Search / Default)
  if (intent === 'SEARCH') {
    let filteredColleges = allData.colleges;
    if (courseName) {
      filteredColleges = filteredColleges.filter(col => col.courses.some(c => c.course_name.toLowerCase().includes(courseName.toLowerCase()) || courseName.toLowerCase().includes(c.course_name.toLowerCase())));
    }
    filteredColleges = filterCollegesList(filteredColleges);

    if (colleges.length > 0 && !courseName && !district && !collegeType) {
      text = `I found **${colleges.length}** colleges matching your query. Click any card below to view their complete details, courses, cutoffs, and fees:`;
      html = `
        <div class="colleges-grid" style="display:grid; grid-template-columns:repeat(auto-fill, minmax(280px, 1fr)); gap:16px; margin-top:16px;">
          ${colleges.map((c, i) => renderCollegeCard(c, i)).join('')}
        </div>
      `;
      return { text, html };
    }

    if (filteredColleges.length === 0) {
      text = `I couldn't find any colleges matching your criteria. Try adjusting your keywords (e.g., location, course, or college type).`;
      return { text, html };
    }

    const typeStr = collegeType ? `**${collegeType.toUpperCase()}** ` : '';
    const locStr = district ? `in **${district}** ` : '';
    const crsStr = courseName ? `offering **${courseName}** ` : '';

    text = `I found **${filteredColleges.length}** ${typeStr}colleges ${locStr}${crsStr}in the database. Click any card below to view full details:`;

    const topColleges = filteredColleges.slice(0, 12);
    html = `
      <div class="colleges-grid" style="display:grid; grid-template-columns:repeat(auto-fill, minmax(280px, 1fr)); gap:16px; margin-top:16px;">
        ${topColleges.map((c, i) => renderCollegeCard(c, i)).join('')}
      </div>
      ${filteredColleges.length > 12 ? `<div style="font-size:12px; color:var(--text-muted); text-align:center; margin-top:16px;">Showed top 12 of ${filteredColleges.length} colleges. Refine your search to see others.</div>` : ''}
    `;

    return { text, html };
  }

  text = `I'm not sure about your query. You can ask me questions like:
  - "Can I get CSE in RV College with rank 5000 in GM?"
  - "What is the fee for Government colleges?"
  - "How many seats are there for Mechanical in Government colleges?"
  - "Show colleges in Mysore offering Computer Science"`;
  
  return { text, html };
}

function formatMarkdown(text) {
  if (!text) return '';
  let escaped = escHtml(text);
  escaped = escaped.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  escaped = escaped.replace(/\*(.*?)\*/g, '<em>$1</em>');
  escaped = escaped.replace(/\n/g, '<br>');
  return escaped;
}

// AI Chatbot Frontend Integration
document.addEventListener('DOMContentLoaded', () => {
  const chatToggle = document.getElementById('agent-chat-toggle');
  const chatContainer = document.getElementById('agent-chat-container');
  const chatClose = document.getElementById('agent-chat-close');
  const chatMessages = document.getElementById('agent-chat-messages');
  const chatInput = document.getElementById('agent-chat-input');
  const chatSend = document.getElementById('agent-chat-send');
  
  if (!chatToggle) return;
  
  let chatHistory = [];
  
  chatToggle.addEventListener('click', () => {
    chatContainer.classList.toggle('open');
    if (chatContainer.classList.contains('open')) {
      chatInput.focus();
    }
  });
  
  chatClose.addEventListener('click', () => {
    chatContainer.classList.remove('open');
  });
  
  async function sendMessage() {
    const text = chatInput.value.trim();
    if (!text) return;
    
    appendMessage('user', text);
    chatInput.value = '';
    
    const loadingId = appendMessage('agent', '<div class="typing-indicator"><div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div></div>');
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          history: chatHistory
        })
      });
      
      const data = await response.json();
      
      const loadingEl = document.getElementById(loadingId);
      if (loadingEl) loadingEl.remove();
      
      if (data.reply) {
        let formattedReply = formatMarkdown(data.reply);
        
        if (data.sql_queries && data.sql_queries.length > 0) {
          formattedReply += '<div style="margin-top: 12px; font-size: 11px; border-top: 1px dashed var(--border); padding-top: 6px; color: var(--text-muted);">🔍 SQL Queries Executed:</div>';
          data.sql_queries.forEach(q => {
            formattedReply += `<div class="agent-msg-sql-log"><code>${escHtml(q.query)}</code></div>`;
          });
        }
        
        appendMessage('agent', formattedReply);
        
        chatHistory.push({ role: 'user', content: text });
        chatHistory.push({ role: 'model', content: data.reply });
      } else {
        appendMessage('agent', 'Error: Received empty response from agent.');
      }
    } catch (err) {
      const loadingEl = document.getElementById(loadingId);
      if (loadingEl) loadingEl.remove();
      appendMessage('agent', 'Error: Could not connect to the server API.');
      console.error(err);
    }
    
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }
  
  function appendMessage(role, content) {
    const msgId = 'msg-' + Math.random().toString(36).substr(2, 9);
    const msgDiv = document.createElement('div');
    msgDiv.id = msgId;
    msgDiv.className = `agent-msg ${role}`;
    msgDiv.innerHTML = content;
    chatMessages.appendChild(msgDiv);
    return msgId;
  }
  
  chatSend.addEventListener('click', sendMessage);
  chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
  });
});

// ─────────────────────────────────────────────────────
// Side-by-Side College Comparison and Fee Calculator
// ─────────────────────────────────────────────────────

function updateComparisonMatrix() {
  const col1Code = document.getElementById('compare-col-1').value;
  const col2Code = document.getElementById('compare-col-2').value;
  const col3Code = document.getElementById('compare-col-3').value;
  
  const wrap = document.getElementById('compare-matrix-wrap');
  const emptyState = document.getElementById('compare-empty-state');
  
  if (!col1Code && !col2Code && !col3Code) {
    if (wrap) wrap.style.display = 'none';
    if (emptyState) emptyState.style.display = 'block';
    return;
  }
  
  if (wrap) wrap.style.display = 'block';
  if (emptyState) emptyState.style.display = 'none';

  // Log comparison event to backend PostgreSQL
  const codes = [col1Code, col2Code, col3Code].filter(Boolean).join(', ');
  fetch('/api/log', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      username: currentUser ? currentUser.name : 'guest',
      action: 'COMPARE',
      details: `Comparing: ${codes}`
    })
  }).catch(err => console.error(err));
  
  const c1 = allData.colleges.find(c => c.kea_code === col1Code);
  const c2 = allData.colleges.find(c => c.kea_code === col2Code);
  const c3 = allData.colleges.find(c => c.kea_code === col3Code);
  
  document.getElementById('compare-head-1').textContent = c1 ? `${c1.kea_code} - ${c1.college_name}` : '—';
  document.getElementById('compare-head-2').textContent = c2 ? `${c2.kea_code} - ${c2.college_name}` : '—';
  document.getElementById('compare-head-3').textContent = c3 ? `${c3.kea_code} - ${c3.college_name}` : '—';
  
  const getFeeString = (col) => {
    if (!col) return '—';
    const feeInfo = getSeatFees(col);
    if (!feeInfo || feeInfo.rows.length === 0) return '—';
    return feeInfo.rows.map(r => `<strong>${r.seatType || r.quota}</strong>: ${r.year1 || r.fee} (${r.subsequent || 'Subsequent'} subseq)`).join('<br>');
  };
  
  const getCoursesString = (col) => {
    if (!col) return '—';
    return col.courses.map(c => `<div style="margin-bottom:6px; font-size:11px; border-bottom:1px solid rgba(255,255,255,0.03); padding-bottom:4px;">🛠️ <strong>${c.course_name}</strong><br><span style="color:var(--text-muted);">Intake: ${c.total_intake} | KEA Seats: ${c.total_kea_seats}</span></div>`).join('');
  };
  
  const getBranchCutoff = (col, branchKeywords) => {
    if (!col) return '—';
    const matched = col.courses.find(c => {
      const name = c.course_name.toLowerCase();
      return branchKeywords.every(kw => name.includes(kw));
    });
    if (!matched) return '—';
    
    const r1 = matched.round1_cutoff ? matched.round1_cutoff['GM'] : null;
    const r2 = matched.round2_cutoff ? matched.round2_cutoff['GM'] : null;
    const r3 = matched.round3_cutoff ? matched.round3_cutoff['GM'] : null;
    const mock = matched.mock_round1_cutoff ? matched.mock_round1_cutoff['GM'] : null;
    
    let parts = [];
    if (mock) parts.push(`Mock: <strong>${parseInt(mock).toLocaleString()}</strong>`);
    if (r1) parts.push(`Round 1: <strong>${parseInt(r1).toLocaleString()}</strong>`);
    if (r2) parts.push(`Round 2: <strong>${parseInt(r2).toLocaleString()}</strong>`);
    if (r3) parts.push(`Round 3: <strong>${parseInt(r3).toLocaleString()}</strong>`);
    return parts.length > 0 ? parts.join('<br>') : '—';
  };
  
  const features = [
    { name: 'KEA Code', val: c => c ? `<strong>${c.kea_code}</strong>` : '—' },
    { name: 'District', val: c => c ? c.district : '—' },
    { name: 'Annexure', val: c => c ? `Annexure ${c.annexure}` : '—' },
    { name: 'College Type', val: c => c ? c.college_type : '—' },
    { name: 'NIRF & Heritage', val: c => c ? `Est: <strong>${c.established || '—'}</strong><br>NIRF Rank: <strong>${c.nirf_rank ? '#' + c.nirf_rank : 'Not Ranked'}</strong>` : '—' },
    { name: 'Accreditations', val: c => c ? `NAAC Grade: <strong>${c.naac_grade || '—'}</strong><br>NBA Status: <strong>${c.nba_accredited || '—'}</strong>` : '—' },
    { name: 'Total Intake', val: c => c ? c.total_intake : '—' },
    { name: 'Total KEA Seats', val: c => c ? c.total_kea_seats : '—' },
    { name: 'COMEDK Seats', val: c => c ? c.courses.reduce((acc, cr) => acc + (parseInt(cr.cat2_seats) || 0), 0) : '—' },
    { name: 'Management Seats', val: c => c ? c.courses.reduce((acc, cr) => acc + (parseInt(cr.cat3_seats) || 0), 0) : '—' },
    { name: 'SNQ Seats (5%)', val: c => c ? c.courses.reduce((acc, cr) => acc + (parseInt(cr.snq_5pct || cr.over_above_5pct) || 0), 0) : '—' },
    { name: 'Placements Stats', val: c => c && c.placements ? `Avg Package: <strong>${c.placements.avg_package || '—'}</strong><br>Max Package: <strong>${c.placements.highest_package || '—'}</strong><br>Rate: <strong>${c.placements.placement_rate || '—'}</strong>` : '—' },
    { name: 'Hostel Details', val: c => c && c.hostel_details ? `Annual Fee: <strong>${c.hostel_details.hostel_fees || '—'}</strong><br>Capacity: <strong>${c.hostel_details.hostel_capacity || '—'}</strong><br>Mess Incl: <strong>${c.hostel_details.mess_included || '—'}</strong>` : '—' },
    { name: 'Campus & Transit', val: c => c && c.campus_life ? `Size: <strong>${c.campus_life.campus_size || '—'}</strong><br>Majestic Dist: <strong>${c.campus_life.majestic_dist_km || '—'} km</strong><br>Transit: <strong>${c.campus_life.nearest_transit || '—'}</strong>` : '—' },
    { name: 'Annual Fees Structure', val: c => getFeeString(c) },
    { name: 'CSE Cutoffs (GM Merit)', val: c => getBranchCutoff(c, ['computer', 'science']) },
    { name: 'ECE Cutoffs (GM Merit)', val: c => getBranchCutoff(c, ['electronics', 'communication']) },
    { name: 'ISE Cutoffs (GM Merit)', val: c => getBranchCutoff(c, ['information', 'science']) },
    { name: 'Courses Offered & Intakes', val: c => getCoursesString(c) }
  ];
  
  const tbody = document.getElementById('compare-table-body');
  tbody.innerHTML = '';
  
  features.forEach(f => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td style="font-weight: 700; color: var(--text-muted); font-size: 11px; background: rgba(255,255,255,0.01); text-transform: uppercase; letter-spacing: 0.05em; vertical-align: top;">${f.name}</td>
      <td style="font-size:12px; line-height:1.4; vertical-align: top;">${f.val(c1)}</td>
      <td style="font-size:12px; line-height:1.4; vertical-align: top;">${f.val(c2)}</td>
      <td style="font-size:12px; line-height:1.4; vertical-align: top;">${f.val(c3)}</td>
    `;
    tbody.appendChild(tr);
  });
}

function calculateTuitionFee() {
  const colCode = document.getElementById('calc-fee-college').value;
  const quota = document.getElementById('calc-fee-quota').value;
  const studyYear = document.getElementById('calc-fee-year').value;
  
  const wrap = document.getElementById('calc-fee-result-wrap');
  const emptyState = document.getElementById('calc-fee-empty-state');
  
  if (!colCode) {
    if (wrap) wrap.style.display = 'none';
    if (emptyState) emptyState.style.display = 'block';
    return;
  }
  
  if (wrap) wrap.style.display = 'block';
  if (emptyState) emptyState.style.display = 'none';
  
  const college = allData.colleges.find(c => c.kea_code === colCode);
  if (!college) return;
  
  const type = college.college_type || '';
  const activeYear = allData.year || '2026';
  
  let feeValue = 0;
  let breakdown = [];
  
  const isGovt = type.includes('Government') || type.includes('VTU Constituent') || type.includes('Public University') || type.includes('University of Visvesvaraya');
  
  if (quota === 'govt_snq') {
    feeValue = (activeYear === '2026') ? 22320 : ((activeYear === '2025') ? 20000 : 21360);
    if (!isGovt && activeYear === '2026') feeValue = 32320;
    breakdown = [
      { item: 'Tuition Fee (Waived)', cost: '₹0' },
      { item: 'University Registration Fees', cost: '₹12,320' },
      { item: 'College Development & Other Fees', cost: `₹${(feeValue - 12320).toLocaleString()}` }
    ];
  } else if (quota === 'govt_gen') {
    if (type.includes('University of Visvesvaraya') || type.includes('UVCE') || type.includes('Public University')) {
      feeValue = (studyYear === 'first') ? 56500 : 54500;
      breakdown = [
        { item: 'KEA Registration Fee', cost: '₹500' },
        { item: 'Tuition Fee', cost: `₹${(studyYear === 'first' ? 43680 : 42180).toLocaleString()}` },
        { item: 'University & Exam Fees', cost: '₹12,320' }
      ];
    } else if (isGovt) {
      feeValue = (studyYear === 'first') ? 47100 : 45100;
      breakdown = [
        { item: 'Tuition Fee', cost: '₹24,780' },
        { item: 'University Fees (VTU)', cost: '₹12,320' },
        { item: 'Other Fees', cost: `₹${(studyYear === 'first' ? 10000 : 8000).toLocaleString()}` }
      ];
    } else {
      feeValue = (activeYear === '2026') ? 110320 : 96574;
      breakdown = [
        { item: 'Tuition Fee (KEA Approved)', cost: `₹${(feeValue - 22320).toLocaleString()}` },
        { item: 'Other & University Fees', cost: '₹22,320' }
      ];
    }
  } else if (quota === 'govt_aided') {
    feeValue = (studyYear === 'first') ? 47100 : 45100;
    breakdown = [
      { item: 'Tuition Fee', cost: '₹24,780' },
      { item: 'University Fees (VTU)', cost: '₹12,320' },
      { item: 'College Administration Fee', cost: `₹${(studyYear === 'first' ? 10000 : 8000).toLocaleString()}` }
    ];
  } else if (quota === 'kea_unaided_a') {
    feeValue = (activeYear === '2026') ? 110320 : 96574;
    breakdown = [
      { item: 'Option A Tuition Fee', cost: `₹${(feeValue - 22320).toLocaleString()}` },
      { item: 'KEA Miscellaneous Fees', cost: '₹22,320' }
    ];
  } else if (quota === 'kea_unaided_b') {
    feeValue = (activeYear === '2026') ? 120320 : 106574;
    breakdown = [
      { item: 'Option B Tuition Fee', cost: `₹${(feeValue - 22320).toLocaleString()}` },
      { item: 'KEA Miscellaneous Fees', cost: '₹22,320' }
    ];
  } else if (quota === 'comedk') {
    feeValue = (activeYear === '2026') ? 264000 : 244000;
    breakdown = [
      { item: 'COMEDK Consensual Tuition Fee', cost: `₹${(feeValue - 20000).toLocaleString()}` },
      { item: 'Other Institutional Fees', cost: '₹20,000' }
    ];
  } else if (quota === 'mgmt') {
    feeValue = isGovt ? 0 : 450000;
    breakdown = [
      { item: 'Institutional Tuition Fee (Varies)', cost: isGovt ? 'N/A (No Management Seats)' : '₹4,00,000' },
      { item: 'Development fee', cost: isGovt ? 'N/A' : '₹50,000' }
    ];
  }
  
  document.getElementById('calc-fee-total-value').textContent = feeValue > 0 ? `₹${feeValue.toLocaleString()}` : 'N/A';
  
  const detailsEl = document.getElementById('calc-fee-breakdown-details');
  if (detailsEl) {
    detailsEl.innerHTML = breakdown.map(b => `
      <div style="display:flex; justify-content:space-between; border-bottom:1px solid rgba(255,255,255,0.05); padding-bottom:6px; margin-bottom:6px;">
        <span style="color:var(--text-muted);">${b.item}</span>
        <span style="font-weight:600; color:var(--text);">${b.cost}</span>
      </div>
    `).join('');
  }
}

let simPreset = 'desktop';
let simOrientation = 'portrait';

function setupViewportSimulator() {
  const bar = document.getElementById('superuser-simulator-bar');
  const wrapper = document.getElementById('app-viewport-wrapper');
  if (!bar || !wrapper) return;

  const isSuper = currentUser && (currentUser.role === 'superuser');
  bar.style.display = isSuper ? 'block' : 'none';

  const btns = bar.querySelectorAll('.sim-btn');
  const rotateBtn = document.getElementById('btn-sim-rotate');

  // Remove existing listeners to avoid duplicates on re-binding
  const newBtns = [];
  btns.forEach(btn => {
    const clone = btn.cloneNode(true);
    btn.parentNode.replaceChild(clone, btn);
    newBtns.push(clone);
  });

  if (rotateBtn) {
    const newRotate = rotateBtn.cloneNode(true);
    rotateBtn.parentNode.replaceChild(newRotate, rotateBtn);
    
    newRotate.addEventListener('click', () => {
      simOrientation = simOrientation === 'portrait' ? 'landscape' : 'portrait';
      if (simPreset !== 'desktop') {
        wrapper.classList.toggle('landscape');
        updateSimDimensionsBadge();
      }
    });
  }

  newBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      newBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const preset = btn.dataset.preset;
      simPreset = preset;
      
      const rotateEl = document.getElementById('btn-sim-rotate');
      
      // Reset classes
      wrapper.className = '';
      if (preset === 'desktop') {
        if (rotateEl) rotateEl.style.display = 'none';
        updateSimDimensionsBadge();
      } else {
        if (rotateEl) rotateEl.style.display = 'inline-block';
        wrapper.classList.add('sim-mode', `sim-${preset}`);
        if (simOrientation === 'landscape') {
          wrapper.classList.add('landscape');
        }
        updateSimDimensionsBadge();
      }
    });
  });

  // Synchronize bottom navigation buttons state
  document.querySelectorAll('.mob-nav-btn').forEach(mnb => {
    mnb.classList.remove('active');
    if (mnb.dataset.tab === currentTab) {
      mnb.classList.add('active');
    }
  });
}

function updateSimDimensionsBadge() {
  const badge = document.getElementById('sim-dimensions-badge');
  if (!badge) return;

  if (simPreset === 'desktop') {
    badge.textContent = '100% Fluid';
    return;
  }

  const dimensions = {
    ipad: { portrait: '768 x 1024 (iPad)', landscape: '1024 x 768 (iPad)' },
    iphone15: { portrait: '393 x 852 (iPhone 15 Pro)', landscape: '852 x 393 (iPhone 15 Pro)' },
    s23: { portrait: '360 x 800 (Galaxy S23)', landscape: '800 x 360 (Galaxy S23)' },
    pixel8: { portrait: '412 x 915 (Pixel 8)', landscape: '915 x 412 (Pixel 8)' }
  };

  const text = dimensions[simPreset]?.[simOrientation] || 'Fluid';
  badge.textContent = text;
}

