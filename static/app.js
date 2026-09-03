/**
 * Frontend logic for Hauler Route & Driver Schedule Optimizer
 */

let currentLoadId = null;
let currentLoadData = null;
let currentSolution = null;
let allLoads = [];
let activeOriginFilter = 'ALL';

document.addEventListener('DOMContentLoaded', () => {
  initEventListeners();
  loadAllLoads();
});

function initEventListeners() {
  // Search input
  const searchInput = document.getElementById('loadSearchInput');
  if (searchInput) {
    searchInput.addEventListener('input', filterAndRenderLoads);
  }

  // VDC Filter Pills
  const vdcPills = document.querySelectorAll('.vdc-pill');
  vdcPills.forEach(pill => {
    pill.addEventListener('click', (e) => {
      vdcPills.forEach(p => {
        p.classList.remove('active', 'bg-sky-600', 'text-white');
        p.classList.add('bg-slate-800', 'text-slate-300');
      });
      pill.classList.add('active', 'bg-sky-600', 'text-white');
      pill.classList.remove('bg-slate-800', 'text-slate-300');
      activeOriginFilter = pill.getAttribute('data-origin');
      filterAndRenderLoads();
    });
  });
}

// Fetch list of loads from API
async function loadAllLoads() {
  try {
    const res = await fetch('/api/loads');
    const data = await res.json();
    allLoads = data.loads || [];
    filterAndRenderLoads();

    // Auto-select first load or 244606 (standard LA long haul)
    if (allLoads.length > 0) {
      const defaultLoad = allLoads.find(l => l.id === 244606) || allLoads[0];
      selectLoad(defaultLoad.id);
    }
  } catch (err) {
    console.error('Failed to load inventory:', err);
    document.getElementById('loadCardList').innerHTML = `
      <div class="p-4 bg-red-950/40 border border-red-800 rounded-lg text-red-300 text-xs text-center">
        Error loading loads inventory from server.
      </div>
    `;
  }
}

// Filter and render sidebar load cards
function filterAndRenderLoads() {
  const searchTerm = (document.getElementById('loadSearchInput')?.value || '').toLowerCase().trim();
  const listContainer = document.getElementById('loadCardList');
  if (!listContainer) return;

  const filtered = allLoads.filter(load => {
    const matchesOrigin = (activeOriginFilter === 'ALL') || (load.origin_legal_entity === activeOriginFilter);
    const matchesSearch = !searchTerm || 
      String(load.id).includes(searchTerm) || 
      String(load.load_num).toLowerCase().includes(searchTerm) ||
      String(load.assigned_hauler_name).toLowerCase().includes(searchTerm) ||
      String(load.load_status).toLowerCase().includes(searchTerm);
    return matchesOrigin && matchesSearch;
  });

  document.getElementById('loadCountBadge').textContent = `${filtered.length} loads`;

  if (filtered.length === 0) {
    listContainer.innerHTML = `
      <div class="text-center py-8 text-slate-500 text-xs">
        <i class="fa-solid fa-filter-circle-xmark text-lg mb-2"></i>
        <p>No matching loads found.</p>
      </div>
    `;
    return;
  }

  listContainer.innerHTML = filtered.map(load => {
    const isActive = load.id === currentLoadId ? 'active' : '';
    const statusColor = load.load_status === 'locked' ? 'text-amber-400 bg-amber-500/10 border-amber-500/20' :
                        load.load_status === 'sent' ? 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20' :
                        'text-slate-400 bg-slate-800 border-slate-700';

    return `
      <div class="load-card p-3 rounded-xl border border-slate-800 hover:border-slate-700 bg-slate-900/60 cursor-pointer transition ${isActive}"
           onclick="selectLoad(${load.id})">
        <div class="flex items-center justify-between mb-1.5">
          <div class="flex items-center space-x-2">
            <span class="font-mono font-bold text-xs text-white">#${load.id}</span>
            <span class="font-mono text-[11px] text-slate-400">${load.load_num}</span>
          </div>
          <span class="text-[10px] font-semibold px-2 py-0.5 rounded border uppercase ${statusColor}">${load.load_status}</span>
        </div>
        
        <div class="flex items-center justify-between text-[11px] text-slate-400 mb-1">
          <span class="flex items-center space-x-1">
            <i class="fa-solid fa-location-dot text-sky-400 text-[10px]"></i>
            <span class="text-slate-300 font-medium">${load.origin_legal_entity} (${load.origin_vdc_name})</span>
          </span>
          <span class="text-slate-400 font-mono">${load.cargo_count} Cars</span>
        </div>

        <div class="text-[11px] text-slate-500 truncate flex items-center justify-between">
          <span class="truncate"><i class="fa-solid fa-truck text-[10px] mr-1"></i>${load.assigned_hauler_name}</span>
          <span class="text-[10px] text-indigo-400 font-mono">${load.dealers_count} Dealers</span>
        </div>
      </div>
    `;
  }).join('');
}

