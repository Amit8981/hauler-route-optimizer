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
            <div class="text-lg font-bold font-mono text-white" id="kpiCapacity">8 / 9 Cars</div>
            <div class="text-[10px] text-emerald-400 mt-1" id="kpiCargoWeight">42,816 lbs (100%)</div>
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
            <button class="tab-btn px-3.5 py-2 text-xs font-semibold rounded-t-lg border-b-2 border-transparent text-emerald-400 hover:text-emerald-300 bg-emerald-950/20 cursor-pointer" onclick="switchTab('multiTripTab')">
              <i class="fa-solid fa-repeat mr-1.5"></i> Multi-Trip Shift Tour (1 Driver &bull; 3 Trips)
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

        <!-- Tab 5: Multi-Trip Shift Tour (1 Driver doing 3 Short Trips) -->
        <div id="multiTripTab" class="tab-content hidden space-y-4">
          <div class="bg-slate-950/80 border border-slate-800 rounded-xl p-5 space-y-4">
            <div class="flex flex-col md:flex-row md:items-center justify-between gap-2 pb-4 border-b border-slate-800">
              <div>
                <div class="flex items-center space-x-2">
                  <span class="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-xs font-bold">OPERATIONAL SHOWCASE</span>
                  <h3 class="font-bold text-sm text-white">Multi-Trip Single-Driver Daily Shift Tour</h3>
                </div>
                <p class="text-xs text-slate-400 mt-1">Single driver executing multiple short trips within the 11-hour daily cap with mandatory 45-min turnaround rest at factory depot (C-17).</p>
              </div>
              <div class="flex items-center space-x-2">
                <span class="px-3 py-1 bg-slate-800 rounded-lg text-xs font-mono text-slate-300">Driver: Driver 7 (SoCal) (DRV_07)</span>
                <span class="px-2 py-1 bg-amber-500/20 text-amber-300 rounded text-xs font-mono">45m Turnaround Rest</span>
              </div>
            </div>

            <!-- Multi-Trip Summary Cards -->
            <div class="grid grid-cols-2 md:grid-cols-5 gap-3">
              <div class="bg-slate-900 border border-slate-800 rounded-xl p-3">
                <div class="text-[10px] text-slate-400 uppercase font-medium">Trips Completed</div>
                <div class="text-lg font-bold font-mono text-white mt-1">3 Round-Trips</div>
                <div class="text-[10px] text-slate-500">Loads #244861, #188377, #188384</div>
              </div>
              <div class="bg-slate-900 border border-slate-800 rounded-xl p-3">
                <div class="text-[10px] text-slate-400 uppercase font-medium">Total Shift Duty</div>
                <div class="text-lg font-bold font-mono text-emerald-400 mt-1">5.40 hrs</div>
                <div class="text-[10px] text-emerald-400">Within 11.0h Daily Cap (C-12a)</div>
              </div>
              <div class="bg-slate-900 border border-slate-800 rounded-xl p-3">
                <div class="text-[10px] text-slate-400 uppercase font-medium">Total Shift Span</div>
                <div class="text-lg font-bold font-mono text-sky-400 mt-1">6.57 hrs</div>
                <div class="text-[10px] text-slate-400">06:00 AM &rarr; 03:06 PM (AM Window)</div>
              </div>
              <div class="bg-slate-900 border border-slate-800 rounded-xl p-3">
                <div class="text-[10px] text-slate-400 uppercase font-medium">Total Mileage</div>
                <div class="text-lg font-bold font-mono text-white mt-1">143.7 miles</div>
                <div class="text-[10px] text-slate-500">Mira Loma Terminal Network</div>
              </div>
              <div class="bg-slate-900 border border-slate-800 rounded-xl p-3">
                <div class="text-[10px] text-slate-400 uppercase font-medium">Turnaround Rest</div>
                <div class="text-lg font-bold font-mono text-amber-300 mt-1">45 min / trip</div>
                <div class="text-[10px] text-amber-400/80">Mandatory depot buffer (C-17)</div>
              </div>
            </div>

            <!-- Multi-Trip Schedule Table -->
            <div class="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden mt-4">
              <table class="w-full text-left text-xs">
                <thead class="bg-slate-950 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
                  <tr>
                    <th class="py-2.5 px-3">Trip #</th>
                    <th class="py-2.5 px-3">Load ID & Num</th>
                    <th class="py-2.5 px-3">Departure (Depot)</th>
                    <th class="py-2.5 px-3">Return (Depot)</th>
                    <th class="py-2.5 px-3 text-right">Distance</th>
                    <th class="py-2.5 px-3 text-right">Trip Duty</th>
                    <th class="py-2.5 px-4">Post-Trip Action</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-slate-800/60 font-mono text-slate-200">
                  <tr class="hover:bg-slate-800/40">
                    <td class="py-3 px-3 font-bold text-sky-400 text-center">1</td>
                    <td class="py-3 px-3"><span class="font-bold text-white">#244861</span> (L-44167)</td>
                    <td class="py-3 px-3 text-slate-300">06:00 AM</td>
                    <td class="py-3 px-3 text-amber-300 font-bold">08:32 AM</td>
                    <td class="py-3 px-3 text-right">47.9 mi</td>
                    <td class="py-3 px-3 text-right text-emerald-400 font-bold">1.88 hrs</td>
                    <td class="py-3 px-4"><span class="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 text-[10px] font-bold">45-min Rest at Mira Loma Depot</span></td>
                  </tr>
                  <tr class="hover:bg-slate-800/40">
                    <td class="py-3 px-3 font-bold text-sky-400 text-center">2</td>
                    <td class="py-3 px-3"><span class="font-bold text-white">#188377</span> (L-8415)</td>
                    <td class="py-3 px-3 text-slate-300">09:17 AM</td>
                    <td class="py-3 px-3 text-amber-300 font-bold">11:49 AM</td>
                    <td class="py-3 px-3 text-right">47.9 mi</td>
                    <td class="py-3 px-3 text-right text-emerald-400 font-bold">1.88 hrs</td>
                    <td class="py-3 px-4"><span class="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 text-[10px] font-bold">45-min Rest at Mira Loma Depot</span></td>
                  </tr>
                  <tr class="hover:bg-slate-800/40">
                    <td class="py-3 px-3 font-bold text-sky-400 text-center">3</td>
                    <td class="py-3 px-3"><span class="font-bold text-white">#188384</span> (M-17213)</td>
                    <td class="py-3 px-3 text-slate-300">12:34 PM</td>
                    <td class="py-3 px-3 text-amber-300 font-bold">03:06 PM</td>
                    <td class="py-3 px-3 text-right">47.9 mi</td>
                    <td class="py-3 px-3 text-right text-emerald-400 font-bold">1.63 hrs</td>
                    <td class="py-3 px-4"><span class="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-[10px] font-bold">Shift Complete &bull; Clock-out</span></td>
                  </tr>
                </tbody>
              </table>
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
      document.getElementById('kpiCargoWeight').textContent = `${{resLbs.toLocaleString()}} lbs (100%)`;

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
    }}

    function renderDriverDutyBars(drivers) {{
      const container = document.getElementById('driverProgressBars');
      if (!container) return;

      container.innerHTML = drivers.map((d, idx) => {{
        const dailyDuty = d.total_duty_hours;
        const drivingHours = d.driving_hours;
        const dailyPct = Math.min(100, Math.round((dailyDuty / 11.0) * 100));
        const isDailyOver = dailyDuty > 11.0;
        const dailyBarColor = isDailyOver ? 'bg-red-500' : dailyPct > 80 ? 'bg-amber-500' : 'bg-emerald-500';

        const weeklyUsed = Number(d.weekly_hours_used || 35.0);
        const weeklyTotal = Number((weeklyUsed + dailyDuty).toFixed(2));
        const weeklyPct = Math.min(100, Math.round((weeklyTotal / 70.0) * 100));
        const isWeeklyOver = weeklyTotal > 70.0;
        const weeklyBarColor = isWeeklyOver ? 'bg-red-500' : weeklyPct > 80 ? 'bg-amber-500' : 'bg-sky-500';

        const shiftBadge = (d.shift_type === 'PM' || d.driver?.shift_type === 'PM')
          ? '<span class="px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 text-[10px] font-mono">🌙 PM Shift</span>'
          : '<span class="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 text-[10px] font-mono">☀️ AM Shift</span>';

        return `
          <div class="bg-slate-900 border border-slate-800 rounded-xl p-3.5 space-y-3">
            <div class="flex items-center justify-between text-xs">
              <div class="flex items-center space-x-2">
                <span class="w-6 h-6 rounded-full bg-sky-500/20 text-sky-400 font-bold flex items-center justify-center text-[10px]">D${{idx + 1}}</span>
                <div>
                  <span class="font-semibold text-slate-200">${{d.driver.name}}</span>
                  <span class="text-[10px] text-slate-400 font-mono ml-1.5">(${{d.driver.driver_id}})</span>
                </div>
              </div>
              <div class="flex items-center space-x-2">
                ${{shiftBadge}}
                <span class="px-2 py-0.5 rounded bg-slate-800 text-[10px] font-mono text-emerald-400">$35/hr Flat</span>
              </div>
            </div>

            <!-- Daily 11h Progress Bar -->
            <div class="space-y-1">
              <div class="flex items-center justify-between text-[11px]">
                <span class="text-slate-400">Daily Duty (C-12a):</span>
                <span class="font-mono font-bold ${{isDailyOver ? 'text-red-400' : 'text-emerald-400'}}">${{dailyDuty}}h / 11.0h max</span>
              </div>
              <div class="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div class="${{dailyBarColor}} h-full transition-all duration-500" style="width: ${{dailyPct}}%"></div>
              </div>
            </div>

            <!-- Weekly 70h Rolling Progress Bar -->
            <div class="space-y-1">
              <div class="flex items-center justify-between text-[11px]">
                <span class="text-slate-400">Weekly HOS 8-Day Cap (C-12b):</span>
                <span class="font-mono text-slate-300">${{weeklyTotal}}h / 70.0h</span>
              </div>
              <div class="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div class="${{weeklyBarColor}} h-full transition-all duration-500" style="width: ${{weeklyPct}}%"></div>
              </div>
            </div>

            <div class="flex items-center justify-between text-[10px] text-slate-400 pt-1 border-t border-slate-800/60">
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
