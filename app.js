/* =========================================
   Karnataka Engineering Seat Matrix 2025
   Main Application Logic
   ========================================= */

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
// ─────────────────────────────
let allData = null;
let filtered = [];
let displayCount = 30;
let currentTab = 'colleges';
let sortMode = 'name';
let viewMode = 'grid';
let filters = { search: '', annexure: 'all', district: '', course: '', minSeats: 0 };

// ─────────────────────────────
// Boot
// ─────────────────────────────
async function init() {
  try {
    const res = await fetch('seat_matrix_data.json?t=' + new Date().getTime());
    allData = await res.json();
    populateFilters();
    updateHeaderStats();
    applyFilters();
    renderStats();
    renderTotals('ALL');
    bindEvents();
  } catch (e) {
    console.error('Failed to load data:', e);
    document.getElementById('colleges-grid').innerHTML =
      `<div class="empty-state"><div class="empty-state-icon">⚠️</div>
       <div class="empty-state-text">Could not load seat_matrix_data.json.<br>Make sure the file is in the same directory.</div></div>`;
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
    opt.value = c; opt.textContent = titleCase(c);
    courseSel.appendChild(opt);
  });

  const predCourseSel = document.getElementById('pred-course');
  if (predCourseSel) {
    predCourseSel.innerHTML = '<option value="">All Courses</option>';
    sortedCourses.forEach(c => {
      const opt = document.createElement('option');
      opt.value = c; opt.textContent = titleCase(c);
      predCourseSel.appendChild(opt);
    });
  }
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

// ─────────────────────────────
// Filtering
// ─────────────────────────────
function applyFilters() {
  const { search, annexure, district, course, minSeats } = filters;
  const q = search.toLowerCase().trim();

  filtered = allData.colleges.filter(c => {
    if (annexure !== 'all' && c.annexure !== annexure) return false;
    if (district && c.district !== district) return false;
    if (course) {
      const has = c.courses.some(cr => cr.course_name === course);
      if (!has) return false;
    }
    if (minSeats > 0 && (c.total_intake || 0) < minSeats) return false;
    if (q) {
      const nameMatch = c.college_name.toLowerCase().includes(q);
      const addrMatch = (c.address || '').toLowerCase().includes(q);
      const distMatch = (c.district || '').toLowerCase().includes(q);
      if (!nameMatch && !addrMatch && !distMatch) return false;
    }
    return true;
  });

  sortFiltered();
  displayCount = 30;
  renderColleges();
  updateSidebarStats();
  renderCourseTable();
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

  // Bind card clicks
  grid.querySelectorAll('.college-card').forEach((el, i) => {
    el.addEventListener('click', () => openModal(toShow[i]));
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

  return `
    <div class="college-card" style="animation-delay:${Math.min(index * 0.03, 0.3)}s" data-index="${index}">
      <div class="card-top">
        <div class="card-badge badge-${ann}">${ANNEXURE_ICONS[ann]}</div>
        <div class="card-info">
          <div class="card-name">${escHtml(college.college_name)}</div>
          <div class="card-location">
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/>
              <circle cx="12" cy="9" r="2.5"/>
            </svg>
            ${escHtml(college.district || 'Karnataka')}
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
      <td>${titleCase(row.name)}</td>
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
}

function renderDonutChart() {
  const s = allData.stats.by_annexure;
  const items = Object.entries(s).map(([k, v], i) => ({
    label: v.label,
    value: v.total_seats,
    color: CHART_COLORS[i]
  }));
  const total = items.reduce((s, i) => s + i.value, 0);

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
    <text x="${cx}" y="${cy-6}" text-anchor="middle" fill="#e8eaf0" font-size="14" font-weight="700" font-family="Space Grotesk">${formatNum(total)}</text>
    <text x="${cx}" y="${cy+12}" text-anchor="middle" fill="#6b7799" font-size="9" font-family="Inter">total seats</text>
  </svg>`;

  document.getElementById('donut-type').innerHTML = svg;
  document.getElementById('legend-type').innerHTML = `<div class="donut-legend">` +
    arcs.map(a => `
      <div class="legend-item">
        <div class="legend-dot" style="background:${a.color}"></div>
        <span class="legend-name">${a.label}</span>
        <span class="legend-val">${a.value.toLocaleString()}</span>
      </div>
    `).join('') + `</div>`;
}

function polarToCart(cx, cy, r, angle) {
  const rad = (angle * Math.PI) / 180;
  return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) };
}