// Select a load
async function selectLoad(loadId) {
  currentLoadId = loadId;
  filterAndRenderLoads(); // update active styling

  // Fetch full details
  try {
    const res = await fetch(`/api/load/${loadId}`);
    const data = await res.json();
    if (!data.success) {
      alert('Error fetching load details: ' + data.error);
      return;
    }

    currentLoadData = data;
    renderLoadBanner(data);
    renderCargoTable(data.cargo_items);

    // Auto trigger solve to show schedule immediately
    triggerSolve();
  } catch (err) {
    console.error('Error selecting load:', err);
  }
}

// Render top banner with load metadata
function renderLoadBanner(data) {
  document.getElementById('bannerLoadId').textContent = `Load #${data.load_id}`;
  document.getElementById('bannerLoadNum').textContent = data.load_num;
  document.getElementById('bannerVdcName').textContent = `${data.origin_name} (${data.origin_code})`;
  
  const statusBadge = document.getElementById('bannerStatusBadge');
  statusBadge.textContent = data.load_status;
  statusBadge.className = `text-xs px-2 py-0.5 rounded-full uppercase font-semibold ` +
    (data.load_status === 'locked' ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' :
     data.load_status === 'sent' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' :
     'bg-slate-800 text-slate-300');

  document.getElementById('bannerHaulerName').textContent = `${data.hauler.name} (${data.hauler.capacity} Car Cap)`;
  document.getElementById('bannerCargoStats').textContent = `${data.total_cargo_units} Vehicles (${data.total_weight_kg.toLocaleString()} kg)`;
  document.getElementById('bannerDealersCount').textContent = `${data.dealers.length} Destination Dealerships`;
  document.getElementById('cargoTotalUnitsWeight').textContent = `${data.total_cargo_units} Units • Total Weight: ${data.total_weight_kg.toLocaleString()} kg`;
}

// Render Cargo Table
function renderCargoTable(cargoList) {
  const tbody = document.getElementById('cargoTableBody');
  if (!tbody) return;

  if (!cargoList || cargoList.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" class="py-6 text-center text-slate-500 text-xs">No vehicle manifest found.</td></tr>`;
    return;
  }

  tbody.innerHTML = cargoList.map((item, idx) => `
    <tr class="hover:bg-slate-800/40 transition">
      <td class="py-2.5 px-3 text-slate-500 text-center">${idx + 1}</td>
      <td class="py-2.5 px-3 font-mono font-medium text-sky-400">${item.vin}</td>
      <td class="py-2.5 px-4 text-white font-medium">${item.model_name}</td>
      <td class="py-2.5 px-3 text-slate-400">${item.brand} ${item.series || ''}</td>
      <td class="py-2.5 px-3 text-right text-slate-300">${item.weight_kg ? Number(item.weight_kg).toLocaleString() : '2,000'}</td>
      <td class="py-2.5 px-3 text-center text-slate-400 text-[11px]">${item.length_m || '-'} &times; ${item.width_m || '-'} &times; ${item.height_m || '-'}m</td>
      <td class="py-2.5 px-4 text-amber-300 font-mono text-[11px]">${item.destination_dealer_id}</td>
    </tr>
  `).join('');
}

