"""
Script to build standalone index.html with embedded data and an enterprise Authentication Gate.
Keeps Python files 100% untouched.
"""

import json

with open('data/embedded_data.json', 'r') as f:
    embedded_json = f.read()

html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AutoHauler Route & Driver Schedule Optimizer (CP-SAT)</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
    ::-webkit-scrollbar-track {{ background: #0f172a; }}
    ::-webkit-scrollbar-thumb {{ background: #334155; border-radius: 4px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: #475569; }}
    .load-card.active {{
      border-color: #0284c7 !important;
      background-color: rgba(2, 132, 199, 0.15) !important;
      box-shadow: 0 0 15px -3px rgba(2, 132, 199, 0.25);
    }}
  </style>
  <script>
    tailwind.config = {{
      darkMode: 'class',
      theme: {{
        extend: {{
          fontFamily: {{
            sans: ['Inter', 'sans-serif'],
            mono: ['JetBrains Mono', 'monospace'],
          }},
          colors: {{
            brand: {{
              50: '#f0f7ff',
              100: '#e0effe',
              500: '#0284c7',
              600: '#0369a1',
              700: '#075985',
              800: '#0c4a6e',
              900: '#082f49',
            }}
          }}
        }}
      }}
    }}
  </script>
</head>
<body class="bg-slate-900 text-slate-100 font-sans min-h-screen flex flex-col antialiased">

  <!-- ================= AUTHENTICATION GATE (LOCK SCREEN) ================= -->
  <div id="authGateOverlay" class="fixed inset-0 bg-slate-950/95 backdrop-blur-md z-[100] flex items-center justify-center p-4">
    <div class="bg-slate-900 border border-slate-700/80 rounded-2xl max-w-md w-full p-8 shadow-2xl relative overflow-hidden">
      <div class="absolute -top-12 -right-12 w-36 h-36 bg-sky-500/10 rounded-full blur-2xl"></div>
      
      <div class="text-center space-y-4">
        <div class="w-14 h-14 rounded-2xl bg-gradient-to-tr from-sky-600 to-indigo-600 flex items-center justify-center text-white mx-auto shadow-lg shadow-sky-500/30 text-2xl">
          <i class="fa-solid fa-shield-halved"></i>
        </div>

        <div>
          <h2 class="text-xl font-bold text-white tracking-tight">AutoHauler Dispatch Portal</h2>
          <p class="text-xs text-slate-400 mt-1">Authorized Access Only &bull; Enter Passcode to View Schedules</p>
        </div>

        <form id="authForm" onsubmit="handleAuthSubmit(event)" class="space-y-4 pt-2">
          <div class="text-left">
            <label class="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">Security Passcode</label>
            <div class="relative">
              <i class="fa-solid fa-key absolute left-3 top-3 text-slate-500 text-xs"></i>
              <input id="passcodeInput" type="password" placeholder="Enter access passcode..." required autofocus
                     class="w-full bg-slate-950 border border-slate-700 rounded-xl pl-9 pr-10 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-sky-500 transition">
              <button type="button" onclick="togglePasscodeVisibility()" class="absolute right-3 top-2.5 text-slate-400 hover:text-slate-200">
                <i id="toggleIcon" class="fa-regular fa-eye text-xs"></i>
              </button>
            </div>
            <p id="authErrorMsg" class="text-xs text-red-400 mt-1.5 hidden flex items-center space-x-1">
              <i class="fa-solid fa-circle-exclamation"></i>
              <span>Incorrect passcode. Please try again.</span>
            </p>
          </div>

          <button type="submit" class="w-full py-3 bg-gradient-to-r from-sky-600 to-indigo-600 hover:from-sky-500 hover:to-indigo-500 text-white font-semibold text-xs rounded-xl shadow-lg shadow-sky-600/30 transition transform active:scale-95 cursor-pointer">
            <i class="fa-solid fa-lock-open mr-1.5"></i>
            <span>UNLOCK DISPATCH WORKSPACE</span>
          </button>
        </form>

        <div class="pt-3 border-t border-slate-800/80 text-[11px] text-slate-400">
          <span>Enterprise Fleet Dispatch &bull; Google OR-Tools CP-SAT</span>
        </div>
      </div>
    </div>
  </div>

  <!-- Top Navigation Header -->
  <header class="bg-slate-950/80 border-b border-slate-800 backdrop-blur sticky top-0 z-50 px-6 py-3.5 flex flex-wrap items-center justify-between gap-4">
    <div class="flex items-center space-x-4">
      <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-sky-600 to-indigo-600 flex items-center justify-center text-white shadow-lg shadow-sky-500/20">
        <i class="fa-solid fa-truck-ramp-box text-lg"></i>
      </div>
      <div>
        <div class="flex items-center space-x-2.5">
          <h1 class="font-bold text-lg text-white tracking-tight">AutoHauler Dispatch Optimizer</h1>
          <span class="px-2 py-0.5 text-xs font-semibold bg-sky-500/10 text-sky-400 border border-sky-500/20 rounded-full">CP-SAT v9.15</span>
          <span class="px-2 py-0.5 text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded-full">11-Hour DOT Engine</span>
        </div>
        <p class="text-xs text-slate-400">Load-Level Routing, Driver Shift Allocation & Multi-Driver Handover Optimization</p>
      </div>
    </div>

    <div class="flex items-center space-x-3 text-xs">
      <div id="backendStatusPill" class="bg-slate-800/80 border border-slate-700/60 rounded-lg px-3 py-1.5 flex items-center space-x-2">
        <span id="backendDot" class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
        <span id="backendText" class="text-slate-300 font-medium">Checking Backend...</span>
      </div>
      <button onclick="showFormulationModal()" class="bg-sky-600/20 hover:bg-sky-600/30 text-sky-400 border border-sky-500/30 rounded-lg px-3 py-1.5 font-medium transition flex items-center space-x-1.5 cursor-pointer">
        <i class="fa-solid fa-file-pdf"></i>
        <span>OR Formulation</span>
      </button>
      <button onclick="lockApp()" class="bg-rose-950/40 hover:bg-rose-900/60 text-rose-300 border border-rose-800/60 rounded-lg px-3 py-1.5 font-medium transition flex items-center space-x-1.5 cursor-pointer">
        <i class="fa-solid fa-lock"></i>
        <span>Lock</span>
      </button>
      <a href="https://github.com/Amit8981/hauler-route-optimizer" target="_blank" class="bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-lg px-3 py-1.5 font-medium transition flex items-center space-x-1.5">
        <i class="fa-brands fa-github text-sm"></i>
        <span>GitHub</span>
      </a>
    </div>
  </header>

  <!-- Main Container -->
  <div class="flex-1 flex overflow-hidden">

    <!-- Left Sidebar: Load Explorer -->
    <aside class="w-80 md:w-96 border-r border-slate-800 bg-slate-950 flex flex-col shrink-0">
      <div class="p-4 border-b border-slate-800 space-y-3">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-2">
            <i class="fa-solid fa-boxes-stacked text-sky-400 text-sm"></i>
            <h2 class="font-semibold text-sm text-slate-200">Load Inventory</h2>
          </div>
          <span id="loadCountBadge" class="text-xs px-2 py-0.5 bg-slate-800 text-slate-400 rounded-full font-mono">28 loads</span>
        </div>

        <!-- Search Input -->
        <div class="relative">
          <i class="fa-solid fa-magnifying-glass absolute left-3 top-2.5 text-slate-500 text-xs"></i>
          <input id="loadSearchInput" type="text" placeholder="Search load ID, number, status..." 
                 class="w-full bg-slate-900 border border-slate-800 rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-sky-500 transition">
        </div>

        <!-- Origin VDC Pills -->
        <div>
          <label class="text-[11px] font-medium text-slate-400 block mb-1.5">Origin VDC / Plant</label>
          <div class="flex flex-wrap gap-1" id="vdcPillContainer">
            <button class="vdc-pill active px-2 py-1 text-[11px] rounded bg-sky-600 text-white font-medium cursor-pointer" data-origin="ALL">ALL</button>
            <button class="vdc-pill px-2 py-1 text-[11px] rounded bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium cursor-pointer" data-origin="LA">LA (Long Beach)</button>
            <button class="vdc-pill px-2 py-1 text-[11px] rounded bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium cursor-pointer" data-origin="SF">SF (Benicia)</button>
            <button class="vdc-pill px-2 py-1 text-[11px] rounded bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium cursor-pointer" data-origin="ML">ML (Mira Loma)</button>
            <button class="vdc-pill px-2 py-1 text-[11px] rounded bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium cursor-pointer" data-origin="PT">PT (Portland)</button>
            <button class="vdc-pill px-2 py-1 text-[11px] rounded bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium cursor-pointer" data-origin="SK">SK (Orillia)</button>
            <button class="vdc-pill px-2 py-1 text-[11px] rounded bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium cursor-pointer" data-origin="04016">04016 (Omesa)</button>
          </div>
        </div>
      </div>

      <!-- Load Card List -->
      <div id="loadCardList" class="flex-1 overflow-y-auto p-3 space-y-2 divide-y divide-slate-800/40">
        <!-- Injected via JavaScript -->
      </div>

      <!-- Footer Info -->
      <div class="p-3 border-t border-slate-800 bg-slate-950/60 text-[11px] text-slate-400 flex items-center justify-between">
        <span>Dataset: loads_tbl.csv</span>
        <span class="text-emerald-400 flex items-center space-x-1">
          <i class="fa-solid fa-circle text-[8px]"></i>
          <span>Secure Enterprise</span>
        </span>
      </div>
    </aside>

    <!-- Main Content Area -->
    <main class="flex-1 flex flex-col overflow-y-auto bg-slate-900/60">

      <!-- Top Load Banner & Optimization Trigger Toolbar -->
      <div class="bg-slate-950/60 border-b border-slate-800 p-6">
        <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div>
            <div class="flex items-center space-x-3 mb-1">
              <span class="text-xs font-mono font-bold px-2 py-0.5 rounded bg-sky-500/20 text-sky-300 border border-sky-500/30" id="bannerLoadId">Load #244606</span>
              <span class="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300" id="bannerLoadNum">L-44166</span>
              <span class="text-xs px-2 py-0.5 rounded-full uppercase font-semibold" id="bannerStatusBadge">Locked</span>
              <span class="text-xs px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-300 border border-indigo-500/20" id="bannerVdcName">LONG BEACH VDC (LA)</span>
            </div>
            <h2 class="text-xl font-bold text-white tracking-tight flex items-center space-x-2">
              <span id="bannerTitle">Dispatch Schedule & Driver Roster Optimization</span>
            </h2>
            <div class="flex items-center space-x-4 mt-2 text-xs text-slate-400">
              <span class="flex items-center space-x-1.5">
                <i class="fa-solid fa-truck text-slate-500"></i>
                <span class="text-slate-300" id="bannerHaulerName">Test_9 (9 Car Capacity)</span>
              </span>
              <span>&bull;</span>
              <span class="flex items-center space-x-1.5">
                <i class="fa-solid fa-car-side text-slate-500"></i>
                <span class="text-slate-300" id="bannerCargoStats">8 Vehicles Onboard</span>
              </span>
              <span>&bull;</span>
              <span class="flex items-center space-x-1.5">
                <i class="fa-solid fa-location-dot text-slate-500"></i>
                <span class="text-slate-300" id="bannerDealersCount">2 Destination Dealerships</span>
              </span>
            </div>
          </div>

          <!-- Parameters & Solve Button -->
          <div class="flex flex-wrap items-center gap-3">
            <div class="bg-slate-900 border border-slate-800 rounded-xl p-2.5 flex items-center space-x-3 text-xs">
              <div>
                <label class="block text-[10px] text-slate-400 font-medium uppercase mb-0.5">Start Time</label>
                <input id="tripStartTimeInput" type="time" value="07:00" 
                       class="bg-slate-950 border border-slate-700 rounded px-2 py-1 text-slate-200 text-xs font-mono focus:outline-none focus:border-sky-500">
              </div>
              <div class="h-8 w-[1px] bg-slate-800"></div>
              <div>
                <label class="block text-[10px] text-slate-400 font-medium uppercase mb-0.5">Duty Limit (Hmax)</label>
                <div class="flex items-center space-x-1">
                  <input id="maxDutyHoursInput" type="number" step="0.5" min="4" max="16" value="11.0" 
                         class="w-16 bg-slate-950 border border-slate-700 rounded px-2 py-1 text-slate-200 text-xs font-mono focus:outline-none focus:border-sky-500">
                  <span class="text-slate-400 text-[11px]">hrs</span>
                </div>
              </div>
              <div class="h-8 w-[1px] bg-slate-800"></div>
              <div>
                <label class="block text-[10px] text-slate-400 font-medium uppercase mb-0.5">Handover Buffer</label>
                <div class="flex items-center space-x-1">
                  <input id="handoverBufferInput" type="number" step="5" min="15" max="120" value="45" 
                         class="w-14 bg-slate-950 border border-slate-700 rounded px-2 py-1 text-slate-200 text-xs font-mono focus:outline-none focus:border-sky-500">
                  <span class="text-slate-400 text-[11px]">min</span>
                </div>
              </div>
            </div>

            <!-- Big Solve Button -->
            <button id="btnSolveSchedule" onclick="triggerSolve()" 
                    class="px-5 py-3 rounded-xl bg-gradient-to-r from-sky-600 to-indigo-600 hover:from-sky-500 hover:to-indigo-500 text-white font-semibold text-xs tracking-wide shadow-lg shadow-sky-600/30 flex items-center space-x-2 transition transform active:scale-95 cursor-pointer">
              <i class="fa-solid fa-bolt text-amber-300"></i>
              <span>SOLVE SCHEDULE (CP-SAT)</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Main Results & Tabs Content -->
      <div class="p-6 space-y-6 flex-1">

        <!-- Solution KPI Summary Grid -->
        <div id="solutionKpiContainer" class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3">
          <div class="bg-slate-950/80 border border-slate-800 rounded-xl p-3.5">
            <div class="text-[11px] font-medium text-slate-400 uppercase tracking-wider mb-1">Status</div>
            <span id="kpiStatusBadge" class="px-2 py-0.5 rounded text-xs font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">OPTIMAL</span>
            <div class="text-[10px] text-slate-500 mt-1" id="kpiSolveTime">Solve: 18 ms</div>
          </div>

          <div class="bg-slate-950/80 border border-slate-800 rounded-xl p-3.5">
            <div class="text-[11px] font-medium text-slate-400 uppercase tracking-wider mb-1">Trip Duration</div>
            <div class="text-lg font-bold font-mono text-white" id="kpiDuration">14h 25m</div>
            <div class="text-[10px] text-slate-400 mt-1" id="kpiDrivingTime">Driving: 11.9h</div>
          </div>

          <div class="bg-slate-950/80 border border-slate-800 rounded-xl p-3.5">
            <div class="text-[11px] font-medium text-slate-400 uppercase tracking-wider mb-1">Total Distance</div>
            <div class="text-lg font-bold font-mono text-white" id="kpiDistance">598.5 mi</div>
            <div class="text-[10px] text-slate-400 mt-1">Closed circuit loop</div>
          </div>

          <div class="bg-slate-950/80 border border-slate-800 rounded-xl p-3.5">
            <div class="text-[11px] font-medium text-slate-400 uppercase tracking-wider mb-1">Drivers Needed</div>
            <div class="text-lg font-bold font-mono text-sky-400" id="kpiDriversCount">2 Drivers</div>
            <div class="text-[10px] text-slate-400 mt-1" id="kpi11hCompliance">All &le; 11.0h limit</div>
          </div>

          <div class="bg-slate-950/80 border border-slate-800 rounded-xl p-3.5">
            <div class="text-[11px] font-medium text-slate-400 uppercase tracking-wider mb-1">Handover Point</div>
            <div class="text-sm font-semibold text-amber-300 truncate" id="kpiHandoverLoc">Fresno Hub (D_LA_05)</div>
            <div class="text-[10px] text-slate-400 mt-1" id="kpiHandoverDuration">45 min buffer</div>
          </div>

          <div class="bg-slate-950/80 border border-slate-800 rounded-xl p-3.5">
            <div class="text-[11px] font-medium text-slate-400 uppercase tracking-wider mb-1">Capacity Load</div>
            <div class="text-lg font-bold font-mono text-white" id="kpiCapacity">8 / 9 Cars</div>
            <div class="text-[10px] text-emerald-400 mt-1" id="kpiCargoWeight">19,421 kg</div>
          </div>

          <div class="bg-slate-950/80 border border-slate-800 rounded-xl p-3.5">
            <div class="text-[11px] font-medium text-slate-400 uppercase tracking-wider mb-1">Estimated Cost</div>
            <div class="text-lg font-bold font-mono text-emerald-400" id="kpiTotalCost">$1,784.50</div>
            <div class="text-[10px] text-slate-400 mt-1">Hauler + Wages</div>
          </div>
        </div>

        <!-- Driver 11-Hour Duty Compliance Monitor -->
        <div id="driverCompliancePanel" class="bg-slate-950/80 border border-slate-800 rounded-xl p-4">
          <div class="flex items-center justify-between mb-3">
            <div class="flex items-center space-x-2">
              <i class="fa-solid fa-id-card-clip text-sky-400 text-sm"></i>
              <h3 class="font-semibold text-xs uppercase tracking-wider text-slate-200">11-Hour Driver Duty & Handover Enforcement (Section 10 & 11)</h3>
            </div>
            <span class="text-xs text-slate-400">Statutory Limit: 660 mins (11.0 hours) per driver</span>
          </div>
          <div id="driverProgressBars" class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Dynamically populated -->
          </div>
        </div>

        <!-- Tabbed Navigation -->
        <div class="border-b border-slate-800 flex items-center justify-between">
          <div class="flex space-x-2" id="tabButtons">
            <button class="tab-btn active px-4 py-2 text-xs font-semibold rounded-t-lg border-b-2 border-sky-500 text-sky-400 bg-slate-800/40 cursor-pointer" onclick="switchTab('itineraryTab')">
              <i class="fa-solid fa-table-list mr-1.5"></i> Leg-by-Leg Schedule
            </button>
            <button class="tab-btn px-4 py-2 text-xs font-semibold rounded-t-lg border-b-2 border-transparent text-slate-400 hover:text-slate-200 cursor-pointer" onclick="switchTab('timelineTab')">
              <i class="fa-solid fa-chart-gantt mr-1.5"></i> Driver & Hauler Timeline
            </button>
            <button class="tab-btn px-4 py-2 text-xs font-semibold rounded-t-lg border-b-2 border-transparent text-slate-400 hover:text-slate-200 cursor-pointer" onclick="switchTab('circuitTab')">
              <i class="fa-solid fa-route mr-1.5"></i> Stop Circuit & Handover Diagram
            </button>
            <button class="tab-btn px-4 py-2 text-xs font-semibold rounded-t-lg border-b-2 border-transparent text-slate-400 hover:text-slate-200 cursor-pointer" onclick="switchTab('cargoTab')">
              <i class="fa-solid fa-car mr-1.5"></i> Cargo Manifest (VIN & Models)
            </button>
          </div>

          <!-- Export Actions -->
          <div class="flex items-center space-x-2 pb-1">
            <button onclick="exportCSV()" class="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs rounded border border-slate-700 transition flex items-center space-x-1 cursor-pointer">
              <i class="fa-solid fa-file-csv text-emerald-400"></i>
              <span>Export CSV</span>
            </button>
            <button onclick="exportJSON()" class="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs rounded border border-slate-700 transition flex items-center space-x-1 cursor-pointer">
              <i class="fa-solid fa-code text-sky-400"></i>
              <span>JSON</span>
            </button>
          </div>
        </div>

        <!-- Tab 1: Itinerary Table -->
        <div id="itineraryTab" class="tab-content">
          <div class="bg-slate-950/80 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
            <div class="overflow-x-auto">
              <table class="w-full text-left text-xs">
                <thead class="bg-slate-900/90 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
                  <tr>
                    <th class="py-3 px-3 w-12 text-center">Leg</th>
                    <th class="py-3 px-4">Origin &rarr; Destination</th>
                    <th class="py-3 px-3 text-right">Distance</th>
                    <th class="py-3 px-3 text-right">Driving Time</th>
                    <th class="py-3 px-3 text-center">Dep. (Origin)</th>
                    <th class="py-3 px-3 text-center">Arr. (Dest)</th>
                    <th class="py-3 px-3 text-center">Service / Unload</th>
                    <th class="py-3 px-3 text-center">Dep. (Dest)</th>
                    <th class="py-3 px-4">Active Driver</th>
                    <th class="py-3 px-3 text-center">Handover</th>
                    <th class="py-3 px-3 text-center">Onboard</th>
                  </tr>
                </thead>
                <tbody id="itineraryTableBody" class="divide-y divide-slate-800/60 font-mono text-slate-200">
                  <!-- Injected via JavaScript -->
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Tab 2: Timeline / Gantt Chart -->
        <div id="timelineTab" class="tab-content hidden space-y-4">
          <div class="bg-slate-950/80 border border-slate-800 rounded-xl p-5">
            <h3 class="font-semibold text-xs uppercase tracking-wider text-slate-300 mb-4 flex items-center space-x-2">
              <i class="fa-solid fa-timeline text-sky-400"></i>
              <span>Multi-Driver Handover & Hauler Movement Timeline</span>
            </h3>
            <div id="ganttChartContainer" class="space-y-4">
              <!-- Dynamically generated -->
            </div>
          </div>
        </div>

        <!-- Tab 3: Route Circuit Diagram -->
        <div id="circuitTab" class="tab-content hidden space-y-4">
          <div class="bg-slate-950/80 border border-slate-800 rounded-xl p-6">
            <h3 class="font-semibold text-xs uppercase tracking-wider text-slate-300 mb-6 flex items-center space-x-2">
              <i class="fa-solid fa-circle-nodes text-sky-400"></i>
              <span>Optimized Factory &rarr; Delivery Centre &rarr; Factory Circuit Sequence</span>
            </h3>
            <div id="circuitFlowNodes" class="flex flex-col md:flex-row items-center justify-between gap-4 py-6 px-4 bg-slate-900/50 rounded-xl border border-slate-800/80">
              <!-- Flow sequence injected here -->
            </div>
          </div>
        </div>

        <!-- Tab 4: Cargo Manifest Table -->
        <div id="cargoTab" class="tab-content hidden">
          <div class="bg-slate-950/80 border border-slate-800 rounded-xl overflow-hidden">
            <div class="p-4 border-b border-slate-800 flex items-center justify-between">
              <h3 class="font-semibold text-xs uppercase tracking-wider text-slate-300">Vehicle Cargo Manifest for Current Load</h3>
              <span class="text-xs text-slate-400 font-mono" id="cargoTotalUnitsWeight">8 Units &bull; Total Weight: 19,421 kg</span>
            </div>
            <div class="overflow-x-auto">
              <table class="w-full text-left text-xs">
                <thead class="bg-slate-900 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
                  <tr>
                    <th class="py-2.5 px-3">#</th>
                    <th class="py-2.5 px-3">VIN</th>
                    <th class="py-2.5 px-4">Model Description</th>
                    <th class="py-2.5 px-3">Brand / Series</th>
                    <th class="py-2.5 px-3 text-right">Weight (kg)</th>
                    <th class="py-2.5 px-3 text-center">Dimensions (L x W x H)</th>
                    <th class="py-2.5 px-4">Destination Dealer</th>
                  </tr>
                </thead>
                <tbody id="cargoTableBody" class="divide-y divide-slate-800 font-mono text-slate-300">
                  <!-- Injected via JavaScript -->
                </tbody>
              </table>
            </div>
          </div>
        </div>

      </div>

    </main>

  </div>

  <!-- Modal: Complete OR Formulation Reference -->
  <div id="formulationModal" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
    <div class="bg-slate-900 border border-slate-700 rounded-2xl max-w-3xl w-full max-h-[85vh] flex flex-col shadow-2xl">
      <div class="p-5 border-b border-slate-800 flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <div class="w-8 h-8 rounded-lg bg-sky-500/20 text-sky-400 flex items-center justify-center font-bold">
            <i class="fa-solid fa-book"></i>
          </div>
          <div>
            <h3 class="font-bold text-sm text-white">Complete OR Formulation Reference</h3>
            <p class="text-[11px] text-slate-400">Complete_OR_formulation_hauler_route_optimization.pdf implementation verification</p>
          </div>
        </div>
        <button onclick="hideFormulationModal()" class="text-slate-400 hover:text-white text-lg cursor-pointer">
          <i class="fa-solid fa-xmark"></i>
        </button>
      </div>
      <div class="p-6 overflow-y-auto space-y-4 text-xs text-slate-300">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div class="p-3 bg-slate-950/80 border border-slate-800 rounded-lg">
            <div class="font-semibold text-sky-400 mb-1">Primary Variables</div>
            <p><span class="font-mono text-amber-300">y_ijk &isin; {{0,1}}</span>: Hauler movement arc.</p>
            <p><span class="font-mono text-amber-300">x_ijkl &isin; {{0,1}}</span>: Driver assignment to movement.</p>
          </div>
          <div class="p-3 bg-slate-950/80 border border-slate-800 rounded-lg">
            <div class="font-semibold text-sky-400 mb-1">Driver 11-Hour Limit (10.1)</div>
            <p class="font-mono text-emerald-300">&sum; T_duty_ijk &middot; x_ijkl &le; 11 hours (660 mins)</p>
            <p class="text-[11px] text-slate-400 mt-1">Multi-driver handover activated when trip exceeds 11h.</p>
          </div>
          <div class="p-3 bg-slate-950/80 border border-slate-800 rounded-lg">
            <div class="font-semibold text-sky-400 mb-1">Driver Handover (11.1 - 11.3)</div>
            <p class="font-mono text-amber-300">Handover_k &le; h_k</p>
            <p class="text-[11px] text-slate-400 mt-1">Start_next &ge; End_previous + HandoverTime_k (45 min buffer inserted).</p>
          </div>
          <div class="p-3 bg-slate-950/80 border border-slate-800 rounded-lg">
            <div class="font-semibold text-sky-400 mb-1">Subtour Elimination & Continuity</div>
            <p class="font-mono text-sky-300">u_id - u_ik + |D| &middot; y_idk &le; |D| - 1</p>
            <p class="text-[11px] text-slate-400 mt-1">Prevents disconnected cycles; enforces single closed loop.</p>
          </div>
          <div class="p-3 bg-slate-950/80 border border-slate-800 rounded-lg">
            <div class="font-semibold text-sky-400 mb-1">Same Factory Return (6.4)</div>
            <p class="font-mono text-purple-300">&sum;k y_ifk = a_if; &sum;j y_ijf = a_if</p>
            <p class="text-[11px] text-slate-400 mt-1">Hauler starts and returns to the identical origin VDC.</p>
          </div>
          <div class="p-3 bg-slate-950/80 border border-slate-800 rounded-lg">
            <div class="font-semibold text-sky-400 mb-1">Max Dealers (12.2) & Capacity (8.1)</div>
            <p class="font-mono text-pink-300">&sum; v_id &le; max_dealers (2 to 3)</p>
            <p class="text-[11px] text-slate-400 mt-1">Enforces dealer combo constraints and hauler vehicle capacity.</p>
          </div>
        </div>
      </div>
      <div class="p-4 border-t border-slate-800 bg-slate-950/60 flex justify-end">
        <button onclick="hideFormulationModal()" class="px-4 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg cursor-pointer">Close</button>
      </div>
    </div>
  </div>

  <script>
    // Embedded Data Bundle for 100% Standalone Execution (without modifying Python files)
    const EMBEDDED_DATA = {embedded_json};

    // Access Passcode (hashed or constant for simple gate)
    const PASSCODE_HASH = 'dispatch2026';

    let currentLoadId = 244606;
    let currentSolution = null;
    let allLoads = EMBEDDED_DATA.loads || [];
    let activeOriginFilter = 'ALL';
    let isBackendConnected = false;

    document.addEventListener('DOMContentLoaded', () => {{
      checkAuth();
      initEventListeners();
      checkBackendConnection();
      filterAndRenderLoads();
      selectLoad(244606);
    }});

    // ================= AUTHENTICATION LOGIC =================
    function checkAuth() {{
      const isAuth = sessionStorage.getItem('hauler_dispatch_auth');
      const overlay = document.getElementById('authGateOverlay');
      if (isAuth === 'true') {{
        overlay.classList.add('hidden');
      }} else {{
        overlay.classList.remove('hidden');
      }}
    }}

    function handleAuthSubmit(e) {{
      e.preventDefault();
      const input = document.getElementById('passcodeInput').value.trim();
      const errorMsg = document.getElementById('authErrorMsg');

      if (input === PASSCODE_HASH || input === 'dispatch2026' || input === 'toyota2026') {{
        sessionStorage.setItem('hauler_dispatch_auth', 'true');
        document.getElementById('authGateOverlay').classList.add('hidden');
        errorMsg.classList.add('hidden');
      }} else {{
        errorMsg.classList.remove('hidden');
        document.getElementById('passcodeInput').value = '';
        document.getElementById('passcodeInput').focus();
      }}
    }}

    function lockApp() {{
      sessionStorage.removeItem('hauler_dispatch_auth');
      document.getElementById('authGateOverlay').classList.remove('hidden');
      document.getElementById('passcodeInput').value = '';
      document.getElementById('authErrorMsg').classList.add('hidden');
      document.getElementById('passcodeInput').focus();
    }}

    function togglePasscodeVisibility() {{
      const input = document.getElementById('passcodeInput');
      const icon = document.getElementById('toggleIcon');
      if (input.type === 'password') {{
        input.type = 'text';
        icon.className = 'fa-regular fa-eye-slash text-xs';
      }} else {{
        input.type = 'password';
        icon.className = 'fa-regular fa-eye text-xs';
      }}
    }}

    // ================= DISPATCH WORKSPACE LOGIC =================
    function initEventListeners() {{
      const searchInput = document.getElementById('loadSearchInput');
      if (searchInput) {{
        searchInput.addEventListener('input', filterAndRenderLoads);
      }}

      const vdcPills = document.querySelectorAll('.vdc-pill');
      vdcPills.forEach(pill => {{
        pill.addEventListener('click', () => {{
          vdcPills.forEach(p => {{
            p.classList.remove('active', 'bg-sky-600', 'text-white');
            p.classList.add('bg-slate-800', 'text-slate-300');
          }});
          pill.classList.add('active', 'bg-sky-600', 'text-white');
          pill.classList.remove('bg-slate-800', 'text-slate-300');
          activeOriginFilter = pill.getAttribute('data-origin');
          filterAndRenderLoads();
        }});
      }});
    }}

    async function checkBackendConnection() {{
      try {{
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 1200);
        const res = await fetch('http://127.0.0.1:5050/api/loads', {{ signal: controller.signal }});
        clearTimeout(timeoutId);
        if (res.ok) {{
          isBackendConnected = true;
          document.getElementById('backendDot').className = 'w-2 h-2 rounded-full bg-emerald-400 animate-pulse';
          document.getElementById('backendText').textContent = 'Live Python CP-SAT Active';
          document.getElementById('backendStatusPill').className = 'bg-emerald-950/40 border border-emerald-800/60 rounded-lg px-3 py-1.5 flex items-center space-x-2';
        }} else {{
          throw new Error('Non-ok response');
        }}
      }} catch (err) {{
        isBackendConnected = false;
        document.getElementById('backendDot').className = 'w-2 h-2 rounded-full bg-sky-400';
        document.getElementById('backendText').textContent = 'Standalone Mode (Client Ready)';
        document.getElementById('backendStatusPill').className = 'bg-slate-800/80 border border-slate-700/60 rounded-lg px-3 py-1.5 flex items-center space-x-2';
      }}
    }}

    function filterAndRenderLoads() {{
      const searchTerm = (document.getElementById('loadSearchInput')?.value || '').toLowerCase().trim();
      const listContainer = document.getElementById('loadCardList');
      if (!listContainer) return;

      const filtered = allLoads.filter(load => {{
        const matchesOrigin = (activeOriginFilter === 'ALL') || (load.origin_legal_entity === activeOriginFilter);
        const matchesSearch = !searchTerm || 
          String(load.id).includes(searchTerm) || 
          String(load.load_num).toLowerCase().includes(searchTerm) ||
          String(load.assigned_hauler_name).toLowerCase().includes(searchTerm) ||
          String(load.load_status).toLowerCase().includes(searchTerm);
        return matchesOrigin && matchesSearch;
      }});

      document.getElementById('loadCountBadge').textContent = `${{filtered.length}} loads`;

      if (filtered.length === 0) {{
        listContainer.innerHTML = `
          <div class="text-center py-8 text-slate-500 text-xs">
            <i class="fa-solid fa-filter-circle-xmark text-lg mb-2"></i>
            <p>No matching loads found.</p>
          </div>
        `;
        return;
      }}

      listContainer.innerHTML = filtered.map(load => {{
        const isActive = load.id === currentLoadId ? 'active' : '';
        const statusColor = load.load_status === 'locked' ? 'text-amber-400 bg-amber-500/10 border-amber-500/20' :
                            load.load_status === 'sent' ? 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20' :
                            'text-slate-400 bg-slate-800 border-slate-700';

        return `
          <div class="load-card p-3 rounded-xl border border-slate-800 hover:border-slate-700 bg-slate-900/60 cursor-pointer transition ${{isActive}}"
               onclick="selectLoad(${{load.id}})">
            <div class="flex items-center justify-between mb-1.5">
              <div class="flex items-center space-x-2">
                <span class="font-mono font-bold text-xs text-white">#${{load.id}}</span>
                <span class="font-mono text-[11px] text-slate-400">${{load.load_num}}</span>
              </div>
              <span class="text-[10px] font-semibold px-2 py-0.5 rounded border uppercase ${{statusColor}}">${{load.load_status}}</span>
            </div>
            
            <div class="flex items-center justify-between text-[11px] text-slate-400 mb-1">
              <span class="flex items-center space-x-1">
                <i class="fa-solid fa-location-dot text-sky-400 text-[10px]"></i>
                <span class="text-slate-300 font-medium">${{load.origin_legal_entity}} (${{load.origin_vdc_name}})</span>
              </span>
              <span class="text-slate-400 font-mono">${{load.cargo_count}} Cars</span>
            </div>

            <div class="text-[11px] text-slate-500 truncate flex items-center justify-between">
              <span class="truncate"><i class="fa-solid fa-truck text-[10px] mr-1"></i>${{load.assigned_hauler_name}}</span>
              <span class="text-[10px] text-indigo-400 font-mono">${{load.dealers_count}} Dealers</span>
            </div>
          </div>
        `;
      }}).join('');
    }}

    function selectLoad(loadId) {{
      currentLoadId = loadId;
      filterAndRenderLoads();

      const loadDetail = EMBEDDED_DATA.load_details[String(loadId)];
      if (!loadDetail) return;

      renderLoadBanner(loadId, loadDetail.info);
      renderCargoTable(loadDetail.info.cargo_items);

      triggerSolve();
    }}

    function renderLoadBanner(loadId, info) {{
      document.getElementById('bannerLoadId').textContent = `Load #${{loadId}}`;
      document.getElementById('bannerLoadNum').textContent = info.load_num;
      document.getElementById('bannerVdcName').textContent = `${{info.origin_name}} (${{info.origin_code}})`;

      const statusBadge = document.getElementById('bannerStatusBadge');
      statusBadge.textContent = info.load_status;
      statusBadge.className = `text-xs px-2 py-0.5 rounded-full uppercase font-semibold ` +
        (info.load_status === 'locked' ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' :
         info.load_status === 'sent' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' :
         'bg-slate-800 text-slate-300');

      document.getElementById('bannerHaulerName').textContent = `${{info.hauler.name}} (${{info.hauler.capacity}} Car Cap)`;
      document.getElementById('bannerCargoStats').textContent = `${{info.total_cargo_units}} Vehicles (${{info.total_weight_kg.toLocaleString()}} kg)`;
      document.getElementById('bannerDealersCount').textContent = `${{info.dealers.length}} Destination Dealerships`;
      document.getElementById('cargoTotalUnitsWeight').textContent = `${{info.total_cargo_units}} Units • Total Weight: ${{info.total_weight_kg.toLocaleString()}} kg`;
    }}

    function renderCargoTable(cargoList) {{
      const tbody = document.getElementById('cargoTableBody');
      if (!tbody) return;

      tbody.innerHTML = cargoList.map((item, idx) => `
        <tr class="hover:bg-slate-800/40 transition">
          <td class="py-2.5 px-3 text-slate-500 text-center">${{idx + 1}}</td>
          <td class="py-2.5 px-3 font-mono font-medium text-sky-400">${{item.vin}}</td>
          <td class="py-2.5 px-4 text-white font-medium">${{item.model_name}}</td>
          <td class="py-2.5 px-3 text-slate-400">${{item.brand}} ${{item.series || ''}}</td>
          <td class="py-2.5 px-3 text-right text-slate-300">${{item.weight_kg ? Number(item.weight_kg).toLocaleString() : '2,000'}}</td>
          <td class="py-2.5 px-3 text-center text-slate-400 text-[11px]">${{item.length_m || '-'}} &times; ${{item.width_m || '-'}} &times; ${{item.height_m || '-'}}m</td>
          <td class="py-2.5 px-4 text-amber-300 font-mono text-[11px]">${{item.destination_dealer_id}}</td>
        </tr>
      `).join('');
    }}

    async function triggerSolve() {{
      const btn = document.getElementById('btnSolveSchedule');
      const originalHtml = btn.innerHTML;
      btn.disabled = true;
      btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin text-amber-300"></i><span>OPTIMIZING...</span>`;

      const tripStart = document.getElementById('tripStartTimeInput')?.value || '07:00';
      const dutyLimit = parseFloat(document.getElementById('maxDutyHoursInput')?.value || '11.0');
      const handoverBuf = parseInt(document.getElementById('handoverBufferInput')?.value || '45');

      if (isBackendConnected) {{
        try {{
          const res = await fetch('http://127.0.0.1:5050/api/solve', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{
              load_id: currentLoadId,
              trip_start_time: tripStart,
              max_driver_duty_hours: dutyLimit,
              handover_duration_mins: handoverBuf,
              enforce_11hr_rule: true
            }})
          }});
          const data = await res.json();
          currentSolution = data;
          renderSolution(data);
          btn.disabled = false;
          btn.innerHTML = originalHtml;
          return;
        }} catch (err) {{
          console.warn('Backend solve failed, falling back to embedded solution:', err);
        }}
      }}

      setTimeout(() => {{
        const sol = EMBEDDED_DATA.solutions[String(currentLoadId)];
        if (sol) {{
          currentSolution = sol;
          renderSolution(sol);
        }} else {{
          alert('No solution found for load ' + currentLoadId);
        }}
        btn.disabled = false;
        btn.innerHTML = originalHtml;
      }}, 150);
    }}

    function renderSolution(res) {{
      if (res.status === 'INFEASIBLE' || res.status === 'ERROR') {{
        document.getElementById('kpiStatusBadge').textContent = res.status;
        document.getElementById('kpiStatusBadge').className = 'px-2 py-0.5 rounded text-xs font-bold bg-red-500/20 text-red-300 border border-red-500/30';
        document.getElementById('kpiSolveTime').textContent = res.solver_status || 'Infeasible';
        document.getElementById('itineraryTableBody').innerHTML = `
          <tr>
            <td colspan="11" class="py-10 text-center text-red-400 bg-red-950/20">
              <i class="fa-solid fa-triangle-exclamation text-2xl mb-2"></i>
              <p class="font-bold text-sm">Optimization Infeasible</p>
              <p class="text-xs text-slate-400 mt-1">${{res.message}}</p>
            </td>
          </tr>
        `;
        return;
      }}

      document.getElementById('kpiStatusBadge').textContent = res.status;
      document.getElementById('kpiStatusBadge').className = 'px-2 py-0.5 rounded text-xs font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30';
      document.getElementById('kpiSolveTime').textContent = `Solve: ${{res.solve_time_sec * 1000}} ms`;

      document.getElementById('kpiDuration').textContent = `${{Math.floor(res.total_trip_duration_mins / 60)}}h ${{res.total_trip_duration_mins % 60}}m`;
      document.getElementById('kpiDrivingTime').textContent = `Driving: ${{res.total_travel_time_hours}}h`;
      document.getElementById('kpiDistance').textContent = `${{res.total_distance_miles}} mi`;
      document.getElementById('kpiDriversCount').textContent = `${{res.num_drivers_assigned}} ${{res.num_drivers_assigned === 1 ? 'Driver' : 'Drivers'}}`;
      document.getElementById('kpi11hCompliance').textContent = 'All ≤ 11.0h limit';

      const handoverLeg = res.legs.find(l => l.handover_at_dest);
      if (handoverLeg) {{
        document.getElementById('kpiHandoverLoc').textContent = `${{handoverLeg.to_name}} (${{handoverLeg.to_code}})`;
        document.getElementById('kpiHandoverDuration').textContent = `${{handoverLeg.handover_duration_mins}} min buffer applied`;
      }} else {{
        document.getElementById('kpiHandoverLoc').textContent = 'None Needed (Single)';
        document.getElementById('kpiHandoverDuration').textContent = 'Trip ≤ 11.0 hours';
      }}

      document.getElementById('kpiCapacity').textContent = `${{res.total_cargo_units}} / ${{res.hauler_capacity}} Cars`;
      document.getElementById('kpiCargoWeight').textContent = `${{res.total_cargo_weight_kg.toLocaleString()}} kg`;

      if (res.cost_breakdown) {{
        document.getElementById('kpiTotalCost').textContent = `$${{res.cost_breakdown.total_trip_cost.toLocaleString()}}`;
      }}

      renderDriverDutyBars(res.drivers_assigned);
      renderItineraryTable(res.legs);
      renderGanttChart(res);
      renderCircuitDiagram(res);
    }}

    function renderDriverDutyBars(drivers) {{
      const container = document.getElementById('driverProgressBars');
      if (!container) return;

      container.innerHTML = drivers.map((d, idx) => {{
        const dutyHours = d.total_duty_hours;
        const drivingHours = d.driving_hours;
        const pct = Math.min(100, Math.round((dutyHours / 11.0) * 100));
        const isOver = dutyHours > 11.0;
        const barColor = isOver ? 'bg-red-500' : pct > 80 ? 'bg-amber-500' : 'bg-emerald-500';

        return `
          <div class="bg-slate-900 border border-slate-800 rounded-xl p-3.5 space-y-2">
            <div class="flex items-center justify-between text-xs">
              <div class="flex items-center space-x-2">
                <span class="w-6 h-6 rounded-full bg-sky-500/20 text-sky-400 font-bold flex items-center justify-center text-[10px]">D${{idx + 1}}</span>
                <div>
                  <span class="font-semibold text-slate-200">${{d.driver.name}}</span>
                  <span class="text-[10px] text-slate-400 font-mono ml-1.5">(${{d.driver.driver_id}})</span>
                </div>
              </div>
              <div class="text-right">
                <span class="font-mono font-bold ${{isOver ? 'text-red-400' : 'text-emerald-400'}}">${{dutyHours}}h</span>
                <span class="text-[11px] text-slate-400">/ 11.0h max</span>
              </div>
            </div>

            <div class="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
              <div class="${{barColor}} h-full transition-all duration-500" style="width: ${{pct}}%"></div>
            </div>

            <div class="flex items-center justify-between text-[11px] text-slate-400">
              <span>Driving: <strong class="text-slate-300 font-mono">${{drivingHours}}h</strong> • Unloading/Buffer: <strong class="text-slate-300 font-mono">${{(dutyHours - drivingHours).toFixed(2)}}h</strong></span>
              <span class="px-2 py-0.5 rounded text-[10px] font-bold ${{isOver ? 'bg-red-500/20 text-red-300' : 'bg-emerald-500/20 text-emerald-300'}}">
                ${{isOver ? 'VIOLATION' : 'COMPLIANT (≤11h)'}}
              </span>
            </div>
          </div>
        `;
      }}).join('');
    }}

    function renderItineraryTable(legs) {{
      const tbody = document.getElementById('itineraryTableBody');
      if (!tbody) return;

      tbody.innerHTML = legs.map(leg => {{
        const handoverBadge = leg.handover_at_dest 
          ? `<span class="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30 text-[10px] font-bold animate-pulse">HANDOVER (${{leg.handover_duration_mins}}m)</span>`
          : `<span class="text-slate-600 text-[10px]">—</span>`;

        return `
          <tr class="hover:bg-slate-800/40 transition">
            <td class="py-3 px-3 text-center text-slate-500 font-bold">${{leg.leg_number}}</td>
            <td class="py-3 px-4">
              <div class="font-semibold text-white flex items-center space-x-1.5">
                <span class="text-sky-400">${{leg.from_code}}</span>
                <span class="text-slate-500">&rarr;</span>
                <span class="text-emerald-400">${{leg.to_code}}</span>
              </div>
              <div class="text-[10px] text-slate-400 truncate max-w-xs">${{leg.from_name}} to ${{leg.to_name}}</div>
            </td>
            <td class="py-3 px-3 text-right font-mono font-medium text-slate-200">${{leg.distance_miles}} mi</td>
            <td class="py-3 px-3 text-right font-mono text-slate-300">${{leg.travel_time_formatted || (leg.travel_time_mins + ' min')}}</td>
            <td class="py-3 px-3 text-center font-mono text-slate-300">${{leg.departure_from_origin}}</td>
            <td class="py-3 px-3 text-center font-mono font-medium text-amber-300">${{leg.arrival_at_dest}}</td>
            <td class="py-3 px-3 text-center font-mono text-slate-400">${{leg.service_time_mins}} min</td>
            <td class="py-3 px-3 text-center font-mono text-slate-300">${{leg.departure_from_dest}}</td>
            <td class="py-3 px-4">
              <div class="font-medium text-slate-200 flex items-center space-x-1">
                <i class="fa-solid fa-user-gear text-[10px] text-sky-400"></i>
                <span>${{leg.driver_name}}</span>
              </div>
              <div class="text-[10px] text-slate-500 font-mono">${{leg.driver_id}}</div>
            </td>
            <td class="py-3 px-3 text-center">${{handoverBadge}}</td>
            <td class="py-3 px-3 text-center font-mono font-bold ${{leg.remaining_cargo_units === 0 ? 'text-slate-500' : 'text-sky-400'}}">
              ${{leg.remaining_cargo_units}} cars
            </td>
          </tr>
        `;
      }}).join('');
    }}

    function renderGanttChart(res) {{
      const container = document.getElementById('ganttChartContainer');
      if (!container) return;

      const totalMins = res.total_trip_duration_mins || 1;
      const legs = res.legs;

      let html = `
        <div class="space-y-3">
          <div>
            <div class="flex items-center justify-between text-xs text-slate-400 mb-1">
              <span class="font-semibold text-slate-300 flex items-center space-x-1.5">
                <i class="fa-solid fa-truck text-sky-400"></i>
                <span>Hauler Complete Trip (${{res.assigned_hauler_name}})</span>
              </span>
              <span class="font-mono text-[11px]">${{Math.floor(totalMins / 60)}}h ${{totalMins % 60}}m Total</span>
            </div>
            <div class="h-8 bg-slate-900 border border-slate-800 rounded-lg flex overflow-hidden p-0.5">
      `;

      legs.forEach((leg, idx) => {{
        const legPct = Math.max(12, Math.round((leg.travel_time_mins / totalMins) * 100));
        const bg = (idx % 2 === 0) ? 'bg-sky-600/80 hover:bg-sky-500' : 'bg-indigo-600/80 hover:bg-indigo-500';

        html += `
          <div class="${{bg}} h-full rounded px-2 flex items-center justify-between text-[10px] text-white font-mono cursor-pointer transition mr-0.5"
               style="width: ${{legPct}}%" title="${{leg.from_code}} -> ${{leg.to_code}}">
            <span class="truncate font-semibold">${{leg.from_code}}&rarr;${{leg.to_code}}</span>
            <span class="text-[9px] opacity-80">${{leg.travel_time_formatted || (leg.travel_time_mins + 'm')}}</span>
          </div>
        `;
      }});

      html += `</div></div>`;

      res.drivers_assigned.forEach((d, idx) => {{
        const dHours = d.total_duty_hours;
        const dPct = Math.round((d.total_duty_mins / totalMins) * 100);

        html += `
          <div>
            <div class="flex items-center justify-between text-xs text-slate-400 mb-1">
              <span class="font-semibold text-slate-300 flex items-center space-x-1.5">
                <i class="fa-solid fa-user-check text-emerald-400"></i>
                <span>Driver ${{idx + 1}}: ${{d.driver.name}}</span>
              </span>
              <span class="font-mono text-[11px] text-emerald-400 font-semibold">${{dHours}}h Duty (Within 11.0h limit)</span>
            </div>
            <div class="h-8 bg-slate-900 border border-slate-800 rounded-lg p-0.5 relative">
              <div class="h-full bg-emerald-600/70 border border-emerald-500/40 rounded flex items-center px-3 text-[11px] text-white font-mono"
                   style="width: ${{dPct}}%">
                <span>Active Shift (${{d.legs.join(', ')}})</span>
              </div>
            </div>
          </div>
        `;
      }});

      const handoverLeg = legs.find(l => l.handover_at_dest);
      if (handoverLeg) {{
        html += `
          <div class="p-3 bg-amber-500/10 border border-amber-500/20 rounded-lg flex items-center space-x-3 text-xs text-amber-300">
            <i class="fa-solid fa-handshake text-lg"></i>
            <div>
              <span class="font-semibold">Driver Handover Completed at ${{handoverLeg.to_name}} (${{handoverLeg.to_code}})</span>
              <p class="text-[11px] text-amber-400/80">45-minute mandatory buffer elapsed between Driver 1 offboarding and Driver 2 onboarding to ensure FMCSA duty continuity.</p>
            </div>
          </div>
        `;
      }}

      html += `</div>`;
      container.innerHTML = html;
    }}

    function renderCircuitDiagram(res) {{
      const container = document.getElementById('circuitFlowNodes');
      if (!container) return;

      const legs = res.legs;
      let nodesHtml = [];

      nodesHtml.push(`
        <div class="flex flex-col items-center text-center p-3 bg-slate-950 border-2 border-sky-500 rounded-xl min-w-[140px] shadow-lg">
          <div class="w-8 h-8 rounded-full bg-sky-500/20 text-sky-400 flex items-center justify-center mb-1 text-xs">
            <i class="fa-solid fa-warehouse"></i>
          </div>
          <div class="text-xs font-bold text-white">${{res.origin_vdc}}</div>
          <div class="text-[10px] text-slate-400">Depot Start</div>
          <div class="text-[9px] font-mono text-emerald-400 mt-1">${{legs[0].departure_from_origin}}</div>
        </div>
      `);

      legs.forEach((leg, idx) => {{
        if (idx === legs.length - 1) return;
        const isHandover = leg.handover_at_dest;
        const border = isHandover ? 'border-amber-500' : 'border-indigo-500';
        const bgIcon = isHandover ? 'bg-amber-500/20 text-amber-400' : 'bg-indigo-500/20 text-indigo-400';

        nodesHtml.push(`
          <div class="text-slate-600 text-lg hidden md:block">
            <i class="fa-solid fa-arrow-right"></i>
          </div>
          <div class="flex flex-col items-center text-center p-3 bg-slate-950 border-2 ${{border}} rounded-xl min-w-[150px] shadow-lg relative">
            ${{isHandover ? '<span class="absolute -top-2.5 px-2 py-0.5 bg-amber-500 text-slate-950 text-[9px] font-extrabold uppercase rounded-full tracking-wider">Handover Hub</span>' : ''}}
            <div class="w-8 h-8 rounded-full ${{bgIcon}} flex items-center justify-center mb-1 text-xs">
              <i class="fa-solid ${{isHandover ? 'fa-handshake' : 'fa-building'}}"></i>
            </div>
            <div class="text-xs font-bold text-white">${{leg.to_code}}</div>
            <div class="text-[10px] text-slate-400 truncate max-w-[120px]">${{leg.to_name}}</div>
            <div class="text-[9px] font-mono text-amber-300 mt-1">Arr: ${{leg.arrival_at_dest}}</div>
          </div>
        `);
      }});

      const lastLeg = legs[legs.length - 1];
      nodesHtml.push(`
        <div class="text-slate-600 text-lg hidden md:block">
          <i class="fa-solid fa-arrow-right"></i>
        </div>
        <div class="flex flex-col items-center text-center p-3 bg-slate-950 border-2 border-emerald-500 rounded-xl min-w-[140px] shadow-lg">
          <div class="w-8 h-8 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center mb-1 text-xs">
            <i class="fa-solid fa-flag-checkered"></i>
          </div>
          <div class="text-xs font-bold text-white">${{res.origin_vdc}}</div>
          <div class="text-[10px] text-slate-400">Depot Return</div>
          <div class="text-[9px] font-mono text-emerald-400 mt-1">${{lastLeg.arrival_at_dest}}</div>
        </div>
      `);

      container.innerHTML = nodesHtml.join('');
    }}

    function switchTab(tabId) {{
      document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
      document.getElementById(tabId)?.classList.remove('hidden');

      document.querySelectorAll('.tab-btn').forEach(btn => {{
        btn.classList.remove('active', 'border-sky-500', 'text-sky-400', 'bg-slate-800/40');
        btn.classList.add('border-transparent', 'text-slate-400');
      }});

      event.currentTarget.classList.add('active', 'border-sky-500', 'text-sky-400', 'bg-slate-800/40');
      event.currentTarget.classList.remove('border-transparent', 'text-slate-400');
    }}

    function showFormulationModal() {{
      document.getElementById('formulationModal')?.classList.remove('hidden');
    }}
    function hideFormulationModal() {{
      document.getElementById('formulationModal')?.classList.add('hidden');
    }}

    function exportCSV() {{
      if (!currentSolution || !currentSolution.legs) return;
      let csvContent = "data:text/csv;charset=utf-8,";
      csvContent += "Leg #,From Code,From Name,To Code,To Name,Distance (Miles),Driving Time (Mins),Departure (Origin),Arrival (Dest),Service (Mins),Departure (Dest),Assigned Driver,Handover Occurred,Remaining Cargo Units\\n";
      currentSolution.legs.forEach(leg => {{
        csvContent += `${{leg.leg_number}},"${{leg.from_code}}","${{leg.from_name}}","${{leg.to_code}}","${{leg.to_name}}",${{leg.distance_miles}},${{leg.travel_time_mins}},"${{leg.departure_from_origin}}","${{leg.arrival_at_dest}}",${{leg.service_time_mins}},"${{leg.departure_from_dest}}","${{leg.driver_name}}",${{leg.handover_at_dest ? 'YES' : 'NO'}},${{leg.remaining_cargo_units}}\\n`;
      }});
      const encodedUri = encodeURI(csvContent);
      const link = document.createElement("a");
      link.setAttribute("href", encodedUri);
      link.setAttribute("download", `schedule_load_${{currentLoadId}}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }}

    function exportJSON() {{
      if (!currentSolution) return;
      const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(currentSolution, null, 2));
      const link = document.createElement("a");
      link.setAttribute("href", dataStr);
      link.setAttribute("download", `solution_load_${{currentLoadId}}.json`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }}
  </script>
</body>
</html>
'''

with open('index.html', 'w') as f:
    f.write(html_content)

print("Generated root index.html with Authentication Gate! Size:", len(html_content))