function renderDistrictBarChart() {
  const s = allData.stats.by_district;
  const rows = Object.entries(s)
    .filter(([k]) => k !== 'Other')
    .sort((a, b) => b[1].total - a[1].total)
    .slice(0, 12);
  const maxVal = rows[0]?.[1].total || 1;

  const html = rows.map(([dist, d], i) => {
    const w = Math.round((d.total / maxVal) * 100);
    const color = CHART_COLORS[i % CHART_COLORS.length];
    return `<div class="bar-item">
      <div class="bar-label">${dist}</div>
      <div class="bar-bg">
        <div class="bar-fill" style="width:${w}%; background:${color};"></div>
      </div>
      <div class="bar-val">${d.total.toLocaleString()}</div>
    </div>`;
  }).join('');

  document.getElementById('bar-district').innerHTML = html;
}

function renderCourseBarChart() {
  const s = allData.stats.by_course;
  const rows = Object.entries(s)
    .sort((a, b) => b[1].total - a[1].total)
    .slice(0, 15);
  const maxVal = rows[0]?.[1].total || 1;

  const html = rows.map(([name, d], i) => {
    const w = Math.round((d.total / maxVal) * 100);
    const color = CHART_COLORS[i % CHART_COLORS.length];
    return `<div class="bar-item horizontal">
      <div class="bar-label" title="${titleCase(name)}">${titleCase(name)}</div>
      <div class="bar-bg">
        <div class="bar-fill" style="width:${w}%; background:${color}; display:flex; align-items:center;">
        </div>
      </div>
      <div class="bar-val">${d.total.toLocaleString()}</div>
    </div>`;
  }).join('');

  document.getElementById('bar-courses').innerHTML = html;
}