// Trigger CP-SAT Solver
async function triggerSolve() {
  if (!currentLoadId) return;

  const btn = document.getElementById('btnSolveSchedule');
  const originalHtml = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin text-amber-300"></i><span>SOLVING WITH CP-SAT...</span>`;

  const tripStart = document.getElementById('tripStartTimeInput')?.value || '07:00';
  const dutyLimit = parseFloat(document.getElementById('maxDutyHoursInput')?.value || '11.0');
  const handoverBuf = parseInt(document.getElementById('handoverBufferInput')?.value || '45');

  try {
    const res = await fetch('/api/solve', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        load_id: currentLoadId,
        trip_start_time: tripStart,
        max_driver_duty_hours: dutyLimit,
        handover_duration_mins: handoverBuf,
        enforce_11hr_rule: true
      })
    });

    const data = await res.json();
    currentSolution = data;
    renderSolution(data);
  } catch (err) {
    console.error('Optimization error:', err);
    alert('Solver request failed. Check server logs.');
  } finally {
    btn.disabled = false;
    btn.innerHTML = originalHtml;
  }
}

// Render the solution into KPIs, Tables, Gantt, and Circuit
function renderSolution(res) {
  // If error or infeasible
  if (res.status === 'INFEASIBLE' || res.status === 'ERROR') {
    document.getElementById('kpiStatusBadge').textContent = res.status;
    document.getElementById('kpiStatusBadge').className = 'px-2 py-0.5 rounded text-xs font-bold bg-red-500/20 text-red-300 border border-red-500/30';
    document.getElementById('kpiSolveTime').textContent = res.solver_status || 'Infeasible';
    
    document.getElementById('itineraryTableBody').innerHTML = `
      <tr>
        <td colspan="11" class="py-10 text-center text-red-400 bg-red-950/20">
          <i class="fa-solid fa-triangle-exclamation text-2xl mb-2"></i>
          <p class="font-bold text-sm">Optimization Infeasible</p>
          <p class="text-xs text-slate-400 mt-1">${res.message}</p>
        </td>
      </tr>
    `;
    return;
  }

  // KPIs
  document.getElementById('kpiStatusBadge').textContent = res.status;
  document.getElementById('kpiStatusBadge').className = 'px-2 py-0.5 rounded text-xs font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30';
  document.getElementById('kpiSolveTime').textContent = `Solve: ${res.solve_time_sec * 1000} ms`;

  document.getElementById('kpiDuration').textContent = `${Math.floor(res.total_trip_duration_mins / 60)}h ${res.total_trip_duration_mins % 60}m`;
  document.getElementById('kpiDrivingTime').textContent = `Driving: ${res.total_travel_time_hours}h`;

  document.getElementById('kpiDistance').textContent = `${res.total_distance_miles} mi`;
  
  document.getElementById('kpiDriversCount').textContent = `${res.num_drivers_assigned} ${res.num_drivers_assigned === 1 ? 'Driver' : 'Drivers'}`;
  document.getElementById('kpi11hCompliance').textContent = 'All ≤ 11.0h limit';

  const handoverLeg = res.legs.find(l => l.handover_at_dest);
  if (handoverLeg) {
    document.getElementById('kpiHandoverLoc').textContent = `${handoverLeg.to_name} (${handoverLeg.to_code})`;
    document.getElementById('kpiHandoverDuration').textContent = `${handoverLeg.handover_duration_mins} min buffer applied`;
  } else {
    document.getElementById('kpiHandoverLoc').textContent = 'None Needed (Single)';
    document.getElementById('kpiHandoverDuration').textContent = 'Trip ≤ 11.0 hours';
  }

  document.getElementById('kpiCapacity').textContent = `${res.total_cargo_units} / ${res.hauler_capacity} Cars`;
  document.getElementById('kpiCargoWeight').textContent = `${res.total_cargo_weight_kg.toLocaleString()} kg`;

  if (res.cost_breakdown) {
    document.getElementById('kpiTotalCost').textContent = `$${res.cost_breakdown.total_trip_cost.toLocaleString()}`;
  }

  // Driver Progress Bars
  renderDriverDutyBars(res.drivers_assigned);

  // Itinerary Table
  renderItineraryTable(res.legs);

  // Gantt Chart
  renderGanttChart(res);

  // Route Circuit
  renderCircuitDiagram(res);
}

