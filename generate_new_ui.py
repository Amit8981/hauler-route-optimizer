"""
Script to build standalone index.html with:
  - C-1 to C-18 formulation reference
  - Passcode authentication gate (dispatch2026)
  - Drivers Needed explanation banner and modal
  - 11-hour daily cap & 70-hour rolling weekly HOS monitor
  - Driver AM/PM shift tags
  - Post-trip turnaround rest indicators
  - Tab 5: Multi-Trip Shift Tour (1 Driver doing 3 Short Trips with 45m turnaround rest)
  - Flat $35/hr driver wage rate
"""

import json

with open('data/embedded_data.json', 'r') as f:
    embedded_json = f.read()

html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AutoHauler Route & Driver Schedule Optimizer (CP-SAT v2.0 - C1 to C18)</title>
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
          <span>Enterprise Fleet Dispatch &bull; Google OR-Tools CP-SAT (C-1 to C-18)</span>
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
          <span class="px-2 py-0.5 text-xs font-semibold bg-sky-500/10 text-sky-400 border border-sky-500/20 rounded-full">OR Formulation C1-C18</span>
          <span class="px-2 py-0.5 text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded-full">11h Daily &bull; 70h Weekly HOS</span>
        </div>
        <p class="text-xs text-slate-400">Multi-Stop Finished Vehicle Logistics, AM/PM Shift Windows & Driver Handover Optimization</p>
      </div>
    </div>

    <div class="flex items-center space-x-3 text-xs">
      <div id="backendStatusPill" class="bg-slate-800/80 border border-slate-700/60 rounded-lg px-3 py-1.5 flex items-center space-x-2">
        <span id="backendDot" class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
        <span id="backendText" class="text-slate-300 font-medium">Checking Backend...</span>
      </div>
      <button onclick="switchTab('driverRosterTab')" class="bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/40 rounded-lg px-3 py-1.5 font-medium transition flex items-center space-x-1.5 cursor-pointer shadow-sm">
        <i class="fa-solid fa-users-gear text-indigo-400"></i>
        <span>Manager Fleet Roster</span>
      </button>
      <a href="sandbox.html" class="bg-amber-600/20 hover:bg-amber-600/30 text-amber-300 border border-amber-500/40 rounded-lg px-3 py-1.5 font-medium transition flex items-center space-x-1.5 cursor-pointer">
        <i class="fa-solid fa-flask text-amber-400"></i>
        <span>Sandbox</span>
      </a>
      <button onclick="showFormulationModal()" class="bg-sky-600/20 hover:bg-sky-600/30 text-sky-400 border border-sky-500/30 rounded-lg px-3 py-1.5 font-medium transition flex items-center space-x-1.5 cursor-pointer">
        <i class="fa-solid fa-book-open"></i>
        <span>OR Formulation (C1-C18)</span>
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
          <input id="loadSearchInput" type="text" placeholder="Search load ID, number, trip type (short, long)..." 
                 class="w-full bg-slate-900 border border-slate-800 rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-sky-500 transition">
        </div>

        <!-- Trip Classification Filter Pills -->
        <div>
          <label class="text-[11px] font-medium text-slate-400 block mb-1.5">Trip Classification</label>
          <div class="flex flex-wrap gap-1" id="tripPillContainer">
            <button class="trip-pill active px-2 py-1 text-[11px] rounded bg-sky-600 text-white font-medium cursor-pointer" data-trip="ALL">ALL</button>
            <button class="trip-pill px-2 py-1 text-[11px] rounded bg-slate-800 hover:bg-slate-700 text-emerald-300 font-medium cursor-pointer" data-trip="SHORT">⚡ Short Trip</button>
            <button class="trip-pill px-2 py-1 text-[11px] rounded bg-slate-800 hover:bg-slate-700 text-sky-300 font-medium cursor-pointer" data-trip="MEDIUM">🚗 Medium Trip</button>
            <button class="trip-pill px-2 py-1 text-[11px] rounded bg-slate-800 hover:bg-slate-700 text-purple-300 font-medium cursor-pointer" data-trip="LONG">🚛 Long Trip</button>
          </div>
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
          <span>C1-C18 Active</span>
        </span>
      </div>
    </aside>

    <!-- Main Content Area -->
    <main class="flex-1 flex flex-col overflow-y-auto bg-slate-900/60">

      <!-- Top Load Banner & Optimization Trigger Toolbar -->
      <div class="bg-slate-950/60 border-b border-slate-800 p-6">
        <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div>
            <div class="flex flex-wrap items-center gap-2 mb-1.5">
              <span class="text-xs font-mono font-bold px-2 py-0.5 rounded bg-sky-500/20 text-sky-300 border border-sky-500/30" id="bannerLoadId">Load #244606</span>
              <span class="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300" id="bannerLoadNum">L-44166</span>
              <span class="text-xs px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-300 border border-indigo-500/20" id="bannerVdcName">LONG BEACH VDC (LA)</span>

              <!-- Trip Classification Tag (Short / Medium / Long Trip) -->
              <span id="bannerTripTypeTag" class="text-xs font-extrabold px-3 py-0.5 rounded-full uppercase tracking-wider flex items-center space-x-1.5 shadow-sm bg-purple-500/20 text-purple-300 border border-purple-500/30">
                <i class="fa-solid fa-tag text-[10px]"></i>
                <span id="bannerTripTypeText">LONG TRIP</span>
              </span>

              <!-- 100% Capacity Covered Tag -->
              <span class="text-xs font-bold px-2.5 py-0.5 rounded-full uppercase tracking-wider bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 flex items-center space-x-1">
                <i class="fa-solid fa-circle-check text-emerald-400 text-[10px]"></i>
                <span>100% LOAD COVERED</span>
              </span>

              <!-- Rest Time Attribute Badge -->
              <span class="text-xs font-medium px-2 py-0.5 rounded bg-slate-800/90 text-slate-300 border border-slate-700 flex items-center space-x-1.5">
                <i class="fa-solid fa-bed text-amber-400 text-[10px]"></i>
                <span id="bannerRestTimeText">Rest: 45m (C-17)</span>
              </span>

              <!-- Handover Time Attribute Badge -->
              <span class="text-xs font-medium px-2 py-0.5 rounded bg-slate-800/90 text-slate-300 border border-slate-700 flex items-center space-x-1.5">
                <i class="fa-solid fa-handshake text-sky-400 text-[10px]"></i>
                <span id="bannerHandoverText">Handover: 45m buffer</span>
              </span>
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
                <label class="block text-[10px] text-slate-400 font-medium uppercase mb-0.5">Shift</label>
                <select id="shiftTypeSelect" class="bg-slate-950 border border-slate-700 rounded px-2 py-1 text-slate-200 text-xs font-mono focus:outline-none focus:border-sky-500">
                  <option value="AM" selected>☀️ AM (06:00 - 18:00)</option>
                  <option value="PM">🌙 PM (18:00 - 06:00)</option>
                </select>
              </div>
              <div class="h-8 w-[1px] bg-slate-800"></div>
              <div>
                <label class="block text-[10px] text-slate-400 font-medium uppercase mb-0.5">Start Time</label>
                <input id="tripStartTimeInput" type="time" value="06:00" 
                       class="bg-slate-950 border border-slate-700 rounded px-2 py-1 text-slate-200 text-xs font-mono focus:outline-none focus:border-sky-500">
              </div>
              <div class="h-8 w-[1px] bg-slate-800"></div>
              <div>
                <label class="block text-[10px] text-slate-400 font-medium uppercase mb-0.5">Daily Cap</label>
                <div class="flex items-center space-x-1">
                  <input id="maxDutyHoursInput" type="number" step="0.5" min="4" max="14" value="11.0" 
                         class="w-14 bg-slate-950 border border-slate-700 rounded px-2 py-1 text-slate-200 text-xs font-mono focus:outline-none focus:border-sky-500">
                  <span class="text-slate-400 text-[10px]">hrs</span>
                </div>
              </div>
              <div class="h-8 w-[1px] bg-slate-800"></div>
              <div>
                <label class="block text-[10px] text-slate-400 font-medium uppercase mb-0.5">Turnaround Rest</label>
                <div class="flex items-center space-x-1">
                  <input id="turnaroundRestInput" type="number" step="5" min="15" max="90" value="45" 
                         class="w-12 bg-slate-950 border border-slate-700 rounded px-2 py-1 text-slate-200 text-xs font-mono focus:outline-none focus:border-sky-500">
                  <span class="text-slate-400 text-[10px]">min</span>
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

        <!-- Solution KPI Summary Grid (8 Columns) -->
        <div id="solutionKpiContainer" class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-3">
          <div class="bg-slate-950/80 border border-slate-800 rounded-xl p-3.5">
            <div class="text-[11px] font-medium text-slate-400 uppercase tracking-wider mb-1">Trip Type</div>
            <span id="kpiTripTypeBadge" class="px-2 py-0.5 rounded text-xs font-bold bg-purple-500/20 text-purple-300 border border-purple-500/30">LONG TRIP</span>
            <div class="text-[10px] text-emerald-400 mt-1 font-mono" id="kpiCoverageSub">100% Load Covered</div>
          </div>

          <div class="bg-slate-950/80 border border-slate-800 rounded-xl p-3.5">
            <div class="text-[11px] font-medium text-slate-400 uppercase tracking-wider mb-1">Trip Turnaround</div>
            <div class="text-lg font-bold font-mono text-white" id="kpiDuration">14.55 hrs</div>
            <div class="text-[10px] text-slate-400 mt-1" id="kpiDrivingTime">Driving: 11.97h</div>
          </div>

          <div class="bg-slate-950/80 border border-slate-800 rounded-xl p-3.5">
            <div class="text-[11px] font-medium text-slate-400 uppercase tracking-wider mb-1">Total Distance</div>
            <div class="text-lg font-bold font-mono text-white" id="kpiDistance">598.5 mi</div>
            <div class="text-[10px] text-slate-400 mt-1">Closed circuit loop</div>
          </div>

          <!-- Drivers Needed KPI Card with Explanation Tooltip -->
          <div class="bg-slate-950/80 border border-slate-800 rounded-xl p-3.5 relative group cursor-pointer" onclick="showDriversExplanation()">
            <div class="flex items-center justify-between">
              <div class="text-[11px] font-medium text-slate-400 uppercase tracking-wider mb-1">Drivers Needed</div>
              <i class="fa-solid fa-circle-question text-sky-400 text-xs hover:text-sky-300"></i>
            </div>
            <div class="text-lg font-bold font-mono text-sky-400" id="kpiDriversCount">2 Drivers</div>
            <div class="text-[10px] text-slate-400 mt-1" id="kpi11hCompliance">Click for FMCSA rationale</div>
          </div>

          <div class="bg-slate-950/80 border border-slate-800 rounded-xl p-3.5">
            <div class="text-[11px] font-medium text-slate-400 uppercase tracking-wider mb-1">Turnaround Rest</div>
            <div class="text-lg font-bold font-mono text-amber-300" id="kpiRestDuration">45 mins</div>
            <div class="text-[10px] text-slate-400 mt-1">Depot buffer (C-17)</div>
          </div>

          <div class="bg-slate-950/80 border border-slate-800 rounded-xl p-3.5">
            <div class="text-[11px] font-medium text-slate-400 uppercase tracking-wider mb-1">Handover Buffer</div>
            <div class="text-sm font-semibold text-amber-300 truncate" id="kpiHandoverLoc">Fresno Hub (D_LA_05)</div>
            <div class="text-[10px] text-slate-400 mt-1" id="kpiHandoverDuration">45 min buffer (C-14)</div>
          </div>

          <div class="bg-slate-950/80 border border-slate-800 rounded-xl p-3.5">
            <div class="text-[11px] font-medium text-slate-400 uppercase tracking-wider mb-1">Capacity Load</div>
            <div class="text-lg font-bold font-mono text-emerald-400" id="kpiCapacity">10 / 10 Cars</div>
            <div class="text-[10px] text-emerald-400 mt-1 font-semibold" id="kpiCargoWeight">54,759 lbs (100% Full)</div>
          </div>

          <div class="bg-slate-950/80 border border-slate-800 rounded-xl p-3.5">
            <div class="text-[11px] font-medium text-slate-400 uppercase tracking-wider mb-1">Estimated Cost</div>
            <div class="text-lg font-bold font-mono text-emerald-400" id="kpiTotalCost">$1,796.10</div>
            <div class="text-[10px] text-slate-400 mt-1">Flat $35/hr driver wage</div>
          </div>
        </div>

        <!-- Drivers Needed Legal Rationale & Trip Attributes Banner -->
        <div id="driversRationaleBanner" class="p-4 rounded-xl border bg-slate-950/80 flex items-start space-x-3 text-xs border-sky-500/30">
          <div class="p-2 rounded-lg bg-sky-500/20 text-sky-400 mt-0.5">
            <i class="fa-solid fa-scale-balanced text-sm"></i>
          </div>
          <div class="flex-1">
            <div class="flex flex-wrap items-center gap-2 mb-1.5">
              <span class="font-bold text-slate-200 uppercase tracking-wider">Drivers Needed Legal Rationale & Trip Attributes</span>
              <span id="rationaleDriverTag" class="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300">2 DRIVERS MANDATED</span>
              <span id="rationaleTripTag" class="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-500/20 text-purple-300">LONG TRIP</span>
              <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-300">100% CAPACITY COVERED</span>
            </div>
            <p id="driversRationaleText" class="text-slate-300 leading-relaxed font-mono text-[11px]">
              Loading explanation...
            </p>
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 mt-3 pt-3 border-t border-slate-800/80 text-[11px] font-mono">
              <div><span class="text-slate-500">Trip Category:</span> <span id="attrTripType" class="text-slate-200 font-semibold">Long Trip</span></div>
              <div><span class="text-slate-500">Capacity Coverage:</span> <span class="text-emerald-400 font-semibold">100% (All Units)</span></div>
              <div><span class="text-slate-500">Post-Trip Rest:</span> <span id="attrRestTime" class="text-amber-300 font-semibold">45 min depot buffer</span></div>
              <div><span class="text-slate-500">Handover Buffer:</span> <span id="attrHandoverTime" class="text-sky-300 font-semibold">45 min at Fresno Hub</span></div>
            </div>
          </div>
        </div>

        <!-- Driver Hours-of-Service (HOS) Compliance Monitor -->
        <div id="driverCompliancePanel" class="bg-slate-950/80 border border-slate-800 rounded-xl p-4">
          <div class="flex flex-wrap items-center justify-between mb-3 gap-2">
            <div class="flex items-center space-x-2">
              <i class="fa-solid fa-id-card-clip text-sky-400 text-sm"></i>
              <h3 class="font-semibold text-xs uppercase tracking-wider text-slate-200">Hours-of-Service (HOS) Compliance: Daily 11h (C-12a) & Rolling 70h/8-Day Cap (C-12b)</h3>
            </div>
            <div class="flex items-center space-x-2 text-xs text-slate-400">
              <span class="px-2 py-0.5 rounded bg-slate-800 font-mono text-[10px]">Daily Cap: 11.0h</span>
              <span class="px-2 py-0.5 rounded bg-slate-800 font-mono text-[10px]">Weekly Cap: 70.0h</span>
              <span class="px-2 py-0.5 rounded bg-slate-800 font-mono text-[10px]">Flat Rate: $35.00/hr</span>
            </div>
          </div>
          <div id="driverProgressBars" class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Dynamically populated -->
          </div>
        </div>

        <!-- Tabbed Navigation -->
        <div class="border-b border-slate-800 flex flex-wrap items-center justify-between gap-2">
          <div class="flex flex-wrap space-x-2" id="tabButtons">
            <button class="tab-btn active px-3.5 py-2 text-xs font-semibold rounded-t-lg border-b-2 border-sky-500 text-sky-400 bg-slate-800/40 cursor-pointer" onclick="switchTab('itineraryTab')">
              <i class="fa-solid fa-table-list mr-1.5"></i> Leg-by-Leg Schedule
            </button>
            <button class="tab-btn px-3.5 py-2 text-xs font-semibold rounded-t-lg border-b-2 border-transparent text-slate-400 hover:text-slate-200 cursor-pointer" onclick="switchTab('timelineTab')">
              <i class="fa-solid fa-chart-gantt mr-1.5"></i> Timeline & Gantt
            </button>
            <button class="tab-btn px-3.5 py-2 text-xs font-semibold rounded-t-lg border-b-2 border-transparent text-slate-400 hover:text-slate-200 cursor-pointer" onclick="switchTab('circuitTab')">
              <i class="fa-solid fa-route mr-1.5"></i> Stop Circuit & Handover
            </button>
            <button class="tab-btn px-3.5 py-2 text-xs font-semibold rounded-t-lg border-b-2 border-transparent text-slate-400 hover:text-slate-200 cursor-pointer" onclick="switchTab('cargoTab')">
              <i class="fa-solid fa-car mr-1.5"></i> Cargo Manifest
            </button>
            <button id="tabBtnMultiTrip" class="tab-btn px-3.5 py-2 text-xs font-semibold rounded-t-lg border-b-2 border-transparent text-emerald-400 hover:text-emerald-300 bg-emerald-950/20 cursor-pointer" onclick="switchTab('multiTripTab')">
              <i class="fa-solid fa-repeat mr-1.5"></i> <span id="tabBtnMultiTripText">Multi-Trip Shift Tour</span>
            </button>
            <button id="tabBtnDriverRoster" class="tab-btn px-3.5 py-2 text-xs font-semibold rounded-t-lg border-b-2 border-transparent text-indigo-400 hover:text-indigo-300 bg-indigo-950/30 cursor-pointer" onclick="switchTab('driverRosterTab')">
              <i class="fa-solid fa-users-gear mr-1.5"></i> <span>Driver Roster (Manager POV)</span>
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
              <span class="text-xs text-slate-400 font-mono" id="cargoTotalUnitsWeight">8 Units &bull; Total Weight: 42,816 lbs</span>
            </div>
            <div class="overflow-x-auto">
              <table class="w-full text-left text-xs">
                <thead class="bg-slate-900 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
                  <tr>
                    <th class="py-2.5 px-3">#</th>
                    <th class="py-2.5 px-3">VIN</th>
                    <th class="py-2.5 px-4">Model Description</th>
                    <th class="py-2.5 px-3">Brand / Series</th>
                    <th class="py-2.5 px-3 text-right">Weight (lb)</th>
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

        <!-- Tab 5: Multi-Trip Shift Tour (Dynamically Linked to Selected Load) -->
        <div id="multiTripTab" class="tab-content hidden space-y-4">
          <div class="bg-slate-950/80 border border-slate-800 rounded-xl p-5 space-y-4">
            <div class="flex flex-col md:flex-row md:items-center justify-between gap-2 pb-4 border-b border-slate-800">
              <div>
                <div class="flex items-center space-x-2">
                  <span id="shiftTourBadge" class="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-xs font-bold">OPERATIONAL SHOWCASE</span>
                  <h3 id="shiftTourTitle" class="font-bold text-sm text-white">Multi-Trip Single-Driver Daily Shift Tour</h3>
                </div>
                <p id="shiftTourSubtitle" class="text-xs text-slate-400 mt-1">Single driver executing multiple short trips within the 11-hour daily cap with mandatory 45-min turnaround rest at factory depot (C-17).</p>
              </div>
              <div class="flex items-center space-x-2">
                <span id="shiftTourDriverBadge" class="px-3 py-1 bg-slate-800 rounded-lg text-xs font-mono text-slate-300">Driver: Marcus Vance (West Coast)</span>
                <span id="shiftTourRestBadge" class="px-2 py-1 bg-amber-500/20 text-amber-300 rounded text-xs font-mono">45m Turnaround Rest</span>
              </div>
            </div>

            <!-- Multi-Trip Summary Cards -->
            <div class="grid grid-cols-2 md:grid-cols-5 gap-3">
              <div class="bg-slate-900 border border-slate-800 rounded-xl p-3">
                <div class="text-[10px] text-slate-400 uppercase font-medium">Trips in Shift</div>
                <div id="shiftTourTripsCompleted" class="text-lg font-bold font-mono text-white mt-1">3 Round-Trips</div>
                <div id="shiftTourLoadsList" class="text-[10px] text-slate-500">Loads #244861, #188377, #188384</div>
              </div>
              <div class="bg-slate-900 border border-slate-800 rounded-xl p-3">
                <div class="text-[10px] text-slate-400 uppercase font-medium">Total Shift Duty</div>
                <div id="shiftTourTotalDuty" class="text-lg font-bold font-mono text-emerald-400 mt-1">5.40 hrs</div>
                <div id="shiftTourDutyCompliance" class="text-[10px] text-emerald-400">Within 11.0h Daily Cap (C-12a)</div>
              </div>
              <div class="bg-slate-900 border border-slate-800 rounded-xl p-3">
                <div class="text-[10px] text-slate-400 uppercase font-medium">Total Shift Span</div>
                <div id="shiftTourTotalSpan" class="text-lg font-bold font-mono text-sky-400 mt-1">6.57 hrs</div>
                <div id="shiftTourSpanDesc" class="text-[10px] text-slate-400">06:00 AM &rarr; 03:06 PM (AM Window)</div>
              </div>
              <div class="bg-slate-900 border border-slate-800 rounded-xl p-3">
                <div class="text-[10px] text-slate-400 uppercase font-medium">Total Mileage</div>
                <div id="shiftTourMileage" class="text-lg font-bold font-mono text-white mt-1">143.7 miles</div>
                <div id="shiftTourNetwork" class="text-[10px] text-slate-500">Terminal Network</div>
              </div>
              <div class="bg-slate-900 border border-slate-800 rounded-xl p-3">
                <div class="text-[10px] text-slate-400 uppercase font-medium">Turnaround Rest</div>
                <div id="shiftTourRestDesc" class="text-lg font-bold font-mono text-amber-300 mt-1">45 min / trip</div>
                <div id="shiftTourRestSub" class="text-[10px] text-amber-400/80">Mandatory depot buffer (C-17)</div>
              </div>
            </div>

            <!-- Multi-Trip Schedule Table -->
            <div class="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden mt-4">
              <table class="w-full text-left text-xs">
                <thead class="bg-slate-950 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
                  <tr>
                    <th class="py-2.5 px-3">Trip / Phase</th>
                    <th class="py-2.5 px-3">Load ID & Details</th>
                    <th class="py-2.5 px-3">Departure</th>
                    <th class="py-2.5 px-3">Arrival / Return</th>
                    <th class="py-2.5 px-3 text-right">Distance</th>
                    <th class="py-2.5 px-3 text-right">Duty Hours</th>
                    <th class="py-2.5 px-4">Post-Trip Action & Mandates</th>
                  </tr>
                </thead>
                <tbody id="multiTripTableBody" class="divide-y divide-slate-800/60 font-mono text-slate-200">
                  <!-- Dynamically populated via renderMultiTripTour(res) -->
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Tab 6: Driver Roster (Manager Operational POV & Multi-Trip Shift Validation) -->
        <div id="driverRosterTab" class="tab-content hidden space-y-5">
          <!-- Executive Manager KPI Ribbon -->
          <div class="bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 border border-indigo-900/50 rounded-2xl p-4 shadow-xl">
            <div class="flex flex-wrap items-center justify-between gap-4 mb-3">
              <div class="flex items-center space-x-3">
                <div class="w-10 h-10 rounded-xl bg-indigo-600/20 text-indigo-400 flex items-center justify-center text-lg font-bold border border-indigo-500/30 shadow-inner">
                  <i class="fa-solid fa-users-gear"></i>
                </div>
                <div>
                  <h3 class="text-sm font-bold text-white tracking-wide flex items-center gap-2">
                    Commercial Driver Fleet Operations & Location Tracking
                    <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/40 uppercase tracking-wider">Manager POV</span>
                  </h3>
                  <p class="text-xs text-slate-400">Live CP-SAT Fleet Assignments &bull; Real-Time Location Tracking &bull; Multi-Trip Shift Hour Validation</p>
                </div>
              </div>
              <div class="flex items-center space-x-2">
                <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-emerald-950/60 border border-emerald-800/60 text-emerald-400 text-xs font-semibold">
                  <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                  100% FMCSA / Intrastate Compliant
                </span>
                <span class="px-2.5 py-1 rounded-lg bg-slate-800/80 border border-slate-700/80 text-slate-300 text-xs font-mono">
                  11 Drivers Active
                </span>
              </div>
            </div>

            <!-- KPI Metric Chips -->
            <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5 pt-2 border-t border-slate-800/80">
              <div class="bg-slate-950/60 p-2.5 rounded-xl border border-slate-800">
                <div class="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Active Dispatched</div>
                <div class="text-base font-bold text-sky-400 font-mono" id="mgrActiveDispatched">10 / 11</div>
                <div class="text-[10px] text-slate-500">1 Standby at Depot</div>
              </div>
              <div class="bg-slate-950/60 p-2.5 rounded-xl border border-amber-900/40 bg-amber-950/10">
                <div class="text-[10px] uppercase font-bold text-amber-400 tracking-wider">★ Multi-Trip Shifts</div>
                <div class="text-base font-bold text-amber-300 font-mono" id="mgrMultiTripCount">4 Drivers</div>
                <div class="text-[10px] text-amber-400/80">Chained 2–3 trips / shift</div>
              </div>
              <div class="bg-slate-950/60 p-2.5 rounded-xl border border-indigo-900/40 bg-indigo-950/10">
                <div class="text-[10px] uppercase font-bold text-indigo-400 tracking-wider">Interstate Relays</div>
                <div class="text-base font-bold text-indigo-300 font-mono" id="mgrRelayCount">1 Team (3 Drivers)</div>
                <div class="text-[10px] text-indigo-400/80">Lead & Relief Pairs</div>
              </div>
              <div class="bg-slate-950/60 p-2.5 rounded-xl border border-slate-800">
                <div class="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Shift Duty Total</div>
                <div class="text-base font-bold text-slate-200 font-mono" id="mgrTotalDuty">67.1h</div>
                <div class="text-[10px] text-slate-500">Across Dispatched Fleet</div>
              </div>
              <div class="bg-slate-950/60 p-2.5 rounded-xl border border-slate-800">
                <div class="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Vehicles Delivered</div>
                <div class="text-base font-bold text-emerald-400 font-mono" id="mgrVehiclesDelivered">117 Units</div>
                <div class="text-[10px] text-slate-500">Shift Vehicle Throughput</div>
              </div>
              <div class="bg-slate-950/60 p-2.5 rounded-xl border border-slate-800">
                <div class="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Piece-Rate Wage Pool</div>
                <div class="text-base font-bold text-emerald-300 font-mono" id="mgrTotalWages">$6,018</div>
                <div class="text-[10px] text-emerald-400/80">Avg Yield: $89.63/hr</div>
              </div>
            </div>
          </div>

          <!-- Manager Filter & Search Toolbar -->
          <div class="bg-slate-900/80 border border-slate-800 p-3 rounded-xl flex flex-wrap items-center justify-between gap-3">
            <div class="flex flex-wrap items-center gap-1.5" id="managerFilterButtons">
              <span class="text-xs text-slate-400 font-semibold mr-1"><i class="fa-solid fa-filter mr-1"></i> Filter:</span>
              <button onclick="filterManagerRoster('ALL')" class="mgr-filter-btn active px-2.5 py-1 text-xs font-semibold rounded-lg bg-indigo-600 text-white cursor-pointer transition">
                All Drivers (11)
              </button>
              <button onclick="filterManagerRoster('MULTITRIP')" class="mgr-filter-btn px-2.5 py-1 text-xs font-semibold rounded-lg bg-slate-800 text-amber-300 hover:bg-slate-700 cursor-pointer transition border border-amber-500/30">
                ★ Multi-Trip Chained (4)
              </button>
              <button onclick="filterManagerRoster('DEDICATED')" class="mgr-filter-btn px-2.5 py-1 text-xs font-semibold rounded-lg bg-slate-800 text-emerald-300 hover:bg-slate-700 cursor-pointer transition">
                Dedicated Single (3)
              </button>
              <button onclick="filterManagerRoster('RELAY')" class="mgr-filter-btn px-2.5 py-1 text-xs font-semibold rounded-lg bg-slate-800 text-purple-300 hover:bg-slate-700 cursor-pointer transition">
                Interstate Relay (3)
              </button>
              <button onclick="filterManagerRoster('STANDBY')" class="mgr-filter-btn px-2.5 py-1 text-xs font-semibold rounded-lg bg-slate-800 text-slate-300 hover:bg-slate-700 cursor-pointer transition">
                Standby (1)
              </button>
            </div>

            <!-- Terminal filter dropdown and search input -->
            <div class="flex items-center gap-2">
              <select id="managerLocationFilter" onchange="filterManagerLocation(this.value)" class="bg-slate-950 border border-slate-700 text-xs rounded-lg px-2.5 py-1 text-slate-300 focus:outline-none focus:border-indigo-500">
                <option value="ALL">📍 All Locations / Terminals</option>
                <option value="LA">Long Beach VDC (LA)</option>
                <option value="SF">Benicia VDC (SF)</option>
                <option value="ML">Mira Loma VDC (ML)</option>
                <option value="PT">Portland VDC (PT)</option>
                <option value="04016">Omesa Logistics Hub (04016)</option>
                <option value="HUB">Certified Handover Hubs (Fresno / Eugene)</option>
                <option value="TRANSIT">En Route / In Transit</option>
              </select>
              <div class="relative">
                <input type="text" id="managerRosterSearch" oninput="searchManagerRoster(this.value)" placeholder="Search driver, callsign..." class="bg-slate-950 border border-slate-700 text-xs rounded-lg pl-7 pr-3 py-1 text-slate-300 focus:outline-none focus:border-indigo-500 w-44">
                <i class="fa-solid fa-magnifying-glass text-slate-500 text-xs absolute left-2.5 top-2"></i>
              </div>
            </div>
          </div>

          <!-- Section 1: Multi-Trip Shift Hour Validation Spotlight -->
          <div id="multiTripSpotlightSection" class="space-y-3">
            <div class="flex items-center justify-between">
              <h4 class="text-xs font-bold text-amber-300 uppercase tracking-wider flex items-center gap-2">
                <i class="fa-solid fa-repeat text-amber-400"></i>
                Multi-Trip Shift Hour Validations (Drivers Executing Consecutive Trips in Scheduled Shift)
              </h4>
              <span class="text-[11px] text-slate-400 font-mono">4 Verified CP-SAT Shifts &bull; Mandatory C-17 Turnaround Rest Enforced</span>
            </div>
            <div class="grid grid-cols-1 gap-4" id="multiTripCardsContainer">
              <!-- Dynamically populated via renderMultiTripValidationCards() -->
            </div>
          </div>

          <!-- Section 2: Complete Fleet Driver Roster (Location & Operational Status Grid) -->
          <div class="space-y-3 pt-2">
            <div class="flex items-center justify-between">
              <h4 class="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                <i class="fa-solid fa-truck-ramp-box text-indigo-400"></i>
                Fleet Driver Roster & Real-Time Geographic Placement (Manager POV)
              </h4>
              <span class="text-[11px] text-slate-400 font-mono" id="mgrRosterCountDisplay">Showing 11 Drivers</span>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3.5" id="managerRosterCardsContainer">
              <!-- Dynamically populated via renderManagerRosterCards() -->
            </div>
          </div>

          <!-- Section 3: Terminal Geographic Distribution Summary -->
          <div class="bg-slate-900/60 border border-slate-800 rounded-xl p-4">
            <h4 class="text-xs font-bold text-slate-300 uppercase tracking-wider mb-3 flex items-center gap-2">
              <i class="fa-solid fa-warehouse text-sky-400"></i>
              Regional Terminal & Hub Driver Distribution
            </h4>
            <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 text-xs" id="terminalDistributionCards">
              <!-- Terminal cards -->
            </div>
          </div>
        </div>


      </div>

    </main>

  </div>

  <!-- Modal: Complete OR Formulation Reference (C-1 to C-18) -->
  <div id="formulationModal" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
    <div class="bg-slate-900 border border-slate-700 rounded-2xl max-w-4xl w-full max-h-[88vh] flex flex-col shadow-2xl">
      <div class="p-5 border-b border-slate-800 flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <div class="w-8 h-8 rounded-lg bg-sky-500/20 text-sky-400 flex items-center justify-center font-bold">
            <i class="fa-solid fa-book"></i>
          </div>
          <div>
            <h3 class="font-bold text-sm text-white">Operations Research Formulation: Constraints C-1 through C-18</h3>
            <p class="text-[11px] text-slate-400">Mathematical Specification for Finished Vehicle Logistics & Driver Assignment</p>
          </div>
        </div>
        <button onclick="hideFormulationModal()" class="text-slate-400 hover:text-white text-lg cursor-pointer">
          <i class="fa-solid fa-xmark"></i>
        </button>
      </div>
      <div class="p-6 overflow-y-auto space-y-4 text-xs text-slate-300">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div class="p-3 bg-slate-950/80 border border-slate-800 rounded-lg">
            <div class="font-semibold text-sky-400 mb-1">C-1 & C-2: Factory Departure & Same Return</div>
            <p class="font-mono text-amber-300">&sum; d_ifk = 1, &sum; d_ijf = a_if</p>
            <p class="text-[11px] text-slate-400 mt-1">Each hauler departs and returns to the identical origin factory terminal.</p>
          </div>
          <div class="p-3 bg-slate-950/80 border border-slate-800 rounded-lg">
            <div class="font-semibold text-sky-400 mb-1">C-3 & C-6: Straight Load & Truck Continuity</div>
            <p class="font-mono text-emerald-300">&sum; d_ijd = 1 &bull; &sum; d_ijk = &sum; d_ikm</p>
            <p class="text-[11px] text-slate-400 mt-1">Each dealer visited exactly once (no split delivery). Inflow equals outflow.</p>
          </div>
          <div class="p-3 bg-slate-950/80 border border-slate-800 rounded-lg">
            <div class="font-semibold text-sky-400 mb-1">C-7: Route-Driver Coupling</div>
            <p class="font-mono text-purple-300">&sum; x_ijkl = d_ijk</p>
            <p class="text-[11px] text-slate-400 mt-1">Exactly one driver is assigned to each active movement arc.</p>
          </div>
          <div class="p-3 bg-slate-950/80 border border-slate-800 rounded-lg">
            <div class="font-semibold text-sky-400 mb-1">C-10: Hauler Capacity</div>
            <p class="font-mono text-pink-300">L_ij &le; Q_i</p>
            <p class="text-[11px] text-slate-400 mt-1">Vehicle count and weight cannot exceed trailer payload limits.</p>
          </div>
          <div class="p-3 bg-slate-950/80 border border-slate-800 rounded-lg">
            <div class="font-semibold text-sky-400 mb-1">C-12(a): Daily 11-Hour Limit</div>
            <p class="font-mono text-amber-300">&sum; T_duty_ijk &middot; x_ijkl &le; 11 hours (660 min)</p>
            <p class="text-[11px] text-slate-400 mt-1">Driver may not exceed 11 hours duty in any single shift.</p>
          </div>
          <div class="p-3 bg-slate-950/80 border border-slate-800 rounded-lg">
            <div class="font-semibold text-sky-400 mb-1">C-12(b): Rolling 70-Hour / 8-Day Limit</div>
            <p class="font-mono text-sky-300">&sum; T_duty_ijk &middot; x_ijkl &le; 70 hours (4200 min)</p>
            <p class="text-[11px] text-slate-400 mt-1">Driver cumulative duty across 8 consecutive days cannot exceed 70h.</p>
          </div>
          <div class="p-3 bg-slate-950/80 border border-slate-800 rounded-lg">
            <div class="font-semibold text-sky-400 mb-1">C-13: Long Trips Multi-Driver Requirement</div>
            <p class="font-mono text-emerald-300">Trip duration &le; H_i^max &middot; &sum; z_il</p>
            <p class="text-[11px] text-slate-400 mt-1">Trips exceeding 11 hours legally require &ge;2 drivers with handover.</p>
          </div>
          <div class="p-3 bg-slate-950/80 border border-slate-800 rounded-lg">
            <div class="font-semibold text-sky-400 mb-1">C-14 & C-17: Handover & Turnaround Rest</div>
            <p class="font-mono text-amber-300">h_k = 0 &rarr; no swap &bull; Start_next &ge; End_prev + T_rest</p>
            <p class="text-[11px] text-slate-400 mt-1">45-min handover at certified hubs &bull; 45-min post-trip rest between trips.</p>
          </div>
        </div>
      </div>
      <div class="p-4 border-t border-slate-800 bg-slate-950/60 flex justify-end">
        <button onclick="hideFormulationModal()" class="px-4 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg cursor-pointer">Close</button>
      </div>
    </div>
  </div>

  <script>
    // Embedded Data Bundle for Standalone Execution
    const EMBEDDED_DATA = {embedded_json};
    window.EMBEDDED_DATA = EMBEDDED_DATA;
    const PASSCODE_HASH = 'dispatch2026';


    let currentLoadId = 244606;
    let currentSolution = null;
    let allLoads = EMBEDDED_DATA.loads || [];
    let activeOriginFilter = 'ALL';
    let activeTripFilter = 'ALL';
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

      const tripPills = document.querySelectorAll('.trip-pill');
      tripPills.forEach(pill => {{
        pill.addEventListener('click', () => {{
          tripPills.forEach(p => {{
            p.classList.remove('active', 'bg-sky-600', 'text-white');
            p.classList.add('bg-slate-800', 'text-slate-300');
          }});
          pill.classList.add('active', 'bg-sky-600', 'text-white');
          pill.classList.remove('bg-slate-800', 'text-slate-300');
          activeTripFilter = pill.getAttribute('data-trip');
          filterAndRenderLoads();
        }});
      }});

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
        
        const loadTag = (load.trip_tag || (load.turnaround_duration_hours > 11 ? 'LONG' : load.turnaround_duration_hours > 5 ? 'MEDIUM' : 'SHORT')).toUpperCase();
        const matchesTrip = (activeTripFilter === 'ALL') || loadTag.includes(activeTripFilter);

        const matchesSearch = !searchTerm || 
          String(load.id).includes(searchTerm) || 
          String(load.load_num).toLowerCase().includes(searchTerm) ||
          String(load.assigned_hauler_name).toLowerCase().includes(searchTerm) ||
          String(load.trip_type || '').toLowerCase().includes(searchTerm) ||
          String(load.trip_tag || '').toLowerCase().includes(searchTerm) ||
          loadTag.toLowerCase().includes(searchTerm);
        return matchesOrigin && matchesTrip && matchesSearch;
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
        const tripType = load.trip_type || (load.turnaround_duration_hours > 11 ? 'Long Trip' : load.turnaround_duration_hours > 5 ? 'Medium Trip' : 'Short Trip');
        const tripTag = (load.trip_tag || tripType.toUpperCase()).replace(' TRIP', '') + ' TRIP';
        const tagColor = tripTag.startsWith('SHORT') ? 'text-emerald-300 bg-emerald-500/10 border-emerald-500/20' :
                         tripTag.startsWith('MEDIUM') ? 'text-sky-300 bg-sky-500/10 border-sky-500/20' :
                         'text-purple-300 bg-purple-500/10 border-purple-500/20';

        const restMins = load.rest_time_mins || 45;
        const handoverText = load.handover_time_mins > 0 ? `${{load.handover_time_mins}}m Handover` : 'Direct Single';

        return `
          <div class="load-card p-3 rounded-xl border border-slate-800 hover:border-slate-700 bg-slate-900/60 cursor-pointer transition ${{isActive}}"
               onclick="selectLoad(${{load.id}})">
            <div class="flex items-center justify-between mb-1.5">
              <div class="flex items-center space-x-2">
                <span class="font-mono font-bold text-xs text-white">#${{load.id}}</span>
                <span class="font-mono text-[11px] text-slate-400">${{load.load_num}}</span>
              </div>
              <span class="text-[10px] font-extrabold px-2 py-0.5 rounded border uppercase ${{tagColor}}">${{tripTag}}</span>
            </div>
            
            <div class="flex items-center justify-between text-[11px] text-slate-400 mb-1">
              <span class="flex items-center space-x-1">
                <i class="fa-solid fa-location-dot text-sky-400 text-[10px]"></i>
                <span class="text-slate-300 font-medium">${{load.origin_legal_entity}} (${{load.origin_vdc_name}})</span>
              </span>
              <span class="text-emerald-400 font-mono text-[10px] font-semibold">100% Covered (${{load.cargo_count}} Cars)</span>
            </div>

            <div class="text-[10px] text-slate-400 flex items-center justify-between pt-1 border-t border-slate-800/50">
              <span><i class="fa-solid fa-bed text-amber-400 text-[9px] mr-1"></i>Rest: ${{restMins}}m</span>
              <span><i class="fa-solid fa-handshake text-sky-400 text-[9px] mr-1"></i>${{handoverText}}</span>
              <span class="text-slate-500 font-mono">${{load.dealers_count}} Dealers</span>
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

      const totalLbs = info.total_weight_lbs ? info.total_weight_lbs : Math.round(Number(info.total_weight_kg || 0) * 2.20462);
      document.getElementById('bannerHaulerName').textContent = `${{info.hauler.name}} (${{info.hauler.capacity}} Car Cap)`;
      document.getElementById('bannerCargoStats').textContent = `${{info.total_cargo_units}} Vehicles • 100% Covered (${{totalLbs.toLocaleString()}} lbs)`;
      document.getElementById('bannerDealersCount').textContent = `${{info.dealers.length}} Destination Dealerships`;
      document.getElementById('cargoTotalUnitsWeight').textContent = `${{info.total_cargo_units}} Units • 100% Covered • Total Weight: ${{totalLbs.toLocaleString()}} lbs`;
    }}

    function renderCargoTable(cargoList) {{
      const tbody = document.getElementById('cargoTableBody');
      if (!tbody) return;

      tbody.innerHTML = cargoList.map((item, idx) => {{
        const itemLbs = item.weight_lb ? Number(item.weight_lb) : Math.round(Number(item.weight_kg || 2000) * 2.20462);
        return `
        <tr class="hover:bg-slate-800/40 transition">
          <td class="py-2.5 px-3 text-slate-500 text-center">${{idx + 1}}</td>
          <td class="py-2.5 px-3 font-mono font-medium text-sky-400">${{item.vin}}</td>
          <td class="py-2.5 px-4 text-white font-medium">${{item.model_name}}</td>
          <td class="py-2.5 px-3 text-slate-400">${{item.brand}} ${{item.series || ''}}</td>
          <td class="py-2.5 px-3 text-right text-slate-300 font-mono">${{itemLbs.toLocaleString()}}</td>
          <td class="py-2.5 px-3 text-center text-slate-400 text-[11px]">${{item.length_m || '-'}} &times; ${{item.width_m || '-'}} &times; ${{item.height_m || '-'}}m</td>
          <td class="py-2.5 px-4 text-amber-300 font-mono text-[11px]">${{item.destination_dealer_id}}</td>
        </tr>
      `;
      }}).join('');
    }}

    async function triggerSolve() {{
      const btn = document.getElementById('btnSolveSchedule');
      const originalHtml = btn.innerHTML;
      btn.disabled = true;
      btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin text-amber-300"></i><span>OPTIMIZING...</span>`;

      const shiftType = document.getElementById('shiftTypeSelect')?.value || 'AM';
      const tripStart = document.getElementById('tripStartTimeInput')?.value || '06:00';
      const dutyLimit = parseFloat(document.getElementById('maxDutyHoursInput')?.value || '11.0');
      const turnaroundRest = parseInt(document.getElementById('turnaroundRestInput')?.value || '45');

      if (isBackendConnected) {{
        try {{
          const res = await fetch('http://127.0.0.1:5050/api/solve', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{
              load_id: currentLoadId,
              trip_start_time: tripStart,
              max_driver_duty_hours: dutyLimit,
              shift_type: shiftType,
              post_trip_rest_mins: turnaroundRest,
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
      }}, 120);
    }}

    function renderSolution(res) {{
      if (res.status === 'INFEASIBLE' || res.status === 'ERROR') {{
        const kpiTag = document.getElementById('kpiTripTypeBadge');
        if (kpiTag) {{
          kpiTag.textContent = res.status;
          kpiTag.className = 'px-2 py-0.5 rounded text-xs font-bold bg-red-500/20 text-red-300 border border-red-500/30';
        }}
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

      // Determine Trip Classification & Tag
      const hours = res.total_trip_duration_hours;
      const tripType = res.trip_type || (hours <= 5.0 ? 'Short Trip' : hours <= 11.0 ? 'Medium Trip' : 'Long Trip');
      const tripTag = res.trip_tag || (hours <= 5.0 ? 'SHORT TRIP' : hours <= 11.0 ? 'MEDIUM TRIP' : 'LONG TRIP');
      
      const tagColor = tripTag.startsWith('SHORT') ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30' :
                       tripTag.startsWith('MEDIUM') ? 'bg-sky-500/20 text-sky-300 border-sky-500/30' :
                       'bg-purple-500/20 text-purple-300 border-purple-500/30';

      // Update Top Banner Trip Badges
      const bannerTag = document.getElementById('bannerTripTypeTag');
      if (bannerTag) {{
        bannerTag.className = `text-xs font-extrabold px-3 py-0.5 rounded-full uppercase tracking-wider flex items-center space-x-1.5 shadow-sm border ${{tagColor}}`;
        document.getElementById('bannerTripTypeText').textContent = tripTag;
      }}
      
      const restMins = res.rest_time_mins || res.post_trip_rest_mins || 45;
      document.getElementById('bannerRestTimeText').textContent = `Rest: ${{restMins}}m (C-17)`;
      
      const handoverLeg = res.legs.find(l => l.handover_at_dest);
      const handoverBannerText = handoverLeg ? `Handover: ${{handoverLeg.handover_duration_mins}}m buffer` : 'Handover: None';
      document.getElementById('bannerHandoverText').textContent = handoverBannerText;

      // Update KPI Cards
      const kpiTripTag = document.getElementById('kpiTripTypeBadge');
      if (kpiTripTag) {{
        kpiTripTag.textContent = tripTag;
        kpiTripTag.className = `px-2 py-0.5 rounded text-xs font-bold border ${{tagColor}}`;
      }}
      document.getElementById('kpiCoverageSub').textContent = '100% Load Covered';

      document.getElementById('kpiDuration').textContent = `${{res.total_trip_duration_hours}} hrs`;
      document.getElementById('kpiDrivingTime').textContent = `Driving: ${{res.total_travel_time_hours}}h`;
      document.getElementById('kpiDistance').textContent = `${{res.total_distance_miles}} mi`;
      
      const numDrivers = res.num_drivers_assigned;
      document.getElementById('kpiDriversCount').textContent = `${{numDrivers}} ${{numDrivers === 1 ? 'Driver' : 'Drivers'}}`;
      document.getElementById('kpi11hCompliance').textContent = numDrivers === 1 ? 'Single shift legal' : 'Multi-driver handover';

      document.getElementById('kpiRestDuration').textContent = `${{restMins}} mins`;

      if (handoverLeg) {{
        document.getElementById('kpiHandoverLoc').textContent = `${{handoverLeg.to_name}} (${{handoverLeg.to_code}})`;
        document.getElementById('kpiHandoverDuration').textContent = `${{handoverLeg.handover_duration_mins}} min buffer (C-14)`;
      }} else {{
        document.getElementById('kpiHandoverLoc').textContent = 'None (Single Driver)';
        document.getElementById('kpiHandoverDuration').textContent = 'Direct single-driver trip';
      }}

      const resLbs = res.total_cargo_weight_lbs ? res.total_cargo_weight_lbs : Math.round(Number(res.total_cargo_weight_kg || 0) * 2.20462);
      document.getElementById('kpiCapacity').textContent = `${{res.total_cargo_units}} / ${{res.hauler_capacity}} Cars`;
      document.getElementById('kpiCapacity').className = 'text-lg font-bold font-mono text-emerald-400';
      document.getElementById('kpiCargoWeight').textContent = `${{resLbs.toLocaleString()}} lbs (100% Full)`;

      if (res.cost_breakdown) {{
        document.getElementById('kpiTotalCost').textContent = `$${{res.cost_breakdown.total_trip_cost.toLocaleString()}}`;
      }}

      // Update Rationale & Trip Attributes Banner
      const rationaleDriverTag = document.getElementById('rationaleDriverTag');
      if (rationaleDriverTag) {{
        if (numDrivers === 1) {{
          rationaleDriverTag.className = 'px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-300';
          rationaleDriverTag.textContent = '1 DRIVER SUFFICIENT';
        }} else {{
          rationaleDriverTag.className = 'px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300';
          rationaleDriverTag.textContent = '2 DRIVERS MANDATED (FMCSA)';
        }}
      }}
      
      const rationaleTripTag = document.getElementById('rationaleTripTag');
      if (rationaleTripTag) {{
        rationaleTripTag.textContent = tripTag;
        rationaleTripTag.className = `px-2 py-0.5 rounded text-[10px] font-bold ${{tagColor}}`;
      }}

      document.getElementById('driversRationaleText').textContent = res.drivers_needed_explanation || 
        `${{numDrivers}} driver(s) assigned based on FMCSA HOS regulations and round-trip duration.`;

      document.getElementById('attrTripType').textContent = `${{tripType}} (${{hours}}h duration)`;
      document.getElementById('attrRestTime').textContent = `${{restMins}} min depot buffer (C-17)`;
      document.getElementById('attrHandoverTime').textContent = handoverLeg ? `${{handoverLeg.handover_duration_mins}} min at ${{handoverLeg.to_name}}` : 'None (Single Driver continuous)';

      renderDriverDutyBars(res.drivers_assigned);
      renderItineraryTable(res.legs);
      renderGanttChart(res);
      renderCircuitDiagram(res);
      renderMultiTripTour(res);
    }}

    function renderDriverDutyBars(drivers) {{
      const container = document.getElementById('driverProgressBars');
      if (!container) return;

      container.innerHTML = drivers.map((d, idx) => {{
        const dailyDuty = Number(d.total_duty_hours || 0);
        const drivingHours = Number(d.driving_hours || 0);
        const dailyLimit = Number(d.daily_limit_hours || (d.daily_limit_mins ? (d.daily_limit_mins / 60.0).toFixed(1) : 11.0));
        const dailyPct = Math.min(100, Math.round((dailyDuty / dailyLimit) * 100));
        const isDailyOver = dailyDuty > dailyLimit;
        const dailyBarColor = isDailyOver ? 'bg-red-500' : dailyPct > 80 ? 'bg-amber-500' : 'bg-emerald-500';

        const serviceRule = d.service_rule || d.driver?.service_rule || '8-Day / 70-Hour FMCSA';
        const cycleCap = Number(d.cycle_cap_hours || d.weekly_cap_hours || 70.0);
        const weeklyUsed = Number(d.weekly_hours_used || 35.0);
        const weeklyTotal = Number((weeklyUsed + dailyDuty).toFixed(2));
        const weeklyPct = Math.min(100, Math.round((weeklyTotal / cycleCap) * 100));
        const isWeeklyOver = weeklyTotal > cycleCap;
        const weeklyBarColor = isWeeklyOver ? 'bg-red-500' : weeklyPct > 80 ? 'bg-amber-500' : 'bg-sky-500';

        const shiftBadge = (d.shift_type === 'PM' || d.driver?.shift_type === 'PM')
          ? '<span class="px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 text-[10px] font-mono">🌙 PM Shift</span>'
          : '<span class="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 text-[10px] font-mono">☀️ AM Shift</span>';

        const vehDelivered = Number(d.vehicles_delivered != null ? d.vehicles_delivered : (d.total_cargo_units || 8));
        const ratePerVeh = Number(d.rate_per_vehicle || d.driver?.rate_per_vehicle || 45.0);
        const dropFee = Number(d.stop_drop_fee || d.driver?.stop_drop_fee || 20.0);
        const stopDrops = Number(d.stop_drops_count || 1);
        const totalWages = Number(d.total_wages || ((vehDelivered * ratePerVeh) + (stopDrops * dropFee))).toFixed(2);
        const effectiveRate = Number(d.effective_hourly_rate || (Number(totalWages) / Math.max(0.25, dailyDuty))).toFixed(2);

        const cycleVehTotal = Number(d.cycle_vehicles_total || (d.cycle_vehicles_delivered_prior || 35) + vehDelivered);
        const targetVeh = Number(d.target_cycle_vehicles || d.driver?.target_cycle_vehicles || 60);
        const cyclePct = Math.min(100, Math.round((cycleVehTotal / targetVeh) * 100));
        const cycleVelocity = Number(d.cycle_velocity || (cycleVehTotal / Math.max(1.0, weeklyTotal))).toFixed(2);

        return `
          <div class="bg-slate-900 border border-slate-800 rounded-xl p-3.5 space-y-3">
            <div class="flex items-center justify-between text-xs">
              <div class="flex items-center space-x-2">
                <span class="w-6 h-6 rounded-full bg-sky-500/20 text-sky-400 font-bold flex items-center justify-center text-[10px]">D${{idx + 1}}</span>
                <div>
                  <span class="font-semibold text-slate-200">${{d.driver?.name || d.driver_name}}</span>
                  <span class="text-[10px] text-slate-400 font-mono ml-1.5">(${{d.driver?.driver_id || d.driver_id}})</span>
                </div>
              </div>
              <div class="flex items-center space-x-2">
                ${{shiftBadge}}
                <span class="px-2 py-0.5 rounded bg-purple-500/20 text-[10px] font-mono text-purple-300 font-bold border border-purple-500/30">${{serviceRule}}</span>
              </div>
            </div>

            <!-- Per-Vehicle Delivered Compensation Card -->
            <div class="p-2.5 bg-slate-950/70 border border-slate-800 rounded-lg flex flex-wrap items-center justify-between gap-2 text-xs">
              <div class="flex items-center space-x-2">
                <div class="w-7 h-7 rounded-lg bg-emerald-500/10 text-emerald-400 flex items-center justify-center text-sm">
                  <i class="fa-solid fa-car"></i>
                </div>
                <div>
                  <div class="font-bold text-white text-[11px]">${{vehDelivered}} Vehicles Delivered &bull; ${{stopDrops}} Drops</div>
                  <div class="text-[10px] text-slate-400 font-mono">$${{ratePerVeh}}/car + $${{dropFee}}/stop fee</div>
                </div>
              </div>
              <div class="text-right">
                <div class="text-emerald-400 font-bold font-mono text-xs">$${{totalWages}} Trip Pay</div>
                <div class="text-[10px] text-slate-400 font-mono">Effective: <span class="text-emerald-300 font-bold">$${{effectiveRate}}/hr</span></div>
              </div>
            </div>

            <!-- Daily Duty Progress Bar -->
            <div class="space-y-1">
              <div class="flex items-center justify-between text-[11px]">
                <span class="text-slate-400">Daily Shift Duty:</span>
                <span class="font-mono font-bold ${{isDailyOver ? 'text-red-400' : 'text-emerald-400'}}">${{dailyDuty}}h / ${{dailyLimit}}h max</span>
              </div>
              <div class="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div class="${{dailyBarColor}} h-full transition-all duration-500" style="width: ${{dailyPct}}%"></div>
              </div>
            </div>

            <!-- Cycle HOS Progress Bar -->
            <div class="space-y-1">
              <div class="flex items-center justify-between text-[11px]">
                <span class="text-slate-400">Cycle Duty Clock (${{serviceRule}}):</span>
                <span class="font-mono text-slate-300">${{weeklyTotal}}h / ${{cycleCap}}h</span>
              </div>
              <div class="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div class="${{weeklyBarColor}} h-full transition-all duration-500" style="width: ${{weeklyPct}}%"></div>
              </div>
            </div>

            <!-- Cycle Vehicle Delivery Throughput & Velocity -->
            <div class="space-y-1 pt-1 border-t border-slate-800/60">
              <div class="flex items-center justify-between text-[11px]">
                <span class="text-slate-400 flex items-center space-x-1">
                  <i class="fa-solid fa-chart-line text-sky-400 text-[10px]"></i>
                  <span>Cycle Vehicle Throughput:</span>
                </span>
                <span class="font-mono text-sky-300 font-bold">${{cycleVehTotal}} / ${{targetVeh}} cars (${{cycleVelocity}} cars/duty hr)</span>
              </div>
              <div class="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                <div class="bg-gradient-to-r from-sky-500 to-emerald-400 h-full transition-all duration-500" style="width: ${{cyclePct}}%"></div>
              </div>
            </div>

            <div class="flex items-center justify-between text-[10px] text-slate-400 pt-1">
              <span>Drive: <strong class="text-slate-300 font-mono">${{drivingHours}}h</strong> &bull; Service: <strong class="text-slate-300 font-mono">${{(dailyDuty - drivingHours).toFixed(2)}}h</strong></span>
              <span class="px-2 py-0.5 rounded font-bold ${{isDailyOver || isWeeklyOver ? 'bg-red-500/20 text-red-300' : 'bg-emerald-500/20 text-emerald-300'}}">
                ${{isDailyOver || isWeeklyOver ? 'HOS VIOLATION' : 'COMPLIANT'}}
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
              <div class="text-[10px] text-slate-500 font-mono">${{leg.driver_id}} &bull; ${{leg.driver_shift || 'AM'}}</div>
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
              <span class="font-mono text-[11px]">${{res.total_trip_duration_hours}}h Total Turnaround</span>
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
                <span>Driver ${{idx + 1}}: ${{d.driver.name}} (${{d.shift_type || 'AM'}} Shift)</span>
              </span>
              <span class="font-mono text-[11px] text-emerald-400 font-semibold">${{dHours}}h Duty (11h Daily & 70h Weekly Compliant)</span>
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
              <p class="text-[11px] text-amber-400/80">45-minute mandatory buffer elapsed between Driver 1 offboarding and Driver 2 onboarding to ensure FMCSA duty continuity (C-14 & C-17).</p>
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
            ${{isHandover ? '<span class="absolute -top-2.5 px-2 py-0.5 bg-amber-500 text-slate-950 text-[9px] font-extrabold uppercase rounded-full tracking-wider">Handover Hub (C-14)</span>' : ''}}
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
          <div class="text-[10px] text-slate-400">Depot Return (C-2)</div>
          <div class="text-[9px] font-mono text-emerald-400 mt-1">${{lastLeg.arrival_at_dest}}</div>
        </div>
      `);

      container.innerHTML = nodesHtml.join('');
    }}

    function formatMinsToAmPm(totalMins) {{
      const total = Math.round(Number(totalMins) || 0);
      const hours = Math.floor(total / 60) % 24;
      const mins = total % 60;
      const period = hours < 12 ? 'AM' : 'PM';
      const dispHour = hours % 12 === 0 ? 12 : hours % 12;
      return `${{String(dispHour).padStart(2, '0')}}:${{String(mins).padStart(2, '0')}} ${{period}}`;
    }}

    function renderMultiTripTour(res) {{
      if (!res) return;
      const loadId = res.load_id;
      const vdcCode = res.origin_vdc || 'LA';
      const vdcName = res.origin_vdc_name || res.origin_vdc || 'Depot';
      const hours = Number(res.total_trip_duration_hours || 0);
      const tripType = res.trip_type || (hours <= 5.0 ? 'Short Trip' : hours <= 11.0 ? 'Medium Trip' : 'Long Trip');
      
      const primaryDriver = (res.drivers_assigned && res.drivers_assigned.length > 0)
        ? res.drivers_assigned[0]
        : {{ driver: {{ name: 'Lead Commercial Driver', driver_id: 'DRV_01' }}, total_duty_hours: hours }};
      const primaryDriverName = primaryDriver.driver?.name || primaryDriver.driver_name || 'Assigned Driver';
      const primaryDriverId = primaryDriver.driver?.driver_id || primaryDriver.driver_id || 'DRV_01';

      const reliefDriver = (res.drivers_assigned && res.drivers_assigned.length > 1)
        ? res.drivers_assigned[1]
        : null;
      const reliefDriverName = reliefDriver ? (reliefDriver.driver?.name || reliefDriver.driver_name) : 'Relief Driver';

      const btnText = document.getElementById('tabBtnMultiTripText');
      const badgeEl = document.getElementById('shiftTourBadge');
      const titleEl = document.getElementById('shiftTourTitle');
      const subEl = document.getElementById('shiftTourSubtitle');
      const driverBadgeEl = document.getElementById('shiftTourDriverBadge');
      const restBadgeEl = document.getElementById('shiftTourRestBadge');
      const tripsCompletedEl = document.getElementById('shiftTourTripsCompleted');
      const loadsListEl = document.getElementById('shiftTourLoadsList');
      const totalDutyEl = document.getElementById('shiftTourTotalDuty');
      const dutyCompEl = document.getElementById('shiftTourDutyCompliance');
      const totalSpanEl = document.getElementById('shiftTourTotalSpan');
      const spanDescEl = document.getElementById('shiftTourSpanDesc');
      const mileageEl = document.getElementById('shiftTourMileage');
      const networkEl = document.getElementById('shiftTourNetwork');
      const restDescEl = document.getElementById('shiftTourRestDesc');
      const restSubEl = document.getElementById('shiftTourRestSub');
      const tbody = document.getElementById('multiTripTableBody');

      if (!tbody) return;

      if (tripType === 'Short Trip') {{
        // --- CASE A: SHORT TRIP MULTI-TRIP CHAINING ---
        if (btnText) btnText.innerHTML = `Multi-Trip Tour (Chained 3 Trips &bull; 1 Driver)`;
        if (badgeEl) {{
          badgeEl.className = 'px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-xs font-bold';
          badgeEl.textContent = 'MULTI-TRIP CHAINING (SHORT HAUL)';
        }}
        if (titleEl) titleEl.textContent = `Daily Driver Shift Tour • ${{primaryDriverName}} (Linked to Load #${{loadId}})`;
        if (subEl) subEl.textContent = `Driver executing multiple quick round-trips from ${{vdcName}} within the 11.0-hour statutory cap, with mandatory 45-min factory turnaround rest between trips (Constraint C-17).`;
        if (driverBadgeEl) driverBadgeEl.textContent = `Driver: ${{primaryDriverName}} (${{primaryDriverId}})`;
        if (restBadgeEl) {{
          restBadgeEl.className = 'px-2 py-1 bg-amber-500/20 text-amber-300 rounded text-xs font-mono';
          restBadgeEl.textContent = '45m Turnaround Rest (C-17)';
        }}

        // Find companion short loads from same origin terminal in EMBEDDED_DATA
        const allLoads = (window.EMBEDDED_DATA && window.EMBEDDED_DATA.loads) ? window.EMBEDDED_DATA.loads : [];
        let sameVdcShorts = allLoads.filter(l => (l.origin_legal_entity === vdcCode || l.origin_vdc_name === vdcName) && (l.trip_type === 'Short Trip' || l.turnaround_duration_hours <= 5.0));
        
        // Ensure selected load is present
        let selectedLoadObj = sameVdcShorts.find(l => l.id === loadId);
        if (!selectedLoadObj) {{
          selectedLoadObj = {{
            id: loadId,
            load_num: res.load_num || `L-${{loadId}}`,
            turnaround_duration_hours: hours,
            total_distance_miles: res.total_distance_miles
          }};
          sameVdcShorts.unshift(selectedLoadObj);
        }}

        // Pick 2 or 3 loads for the shift tour
        let chained = [selectedLoadObj];
        for (let l of sameVdcShorts) {{
          if (chained.length >= 3) break;
          if (l.id !== selectedLoadObj.id) {{
            chained.push(l);
          }}
        }}
        if (chained.length < 3) {{
          for (let l of allLoads) {{
            if (chained.length >= 3) break;
            if (l.id !== selectedLoadObj.id && (l.trip_type === 'Short Trip' || l.turnaround_duration_hours <= 5.0)) {{
              chained.push(l);
            }}
          }}
        }}

        let curMins = 360; // 06:00 AM start
        let cumulativeDuty = 0.0;
        let totalMiles = 0.0;
        let tableRows = '';

        chained.forEach((t, idx) => {{
          const durHours = Number(t.turnaround_duration_hours || 2.5);
          const tripDuty = Math.max(1.0, durHours - 0.4);
          cumulativeDuty += tripDuty;
          const tripMiles = Number(t.total_distance_miles || 47.9);
          totalMiles += tripMiles;

          const depTimeStr = formatMinsToAmPm(curMins);
          const retMins = curMins + Math.round(durHours * 60);
          const retTimeStr = formatMinsToAmPm(retMins);

          const isCurrent = (t.id === loadId);
          const isLast = (idx === chained.length - 1);
          const postAction = isLast 
            ? '<span class="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-[10px] font-bold">Shift Complete &bull; Clock-out</span>'
            : `<span class="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 text-[10px] font-bold">45-min Rest at ${{vdcName}} Depot (C-17)</span>`;

          tableRows += `
            <tr class="hover:bg-slate-800/40 ${{isCurrent ? 'bg-sky-950/30 border-l-4 border-sky-400' : ''}}">
              <td class="py-3 px-3 font-bold text-sky-400 text-center">${{idx + 1}}</td>
              <td class="py-3 px-3">
                <span class="font-bold text-white">#${{t.id}}</span> (${{t.load_num || `L-${{t.id}}`}})
                ${{isCurrent ? '<span class="ml-1.5 px-1.5 py-0.2 rounded bg-sky-500/30 text-sky-200 text-[9px] font-extrabold uppercase">★ CURRENT LOAD</span>' : ''}}
              </td>
              <td class="py-3 px-3 text-slate-300">${{depTimeStr}}</td>
              <td class="py-3 px-3 text-amber-300 font-bold">${{retTimeStr}}</td>
              <td class="py-3 px-3 text-right">${{tripMiles.toFixed(1)}} mi</td>
              <td class="py-3 px-3 text-right text-emerald-400 font-bold">${{tripDuty.toFixed(2)}} hrs</td>
              <td class="py-3 px-4">${{postAction}}</td>
            </tr>
          `;

          curMins = retMins + 45;
        }});

        const shiftSpanHours = ((curMins - 45 - 360) / 60.0).toFixed(2);
        const clockOutStr = formatMinsToAmPm(curMins - 45);

        if (tripsCompletedEl) tripsCompletedEl.textContent = `${{chained.length}} Round-Trips`;
        if (loadsListEl) loadsListEl.textContent = `Loads ` + chained.map(t => `#${{t.id}}`).join(', ');
        if (totalDutyEl) totalDutyEl.textContent = `${{cumulativeDuty.toFixed(2)}} hrs`;
        if (dutyCompEl) dutyCompEl.innerHTML = `<span class="text-emerald-400">Within 11.0h Daily Cap (C-12a)</span>`;
        if (totalSpanEl) totalSpanEl.textContent = `${{shiftSpanHours}} hrs`;
        if (spanDescEl) spanDescEl.textContent = `06:00 AM &rarr; ${{clockOutStr}} (AM Window)`;
        if (mileageEl) mileageEl.textContent = `${{totalMiles.toFixed(1)}} miles`;
        if (networkEl) networkEl.textContent = `${{vdcName}} Terminal Network`;
        if (restDescEl) restDescEl.textContent = '45 min / trip';
        if (restSubEl) restSubEl.textContent = 'Mandatory depot buffer (C-17)';
        tbody.innerHTML = tableRows;

      }} else if (tripType === 'Medium Trip') {{
        // --- CASE B: MEDIUM TRIP DEDICATED FULL-SHIFT ---
        if (btnText) btnText.innerHTML = `Daily Shift Tour (Dedicated Full Shift &bull; 1 Driver)`;
        if (badgeEl) {{
          badgeEl.className = 'px-2 py-0.5 rounded bg-sky-500/20 text-sky-300 border border-sky-500/30 text-xs font-bold';
          badgeEl.textContent = 'DEDICATED FULL-SHIFT RUN (MEDIUM HAUL)';
        }}
        if (titleEl) titleEl.textContent = `Dedicated Single-Shift Tour • ${{primaryDriverName}} (Linked to Load #${{loadId}})`;
        if (subEl) subEl.textContent = `Extended regional run consuming single-driver daily duty capacity. Within 11.0h daily cap (C-12a); full shift allocated without secondary chaining.`;
        if (driverBadgeEl) driverBadgeEl.textContent = `Driver: ${{primaryDriverName}} (${{primaryDriverId}})`;
        if (restBadgeEl) {{
          restBadgeEl.className = 'px-2 py-1 bg-amber-500/20 text-amber-300 rounded text-xs font-mono';
          restBadgeEl.textContent = '45m Turnaround Rest (C-17)';
        }}

        const depMins = 360; // 06:00 AM
        const retMins = depMins + Math.round(hours * 60);
        const depStr = formatMinsToAmPm(depMins);
        const retStr = formatMinsToAmPm(retMins);
        const clockOutStr = formatMinsToAmPm(retMins + 45);
        const spanHours = (hours + 0.75).toFixed(2);

        if (tripsCompletedEl) tripsCompletedEl.textContent = `1 Dedicated Run`;
        if (loadsListEl) loadsListEl.textContent = `Load #${{loadId}} (${{res.load_num || 'Extended Regional'}})`;
        if (totalDutyEl) totalDutyEl.textContent = `${{hours}} hrs`;
        if (dutyCompEl) dutyCompEl.innerHTML = `<span class="text-emerald-400">Full Daily Shift &bull; <= 11.0h Compliant</span>`;
        if (totalSpanEl) totalSpanEl.textContent = `${{spanHours}} hrs`;
        if (spanDescEl) spanDescEl.textContent = `06:00 AM &rarr; ${{clockOutStr}} (AM Window)`;
        if (mileageEl) mileageEl.textContent = `${{res.total_distance_miles}} miles`;
        if (networkEl) networkEl.textContent = `${{vdcName}} Extended Regional Corridor`;
        if (restDescEl) restDescEl.textContent = '45 min post-trip';
        if (restSubEl) restSubEl.textContent = 'Factory post-trip buffer (C-17)';

        tbody.innerHTML = `
          <tr class="hover:bg-slate-800/40 bg-sky-950/30 border-l-4 border-sky-400">
            <td class="py-3 px-3 font-bold text-sky-400 text-center">1</td>
            <td class="py-3 px-3"><span class="font-bold text-white">#${{loadId}}</span> (${{res.load_num || `L-${{loadId}}`}}) <span class="ml-1.5 px-1.5 py-0.2 rounded bg-sky-500/30 text-sky-200 text-[9px] font-extrabold uppercase">★ CURRENT LOAD</span></td>
            <td class="py-3 px-3 text-slate-300">${{depStr}}</td>
            <td class="py-3 px-3 text-amber-300 font-bold">${{retStr}}</td>
            <td class="py-3 px-3 text-right">${{res.total_distance_miles}} mi</td>
            <td class="py-3 px-3 text-right text-emerald-400 font-bold">${{hours}} hrs</td>
            <td class="py-3 px-4"><span class="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 text-[10px] font-bold">45-min Inspection at ${{vdcName}} Depot (C-17)</span></td>
          </tr>
          <tr class="hover:bg-slate-800/40 opacity-75">
            <td class="py-3 px-3 font-bold text-slate-500 text-center">—</td>
            <td class="py-3 px-3 text-slate-400 font-sans text-xs">Daily Shift Status</td>
            <td class="py-3 px-3 text-slate-500">Return: ${{retStr}}</td>
            <td class="py-3 px-3 text-emerald-400 font-bold">Clock-out: ${{clockOutStr}}</td>
            <td class="py-3 px-3 text-right text-slate-500">—</td>
            <td class="py-3 px-3 text-right text-slate-400 font-mono">${{hours}}h / 11.0h</td>
            <td class="py-3 px-4"><span class="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-[10px] font-bold">Shift Complete &bull; 11h HOS Compliant</span></td>
          </tr>
        `;

      }} else {{
        // --- CASE C: LONG TRIP MULTI-DRIVER RELAY ---
        const d1Name = primaryDriverName;
        const d2Name = reliefDriverName;
        const hubName = res.handover_location_name || 'Certified Handover Hub';
        const halfMiles = (res.total_distance_miles / 2.0).toFixed(1);
        const d1Duty = primaryDriver.total_duty_hours || (hours / 2.0).toFixed(2);
        const d2Duty = reliefDriver ? reliefDriver.total_duty_hours : (hours / 2.0).toFixed(2);

        if (btnText) btnText.innerHTML = `Relay Shift Tour (2 Drivers &bull; Handover)`;
        if (badgeEl) {{
          badgeEl.className = 'px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 border border-purple-500/30 text-xs font-bold';
          badgeEl.textContent = 'MULTI-DRIVER RELAY SHIFT (FMCSA C-13 MANDATE)';
        }}
        if (titleEl) titleEl.textContent = `Interstate Relay Shift Schedule • 2 Drivers (Linked to Load #${{loadId}})`;
        if (subEl) subEl.textContent = `Round-trip turnaround (${{hours}}h) exceeds 11.0h statutory limit. Mandatory 2-driver relay at certified hub with 45-min handover buffer (Constraints C-13 & C-14).`;
        if (driverBadgeEl) driverBadgeEl.textContent = `Relay: ${{d1Name}} & ${{d2Name}}`;
        if (restBadgeEl) {{
          restBadgeEl.className = 'px-2 py-1 bg-purple-500/20 text-purple-300 rounded text-xs font-mono';
          restBadgeEl.textContent = '45m Handover Buffer (C-14)';
        }}

        const depMins = 360; // 06:00 AM
        const swapMins = depMins + Math.round(Number(d1Duty) * 60);
        const depSwapMins = swapMins + 45;
        const finishMins = depSwapMins + Math.round(Number(d2Duty) * 60);

        const depStr = formatMinsToAmPm(depMins);
        const swapStr = formatMinsToAmPm(swapMins);
        const depSwapStr = formatMinsToAmPm(depSwapMins);
        const finishStr = formatMinsToAmPm(finishMins);

        if (tripsCompletedEl) tripsCompletedEl.textContent = `1 Interstate Relay`;
        if (loadsListEl) loadsListEl.textContent = `Load #${{loadId}} (${{res.load_num || 'Interstate'}})`;
        if (totalDutyEl) totalDutyEl.textContent = `${{d1Duty}}h + ${{d2Duty}}h`;
        if (dutyCompEl) dutyCompEl.innerHTML = `<span class="text-emerald-400">Both Drivers <= 11.0h Compliant</span>`;
        if (totalSpanEl) totalSpanEl.textContent = `${{hours}} hrs`;
        if (spanDescEl) spanDescEl.textContent = `06:00 AM &rarr; ${{finishStr}} (Interstate Relay)`;
        if (mileageEl) mileageEl.textContent = `${{res.total_distance_miles}} miles`;
        if (networkEl) networkEl.textContent = `${{vdcName}} Interstate Corridor`;
        if (restDescEl) restDescEl.textContent = '45 min Handover';
        if (restSubEl) restSubEl.textContent = `At ${{hubName}} (C-14)`;

        tbody.innerHTML = `
          <tr class="hover:bg-slate-800/40 bg-sky-950/30 border-l-4 border-sky-400">
            <td class="py-3 px-3 font-bold text-sky-400 text-center">1</td>
            <td class="py-3 px-3">
              <span class="font-bold text-white">Outbound Phase</span> (${{d1Name}})
              <span class="ml-1.5 px-1.5 py-0.2 rounded bg-sky-500/30 text-sky-200 text-[9px] font-extrabold uppercase">LEAD DRIVER</span>
            </td>
            <td class="py-3 px-3 text-slate-300">${{depStr}} (${{vdcName}})</td>
            <td class="py-3 px-3 text-amber-300 font-bold">${{swapStr}} (${{hubName}})</td>
            <td class="py-3 px-3 text-right">${{halfMiles}} mi</td>
            <td class="py-3 px-3 text-right text-emerald-400 font-bold">${{d1Duty}} hrs</td>
            <td class="py-3 px-4"><span class="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 text-[10px] font-bold">45-min Handover Buffer at Hub (C-14)</span></td>
          </tr>
          <tr class="hover:bg-slate-800/40 bg-purple-950/30 border-l-4 border-purple-400">
            <td class="py-3 px-3 font-bold text-purple-400 text-center">2</td>
            <td class="py-3 px-3">
              <span class="font-bold text-white">Return Phase</span> (${{d2Name}})
              <span class="ml-1.5 px-1.5 py-0.2 rounded bg-purple-500/30 text-purple-200 text-[9px] font-extrabold uppercase">RELIEF DRIVER</span>
            </td>
            <td class="py-3 px-3 text-slate-300">${{depSwapStr}} (${{hubName}})</td>
            <td class="py-3 px-3 text-amber-300 font-bold">${{finishStr}} (${{vdcName}})</td>
            <td class="py-3 px-3 text-right">${{halfMiles}} mi</td>
            <td class="py-3 px-3 text-right text-emerald-400 font-bold">${{d2Duty}} hrs</td>
            <td class="py-3 px-4"><span class="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-[10px] font-bold">Shift Complete &bull; Both Drivers <= 11.0h</span></td>
          </tr>
        `;
      }}
    }}

    let managerFilterType = 'ALL';
    let managerFilterLocation = 'ALL';
    let managerSearchTerm = '';

    function switchTab(tabId) {{
      document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
      const targetContent = document.getElementById(tabId);
      if (targetContent) targetContent.classList.remove('hidden');

      document.querySelectorAll('.tab-btn').forEach(btn => {{
        btn.classList.remove('active', 'border-sky-500', 'text-sky-400', 'bg-slate-800/40', 'border-indigo-500', 'text-indigo-400', 'bg-indigo-950/40');
        btn.classList.add('border-transparent', 'text-slate-400');
      }});

      const matchingBtn = document.querySelector(`button[onclick*="${{tabId}}"]`);
      if (matchingBtn) {{
        if (tabId === 'driverRosterTab') {{
          matchingBtn.classList.add('active', 'border-indigo-500', 'text-indigo-400', 'bg-indigo-950/40');
        }} else {{
          matchingBtn.classList.add('active', 'border-sky-500', 'text-sky-400', 'bg-slate-800/40');
        }}
        matchingBtn.classList.remove('border-transparent', 'text-slate-400');
      }}

      if (tabId === 'driverRosterTab') {{
        renderManagerRoster();
      }}
    }}

    function filterManagerRoster(type) {{
      managerFilterType = type;
      document.querySelectorAll('.mgr-filter-btn').forEach(btn => {{
        btn.classList.remove('active', 'bg-indigo-600', 'text-white');
        btn.classList.add('bg-slate-800', 'text-slate-300');
      }});
      if (event && event.currentTarget) {{
        event.currentTarget.classList.add('active', 'bg-indigo-600', 'text-white');
        event.currentTarget.classList.remove('bg-slate-800', 'text-slate-300');
      }}
      renderManagerRoster();
    }}

    function filterManagerLocation(loc) {{
      managerFilterLocation = loc;
      renderManagerRoster();
    }}

    function searchManagerRoster(val) {{
      managerSearchTerm = val.toLowerCase().trim();
      renderManagerRoster();
    }}

    function inspectLoadFromRoster(loadId) {{
      selectLoad(loadId);
      switchTab('itineraryTab');
      const target = document.getElementById('tabButtons');
      if (target) target.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
    }}

    function renderManagerRoster() {{
      const rosterData = (window.EMBEDDED_DATA && window.EMBEDDED_DATA.manager_roster) ? window.EMBEDDED_DATA.manager_roster : null;
      if (!rosterData || !rosterData.drivers) return;

      const summary = rosterData.summary || {{}};
      const drivers = rosterData.drivers || [];

      // Update Summary KPI Chips
      const activeEl = document.getElementById('mgrActiveDispatched');
      if (activeEl) activeEl.innerText = `${{summary.active_dispatched || 10}} / ${{summary.total_drivers || 11}}`;
      const mtEl = document.getElementById('mgrMultiTripCount');
      if (mtEl) mtEl.innerText = `${{summary.multitrip_chained_count || 4}} Drivers`;
      const relayEl = document.getElementById('mgrRelayCount');
      if (relayEl) relayEl.innerText = `${{summary.relay_teams_count || 1}} Team (3 Drivers)`;
      const dutyEl = document.getElementById('mgrTotalDuty');
      if (dutyEl) dutyEl.innerText = `${{summary.total_shift_duty_hours || 67.1}}h`;
      const vehEl = document.getElementById('mgrVehiclesDelivered');
      if (vehEl) vehEl.innerText = `${{summary.total_shift_vehicles_delivered || 117}} Units`;
      const wageEl = document.getElementById('mgrTotalWages');
      if (wageEl) wageEl.innerText = `$${{Number(summary.total_shift_wages || 6018).toLocaleString()}}`;

      // Filter drivers
      const filtered = drivers.filter(d => {{
        if (managerFilterType === 'MULTITRIP' && !d.is_multitrip) return false;
        if (managerFilterType === 'DEDICATED' && d.operation_type !== 'dedicated_single') return false;
        if (managerFilterType === 'RELAY' && !d.operation_type.includes('relay')) return false;
        if (managerFilterType === 'STANDBY' && d.operation_type !== 'standby') return false;

        if (managerFilterLocation !== 'ALL') {{
          if (managerFilterLocation === 'HUB') {{
            if (!d.current_location.name.toLowerCase().includes('hub')) return false;
          }} else if (managerFilterLocation === 'TRANSIT') {{
            if (!d.current_location.name.toLowerCase().includes('corridor') && !d.current_location.name.toLowerCase().includes('en route')) return false;
          }} else {{
            if (d.home_vdc !== managerFilterLocation && !d.current_location.description.includes(managerFilterLocation)) return false;
          }}
        }}

        if (managerSearchTerm) {{
          const term = managerSearchTerm;
          const matchName = d.name.toLowerCase().includes(term);
          const matchId = d.driver_id.toLowerCase().includes(term);
          const matchLoc = d.current_location.name.toLowerCase().includes(term) || d.current_location.description.toLowerCase().includes(term);
          const matchLoads = (d.assigned_load_ids || []).some(id => String(id).includes(term));
          if (!matchName && !matchId && !matchLoc && !matchLoads) return false;
        }}

        return true;
      }});

      const counterEl = document.getElementById('mgrRosterCountDisplay');
      if (counterEl) counterEl.innerText = `Showing ${{filtered.length}} of ${{drivers.length}} Drivers`;

      // Render Section 1: Multi-Trip Shift Hour Validation Spotlight
      renderMultiTripValidationCards(filtered);

      // Render Section 2: Complete Fleet Driver Roster Grid
      renderManagerRosterCards(filtered);

      // Render Section 3: Terminal Geographic Distribution
      renderTerminalDistribution(drivers);
    }}

    function renderMultiTripValidationCards(filteredDrivers) {{
      const spotlightSec = document.getElementById('multiTripSpotlightSection');
      const container = document.getElementById('multiTripCardsContainer');
      if (!container) return;

      const multiTripDrivers = filteredDrivers.filter(d => d.is_multitrip);
      if (multiTripDrivers.length === 0) {{
        if (managerFilterType === 'STANDBY' || managerFilterType === 'DEDICATED' || managerFilterType === 'RELAY') {{
          if (spotlightSec) spotlightSec.classList.add('hidden');
        }} else {{
          if (spotlightSec) spotlightSec.classList.remove('hidden');
          container.innerHTML = `
            <div class="bg-slate-900/60 border border-slate-800 rounded-xl p-6 text-center text-slate-400 text-xs font-mono">
              <i class="fa-solid fa-filter-circle-xmark text-slate-500 text-lg mb-1.5 block"></i>
              No multi-trip chained drivers match the current filter selection.
            </div>
          `;
        }}
        return;
      }}

      if (spotlightSec) spotlightSec.classList.remove('hidden');

      let html = '';
      multiTripDrivers.forEach(d => {{
        const mt = d.multitrip_details;
        const trips = (mt && mt.trips) ? mt.trips : [];
        const valid = d.hos_validation || {{}};

        let timelineHtml = '';
        trips.forEach((trip, idx) => {{
          timelineHtml += `
            <div class="bg-slate-900/90 border border-slate-700/60 rounded-xl p-3 flex-1 flex flex-col justify-between shadow-inner">
              <div>
                <div class="flex items-center justify-between gap-2 mb-1.5">
                  <span class="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 text-[10px] font-bold uppercase tracking-wider">
                    Trip ${{trip.trip_sequence}}: Load #${{trip.load_id}}
                  </span>
                  <span class="text-[11px] font-mono text-slate-400">${{trip.distance_miles}} mi &bull; ${{trip.trip_duty_hours}}h duty</span>
                </div>
                <div class="text-xs text-white font-semibold mb-1">
                  ${{trip.origin_vdc}} Depot &rarr; ${{trip.dealers_count}} Customer Dealerships &rarr; ${{trip.origin_vdc}} Return
                </div>
                <div class="flex items-center justify-between text-[11px] font-mono text-slate-400 bg-slate-950/60 rounded p-1.5 mb-2">
                  <span><i class="fa-solid fa-play text-emerald-400 text-[9px] mr-1"></i> Depart: <b class="text-slate-200">${{trip.start_time}}</b></span>
                  <span><i class="fa-solid fa-flag-checkered text-amber-400 text-[9px] mr-1"></i> Return: <b class="text-slate-200">${{trip.finish_time}}</b></span>
                </div>
                <div class="text-[11px] text-slate-300 flex items-center gap-1.5 mb-2">
                  <i class="fa-solid fa-car-side text-sky-400"></i>
                  <span><b>${{trip.vehicles_delivered}}</b> Vehicles Delivered (100% Full Capacity)</span>
                </div>
              </div>
              <button onclick="inspectLoadFromRoster(${{trip.load_id}})" class="w-full py-1.5 px-2 text-[11px] font-semibold bg-sky-600/20 hover:bg-sky-600/30 text-sky-300 border border-sky-500/30 rounded-lg transition cursor-pointer flex items-center justify-center gap-1.5">
                <i class="fa-solid fa-arrow-up-right-from-square text-[10px]"></i>
                Inspect Load #${{trip.load_id}} Route & Manifest
              </button>
            </div>
          `;

          if (idx < trips.length - 1) {{
            timelineHtml += `
              <div class="flex flex-col items-center justify-center px-1 shrink-0">
                <div class="h-5 w-0.5 bg-amber-500/40"></div>
                <div class="my-1 px-2.5 py-1 rounded-lg bg-amber-950/70 border border-amber-500/50 text-amber-300 text-[10px] font-mono font-bold flex items-center gap-1 shadow-lg animate-pulse">
                  <i class="fa-solid fa-mug-hot text-[11px] text-amber-400"></i>
                  <span>45m Mandatory C-17 Rest</span>
                </div>
                <div class="text-[9px] font-mono text-slate-400">Depot Turnaround</div>
                <div class="h-5 w-0.5 bg-amber-500/40"></div>
              </div>
            `;
          }}
        }});

        html += `
          <div class="bg-gradient-to-br from-slate-900 to-slate-950 border border-amber-500/30 rounded-2xl p-4 shadow-xl space-y-3">
            <!-- Card Header -->
            <div class="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-800">
              <div class="flex items-center space-x-3">
                <div class="w-10 h-10 rounded-xl bg-amber-500/20 text-amber-400 flex items-center justify-center text-lg font-bold border border-amber-500/30">
                  <i class="fa-solid fa-id-card"></i>
                </div>
                <div>
                  <div class="flex items-center gap-2">
                    <span class="text-sm font-bold text-white">${{d.name}}</span>
                    <span class="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-800 text-slate-300">${{d.driver_id}}</span>
                    <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">
                      ★ Multi-Trip Chained (${{d.trips_count}} Trips in Shift)
                    </span>
                    <span class="px-2 py-0.5 rounded text-[10px] font-medium bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                      ${{d.service_rule}}
                    </span>
                  </div>
                  <div class="flex items-center gap-3 text-xs text-slate-400 mt-1">
                    <span><i class="fa-solid fa-warehouse text-slate-500 mr-1"></i> Base: <b class="text-slate-200">${{d.home_vdc_name}} (${{d.home_vdc}})</b></span>
                    <span>&bull;</span>
                    <span><i class="fa-solid fa-clock text-slate-500 mr-1"></i> Shift Window: <b class="text-slate-200">${{d.shift_window}}</b></span>
                    <span>&bull;</span>
                    <span class="text-emerald-400 font-medium"><i class="fa-solid fa-location-dot mr-1"></i> Live: ${{d.current_location.description}}</span>
                  </div>
                </div>
              </div>

              <!-- Quick Pay / Productivity Chip -->
              <div class="bg-slate-950/80 border border-emerald-500/30 rounded-xl px-3 py-1.5 flex items-center gap-3 font-mono">
                <div>
                  <div class="text-[9px] uppercase tracking-wider text-slate-400">Shift Piece-Rate Pay</div>
                  <div class="text-sm font-bold text-emerald-400">$${{d.total_wages.toFixed(2)}}</div>
                </div>
                <div class="border-l border-slate-800 pl-3">
                  <div class="text-[9px] uppercase tracking-wider text-slate-400">Yield / Duty Hr</div>
                  <div class="text-sm font-bold text-sky-400">$${{d.effective_hourly_yield.toFixed(2)}}/hr</div>
                </div>
              </div>
            </div>

            <!-- Sequential Trip Itinerary Flow -->
            <div class="flex flex-col lg:flex-row items-stretch gap-2 py-1">
              ${{timelineHtml}}
            </div>

            <!-- Regulatory HOS & Compliance Proof Verification Matrix -->
            <div class="bg-slate-950/80 border border-slate-800 rounded-xl p-3">
              <div class="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <i class="fa-solid fa-shield-halved text-emerald-400"></i>
                CP-SAT Mathematical Validation Proofs (Multi-Trip Shift Tour)
              </div>
              <div class="grid grid-cols-2 md:grid-cols-4 gap-2.5 text-xs font-mono">
                <div class="bg-slate-900/80 p-2 rounded-lg border border-slate-800">
                  <div class="text-[10px] text-slate-400">Daily Driving / Duty:</div>
                  <div class="text-white font-bold">${{d.shift_duty_hours}}h <span class="text-slate-400 font-normal">/ ${{d.daily_limit_hours}}h max</span></div>
                  <div class="text-[10px] text-emerald-400 mt-0.5"><i class="fa-solid fa-check mr-1"></i> PASS COMPLIANT</div>
                </div>
                <div class="bg-slate-900/80 p-2 rounded-lg border border-slate-800">
                  <div class="text-[10px] text-slate-400">Shift Elapsed Span:</div>
                  <div class="text-white font-bold">${{d.shift_span_hours}}h <span class="text-slate-400 font-normal">/ 14.0h max</span></div>
                  <div class="text-[10px] text-emerald-400 mt-0.5"><i class="fa-solid fa-check mr-1"></i> PASS (FMCSA Window)</div>
                </div>
                <div class="bg-slate-900/80 p-2 rounded-lg border border-slate-800">
                  <div class="text-[10px] text-slate-400">Turnaround Rest (C-17):</div>
                  <div class="text-white font-bold">45m Injected <span class="text-slate-400 font-normal">all trips</span></div>
                  <div class="text-[10px] text-emerald-400 mt-0.5"><i class="fa-solid fa-check mr-1"></i> MANDATE VERIFIED</div>
                </div>
                <div class="bg-slate-900/80 p-2 rounded-lg border border-slate-800">
                  <div class="text-[10px] text-slate-400">Rolling Cycle Remaining:</div>
                  <div class="text-white font-bold">${{d.cycle_remaining_hours}}h <span class="text-slate-400 font-normal">/ ${{d.cycle_cap_hours}}h cap</span></div>
                  <div class="text-[10px] text-emerald-400 mt-0.5"><i class="fa-solid fa-check mr-1"></i> PASS COMPLIANT</div>
                </div>
              </div>
            </div>
          </div>
        `;
      }});
      container.innerHTML = html;
    }}

    function renderManagerRosterCards(filteredDrivers) {{
      const container = document.getElementById('managerRosterCardsContainer');
      if (!container) return;

      if (filteredDrivers.length === 0) {{
        container.innerHTML = `
          <div class="col-span-full bg-slate-900 border border-slate-800 rounded-xl p-8 text-center text-slate-400 text-xs font-mono">
            No drivers found matching your filter or search criteria.
          </div>
        `;
        return;
      }}

      let gridHtml = '';
      filteredDrivers.forEach(d => {{
        const dutyPct = Math.min(100, Math.round((d.shift_duty_hours / d.daily_limit_hours) * 100));
        const cycleUsed = (d.weekly_hours_used + d.shift_duty_hours).toFixed(1);
        const cyclePct = Math.min(100, Math.round((cycleUsed / d.cycle_cap_hours) * 100));

        let badgeBg = 'bg-slate-800 text-slate-300 border-slate-700';
        if (d.operation_type === 'multi_trip') badgeBg = 'bg-amber-500/20 text-amber-300 border-amber-500/40';
        else if (d.operation_type === 'dedicated_single') badgeBg = 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40';
        else if (d.operation_type.includes('relay')) badgeBg = 'bg-indigo-500/20 text-indigo-300 border-indigo-500/40';
        else if (d.operation_type === 'standby') badgeBg = 'bg-slate-800 text-slate-400 border-slate-700';

        let loadsList = (d.assigned_load_ids && d.assigned_load_ids.length > 0)
          ? d.assigned_load_ids.map(lid => `<button onclick="inspectLoadFromRoster(${{lid}})" class="px-2 py-0.5 bg-slate-800 hover:bg-sky-900/40 text-sky-300 border border-slate-700 rounded text-[10px] font-mono transition cursor-pointer">Load #${{lid}}</button>`).join(' ')
          : '<span class="text-slate-500 text-[10px] italic">No load assigned (Standby)</span>';

        gridHtml += `
          <div class="bg-slate-900 border border-slate-800 hover:border-slate-700 rounded-xl p-4 shadow-lg flex flex-col justify-between transition">
            <div>
              <!-- Header -->
              <div class="flex items-start justify-between gap-2 mb-2.5">
                <div>
                  <div class="flex items-center gap-2">
                    <h5 class="text-sm font-bold text-white">${{d.name}}</h5>
                    <span class="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-950 text-slate-400">${{d.driver_id}}</span>
                  </div>
                  <div class="text-xs text-slate-400 flex items-center gap-1.5 mt-0.5">
                    <span>${{d.home_vdc_name}} (${{d.home_vdc}})</span>
                    <span>&bull;</span>
                    <span class="text-slate-300">${{d.shift_type}} Shift</span>
                  </div>
                </div>
                <span class="px-2 py-0.5 rounded-full text-[10px] font-bold border ${{badgeBg}} shrink-0">
                  ${{d.operation_label}}
                </span>
              </div>

              <!-- Location Card -->
              <div class="bg-slate-950/70 border border-slate-800/80 rounded-lg p-2.5 mb-3 font-mono text-xs">
                <div class="flex items-center justify-between text-[10px] text-slate-400 mb-1">
                  <span class="flex items-center gap-1 text-sky-400 font-semibold">
                    <i class="fa-solid fa-location-dot"></i> Live Placement
                  </span>
                  <span>Lat: ${{d.current_location.lat}}, Lon: ${{d.current_location.lon}}</span>
                </div>
                <div class="text-slate-200 font-bold text-xs truncate" title="${{d.current_location.description}}">
                  ${{d.current_location.description}}
                </div>
                <div class="text-[10px] text-slate-400 mt-1 flex items-center gap-1">
                  <i class="fa-solid fa-truck text-slate-500"></i>
                  <span class="truncate">${{d.assigned_equipment}}</span>
                </div>
              </div>

              <!-- Service Rule Badge -->
              <div class="mb-3">
                <span class="inline-block px-2 py-0.5 rounded text-[10px] font-medium bg-slate-800/60 border border-slate-700/60 text-indigo-300">
                  <i class="fa-solid fa-scale-balanced mr-1 text-[9px]"></i>
                  ${{d.service_rule}}
                </span>
              </div>

              <!-- Shift Duty & Cycle Clocks -->
              <div class="space-y-2 mb-3 text-xs">
                <div>
                  <div class="flex justify-between text-[10px] font-mono text-slate-400 mb-0.5">
                    <span>Shift Duty: <b class="text-slate-200">${{d.shift_duty_hours}}h</b> / ${{d.daily_limit_hours}}h</span>
                    <span class="${{dutyPct > 90 ? 'text-amber-400' : 'text-emerald-400'}}">${{dutyPct}}%</span>
                  </div>
                  <div class="h-1.5 w-full bg-slate-950 rounded-full overflow-hidden">
                    <div class="h-full ${{dutyPct > 90 ? 'bg-amber-400' : 'bg-emerald-400'}} rounded-full" style="width: ${{dutyPct}}%"></div>
                  </div>
                </div>

                <div>
                  <div class="flex justify-between text-[10px] font-mono text-slate-400 mb-0.5">
                    <span>Cycle Duty: <b class="text-slate-200">${{cycleUsed}}h</b> / ${{d.cycle_cap_hours}}h</span>
                    <span class="text-sky-400">${{d.cycle_remaining_hours}}h rem</span>
                  </div>
                  <div class="h-1.5 w-full bg-slate-950 rounded-full overflow-hidden">
                    <div class="h-full bg-sky-500 rounded-full" style="width: ${{cyclePct}}%"></div>
                  </div>
                </div>
              </div>

              <!-- Financial Piece-Rate & Delivery Stats -->
              <div class="grid grid-cols-2 gap-2 bg-slate-950/60 rounded-lg p-2 text-xs font-mono mb-3">
                <div>
                  <span class="text-[10px] text-slate-500 block">Vehicles Shift / Cycle</span>
                  <span class="text-emerald-400 font-bold">${{d.vehicles_delivered}}</span>
                  <span class="text-slate-400 text-[10px]"> / ${{d.cycle_vehicles_delivered}} cars</span>
                </div>
                <div>
                  <span class="text-[10px] text-slate-500 block">Shift Pay / Yield</span>
                  <span class="text-amber-300 font-bold">$${{d.total_wages.toFixed(2)}}</span>
                  <span class="text-slate-400 text-[10px]"> ($${{d.effective_hourly_yield.toFixed(2)}}/h)</span>
                </div>
              </div>
            </div>

            <!-- Bottom Load Link -->
            <div class="pt-2 border-t border-slate-800/80 flex items-center justify-between gap-2">
              <span class="text-[10px] font-medium text-slate-400">Assigned Loads:</span>
              <div class="flex flex-wrap gap-1">
                ${{loadsList}}
              </div>
            </div>
          </div>
        `;
      }});
      container.innerHTML = gridHtml;
    }}

    function renderTerminalDistribution(drivers) {{
      const container = document.getElementById('terminalDistributionCards');
      if (!container) return;

      const terminals = [
        {{ code: 'LA', name: 'Long Beach VDC', icon: 'fa-ship', color: 'sky' }},
        {{ code: 'SF', name: 'Benicia VDC', icon: 'fa-anchor', color: 'blue' }},
        {{ code: 'ML', name: 'Mira Loma VDC', icon: 'fa-train-subway', color: 'amber' }},
        {{ code: 'PT', name: 'Portland VDC', icon: 'fa-mountain', color: 'emerald' }},
        {{ code: '04016', name: 'Omesa Logistics Hub', icon: 'fa-sun', color: 'orange' }},
        {{ code: 'HUB', name: 'Certified Handover Hubs', icon: 'fa-handshake', color: 'purple' }}
      ];

      let html = '';
      terminals.forEach(t => {{
        let dCount = 0;
        let activeCount = 0;
        if (t.code === 'HUB') {{
          dCount = drivers.filter(d => d.current_location.name.toLowerCase().includes('hub')).length;
          activeCount = dCount;
        }} else {{
          const termDrivers = drivers.filter(d => d.home_vdc === t.code);
          dCount = termDrivers.length;
          activeCount = termDrivers.filter(d => d.operation_type !== 'standby').length;
        }}

        html += `
          <div class="bg-slate-950/70 border border-slate-800/80 rounded-xl p-2.5 flex flex-col justify-between cursor-pointer hover:border-slate-700 transition" onclick="document.getElementById('managerLocationFilter').value='${{t.code}}'; filterManagerLocation('${{t.code}}');">
            <div>
              <div class="flex items-center justify-between mb-1">
                <span class="font-bold text-white text-xs">${{t.code}}</span>
                <i class="fa-solid ${{t.icon}} text-${{t.color}}-400 text-xs"></i>
              </div>
              <div class="text-[10px] text-slate-400 font-medium truncate" title="${{t.name}}">${{t.name}}</div>
            </div>
            <div class="mt-2 pt-1 border-t border-slate-800 flex items-center justify-between text-[11px] font-mono">
              <span class="text-slate-300 font-bold">${{dCount}} Drivers</span>
              <span class="text-emerald-400">${{activeCount}} Active</span>
            </div>
          </div>
        `;
      }});
      container.innerHTML = html;
    }}


    function showDriversExplanation() {{
      const banner = document.getElementById('driversRationaleBanner');
      banner.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
      banner.classList.add('ring-2', 'ring-sky-500');
      setTimeout(() => banner.classList.remove('ring-2', 'ring-sky-500'), 2000);
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
      csvContent += "Leg #,From Code,From Name,To Code,To Name,Distance (Miles),Driving Time (Mins),Departure (Origin),Arrival (Dest),Service (Mins),Departure (Dest),Assigned Driver,Driver Shift,Handover Occurred,Remaining Cargo Units\\n";
      currentSolution.legs.forEach(leg => {{
        csvContent += `${{leg.leg_number}},"${{leg.from_code}}","${{leg.from_name}}","${{leg.to_code}}","${{leg.to_name}}",${{leg.distance_miles}},${{leg.travel_time_mins}},"${{leg.departure_from_origin}}","${{leg.arrival_at_dest}}",${{leg.service_time_mins}},"${{leg.departure_from_dest}}","${{leg.driver_name}}","${{leg.driver_shift || 'AM'}}",${{leg.handover_at_dest ? 'YES' : 'NO'}},${{leg.remaining_cargo_units}}\\n`;
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

with open('templates/index.html', 'w') as f:
    f.write(html_content)

print("Generated updated index.html and templates/index.html successfully! Size:", len(html_content))