// ─────────────────────────────
// Modal
// ─────────────────────────────
function openModal(college) {
  const ann = college.annexure || 'C';
  const annLabel = ANNEXURE_LABELS[ann] || ann;

  const totalIntake = college.total_intake || college.courses.reduce((s, c) => s + (c.total_intake || 0), 0);
  const totalKea = college.total_kea_seats || college.courses.reduce((s, c) => s + (c.total_kea_seats || 0), 0);
  const totalComedk = college.courses.reduce((s, c) => s + (c.cat2_seats || 0), 0);
  const totalMgmt = college.courses.reduce((s, c) => s + (c.cat3_seats || 0), 0);

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

  // Get default category from predictor if available, else default to GM
  const predCatEl = document.getElementById('pred-category');
  const defaultCat = predCatEl ? predCatEl.value : 'GM';

  const courseRows = college.courses.map((c, idx) => {
    const comEdkCol = c.cat2_seats > 0 ? `<td class="td-comedk">${c.cat2_seats}</td>` : '';
    const mgmtCol = c.cat3_seats > 0 ? `<td class="td-mgmt">${c.cat3_seats}</td>` : '';
    const hkCol = (c.kea_hk || 0) > 0 ? `<td class="td-hk">${c.kea_hk}</td>` : '';
    const rkCol = (c.kea_rk || 0) > 0 ? `<td class="td-rk">${c.kea_rk}</td>` : '';
    
    const r1_cutoffs = c.round1_cutoff || {};
    const r1_cutoff_val = r1_cutoffs[defaultCat];
    const initialCutoffR1 = r1_cutoff_val ? parseInt(r1_cutoff_val).toLocaleString() : '—';

    const r2_cutoffs = c.round2_cutoff || {};
    const r2_cutoff_val = r2_cutoffs[defaultCat];
    const initialCutoffR2 = r2_cutoff_val ? parseInt(r2_cutoff_val).toLocaleString() : '—';

    const r3_cutoffs = c.round3_cutoff || {};
    const r3_cutoff_val = r3_cutoffs[defaultCat];
    const initialCutoffR3 = r3_cutoff_val ? parseInt(r3_cutoff_val).toLocaleString() : '—';

    return `<tr>
      <td>${titleCase(c.course_name)}</td>
      <td class="td-total">${c.total_intake || 0}</td>
      <td class="td-kea">${c.total_kea_seats || 0}</td>
      ${comEdkCol || '<td>—</td>'}
      ${mgmtCol || '<td>—</td>'}
      ${hkCol || '<td>—</td>'}
      ${rkCol || '<td>—</td>'}
      <td class="td-cutoff-r1" data-course-idx="${idx}" style="color:var(--blue); text-align:right; font-family:var(--font-display); font-weight:700;">${initialCutoffR1}</td>
      <td class="td-cutoff-r2" data-course-idx="${idx}" style="color:var(--purple); text-align:right; font-family:var(--font-display); font-weight:700;">${initialCutoffR2}</td>
      <td class="td-cutoff-r3" data-course-idx="${idx}" style="color:var(--pink); text-align:right; font-family:var(--font-display); font-weight:700;">${initialCutoffR3}</td>
    </tr>`;
  }).join('');

  const hasComDk = college.courses.some(c => c.cat2_seats > 0);
  const hasMgmt = college.courses.some(c => c.cat3_seats > 0);
  const hasHk = college.courses.some(c => (c.kea_hk || 0) > 0);

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

  const categories = ['GM', 'GMK', 'GMR', '1G', '1K', '1R', '2AG', '2AK', '2AR', '2BG', '2BK', '2BR', '3AG', '3AK', '3AR', '3BG', '3BK', '3BR', 'SCG', 'SCK', 'SCR', 'STG', 'STK', 'STR'];
  const optionsHtml = categories
    .map(cat => `<option value="${cat}" ${cat === defaultCat ? 'selected' : ''}>${cat}</option>`)
    .join('');

  document.getElementById('modal-content').innerHTML = `
    <div class="modal-header">
      <div class="modal-badge-row">
        <span class="card-type-pill pill-${ann}">${ANNEXURE_ICONS[ann]} ${annLabel}</span>
        <span class="card-location" style="color:var(--text-muted); font-size:13px">
          📍 ${escHtml(college.district || 'Karnataka')}
        </span>
      </div>
      <div class="modal-title">${escHtml(college.college_name)}</div>
      <div class="modal-address">📌 ${escHtml(college.address || 'Karnataka')}</div>
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
    </div>

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
            <th>${hasComDk ? 'COMEDK' : '—'}</th>
            <th>${hasMgmt ? 'Mgmt' : '—'}</th>
            <th>${hasHk ? 'HK' : '—'}</th>
            <th>RK</th>
            <th style="color:var(--blue); text-align:right;">R1 Cut-off</th>
            <th style="color:var(--purple); text-align:right;">R2 Cut-off</th>
            <th style="color:var(--pink); text-align:right;">R3 Cut-off</th>
          </tr>
        </thead>
        <tbody>${courseRows}</tbody>
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
}

function closeModal() {
  document.getElementById('modal-overlay').classList.remove('open');
  document.body.style.overflow = '';
}

// Helper to determine fees by college type & course names (from KEA_FEES_2025.pdf)
function getSeatFees(college) {
  const type = college.college_type || '';
  const result = {
    type: 'standard',
    hasConcession: false,
    rows: []
  };

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
    // Private / Minority / Deemed / Private University
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

  return result;
}

// Category details resolver based on KEA_FEES_2025.pdf
function getCategoryFeeDetails(college, category, courseType) {
  const type = college.college_type || '';
  const isConcession = courseType === 'concession';
  const isGovt = type.includes('Government / VTU Constituent');

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

  // Min seats slider
  const slider = document.getElementById('min-seats');
  const sliderVal = document.getElementById('min-seats-val');
  slider.addEventListener('input', () => {
    filters.minSeats = parseInt(slider.value);
    sliderVal.textContent = filters.minSeats > 0 ? `${filters.minSeats}+` : '0+';
    applyFilters();
  });

  // Reset
  document.getElementById('reset-btn').addEventListener('click', () => {
    filters = { search: '', annexure: 'all', district: '', course: '', minSeats: 0 };
    searchInput.value = '';
    document.getElementById('district-filter').value = '';
    document.getElementById('course-filter').value = '';
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

  // Download handlers
  document.getElementById('btn-download-json').addEventListener('click', downloadJSON);
  document.getElementById('btn-download-csv').addEventListener('click', downloadCSV);

  // Predictor handlers
  const predBtn = document.getElementById('pred-btn');
  if (predBtn) {
    predBtn.addEventListener('click', runPrediction);
  }
  const predRankInput = document.getElementById('pred-rank');
  if (predRankInput) {
    predRankInput.addEventListener('keydown', e => {
      if (e.key === 'Enter') runPrediction();
    });
  }
}

// ─────────────────────────────
// Helpers
// ─────────────────────────────
function escHtml(str) {
  return (str || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function titleCase(str) {
  if (!str) return '';
  const exceptions = new Set(['AND', 'OF', 'IN', 'THE', 'FOR', 'WITH', 'A', 'AN', 'TO', 'AT', 'BY', 'OR', '&']);
  return str.toLowerCase().split(' ').map((w, i) => {
    const upper = w.toUpperCase();
    if (i === 0 || !exceptions.has(upper)) return w.charAt(0).toUpperCase() + w.slice(1);
    return w;
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
  const colleges = allData.colleges.filter(c =>
    annFilter === 'ALL' || c.annexure === annFilter
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
    ? ['A','B','C','D','M','O','P','Z','E','V']
    : [annFilter];

  const annLabels = {
    A:'Government / VTU', B:'Govt Aided', C:'Private Unaided',
    D:'Private Minority', M:'Public University (UVCE)',
    O:'Private University', P:'Deemed University', Z:'Government (Higher Fees)',
    E:'New Intake (Govt/Pvt)', V:'New Intake (Univ)'
  };
  const annIcons = { A:'🏛️', B:'🤝', C:'🏢', D:'⭐', M:'🎓', O:'🌍', P:'🎖️', Z:'🏛️', E:'✨', V:'⚡' };

  const annRows = annexures.map(ann => {
    const cols = allData.colleges.filter(c => c.annexure === ann);
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
      <td class="td-comedk">${a2 > 0 ? a2.toLocaleString() : '—'}</td>
      <td class="td-mgmt">${a3 > 0 ? a3.toLocaleString() : '—'}</td>
      <td><span class="kea-pct-badge ${pctCls}">${keaPct}%</span></td>
    </tr>`;
  });

  // Grand total row
  const gt2 = totalCat2 > 0 ? totalCat2.toLocaleString() : '—';
  const gt3 = totalCat3 > 0 ? totalCat3.toLocaleString() : '—';
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
    const cols = allData.colleges.filter(c => c.annexure === ann);
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
function downloadJSON() {
  const annSel = document.getElementById('download-ann-select').value;
  let dataToDownload;
  let filename;

  if (annSel === 'ALL') {
    dataToDownload = allData.colleges;
    filename = 'karnataka_seat_matrix_2025_all.json';
  } else {
    dataToDownload = allData.colleges.filter(c => c.annexure === annSel);
    filename = `karnataka_seat_matrix_2025_annexure_${annSel}.json`;
  }

  const jsonStr = JSON.stringify(dataToDownload, null, 2);
  const blob = new Blob([jsonStr], { type: 'application/json' });
  triggerDownload(blob, filename);
}