// Render driver compliance progress bars
function renderDriverDutyBars(drivers) {
  const container = document.getElementById('driverProgressBars');
  if (!container) return;

  if (!drivers || drivers.length === 0) {
    container.innerHTML = `<div class="text-xs text-slate-500">No driver assignments recorded.</div>`;
    return;
  }

  container.innerHTML = drivers.map((d, idx) => {
    const dutyHours = d.total_duty_hours;
    const drivingHours = d.driving_hours;
    const pct = Math.min(100, Math.round((dutyHours / 11.0) * 100));
    const isOver = dutyHours > 11.0;
    const barColor = isOver ? 'bg-red-500' : pct > 80 ? 'bg-amber-500' : 'bg-emerald-500';

    return `
      <div class="bg-slate-900 border border-slate-800 rounded-xl p-3.5 space-y-2">
        <div class="flex items-center justify-between text-xs">
          <div class="flex items-center space-x-2">
            <span class="w-6 h-6 rounded-full bg-sky-500/20 text-sky-400 font-bold flex items-center justify-center text-[10px]">D${idx + 1}</span>
            <div>
              <span class="font-semibold text-slate-200">${d.driver.name}</span>
              <span class="text-[10px] text-slate-400 font-mono ml-1.5">(${d.driver.driver_id})</span>
            </div>
          </div>
          <div class="text-right">
            <span class="font-mono font-bold ${isOver ? 'text-red-400' : 'text-emerald-400'}">${dutyHours}h</span>
            <span class="text-[11px] text-slate-400">/ 11.0h max</span>
          </div>
        </div>

        <div class="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
          <div class="${barColor} h-full transition-all duration-500" style="width: ${pct}%"></div>
        </div>

        <div class="flex items-center justify-between text-[11px] text-slate-400">
          <span>Driving: <strong class="text-slate-300 font-mono">${drivingHours}h</strong> • Unloading/Buffer: <strong class="text-slate-300 font-mono">${(dutyHours - drivingHours).toFixed(2)}h</strong></span>
          <span class="px-2 py-0.5 rounded text-[10px] font-bold ${isOver ? 'bg-red-500/20 text-red-300' : 'bg-emerald-500/20 text-emerald-300'}">
            ${isOver ? 'VIOLATION' : 'COMPLIANT (≤11h)'}
          </span>
        </div>
      </div>
    `;
  }).join('');
}

// Render Itinerary Table
function renderItineraryTable(legs) {
  const tbody = document.getElementById('itineraryTableBody');
  if (!tbody) return;

  tbody.innerHTML = legs.map(leg => {
    const handoverBadge = leg.handover_at_dest 
      ? `<span class="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30 text-[10px] font-bold animate-pulse">HANDOVER (${leg.handover_duration_mins}m)</span>`
      : `<span class="text-slate-600 text-[10px]">—</span>`;

    return `
      <tr class="hover:bg-slate-800/40 transition">
        <td class="py-3 px-3 text-center text-slate-500 font-bold">${leg.leg_number}</td>
        <td class="py-3 px-4">
          <div class="font-semibold text-white flex items-center space-x-1.5">
            <span class="text-sky-400">${leg.from_code}</span>
            <span class="text-slate-500">&rarr;</span>
            <span class="text-emerald-400">${leg.to_code}</span>
          </div>
          <div class="text-[10px] text-slate-400 truncate max-w-xs">${leg.from_name} to ${leg.to_name}</div>
        </td>
        <td class="py-3 px-3 text-right font-mono font-medium text-slate-200">${leg.distance_miles} mi</td>
        <td class="py-3 px-3 text-right font-mono text-slate-300">${leg.travel_time_formatted}</td>
        <td class="py-3 px-3 text-center font-mono text-slate-300">${leg.departure_from_origin}</td>
        <td class="py-3 px-3 text-center font-mono font-medium text-amber-300">${leg.arrival_at_dest}</td>
        <td class="py-3 px-3 text-center font-mono text-slate-400">${leg.service_time_mins} min</td>
        <td class="py-3 px-3 text-center font-mono text-slate-300">${leg.departure_from_dest}</td>
        <td class="py-3 px-4">
          <div class="font-medium text-slate-200 flex items-center space-x-1">
            <i class="fa-solid fa-user-gear text-[10px] text-sky-400"></i>
            <span>${leg.driver_name}</span>
          </div>
          <div class="text-[10px] text-slate-500 font-mono">${leg.driver_id}</div>
        </td>
        <td class="py-3 px-3 text-center">${handoverBadge}</td>
        <td class="py-3 px-3 text-center font-mono font-bold ${leg.remaining_cargo_units === 0 ? 'text-slate-500' : 'text-sky-400'}">
          ${leg.remaining_cargo_units} cars
        </td>
      </tr>
    `;
  }).join('');
}

// Render Timeline / Gantt Chart
function renderGanttChart(res) {
  const container = document.getElementById('ganttChartContainer');
  if (!container) return;

  const totalMins = res.total_trip_duration_mins || 1;
  const legs = res.legs;

  // Render Hauler Row & Drivers Rows
  let html = `
    <div class="space-y-3">
      <!-- Hauler Trip Progression -->
      <div>
        <div class="flex items-center justify-between text-xs text-slate-400 mb-1">
          <span class="font-semibold text-slate-300 flex items-center space-x-1.5">
            <i class="fa-solid fa-truck text-sky-400"></i>
            <span>Hauler Complete Trip (${res.assigned_hauler_name})</span>
          </span>
          <span class="font-mono text-[11px]">${Math.floor(totalMins / 60)}h ${totalMins % 60}m Total</span>
        </div>
        <div class="h-8 bg-slate-900 border border-slate-800 rounded-lg flex overflow-hidden p-0.5">
  `;

  legs.forEach((leg, idx) => {
    const legPct = Math.max(12, Math.round((leg.travel_time_mins / totalMins) * 100));
    const isEven = idx % 2 === 0;
    const bg = isEven ? 'bg-sky-600/80 hover:bg-sky-500' : 'bg-indigo-600/80 hover:bg-indigo-500';

    html += `
      <div class="${bg} h-full rounded px-2 flex items-center justify-between text-[10px] text-white font-mono cursor-pointer transition mr-0.5"
           style="width: ${legPct}%" title="${leg.from_code} -> ${leg.to_code}: ${leg.travel_time_formatted}">
        <span class="truncate font-semibold">${leg.from_code}&rarr;${leg.to_code}</span>
        <span class="text-[9px] opacity-80">${leg.travel_time_formatted}</span>
      </div>
    `;
  });

  html += `</div></div>`;

  // Assigned Drivers Duty Rows
  res.drivers_assigned.forEach((d, idx) => {
    const dHours = d.total_duty_hours;
    const dPct = Math.round((d.total_duty_mins / totalMins) * 100);

    html += `
      <div>
        <div class="flex items-center justify-between text-xs text-slate-400 mb-1">
          <span class="font-semibold text-slate-300 flex items-center space-x-1.5">
            <i class="fa-solid fa-user-check text-emerald-400"></i>
            <span>Driver ${idx + 1}: ${d.driver.name}</span>
          </span>
          <span class="font-mono text-[11px] text-emerald-400 font-semibold">${dHours}h Duty (Within 11.0h limit)</span>
        </div>
        <div class="h-8 bg-slate-900 border border-slate-800 rounded-lg p-0.5 relative">
          <div class="h-full bg-emerald-600/70 border border-emerald-500/40 rounded flex items-center px-3 text-[11px] text-white font-mono"
               style="width: ${dPct}%">
            <span>Active Shift (${d.legs.join(', ')})</span>
          </div>
        </div>
      </div>
    `;
  });

  // If Handover occurred, add handover annotation
  const handoverLeg = legs.find(l => l.handover_at_dest);
  if (handoverLeg) {
    html += `
      <div class="p-3 bg-amber-500/10 border border-amber-500/20 rounded-lg flex items-center space-x-3 text-xs text-amber-300">
        <i class="fa-solid fa-handshake text-lg"></i>
        <div>
          <span class="font-semibold">Driver Handover Completed at ${handoverLeg.to_name} (${handoverLeg.to_code})</span>
          <p class="text-[11px] text-amber-400/80">45-minute mandatory buffer elapsed between Driver 1 offboarding and Driver 2 onboarding to ensure FMCSA duty continuity.</p>
        </div>
      </div>
    `;
  }

  html += `</div>`;
  container.innerHTML = html;
}