function downloadCSV() {
  const annSel = document.getElementById('download-ann-select').value;
  let colleges;
  let filename;

  if (annSel === 'ALL') {
    colleges = allData.colleges;
    filename = 'karnataka_seat_matrix_2025_all.csv';
  } else {
    colleges = allData.colleges.filter(c => c.annexure === annSel);
    filename = `karnataka_seat_matrix_2025_annexure_${annSel}.csv`;
  }

  const headers = [
    'College Number',
    'College Name',
    'Address',
    'Annexure',
    'College Type',
    'District',
    'Course Name',
    'Total Intake',
    'Total KEA Seats',
    'PH Seats',
    'SPL Seats',
    'HK Seats',
    'RK Seats',
    'TOT HK-RK',
    'COMEDK Seats',
    'Mgmt Seats',
    'SNQ Seats'
  ];

  const csvRows = [headers.join(',')];

  colleges.forEach(col => {
    col.courses.forEach(c => {
      const row = [
        col.college_number,
        `"${col.college_name.replace(/"/g, '""')}"`,
        `"${(col.address || '').replace(/"/g, '""')}"`,
        col.annexure,
        `"${col.college_type}"`,
        col.district || '',
        `"${c.course_name}"`,
        c.total_intake || 0,
        c.total_kea_seats || 0,
        c.kea_ph || 0,
        c.kea_spl || 0,
        c.kea_hk || 0,
        c.kea_rk || 0,
        c.kea_tot || 0,
        c.cat2_seats || 0,
        c.cat3_seats || 0,
        c.over_above_5pct || 0
      ];
      csvRows.push(row.join(','));
    });
  });

  const csvContent = '\uFEFF' + csvRows.join('\n');
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  triggerDownload(blob, filename);
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
  const selectedRound = roundSel ? roundSel.value : 'round3';
  const preferredCourse = courseSel.value;
  
  const results = [];
  const seen = new Set();
  
  const cutoffKey = selectedRound === 'round1' ? 'round1_cutoff' : (selectedRound === 'round2' ? 'round2_cutoff' : 'round3_cutoff');
  
  allData.colleges.forEach(college => {
    college.courses.forEach(course => {
      // Filter by course name if selected
      if (preferredCourse && course.course_name !== preferredCourse) {
        return;
      }
      
      const cutoffs = course[cutoffKey] || {};
      const cutoffStr = cutoffs[category];
      if (!cutoffStr) return; // No cutoff for this category
      
      const cutoff = parseFloat(cutoffStr);
      if (isNaN(cutoff)) return;
      
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
      
      results.push({
        college,
        courseName: course.course_name,
        cutoff: cutoff,
        diff: diff,
        chance: chance,
        chanceClass: chanceClass
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
    header.textContent = selectedRound === 'round1' ? 'Cutoff Rank (R1)' : (selectedRound === 'round2' ? 'Cutoff Rank (R2)' : 'Cutoff Rank (R3)');
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
    
    return `<tr class="pred-row" data-college-number="${col.college_number}" style="cursor:pointer; transition:background 0.2s;">
      <td><span class="card-type-pill pill-${col.annexure}" style="font-size:11px; padding: 2px 6px;">${col.kea_code || col.college_number}</span></td>
      <td><strong>${escHtml(col.college_name)}</strong><br><small style="color:var(--text-muted)">📍 ${escHtml(col.district)}</small></td>
      <td>${titleCase(res.courseName)}</td>
      <td style="font-family:var(--font-display); font-weight:700; text-align:right;">${res.cutoff.toLocaleString()}</td>
      <td class="${diffClass}" style="font-family:var(--font-display); font-weight:700; text-align:right;">${diffText}</td>
      <td style="text-align:center;"><span class="badge-chance ${res.chanceClass}">${res.chance}</span></td>
    </tr>`;
  }).join('');
  
  // Attach event listener for row clicks
  tbody.querySelectorAll('.pred-row').forEach(row => {
    row.addEventListener('click', () => {
      const colNum = row.dataset.collegeNumber;
      const collegeObj = allData.colleges.find(c => c.college_number === colNum);
      if (collegeObj) {
        openModal(collegeObj);
      }
    });
  });
}