// Render Stop Circuit Diagram
function renderCircuitDiagram(res) {
  const container = document.getElementById('circuitFlowNodes');
  if (!container) return;

  const legs = res.legs;
  let nodesHtml = [];

  // Start Node
  nodesHtml.push(`
    <div class="flex flex-col items-center text-center p-3 bg-slate-950 border-2 border-sky-500 rounded-xl min-w-[140px] shadow-lg">
      <div class="w-8 h-8 rounded-full bg-sky-500/20 text-sky-400 flex items-center justify-center mb-1 text-xs">
        <i class="fa-solid fa-warehouse"></i>
      </div>
      <div class="text-xs font-bold text-white">${res.origin_vdc}</div>
      <div class="text-[10px] text-slate-400">Depot Start</div>
      <div class="text-[9px] font-mono text-emerald-400 mt-1">${legs[0].departure_from_origin}</div>
    </div>
  `);

  // Intermediate Dealership Nodes
  legs.forEach((leg, idx) => {
    const isReturn = idx === legs.length - 1;
    if (isReturn) return; // return node handled at end

    const isHandover = leg.handover_at_dest;
    const border = isHandover ? 'border-amber-500' : 'border-indigo-500';
    const bgIcon = isHandover ? 'bg-amber-500/20 text-amber-400' : 'bg-indigo-500/20 text-indigo-400';

    nodesHtml.push(`
      <div class="text-slate-600 text-lg hidden md:block">
        <i class="fa-solid fa-arrow-right"></i>
      </div>

      <div class="flex flex-col items-center text-center p-3 bg-slate-950 border-2 ${border} rounded-xl min-w-[150px] shadow-lg relative">
        ${isHandover ? '<span class="absolute -top-2.5 px-2 py-0.5 bg-amber-500 text-slate-950 text-[9px] font-extrabold uppercase rounded-full tracking-wider">Handover Hub</span>' : ''}
        <div class="w-8 h-8 rounded-full ${bgIcon} flex items-center justify-center mb-1 text-xs">
          <i class="fa-solid ${isHandover ? 'fa-handshake' : 'fa-building'}"></i>
        </div>
        <div class="text-xs font-bold text-white">${leg.to_code}</div>
        <div class="text-[10px] text-slate-400 truncate max-w-[120px]">${leg.to_name}</div>
        <div class="text-[9px] font-mono text-amber-300 mt-1">Arr: ${leg.arrival_at_dest}</div>
      </div>
    `);
  });

  // End Node (Return to Factory)
  const lastLeg = legs[legs.length - 1];
  nodesHtml.push(`
    <div class="text-slate-600 text-lg hidden md:block">
      <i class="fa-solid fa-arrow-right"></i>
    </div>

    <div class="flex flex-col items-center text-center p-3 bg-slate-950 border-2 border-emerald-500 rounded-xl min-w-[140px] shadow-lg">
      <div class="w-8 h-8 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center mb-1 text-xs">
        <i class="fa-solid fa-flag-checkered"></i>
      </div>
      <div class="text-xs font-bold text-white">${res.origin_vdc}</div>
      <div class="text-[10px] text-slate-400">Depot Return</div>
      <div class="text-[9px] font-mono text-emerald-400 mt-1">${lastLeg.arrival_at_dest}</div>
    </div>
  `);

  container.innerHTML = nodesHtml.join('');
}

// Tab Switching
function switchTab(tabId) {
  document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
  document.getElementById(tabId)?.classList.remove('hidden');

  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.classList.remove('active', 'border-sky-500', 'text-sky-400', 'bg-slate-800/40');
    btn.classList.add('border-transparent', 'text-slate-400');
  });

  event.currentTarget.classList.add('active', 'border-sky-500', 'text-sky-400', 'bg-slate-800/40');
  event.currentTarget.classList.remove('border-transparent', 'text-slate-400');
}

// Formulation Modal Handlers
function showFormulationModal() {
  document.getElementById('formulationModal')?.classList.remove('hidden');
}
function hideFormulationModal() {
  document.getElementById('formulationModal')?.classList.add('hidden');
}

// Export CSV
function exportCSV() {
  if (!currentLoadId) return;
  window.location.href = `/api/export/csv/${currentLoadId}`;
}

// Export JSON
function exportJSON() {
  if (!currentLoadId) return;
  window.open(`/api/export/json/${currentLoadId}`, '_blank');
}
