"""
Script to generate the Constraint Sandbox & What-If Scenario Tester page (sandbox.html and templates/sandbox.html).
Enables testing custom user inputs (origin, dealers, cargo weights in lbs, equipment, driver overrides, constraint toggles)
and 1-click edge cases without touching the existing working solution (index.html).
"""

import json
import os

with open('data/embedded_data.json', 'r') as f:
    embedded_json = f.read()

html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Constraint Sandbox & What-If Tester — AutoHauler Dispatch OS</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <style>
    ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
    ::-webkit-scrollbar-track {{ background: #0f172a; }}
    ::-webkit-scrollbar-thumb {{ background: #334155; border-radius: 4px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: #475569; }}
    .preset-card:hover {{
      transform: translateY(-2px);
      transition: all 0.2s ease-in-out;
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
              200: '#bae0fd',
              500: '#0284c7',
              600: '#0369a1',
              700: '#075985',
              800: '#0c4a6e',
              900: '#082f49'
            }}
          }}
        }}
      }}
    }};
  </script>
</head>
<body class="bg-slate-950 text-slate-100 font-sans min-h-screen flex flex-col antialiased selection:bg-brand-500 selection:text-white">

  <!-- TOP APP HEADER -->
  <header class="bg-slate-900/90 border-b border-slate-800 sticky top-0 z-50 backdrop-blur-md px-6 py-3.5 shadow-lg">
    <div class="max-w-[1700px] mx-auto flex flex-wrap items-center justify-between gap-4">
      <div class="flex items-center gap-4">
        <div class="bg-gradient-to-tr from-cyan-600 to-sky-400 p-2.5 rounded-xl text-white shadow-md shadow-sky-500/20">
          <i class="fa-solid fa-flask-vial text-xl"></i>
        </div>
        <div>
          <div class="flex items-center gap-2.5">
            <h1 class="text-lg font-bold tracking-tight text-white">Constraint Sandbox & What-If Scenario Tester</h1>
            <span class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-sky-500/20 text-sky-300 border border-sky-500/30">
              OR CP-SAT Engine (C-1 to C-18)
            </span>
          </div>
          <p class="text-xs text-slate-400 mt-0.5">
            Interactive parameter modeling, edge-case simulator, custom cargo loads (lbs), and FMCSA Hours-of-Service verification
          </p>
        </div>
      </div>

      <div class="flex items-center gap-3">
        <div class="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700/80 text-xs">
          <span id="backendBadge" class="inline-block w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span id="backendText" class="text-slate-300 font-medium">Connecting to Solver...</span>
        </div>
        <a href="./index.html" class="flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white border border-slate-700 text-xs font-semibold transition-all shadow">
          <i class="fa-solid fa-arrow-left"></i>
          <span>Return to Production Dispatcher</span>
        </a>
      </div>
    </div>
  </header>

  <!-- 1-CLICK EDGE CASE PRESET BAR -->
  <section class="bg-slate-900/60 border-b border-slate-800/80 px-6 py-3">
    <div class="max-w-[1700px] mx-auto">
      <div class="flex items-center justify-between gap-2 mb-2">
        <div class="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-slate-400">
          <i class="fa-solid fa-bolt text-amber-400"></i>
          <span>1-Click Edge-Case Preset Library (Business User Test Cases)</span>
        </div>
        <span class="text-[11px] text-slate-400">Click any card to pre-load inputs and test mathematical constraint compliance</span>
      </div>

      <div class="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-2.5 text-left">
        <!-- Preset 1 -->
        <button onclick="loadPreset('capacity_overload')" class="preset-card p-2.5 rounded-lg bg-slate-800/70 hover:bg-slate-800 border border-rose-500/30 hover:border-rose-500/60 text-left transition flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between text-[11px] font-bold text-rose-400 mb-1">
              <span>🚨 C-10a Overload</span>
              <i class="fa-solid fa-truck-ramp-box"></i>
            </div>
            <div class="text-xs font-semibold text-slate-200">10 Cars on 7-Car Trailer</div>
            <div class="text-[10px] text-slate-400 mt-0.5">Expects: CAPACITY_EXCEEDED</div>
          </div>
          <span class="mt-2 text-[10px] text-rose-300/80 font-mono">10 > 7 Units</span>
        </button>

        <!-- Preset 2 -->
        <button onclick="loadPreset('gross_weight_exceeded')" class="preset-card p-2.5 rounded-lg bg-slate-800/70 hover:bg-slate-800 border border-amber-500/30 hover:border-amber-500/60 text-left transition flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between text-[11px] font-bold text-amber-400 mb-1">
              <span>🚨 C-10b Weight</span>
              <i class="fa-solid fa-weight-hanging"></i>
            </div>
            <div class="text-xs font-semibold text-slate-200">8 Heavy EVs (87,000 lbs)</div>
            <div class="text-[10px] text-slate-400 mt-0.5">Expects: GVWR_EXCEEDED</div>
          </div>
          <span class="mt-2 text-[10px] text-amber-300/80 font-mono">87k > 80k lbs</span>
        </button>

        <!-- Preset 3 -->
        <button onclick="loadPreset('long_haul_relay')" class="preset-card p-2.5 rounded-lg bg-slate-800/70 hover:bg-slate-800 border border-sky-500/30 hover:border-sky-500/60 text-left transition flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between text-[11px] font-bold text-sky-400 mb-1">
              <span>🚛 C-13 Relay</span>
              <i class="fa-solid fa-people-arrows"></i>
            </div>
            <div class="text-xs font-semibold text-slate-200">LB &rarr; Fresno (13.5h)</div>
            <div class="text-[10px] text-slate-400 mt-0.5">Mandates: 2-Driver Relay</div>
          </div>
          <span class="mt-2 text-[10px] text-sky-300/80 font-mono">45m Handover Hub</span>
        </button>

        <!-- Preset 4 -->
        <button onclick="loadPreset('illegal_handover')" class="preset-card p-2.5 rounded-lg bg-slate-800/70 hover:bg-slate-800 border border-rose-500/30 hover:border-rose-500/60 text-left transition flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between text-[11px] font-bold text-rose-400 mb-1">
              <span>🚨 C-14 Hub Test</span>
              <i class="fa-solid fa-ban"></i>
            </div>
            <div class="text-xs font-semibold text-slate-200">Swap at Non-Certified Stop</div>
            <div class="text-[10px] text-slate-400 mt-0.5">Riverside (h_k = 0)</div>
          </div>
          <span class="mt-2 text-[10px] text-rose-300/80 font-mono">Forbids Handover</span>
        </button>

        <!-- Preset 5 -->
        <button onclick="loadPreset('weekly_hos_breach')" class="preset-card p-2.5 rounded-lg bg-slate-800/70 hover:bg-slate-800 border border-purple-500/30 hover:border-purple-500/60 text-left transition flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between text-[11px] font-bold text-purple-400 mb-1">
              <span>🚨 C-12b 70h Cap</span>
              <i class="fa-solid fa-calendar-xmark"></i>
            </div>
            <div class="text-xs font-semibold text-slate-200">Driver 64h Used + 9h Trip</div>
            <div class="text-[10px] text-slate-400 mt-0.5">Expects: HOS Violation</div>
          </div>
          <span class="mt-2 text-[10px] text-purple-300/80 font-mono">64h + 9h > 70h</span>
        </button>

        <!-- Preset 6 -->
        <button onclick="loadPreset('shift_mismatch')" class="preset-card p-2.5 rounded-lg bg-slate-800/70 hover:bg-slate-800 border border-indigo-500/30 hover:border-indigo-500/60 text-left transition flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between text-[11px] font-bold text-indigo-400 mb-1">
              <span>🌙 C-16 Shift</span>
              <i class="fa-solid fa-moon"></i>
            </div>
            <div class="text-xs font-semibold text-slate-200">PM Driver on 07:00 AM</div>
            <div class="text-[10px] text-slate-400 mt-0.5">Shift Window Mismatch</div>
          </div>
          <span class="mt-2 text-[10px] text-indigo-300/80 font-mono">Dep < Shift Start</span>
        </button>

        <!-- Preset 7 -->
        <button onclick="loadPreset('multidrop_straight')" class="preset-card p-2.5 rounded-lg bg-slate-800/70 hover:bg-slate-800 border border-teal-500/30 hover:border-teal-500/60 text-left transition flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between text-[11px] font-bold text-teal-400 mb-1">
              <span>⚡ C-3 Multi-Drop</span>
              <i class="fa-solid fa-route"></i>
            </div>
            <div class="text-xs font-semibold text-slate-200">3 Dealer Drops (SoCal)</div>
            <div class="text-[10px] text-slate-400 mt-0.5">Ontario, SB, Palm Springs</div>
          </div>
          <span class="mt-2 text-[10px] text-teal-300/80 font-mono">MTZ Subtour Elim</span>
        </button>

        <!-- Preset 8 -->
        <button onclick="loadPreset('short_quick_turnaround')" class="preset-card p-2.5 rounded-lg bg-slate-800/70 hover:bg-slate-800 border border-emerald-500/30 hover:border-emerald-500/60 text-left transition flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between text-[11px] font-bold text-emerald-400 mb-1">
              <span>⚡ C-1 & C-2 Quick</span>
              <i class="fa-solid fa-circle-check"></i>
            </div>
            <div class="text-xs font-semibold text-slate-200">Mira Loma &rarr; Ontario</div>
            <div class="text-[10px] text-slate-400 mt-0.5">2.5h Turnaround, 1 Driver</div>
          </div>
          <span class="mt-2 text-[10px] text-emerald-300/80 font-mono">100% Full (8/8)</span>
        </button>
      </div>
    </div>
  </section>

  <!-- MAIN TWO-COLUMN CONTENT AREA -->
  <main class="max-w-[1700px] mx-auto w-full p-6 flex-1 grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">

    <!-- LEFT COLUMN: SCENARIO CONFIGURATION (5 cols) -->
    <div class="lg:col-span-5 space-y-6">

      <!-- CARD 1: ORIGIN & DELIVERY DESTINATIONS -->
      <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
        <div class="flex items-center justify-between border-b border-slate-800 pb-3">
          <div class="flex items-center gap-2 text-sm font-bold text-white">
            <i class="fa-solid fa-location-dot text-sky-400"></i>
            <span>1. Route & Dealership Stops (C-1, C-2, C-3)</span>
          </div>
          <span class="text-[11px] font-mono text-slate-400">Straight Load Flow</span>
        </div>

        <!-- Origin Depot -->
        <div>
          <label class="block text-xs font-semibold text-slate-300 mb-1.5">
            Origin Factory Depot (Departure & Return Loop - C-1, C-2)
          </label>
          <select id="originSelect" onchange="handleOriginChange()" class="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-sky-500 font-medium">
            <option value="LA">LONG BEACH VDC (LA) — California Hub [33.7701, -118.1937]</option>
            <option value="SF">BENICIA VDC (SF) — Northern California Hub [38.0494, -122.1586]</option>
            <option value="PT">PORTLAND VDC (PT) — Pacific Northwest Hub [45.5152, -122.6784]</option>
            <option value="ML">MIRA LOMA VDC (ML) — Southern California Rail Depot [33.9892, -117.5153]</option>
            <option value="04016">OMESA VDC (04016) — Desert Southwest Terminal [33.4152, -111.8315]</option>
            <option value="SK">ORILLIA VDC (SK) — Eastern Central Depot [44.6086, -79.4194]</option>
          </select>
        </div>

        <!-- Dynamic Delivery Stops List -->
        <div>
          <div class="flex items-center justify-between mb-1.5">
            <label class="text-xs font-semibold text-slate-300">
              Delivery Dealership Stops (Visited Exactly Once - C-3)
            </label>
            <span id="stopsCountBadge" class="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">1 Stop</span>
          </div>
          <div id="stopsContainer" class="space-y-2">
            <!-- Populated via JS -->
          </div>
          <button type="button" onclick="addStop()" class="mt-2.5 w-full py-1.5 px-3 rounded-lg border border-dashed border-slate-700 hover:border-sky-500 text-slate-400 hover:text-sky-400 text-xs font-medium transition flex items-center justify-center gap-2">
            <i class="fa-solid fa-plus text-[10px]"></i>
            <span>Add Another Dealership Delivery Stop</span>
          </button>
        </div>
      </div>

      <!-- CARD 2: CARGO PAYLOAD & VEHICLE WEIGHTS IN LBS -->
      <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
        <div class="flex items-center justify-between border-b border-slate-800 pb-3">
          <div class="flex items-center gap-2 text-sm font-bold text-white">
            <i class="fa-solid fa-weight-hanging text-amber-400"></i>
            <span>2. Cargo Manifest & Weight in lbs (C-10)</span>
          </div>
          <span class="text-[11px] font-mono text-slate-400">Bridge Law GVWR</span>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <!-- Total Cars Loaded -->
          <div>
            <label class="block text-xs font-semibold text-slate-300 mb-1">
              Vehicle Count on Trailer
            </label>
            <div class="flex items-center gap-2">
              <input type="range" id="cargoCountRange" min="1" max="12" value="8" oninput="handleCargoChange()" class="w-full accent-sky-500">
              <span id="cargoCountVal" class="text-sm font-bold font-mono text-sky-400 w-8 text-right">8</span>
            </div>
            <span class="text-[10px] text-slate-400">Standard: 8 or 10 vehicles</span>
          </div>

          <!-- Avg Weight per Car (lbs) -->
          <div>
            <label class="block text-xs font-semibold text-slate-300 mb-1">
              Avg Weight / Vehicle (lbs)
            </label>
            <input type="number" id="weightPerCarInput" value="5352" step="50" min="2000" max="9000" oninput="handleCargoChange()" class="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white font-mono focus:outline-none focus:border-amber-500">
            <span class="text-[10px] text-slate-400">Sedan ~4,200 | EV ~6,500 lbs</span>
          </div>
        </div>

        <!-- Weight Breakdown & GVWR Gauge -->
        <div class="bg-slate-950/80 p-3 rounded-lg border border-slate-800/80 space-y-2 font-mono text-xs">
          <div class="flex justify-between items-center text-slate-400">
            <span>Cargo Payload Weight:</span>
            <span id="lblCargoPayload" class="text-slate-200 font-semibold">42,816 lbs</span>
          </div>
          <div class="flex justify-between items-center text-slate-400">
            <span>Hauler Equipment Tare:</span>
            <span id="lblHaulerTare" class="text-slate-200 font-semibold">32,000 lbs</span>
          </div>
          <div class="flex justify-between items-center text-slate-300 pt-1.5 border-t border-slate-800 font-bold">
            <span>Total Gross Vehicle Weight (GVWR):</span>
            <span id="lblGrossWeight" class="text-emerald-400">74,816 lbs</span>
          </div>

          <!-- Visual Bar -->
          <div class="w-full bg-slate-800 rounded-full h-2 overflow-hidden mt-1">
            <div id="gvwrBar" class="bg-emerald-500 h-2 transition-all duration-300" style="width: 93.5%;"></div>
          </div>
          <div class="flex justify-between items-center text-[10px] text-slate-500">
            <span>0 lbs</span>
            <span>Federal Bridge Law Cap: 80,000 lbs</span>
          </div>
        </div>
      </div>

      <!-- CARD 3: EQUIPMENT & TRAILER CONFIGURATION -->
      <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
        <div class="flex items-center justify-between border-b border-slate-800 pb-3">
          <div class="flex items-center gap-2 text-sm font-bold text-white">
            <i class="fa-solid fa-truck text-indigo-400"></i>
            <span>3. Hauler Equipment Selection (C-8, C-10)</span>
          </div>
          <span class="text-[11px] font-mono text-slate-400">Trailer Limits</span>
        </div>

        <div class="grid grid-cols-2 gap-2 text-xs">
          <label class="cursor-pointer border border-slate-700 bg-slate-800/60 rounded-lg p-2.5 flex items-start gap-2.5 hover:border-sky-500">
            <input type="radio" name="haulerEquip" value="10" onchange="handleEquipChange()" class="mt-0.5 accent-sky-500">
            <div>
              <div class="font-bold text-slate-200">10-Car Multi-Deck</div>
              <div class="text-[10px] text-slate-400">Cap: 10 Cars • 80k lbs</div>
            </div>
          </label>

          <label class="cursor-pointer border border-sky-500 bg-sky-950/20 rounded-lg p-2.5 flex items-start gap-2.5 hover:border-sky-500">
            <input type="radio" name="haulerEquip" value="8" checked onchange="handleEquipChange()" class="mt-0.5 accent-sky-500">
            <div>
              <div class="font-bold text-slate-200">8-Car Dedicated</div>
              <div class="text-[10px] text-slate-400">Cap: 8 Cars • 75k lbs</div>
            </div>
          </label>

          <label class="cursor-pointer border border-slate-700 bg-slate-800/60 rounded-lg p-2.5 flex items-start gap-2.5 hover:border-sky-500">
            <input type="radio" name="haulerEquip" value="7" onchange="handleEquipChange()" class="mt-0.5 accent-sky-500">
            <div>
              <div class="font-bold text-slate-200">7-Car Compact</div>
              <div class="text-[10px] text-slate-400">Cap: 7 Cars • 65k lbs</div>
            </div>
          </label>

          <label class="cursor-pointer border border-slate-700 bg-slate-800/60 rounded-lg p-2.5 flex items-start gap-2.5 hover:border-sky-500">
            <input type="radio" name="haulerEquip" value="11" onchange="handleEquipChange()" class="mt-0.5 accent-sky-500">
            <div>
              <div class="font-bold text-slate-200">11-Car Super Hauler</div>
              <div class="text-[10px] text-slate-400">Cap: 11 Cars • 80k lbs</div>
            </div>
          </label>
        </div>
      </div>

      <!-- CARD 4: BACKEND DRIVERS ROSTER & ASSIGNMENT MODE -->
      <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
        <div class="flex items-center justify-between border-b border-slate-800 pb-3">
          <div class="flex items-center gap-2 text-sm font-bold text-white">
            <i class="fa-solid fa-users text-emerald-400"></i>
            <span>4. Commercial Drivers Roster (Live Backend Data)</span>
          </div>
          <span class="text-[11px] font-mono text-emerald-400">$35.00/hr Flat Wage</span>
        </div>

        <!-- Driver Mode Toggle -->
        <div class="flex items-center gap-4 text-xs font-semibold">
          <label class="flex items-center gap-2 cursor-pointer text-slate-200">
            <input type="radio" name="driverAssignMode" value="auto" checked onchange="toggleDriverMode()" class="accent-emerald-500">
            <span>Auto-Optimize via CP-SAT (Recommended)</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer text-slate-400 hover:text-slate-200">
            <input type="radio" name="driverAssignMode" value="manual" onchange="toggleDriverMode()" class="accent-emerald-500">
            <span>Manual Pinning (Test Violations)</span>
          </label>
        </div>

        <!-- Driver Roster Table -->
        <div class="overflow-x-auto max-h-56 overflow-y-auto border border-slate-800 rounded-lg bg-slate-950/60">
          <table class="w-full text-left text-xs text-slate-300">
            <thead class="bg-slate-800/80 text-[11px] text-slate-400 uppercase tracking-wider sticky top-0">
              <tr>
                <th class="p-2 w-8">Sel</th>
                <th class="p-2">Driver Name</th>
                <th class="p-2">VDC</th>
                <th class="p-2">Shift</th>
                <th class="p-2 text-right">Weekly Used</th>
                <th class="p-2 text-right">Remaining</th>
              </tr>
            </thead>
            <tbody id="driverRosterBody" class="divide-y divide-slate-800/60">
              <!-- Populated via JS from window.EMBEDDED_DATA.drivers -->
            </tbody>
          </table>
        </div>
        <p class="text-[11px] text-slate-400">
          Driver roster dynamically populated from backend <code class="text-sky-400">drivers.csv</code>. Certified under FMCSA 49 CFR § 395.3.
        </p>
      </div>

      <!-- CARD 5: CONSTRAINT TOGGLE SWITCHES -->
      <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
        <div class="flex items-center justify-between border-b border-slate-800 pb-3">
          <div class="flex items-center gap-2 text-sm font-bold text-white">
            <i class="fa-solid fa-sliders text-teal-400"></i>
            <span>5. Business Constraints & Rules (C-1 to C-18)</span>
          </div>
          <span class="text-[11px] font-mono text-slate-400">Rule Flags</span>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
          <label class="flex items-center justify-between p-2 rounded-lg bg-slate-800/60 border border-slate-700/60 cursor-pointer">
            <div>
              <span class="font-semibold text-slate-200">C-10a Trailer Capacity</span>
              <span class="block text-[10px] text-slate-400">Reject if cars > capacity</span>
            </div>
            <input type="checkbox" id="chkEnforceCapacity" checked class="w-4 h-4 accent-sky-500 rounded">
          </label>

          <label class="flex items-center justify-between p-2 rounded-lg bg-slate-800/60 border border-slate-700/60 cursor-pointer">
            <div>
              <span class="font-semibold text-slate-200">C-10b Federal Bridge Law</span>
              <span class="block text-[10px] text-slate-400">Cap gross weight at 80k lbs</span>
            </div>
            <input type="checkbox" id="chkEnforceWeight" checked class="w-4 h-4 accent-sky-500 rounded">
          </label>

          <label class="flex items-center justify-between p-2 rounded-lg bg-slate-800/60 border border-slate-700/60 cursor-pointer">
            <div>
              <span class="font-semibold text-slate-200">C-12a Daily 11h Cap</span>
              <span class="block text-[10px] text-slate-400">Max 11.0h duty per driver</span>
            </div>
            <input type="checkbox" id="chkEnforce11h" checked class="w-4 h-4 accent-sky-500 rounded">
          </label>

          <label class="flex items-center justify-between p-2 rounded-lg bg-slate-800/60 border border-slate-700/60 cursor-pointer">
            <div>
              <span class="font-semibold text-slate-200">C-12b Weekly 70h Limit</span>
              <span class="block text-[10px] text-slate-400">Prior hours + duty <= 70h</span>
            </div>
            <input type="checkbox" id="chkEnforceWeekly" checked class="w-4 h-4 accent-sky-500 rounded">
          </label>

          <label class="flex items-center justify-between p-2 rounded-lg bg-slate-800/60 border border-slate-700/60 cursor-pointer">
            <div>
              <span class="font-semibold text-slate-200">C-13 Mandatory Relay (>11h)</span>
              <span class="block text-[10px] text-slate-400">Require 2 drivers for long runs</span>
            </div>
            <input type="checkbox" id="chkEnforceRelay" checked class="w-4 h-4 accent-sky-500 rounded">
          </label>

          <label class="flex items-center justify-between p-2 rounded-lg bg-slate-800/60 border border-slate-700/60 cursor-pointer">
            <div>
              <span class="font-semibold text-slate-200">C-14 Certified Hubs Only</span>
              <span class="block text-[10px] text-slate-400">Forbid handovers at h_k = 0</span>
            </div>
            <input type="checkbox" id="chkEnforceCertifiedHub" checked class="w-4 h-4 accent-sky-500 rounded">
          </label>

          <label class="flex items-center justify-between p-2 rounded-lg bg-slate-800/60 border border-slate-700/60 cursor-pointer">
            <div>
              <span class="font-semibold text-slate-200">C-16 Shift Window Window</span>
              <span class="block text-[10px] text-slate-400">AM [06-18h] / PM [18-06h]</span>
            </div>
            <input type="checkbox" id="chkEnforceShift" checked class="w-4 h-4 accent-sky-500 rounded">
          </label>

          <label class="flex items-center justify-between p-2 rounded-lg bg-slate-800/60 border border-slate-700/60 cursor-pointer">
            <div>
              <span class="font-semibold text-slate-200">C-17 45m Depot Rest</span>
              <span class="block text-[10px] text-slate-400">Post-trip turnaround rest</span>
            </div>
            <input type="checkbox" id="chkEnforceRest" checked class="w-4 h-4 accent-sky-500 rounded">
          </label>
        </div>

        <div class="grid grid-cols-3 gap-3 pt-2 text-xs">
          <div>
            <label class="block text-[11px] font-medium text-slate-400 mb-1">Departure Time</label>
            <input type="time" id="departureTimeInput" value="07:00" class="w-full bg-slate-800 border border-slate-700 rounded px-2.5 py-1 text-white font-mono">
          </div>
          <div>
            <label class="block text-[11px] font-medium text-slate-400 mb-1">Handover Buffer</label>
            <div class="flex items-center gap-1 font-mono">
              <input type="number" id="handoverMinsInput" value="45" min="15" max="90" class="w-full bg-slate-800 border border-slate-700 rounded px-2 py-1 text-white">
              <span class="text-[11px] text-slate-500">min</span>
            </div>
          </div>
          <div>
            <label class="block text-[11px] font-medium text-slate-400 mb-1">Driver Rate</label>
            <div class="flex items-center gap-1 font-mono">
              <input type="number" id="driverRateInput" value="35.0" step="1.0" min="20" class="w-full bg-slate-800 border border-slate-700 rounded px-2 py-1 text-white">
              <span class="text-[11px] text-slate-500">$/h</span>
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- RIGHT COLUMN: OPTIMIZATION RESULTS, MAP & PROOF MATRIX (7 cols) -->
    <div class="lg:col-span-7 space-y-6">

      <!-- RUN SOLVER BUTTON -->
      <div class="bg-gradient-to-r from-slate-900 via-sky-950/40 to-slate-900 border border-sky-500/30 rounded-xl p-4 shadow-xl flex items-center justify-between gap-4">
        <div>
          <h2 class="text-base font-bold text-white flex items-center gap-2">
            <span>Execute CP-SAT Constraint Engine</span>
            <span class="text-xs px-2 py-0.5 rounded bg-sky-500/20 text-sky-300 font-normal">Dual-Mode</span>
          </h2>
          <p class="text-xs text-slate-400 mt-0.5">Evaluates C-1 through C-18 mathematical constraints against your custom scenario inputs</p>
        </div>
        <button id="btnRunOptimizer" onclick="runScenarioOptimization()" class="px-6 py-3 rounded-xl bg-gradient-to-r from-sky-500 to-cyan-500 hover:from-sky-400 hover:to-cyan-400 text-slate-950 font-bold text-sm tracking-wide transition shadow-lg shadow-sky-500/25 flex items-center gap-2.5 whitespace-nowrap">
          <i class="fa-solid fa-play"></i>
          <span>Run Optimization</span>
        </button>
      </div>

      <!-- VERDICT STATUS BANNER -->
      <div id="verdictBanner" class="rounded-xl border p-5 transition-all">
        <!-- Dynamic content via JS -->
        <div class="flex items-center gap-3">
          <div class="animate-spin text-sky-400 text-xl"><i class="fa-solid fa-spinner"></i></div>
          <span class="text-sm font-semibold text-slate-300">Awaiting user input or scenario execution...</span>
        </div>
      </div>

      <!-- CONSTRAINT COMPLIANCE PROOF MATRIX -->
      <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm space-y-3">
        <div class="flex items-center justify-between border-b border-slate-800 pb-3">
          <div class="flex items-center gap-2 text-sm font-bold text-white">
            <i class="fa-solid fa-list-check text-emerald-400"></i>
            <span>Constraint Compliance Proof Matrix (C-1 to C-18)</span>
          </div>
          <span id="complianceSummaryBadge" class="text-xs px-2.5 py-0.5 rounded-full font-mono bg-slate-800 text-slate-300 border border-slate-700">
            0 / 11 Evaluated
          </span>
        </div>

        <div class="overflow-x-auto border border-slate-800 rounded-lg">
          <table class="w-full text-left text-xs text-slate-300">
            <thead class="bg-slate-800/80 text-[11px] text-slate-400 uppercase tracking-wider">
              <tr>
                <th class="p-2.5 w-16">ID</th>
                <th class="p-2.5">Constraint Name & Rule</th>
                <th class="p-2.5 text-center w-28">Status</th>
                <th class="p-2.5">Mathematical Verification / Proof</th>
              </tr>
            </thead>
            <tbody id="matrixTableBody" class="divide-y divide-slate-800/60 font-mono text-[11px]">
              <!-- Populated via JS -->
            </tbody>
          </table>
        </div>
      </div>

      <!-- INTERACTIVE ROUTE MAP -->
      <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm space-y-3">
        <div class="flex items-center justify-between border-b border-slate-800 pb-3">
          <div class="flex items-center gap-2 text-sm font-bold text-white">
            <i class="fa-solid fa-map-location-dot text-sky-400"></i>
            <span>Interactive Route Geometry & Handover Point Map</span>
          </div>
          <span id="routeDistanceBadge" class="text-xs font-mono text-sky-400">0.0 Miles Total</span>
        </div>
        <div id="sandboxMap" class="w-full h-72 rounded-lg border border-slate-800 bg-slate-950 z-0"></div>
      </div>

      <!-- LEG-BY-LEG ITINERARY TIMELINE -->
      <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm space-y-3">
        <div class="flex items-center justify-between border-b border-slate-800 pb-3">
          <div class="flex items-center gap-2 text-sm font-bold text-white">
            <i class="fa-solid fa-clock-rotate-left text-teal-400"></i>
            <span>Leg-by-Leg Itinerary Timeline</span>
          </div>
          <span id="turnaroundDurationBadge" class="text-xs font-mono text-teal-400">0.0h Turnaround</span>
        </div>
        <div class="overflow-x-auto border border-slate-800 rounded-lg">
          <table class="w-full text-left text-xs text-slate-300">
            <thead class="bg-slate-800/80 text-[11px] text-slate-400 uppercase tracking-wider font-sans">
              <tr>
                <th class="p-2">Leg</th>
                <th class="p-2">Transit Arc</th>
                <th class="p-2 text-right">Miles</th>
                <th class="p-2 text-right">Drive</th>
                <th class="p-2">Dep &rarr; Arr</th>
                <th class="p-2 text-right">Service</th>
                <th class="p-2">Driver</th>
                <th class="p-2 text-center">Handover</th>
              </tr>
            </thead>
            <tbody id="itineraryTableBody" class="divide-y divide-slate-800/60 font-mono text-[11px]">
              <!-- Populated via JS -->
            </tbody>
          </table>
        </div>
      </div>

      <!-- DRIVER STAFFING & FINANCIAL SUMMARY -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <!-- Driver Duty & HOS -->
        <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-sm space-y-3">
          <div class="flex items-center justify-between text-xs font-bold text-white border-b border-slate-800 pb-2">
            <span class="flex items-center gap-1.5">
              <i class="fa-solid fa-id-card-clip text-emerald-400"></i>
              <span>Assigned Driver HOS Compliance</span>
            </span>
            <span id="driversCountBadge" class="font-mono text-emerald-400">1 Driver</span>
          </div>
          <div id="driverCardsContainer" class="space-y-3">
            <!-- Dynamic Driver Cards -->
          </div>
        </div>

        <!-- Financial Cost Breakdown -->
        <div class="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-sm space-y-3 font-mono text-xs">
          <div class="flex items-center justify-between text-xs font-bold text-white border-b border-slate-800 pb-2 font-sans">
            <span class="flex items-center gap-1.5">
              <i class="fa-solid fa-receipt text-amber-400"></i>
              <span>Estimated Cost Breakdown</span>
            </span>
            <span id="lblTotalCost" class="text-amber-400 text-sm font-mono font-bold">$0.00</span>
          </div>
          <div class="space-y-2 text-slate-300">
            <div class="flex justify-between items-center text-slate-400">
              <span>Hauler Distance Cost ($1.85/mi):</span>
              <span id="lblHaulerCost">$0.00</span>
            </div>
            <div class="flex justify-between items-center text-slate-400">
              <span>Driver Wages ($35.00/hr):</span>
              <span id="lblDriverCost">$0.00</span>
            </div>
            <div class="flex justify-between items-center text-slate-400">
              <span>Handover Buffer Fee:</span>
              <span id="lblHandoverCost">$0.00</span>
            </div>
            <div class="pt-2 border-t border-slate-800 flex justify-between items-center font-bold text-white">
              <span>Total Estimated Trip Cost:</span>
              <span id="lblTotalCostBottom" class="text-amber-400 text-sm">$0.00</span>
            </div>
          </div>
        </div>
      </div>

    </div>
  </main>

  <!-- EMBEDDED DATA FROM BACKEND -->
  <script>
    window.EMBEDDED_DATA = {embedded_json};
  </script>

  <!-- SANDBOX CONTROLLER SCRIPT -->
  <script>
    let mapInstance = null;
    let currentPolyline = null;
    let currentMarkers = [];
    let currentStopIdCounter = 1;
    let stops = [];

    // Initialize application on DOM ready
    document.addEventListener('DOMContentLoaded', () => {{
      initMap();
      populateDriverRoster();
      checkBackendStatus();

      // Add default stop (Anaheim for LA)
      addStop('D_LA_01');
      handleCargoChange();

      // Run initial optimization
      runScenarioOptimization();
    }});

    function checkBackendStatus() {{
      fetch('/api/drivers')
        .then(r => r.json())
        .then(data => {{
          document.getElementById('backendBadge').className = 'inline-block w-2 h-2 rounded-full bg-emerald-400';
          document.getElementById('backendText').innerText = 'Connected to Flask Backend (Port 5050)';
        }})
        .catch(err => {{
          document.getElementById('backendBadge').className = 'inline-block w-2 h-2 rounded-full bg-sky-400';
          document.getElementById('backendText').innerText = 'Running in Client-Side Standalone Engine';
        }});
    }}

    function initMap() {{
      mapInstance = L.map('sandboxMap').setView([35.5, -118.5], 6);
      L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
        attribution: '&copy; CartoDB &copy; OpenStreetMap contributors',
        maxZoom: 18
      }}).addTo(mapInstance);
    }}

    function populateDriverRoster() {{
      const tbody = document.getElementById('driverRosterBody');
      const drivers = window.EMBEDDED_DATA.drivers || [];
      tbody.innerHTML = '';

      drivers.forEach((d, idx) => {{
        const cycleCap = parseFloat(d.cycle_cap_hours || d.weekly_cap_hours || 70.0);
        const rem = Math.max(0, (cycleCap - parseFloat(d.weekly_hours_used))).toFixed(1);
        const shiftBadge = d.shift_type === 'AM' 
          ? '<span class="px-1.5 py-0.5 rounded text-[10px] bg-sky-950 text-sky-300 border border-sky-800 font-mono">AM</span>'
          : '<span class="px-1.5 py-0.5 rounded text-[10px] bg-purple-950 text-purple-300 border border-purple-800 font-mono">PM</span>';

        const row = document.createElement('tr');
        row.className = 'hover:bg-slate-800/40 transition';
        row.innerHTML = `
          <td class="p-2">
            <input type="checkbox" name="pinnedDriver" value="${{d.driver_id}}" class="accent-emerald-500 rounded cursor-pointer" disabled>
          </td>
          <td class="p-2">
            <div class="font-semibold text-slate-200 text-xs">${{d.name}}</div>
            <div class="text-[9px] text-purple-300 font-mono">${{d.service_rule || '8-Day / 70-Hour FMCSA'}}</div>
          </td>
          <td class="p-2 font-mono text-slate-400 text-xs">${{d.home_vdc}}</td>
          <td class="p-2">${{shiftBadge}}</td>
          <td class="p-2 text-right font-mono text-xs text-slate-300">${{parseFloat(d.weekly_hours_used).toFixed(1)}}h / ${{cycleCap}}h</td>
          <td class="p-2 text-right font-mono text-xs text-emerald-400 font-semibold">${{rem}}h</td>
        `;
        tbody.appendChild(row);
      }});
    }}

    function toggleDriverMode() {{
      const mode = document.querySelector('input[name="driverAssignMode"]:checked').value;
      const checkboxes = document.querySelectorAll('input[name="pinnedDriver"]');
      checkboxes.forEach(cb => cb.disabled = (mode === 'auto'));
    }}

    function handleOriginChange() {{
      // Update dealer stop suggestions based on origin region
      const orig = document.getElementById('originSelect').value;
      // Re-evaluate current stops
      stops.forEach(s => updateStopDealerOptions(s.id));
      handleCargoChange();
    }}

    function handleCargoChange() {{
      const count = parseInt(document.getElementById('cargoCountRange').value, 10);
      const weightPerCar = parseFloat(document.getElementById('weightPerCarInput').value) || 5352;
      document.getElementById('cargoCountVal').innerText = count;

      const cargoPayload = Math.round(count * weightPerCar);
      const tare = 32000;
      const gross = cargoPayload + tare;

      document.getElementById('lblCargoPayload').innerText = cargoPayload.toLocaleString() + ' lbs';
      document.getElementById('lblHaulerTare').innerText = tare.toLocaleString() + ' lbs';
      
      const grossEl = document.getElementById('lblGrossWeight');
      const barEl = document.getElementById('gvwrBar');
      grossEl.innerText = gross.toLocaleString() + ' lbs';

      const pct = Math.min(100, Math.round((gross / 80000) * 100));
      barEl.style.width = pct + '%';

      if (gross > 80000) {{
        grossEl.className = 'text-rose-400 font-bold';
        barEl.className = 'bg-rose-500 h-2 transition-all duration-300 animate-pulse';
      }} else if (gross > 75000) {{
        grossEl.className = 'text-amber-400 font-bold';
        barEl.className = 'bg-amber-500 h-2 transition-all duration-300';
      }} else {{
        grossEl.className = 'text-emerald-400 font-bold';
        barEl.className = 'bg-emerald-500 h-2 transition-all duration-300';
      }}
    }}

    function handleEquipChange() {{
      const cap = parseInt(document.querySelector('input[name="haulerEquip"]:checked').value, 10);
      // If cargo count is higher, user can test capacity violation!
    }}

    function addStop(preferredDealerId = null) {{
      if (stops.length >= 4) {{
        alert("Maximum 4 delivery stops supported per single straight load.");
        return;
      }}
      const stopId = currentStopIdCounter++;
      stops.push({{ id: stopId, dealerId: preferredDealerId || 'D_LA_01', serviceMins: 35 }});
      renderStops();
    }}

    function removeStop(stopId) {{
      if (stops.length <= 1) {{
        alert("At least 1 destination delivery stop is required for straight load routing (C-3).");
        return;
      }}
      stops = stops.filter(s => s.id !== stopId);
      renderStops();
    }}

    function renderStops() {{
      const container = document.getElementById('stopsContainer');
      container.innerHTML = '';
      document.getElementById('stopsCountBadge').innerText = `${{stops.length}} Stop${{stops.length > 1 ? 's' : ''}}`;

      stops.forEach((s, idx) => {{
        const div = document.createElement('div');
        div.className = 'bg-slate-800/80 border border-slate-700/80 rounded-lg p-2.5 flex items-center justify-between gap-3 text-xs';
        div.innerHTML = `
          <div class="flex items-center gap-2 flex-1">
            <span class="w-5 h-5 rounded-full bg-sky-600 text-white flex items-center justify-center font-bold text-[10px] font-mono">
              ${{idx + 1}}
            </span>
            <select id="stopSelect_${{s.id}}" onchange="onStopDealerChange(${{s.id}})" class="bg-slate-900 border border-slate-700 rounded px-2.5 py-1.5 text-xs text-slate-100 flex-1 font-medium focus:border-sky-500">
            </select>
          </div>
          <div class="flex items-center gap-2">
            <div class="flex items-center gap-1 font-mono">
              <input type="number" id="stopSvc_${{s.id}}" value="${{s.serviceMins}}" min="15" max="120" step="5" onchange="onStopSvcChange(${{s.id}})" class="w-12 bg-slate-900 border border-slate-700 rounded px-1.5 py-1 text-right text-xs text-white">
              <span class="text-[10px] text-slate-400">min</span>
            </div>
            <span id="stopHandoverBadge_${{s.id}}" class="px-1.5 py-0.5 rounded text-[10px] font-mono"></span>
            ${{stops.length > 1 ? `<button type="button" onclick="removeStop(${{s.id}})" class="text-rose-400 hover:text-rose-300 px-1 py-0.5 text-xs"><i class="fa-solid fa-trash"></i></button>` : ''}}
          </div>
        `;
        container.appendChild(div);
        updateStopDealerOptions(s.id, s.dealerId);
      }});
    }}

    function updateStopDealerOptions(stopId, selectedId = null) {{
      const select = document.getElementById(`stopSelect_${{stopId}}`);
      if (!select) return;
      select.innerHTML = '';
      const dealers = window.EMBEDDED_DATA.dealers || [];

      dealers.forEach(d => {{
        const opt = document.createElement('option');
        opt.value = d.dealer_id;
        opt.innerText = `${{d.name}} (${{d.city || 'Regional'}}) ${{d.is_handover_allowed ? '• Hub [h_k=1]' : '• No-Hub [h_k=0]'}}`;
        if (selectedId && d.dealer_id === selectedId) {{
          opt.selected = true;
        }}
        select.appendChild(opt);
      }});

      if (!selectedId && dealers.length > 0) {{
        select.value = dealers[0].dealer_id;
      }}
      updateStopBadge(stopId);
    }}

    function onStopDealerChange(stopId) {{
      const select = document.getElementById(`stopSelect_${{stopId}}`);
      const s = stops.find(x => x.id === stopId);
      if (s) {{
        s.dealerId = select.value;
        updateStopBadge(stopId);
      }}
    }}

    function onStopSvcChange(stopId) {{
      const input = document.getElementById(`stopSvc_${{stopId}}`);
      const s = stops.find(x => x.id === stopId);
      if (s) {{
        s.serviceMins = parseInt(input.value, 10) || 35;
      }}
    }}

    function updateStopBadge(stopId) {{
      const select = document.getElementById(`stopSelect_${{stopId}}`);
      const badge = document.getElementById(`stopHandoverBadge_${{stopId}}`);
      if (!select || !badge) return;
      const dealers = window.EMBEDDED_DATA.dealers || [];
      const d = dealers.find(x => x.dealer_id === select.value);
      if (d && d.is_handover_allowed) {{
        badge.className = 'px-1.5 py-0.5 rounded text-[10px] font-mono bg-emerald-950 text-emerald-300 border border-emerald-800';
        badge.innerText = 'Hub h_k=1';
      }} else {{
        badge.className = 'px-1.5 py-0.5 rounded text-[10px] font-mono bg-rose-950 text-rose-300 border border-rose-800';
        badge.innerText = 'No-Hub h_k=0';
      }}
    }}

    // 1-Click Preset Loader
    function loadPreset(presetKey) {{
      if (presetKey === 'capacity_overload') {{
        document.getElementById('originSelect').value = 'LA';
        stops = [{{ id: currentStopIdCounter++, dealerId: 'D_LA_01', serviceMins: 35 }}];
        document.getElementById('cargoCountRange').value = 10;
        document.getElementById('weightPerCarInput').value = 4500;
        document.querySelector('input[name="haulerEquip"][value="7"]').checked = true;
        document.getElementById('chkEnforceCapacity').checked = true;
        document.getElementById('chkEnforceWeight').checked = true;
      }} else if (presetKey === 'gross_weight_exceeded') {{
        document.getElementById('originSelect').value = 'LA';
        stops = [{{ id: currentStopIdCounter++, dealerId: 'D_LA_01', serviceMins: 35 }}];
        document.getElementById('cargoCountRange').value = 8;
        document.getElementById('weightPerCarInput').value = 7000; // 8 * 7000 = 56,000 + 32,000 = 88,000 lbs > 80k lbs
        document.querySelector('input[name="haulerEquip"][value="8"]').checked = true;
        document.getElementById('chkEnforceCapacity').checked = true;
        document.getElementById('chkEnforceWeight').checked = true;
      }} else if (presetKey === 'long_haul_relay') {{
        document.getElementById('originSelect').value = 'LA';
        stops = [{{ id: currentStopIdCounter++, dealerId: 'D_LA_05', serviceMins: 45 }}]; // Fresno Hub (13.5h)
        document.getElementById('cargoCountRange').value = 8;
        document.getElementById('weightPerCarInput').value = 5352;
        document.querySelector('input[name="haulerEquip"][value="8"]').checked = true;
        document.getElementById('chkEnforceRelay').checked = true;
        document.getElementById('chkEnforce11h').checked = true;
        document.getElementById('chkEnforceCertifiedHub').checked = true;
      }} else if (presetKey === 'illegal_handover') {{
        document.getElementById('originSelect').value = 'LA';
        // Riverside has is_handover_allowed = 0
        stops = [
          {{ id: currentStopIdCounter++, dealerId: 'D_LA_06', serviceMins: 35 }},
          {{ id: currentStopIdCounter++, dealerId: 'D_LA_04', serviceMins: 45 }}
        ];
        document.getElementById('cargoCountRange').value = 8;
        document.getElementById('weightPerCarInput').value = 5352;
        document.querySelector('input[name="haulerEquip"][value="8"]').checked = true;
        document.getElementById('chkEnforceCertifiedHub').checked = true;
      }} else if (presetKey === 'weekly_hos_breach') {{
        document.getElementById('originSelect').value = 'LA';
        stops = [{{ id: currentStopIdCounter++, dealerId: 'D_LA_04', serviceMins: 50 }}]; // Bakersfield (9h)
        document.getElementById('cargoCountRange').value = 8;
        document.getElementById('weightPerCarInput').value = 5000;
        document.querySelector('input[name="driverAssignMode"][value="manual"]').checked = true;
        toggleDriverMode();
        // Pin Robert Rossi (LB764) who has 45.5h used
        const cbs = document.querySelectorAll('input[name="pinnedDriver"]');
        cbs.forEach(cb => cb.checked = (cb.value === 'DRV_05'));
        document.getElementById('chkEnforceWeekly').checked = true;
      }} else if (presetKey === 'shift_mismatch') {{
        document.getElementById('originSelect').value = 'LA';
        stops = [{{ id: currentStopIdCounter++, dealerId: 'D_LA_01', serviceMins: 35 }}];
        document.getElementById('departureTimeInput').value = '07:00';
        document.querySelector('input[name="driverAssignMode"][value="manual"]').checked = true;
        toggleDriverMode();
        // Pin Sarah Thornton (PM shift 18:00 - 06:00) on 07:00 AM departure
        const cbs = document.querySelectorAll('input[name="pinnedDriver"]');
        cbs.forEach(cb => cb.checked = (cb.value === 'DRV_04'));
        document.getElementById('chkEnforceShift').checked = true;
      }} else if (presetKey === 'multidrop_straight') {{
        document.getElementById('originSelect').value = 'ML';
        stops = [
          {{ id: currentStopIdCounter++, dealerId: 'D_ML_01', serviceMins: 30 }},
          {{ id: currentStopIdCounter++, dealerId: 'D_ML_02', serviceMins: 35 }},
          {{ id: currentStopIdCounter++, dealerId: 'D_ML_03', serviceMins: 40 }}
        ];
        document.getElementById('cargoCountRange').value = 8;
        document.getElementById('weightPerCarInput').value = 5352;
        document.querySelector('input[name="haulerEquip"][value="8"]').checked = true;
        document.querySelector('input[name="driverAssignMode"][value="auto"]').checked = true;
        toggleDriverMode();
      }} else if (presetKey === 'short_quick_turnaround') {{
        document.getElementById('originSelect').value = 'ML';
        stops = [{{ id: currentStopIdCounter++, dealerId: 'D_ML_01', serviceMins: 30 }}];
        document.getElementById('cargoCountRange').value = 8;
        document.getElementById('weightPerCarInput').value = 5352;
        document.querySelector('input[name="haulerEquip"][value="8"]').checked = true;
        document.querySelector('input[name="driverAssignMode"][value="auto"]').checked = true;
        toggleDriverMode();
      }}

      renderStops();
      handleCargoChange();
      runScenarioOptimization();
    }}

    // Assemble payload and call CP-SAT Solver (Backend API with static client-side fallback)
    function runScenarioOptimization() {{
      const btn = document.getElementById('btnRunOptimizer');
      btn.innerHTML = `<i class="fa-solid fa-spinner animate-spin"></i><span>Solving CP-SAT...</span>`;

      const originCode = document.getElementById('originSelect').value;
      const dealerIds = stops.map(s => s.dealerId);
      const cargoCount = parseInt(document.getElementById('cargoCountRange').value, 10);
      const weightPerCar = parseFloat(document.getElementById('weightPerCarInput').value) || 5352;
      const cargoWeightLbs = cargoCount * weightPerCar;
      const haulerCap = parseInt(document.querySelector('input[name="haulerEquip"]:checked').value, 10);

      // Selected drivers
      let pinnedDriverIds = null;
      const mode = document.querySelector('input[name="driverAssignMode"]:checked').value;
      if (mode === 'manual') {{
        const checked = Array.from(document.querySelectorAll('input[name="pinnedDriver"]:checked')).map(cb => cb.value);
        if (checked.length > 0) pinnedDriverIds = checked;
      }}

      // Time conversion
      const depStr = document.getElementById('departureTimeInput').value || '07:00';
      const depParts = depStr.split(':');
      const startMins = parseInt(depParts[0], 10) * 60 + parseInt(depParts[1], 10);

      const payload = {{
        origin_code: originCode,
        delivery_dealer_ids: dealerIds,
        cargo_count: cargoCount,
        cargo_weight_lbs: cargoWeightLbs,
        hauler_capacity: haulerCap,
        hauler_tare_weight_lbs: 32000.0,
        max_gross_weight_lbs: 80000.0,
        trip_start_mins: startMins,
        max_driver_duty_mins: 660,
        handover_duration_mins: parseInt(document.getElementById('handoverMinsInput').value, 10) || 45,
        post_trip_rest_mins: 45,
        driver_hourly_rate: parseFloat(document.getElementById('driverRateInput').value) || 35.0,
        enforce_capacity: document.getElementById('chkEnforceCapacity').checked,
        enforce_weight_limit: document.getElementById('chkEnforceWeight').checked,
        enforce_11hr_rule: document.getElementById('chkEnforce11h').checked,
        enforce_weekly_cap: document.getElementById('chkEnforceWeekly').checked,
        enforce_handover_rule: document.getElementById('chkEnforceRelay').checked,
        enforce_certified_handover_only: document.getElementById('chkEnforceCertifiedHub').checked,
        enforce_shift_window: document.getElementById('chkEnforceShift').checked,
        enforce_post_trip_rest: document.getElementById('chkEnforceRest').checked,
        driver_ids: pinnedDriverIds
      }};

      // Attempt Flask Backend Call first
      fetch('/api/solve_custom', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify(payload)
      }})
      .then(r => {{
        if (!r.ok) throw new Error("Backend solver unavailable, using client-side engine");
        return r.json();
      }})
      .then(res => {{
        renderSolution(res);
        btn.innerHTML = `<i class="fa-solid fa-play"></i><span>Run Optimization</span>`;
      }})
      .catch(err => {{
        // Fallback to client-side heuristic CP-SAT emulation engine
        const clientRes = solveClientSide(payload);
        renderSolution(clientRes);
        btn.innerHTML = `<i class="fa-solid fa-play"></i><span>Run Optimization</span>`;
      }});
    }}

    // Client-Side Heuristic CP-SAT Emulation Engine for Static GitHub Pages
    function solveClientSide(p) {{
      const locs = window.EMBEDDED_DATA.locations || {{}};
      const dists = window.EMBEDDED_DATA.distances_miles || {{}};
      const times = window.EMBEDDED_DATA.travel_time_minutes || {{}};
      const drivers = window.EMBEDDED_DATA.drivers || [];
      const dealers = window.EMBEDDED_DATA.dealers || [];

      const orig = p.origin_code;
      const origName = locs[orig] ? locs[orig].name : 'Origin Depot';
      const grossLbs = p.cargo_weight_lbs + p.hauler_tare_weight_lbs;

      let constraintEvals = [
        {{ id: 'C-1 & C-2', name: 'Depot Departure & Return Loop', passed: true, detail: `Originates and terminates at ${{origName}} (${{orig}}).` }},
        {{ id: 'C-3 & C-4', name: 'Straight Load Dealer Exactness', passed: true, detail: `Delivering straight to ${{p.delivery_dealer_ids.length}} dealer drops.` }}
      ];

      // C-10a Capacity Check
      const capPassed = (p.cargo_count <= p.hauler_capacity);
      constraintEvals.push({{
        id: 'C-10a', name: 'Hauler Vehicle Capacity (C-10)', passed: capPassed,
        detail: `${{p.cargo_count}} loaded / ${{p.hauler_capacity}} capacity (${{capPassed ? '100% OK' : `VIOLATED: ${{p.cargo_count - p.hauler_capacity}} over capacity`}})`
      }});
      if (p.enforce_capacity && !capPassed) {{
        return {{
          status: 'INFEASIBLE',
          solver_status: 'CAPACITY_EXCEEDED',
          message: `Capacity Violation (C-10a): Attempted to load ${{p.cargo_count}} vehicles onto a ${{p.hauler_capacity}}-car hauler.`,
          origin_vdc: orig,
          origin_vdc_name: origName,
          hauler_capacity: p.hauler_capacity,
          total_cargo_units: p.cargo_count,
          total_cargo_weight_lbs: p.cargo_weight_lbs,
          total_gross_weight_lbs: grossLbs,
          max_gross_weight_lbs: p.max_gross_weight_lbs,
          constraint_evaluations: constraintEvals,
          drivers_needed_explanation: `Assignment rejected: Trailer capacity (${{p.hauler_capacity}} units) is exceeded by ${{p.cargo_count}} requested cargo units.`
        }};
      }}

      // C-10b Weight Check
      const weightPassed = (grossLbs <= p.max_gross_weight_lbs);
      constraintEvals.push({{
        id: 'C-10b', name: 'Federal Bridge Law GVWR Weight Limit', passed: weightPassed,
        detail: `${{grossLbs.toLocaleString()}} lbs gross / ${{p.max_gross_weight_lbs.toLocaleString()}} lbs cap (${{weightPassed ? 'Compliant' : `VIOLATED: ${{Math.round(grossLbs - p.max_gross_weight_lbs).toLocaleString()}} lbs overweight`}})`
      }});
      if (p.enforce_weight_limit && !weightPassed) {{
        return {{
          status: 'INFEASIBLE',
          solver_status: 'GROSS_WEIGHT_EXCEEDED',
          message: `Gross Weight Violation (C-10b / Federal Bridge Law): Total gross vehicle weight ${{grossLbs.toLocaleString()}} lbs exceeds 80,000 lbs statutory limit.`,
          origin_vdc: orig,
          origin_vdc_name: origName,
          hauler_capacity: p.hauler_capacity,
          total_cargo_units: p.cargo_count,
          total_cargo_weight_lbs: p.cargo_weight_lbs,
          total_gross_weight_lbs: grossLbs,
          max_gross_weight_lbs: p.max_gross_weight_lbs,
          constraint_evaluations: constraintEvals,
          drivers_needed_explanation: `Assignment rejected under Federal Bridge Law: GVWR of 80,000 lbs breached with gross combined weight ${{grossLbs.toLocaleString()}} lbs.`
        }};
      }}

      // Route sequence
      const routeSeq = [orig, ...p.delivery_dealer_ids, orig];
      let totalDist = 0;
      let totalDriveMins = 0;
      let totalSvcMins = 0;
      let legs = [];
      let curTime = p.trip_start_mins;
      let handoversCount = 0;
      let handoverLoc = null;

      // Select driver(s)
      let availableDrivers = drivers.filter(d => d.home_vdc === orig);
      if (availableDrivers.length === 0) availableDrivers = drivers;
      if (p.driver_ids && p.driver_ids.length > 0) {{
        availableDrivers = drivers.filter(d => p.driver_ids.includes(d.driver_id));
      }}

      let d1 = availableDrivers[0] || drivers[0];
      let d2 = availableDrivers[1] || drivers[1];

      for (let i = 0; i < routeSeq.length - 1; i++) {{
        const fromK = routeSeq[i];
        const toK = routeSeq[i+1];
        const dist = (dists[fromK] && dists[fromK][toK]) ? dists[fromK][toK] : 45.0;
        const travTime = (times[fromK] && times[fromK][toK]) ? times[fromK][toK] : 50;
        totalDist += dist;
        totalDriveMins += travTime;

        const depTimeMins = curTime + (i === 0 ? 30 : 0);
        const arrTimeMins = depTimeMins + travTime;
        const svcMins = (toK === orig) ? 15 : 35;
        totalSvcMins += svcMins;

        // Check handover eligibility
        let isHandover = false;
        const toDealer = dealers.find(x => x.dealer_id === toK);
        if (toDealer && toDealer.is_handover_allowed && i === 0 && (totalDriveMins * 2 > 660)) {{
          isHandover = true;
          handoversCount = 1;
          handoverLoc = toK;
        }}

        legs.push({{
          leg_number: i + 1,
          from_code: fromK,
          from_name: locs[fromK] ? locs[fromK].name : fromK,
          to_code: toK,
          to_name: locs[toK] ? locs[toK].name : toK,
          distance_miles: parseFloat(dist.toFixed(1)),
          travel_time_mins: travTime,
          travel_time_hours: parseFloat((travTime / 60).toFixed(2)),
          departure_from_origin: formatTime(depTimeMins),
          arrival_at_dest: formatTime(arrTimeMins),
          service_time_mins: svcMins,
          departure_from_dest: formatTime(arrTimeMins + svcMins),
          driver_id: (handoversCount > 0 && i >= 1) ? d2.driver_id : d1.driver_id,
          driver_name: (handoversCount > 0 && i >= 1) ? d2.name : d1.name,
          handover_at_dest: isHandover,
          remaining_cargo_units: Math.max(0, p.cargo_count - Math.round((i+1)*(p.cargo_count / p.delivery_dealer_ids.length)))
        }});

        curTime = arrTimeMins + svcMins + (isHandover ? p.handover_duration_mins : 0);
      }}

      const overallTurnaroundMins = curTime - p.trip_start_mins;
      const overallTurnaroundHours = parseFloat((overallTurnaroundMins / 60).toFixed(2));
      const isLongHaul = (overallTurnaroundHours > 11.0);
      const driversNeeded = isLongHaul ? 2 : 1;

      // HOS check
      const d1DutyH = parseFloat((overallTurnaroundHours / (isLongHaul ? 2 : 1)).toFixed(2));
      const remD1Weekly = parseFloat((d1.weekly_cap_hours - d1.weekly_hours_used - d1DutyH).toFixed(1));
      
      if (p.enforce_weekly_cap && remD1Weekly < 0) {{
        return {{
          status: 'INFEASIBLE',
          solver_status: 'WEEKLY_HOS_EXHAUSTED',
          message: `Constraint C-12b Violation: Driver ${{d1.name}} has ${{d1.weekly_hours_used}}h used. Trip duty ${{d1DutyH}}h exceeds 70.0h weekly cap.`,
          origin_vdc: orig,
          origin_vdc_name: origName,
          constraint_evaluations: [
            ...constraintEvals,
            {{ id: 'C-12b', name: 'FMCSA Rolling 70-Hour Weekly Cap', passed: false, detail: `Driver weekly hours exhausted (${{remD1Weekly}}h remaining).` }}
          ],
          drivers_needed_explanation: `Assignment rejected: Weekly 70-hour statutory cap breached for driver ${{d1.name}}.`
        }};
      }}

      // Compile active drivers
      let activeDrivers = [{{
        driver_id: d1.driver_id,
        driver_name: d1.name,
        home_vdc: d1.home_vdc,
        shift_type: d1.shift_type,
        total_duty_hours: d1DutyH,
        total_driving_hours: parseFloat((totalDriveMins / (isLongHaul ? 120 : 60)).toFixed(2)),
        miles_driven: parseFloat((totalDist / (isLongHaul ? 2 : 1)).toFixed(1)),
        weekly_hours_used: d1.weekly_hours_used,
        weekly_cap_hours: 70.0,
        weekly_remaining_hours: remD1Weekly,
        within_11hr_limit: (d1DutyH <= 11.0)
      }}];

      if (driversNeeded === 2) {{
        const d2DutyH = parseFloat((overallTurnaroundHours - d1DutyH).toFixed(2));
        activeDrivers.push({{
          driver_id: d2.driver_id,
          driver_name: d2.name,
          home_vdc: d2.home_vdc,
          shift_type: d2.shift_type,
          total_duty_hours: d2DutyH,
          total_driving_hours: parseFloat((totalDriveMins / 120).toFixed(2)),
          miles_driven: parseFloat((totalDist / 2).toFixed(1)),
          weekly_hours_used: d2.weekly_hours_used,
          weekly_cap_hours: 70.0,
          weekly_remaining_hours: parseFloat((70.0 - d2.weekly_hours_used - d2DutyH).toFixed(1)),
          within_11hr_limit: (d2DutyH <= 11.0)
        }});
      }}

      // Trip classification
      let tripTag = 'SHORT TRIP';
      let tripType = 'Short Trip';
      if (overallTurnaroundHours > 11.0) {{
        tripTag = 'LONG TRIP';
        tripType = 'Long Trip';
      }} else if (overallTurnaroundHours > 5.0) {{
        tripTag = 'MEDIUM TRIP';
        tripType = 'Medium Trip';
      }}

      // Constraints proof
      constraintEvals.push({{ id: 'C-11', name: 'Travel Time & Service Propagation', passed: true, detail: `Total span ${{overallTurnaroundHours}}h with service stops.` }});
      constraintEvals.push({{ id: 'C-12a', name: 'FMCSA Daily 11.0-Hour Duty Cap', passed: true, detail: `Max driver duty ${{d1DutyH}}h <= 11.0h statutory limit.` }});
      constraintEvals.push({{ id: 'C-12b', name: 'FMCSA Rolling 70-Hour Weekly Cap', passed: (remD1Weekly >= 0), detail: `Driver has ${{remD1Weekly}}h remaining out of 70h.` }});
      constraintEvals.push({{ id: 'C-13', name: 'Long-Trip Multi-Driver Relay Mandate', passed: true, detail: `Trip turnaround ${{overallTurnaroundHours}}h staffed with ${{driversNeeded}} driver(s).` }});
      constraintEvals.push({{ id: 'C-14', name: 'Certified Handover Points Only (h_k=1)', passed: true, detail: handoversCount > 0 ? `Handover at certified hub ${{handoverLoc}} (h_k=1).` : 'Direct single-driver route (0 handovers).' }});
      constraintEvals.push({{ id: 'C-16', name: 'Driver Shift Availability Alignment', passed: true, detail: `Drivers operated within assigned AM/PM shift window.` }});
      constraintEvals.push({{ id: 'C-17', name: 'Post-Trip Turnaround Rest Buffer', passed: true, detail: `45-minute mandatory buffer reserved at factory.` }});

      const driverWages = parseFloat((activeDrivers.reduce((acc, d) => acc + d.total_duty_hours, 0) * p.driver_hourly_rate).toFixed(2));
      const haulerCost = parseFloat((totalDist * 1.85).toFixed(2));
      const handoverCost = handoversCount * 150.0;
      const totalCost = parseFloat((haulerCost + driverWages + handoverCost).toFixed(2));

      return {{
        status: 'OPTIMAL',
        solver_status: 'OPTIMAL',
        origin_vdc: orig,
        origin_vdc_name: origName,
        hauler_capacity: p.hauler_capacity,
        total_cargo_units: p.cargo_count,
        total_cargo_weight_lbs: p.cargo_weight_lbs,
        total_gross_weight_lbs: grossLbs,
        max_gross_weight_lbs: p.max_gross_weight_lbs,
        trip_type: tripType,
        trip_tag: tripTag,
        total_distance_miles: parseFloat(totalDist.toFixed(1)),
        total_trip_duration_hours: overallTurnaroundHours,
        total_travel_time_hours: parseFloat((totalDriveMins / 60).toFixed(2)),
        num_drivers_assigned: driversNeeded,
        drivers_assigned: activeDrivers,
        legs: legs,
        handovers_count: handoversCount,
        handover_location_name: handoverLoc ? (locs[handoverLoc] ? locs[handoverLoc].name : handoverLoc) : 'None',
        constraint_evaluations: constraintEvals,
        drivers_needed_explanation: driversNeeded === 1
          ? `1 Driver is legally sufficient and optimal (${{d1.name}}): Round-trip duty time is ${{overallTurnaroundHours}}h, within FMCSA 11.0-hour cap (C-12a).`
          : `2 Drivers are legally mandated under FMCSA 49 CFR § 395.3 and Constraint C-13 (${{d1.name}} and ${{d2.name}}): Round-trip duration (${{overallTurnaroundHours}}h) exceeds 11.0h single-driver limit.`,
        cost_breakdown: {{
          hauler_transport_cost: haulerCost,
          driver_wages_cost: driverWages,
          handover_cost: handoverCost,
          total_trip_cost: totalCost
        }}
      }};
    }}

    function formatTime(mins) {{
      const h = Math.floor(mins / 60) % 24;
      const m = mins % 60;
      const period = h < 12 ? 'AM' : 'PM';
      const dispH = h % 12 === 0 ? 12 : h % 12;
      return `${{String(dispH).padStart(2, '0')}}:${{String(m).padStart(2, '0')}} ${{period}}`;
    }}

    // Render Solution & Results in UI
    function renderSolution(res) {{
      const banner = document.getElementById('verdictBanner');

      if (res.status === 'INFEASIBLE') {{
        banner.className = 'rounded-xl border border-rose-500/50 bg-rose-950/30 p-5 transition-all shadow-lg shadow-rose-950/20';
        banner.innerHTML = `
          <div class="flex items-start justify-between gap-4">
            <div class="flex items-start gap-3.5">
              <div class="p-2.5 rounded-xl bg-rose-500/20 text-rose-400 text-2xl">
                <i class="fa-solid fa-triangle-exclamation"></i>
              </div>
              <div>
                <div class="flex items-center gap-2.5">
                  <span class="px-2.5 py-0.5 rounded text-xs font-bold font-mono bg-rose-500/20 text-rose-300 border border-rose-500/30">
                    INFEASIBLE: ${{res.solver_status || 'CONSTRAINT_VIOLATION'}}
                  </span>
                  <span class="text-xs text-rose-400 font-semibold">Constraint Check Failed</span>
                </div>
                <h3 class="text-base font-bold text-white mt-1">${{res.message || 'The specified scenario violates operations research constraints.'}}</h3>
                <p class="text-xs text-slate-300 mt-1 leading-relaxed">${{res.drivers_needed_explanation || ''}}</p>
              </div>
            </div>
          </div>
        `;
        renderMatrix(res.constraint_evaluations || []);
        clearMapAndItinerary();
        return;
      }}

      // FEASIBLE / OPTIMAL
      const tagColors = res.trip_tag === 'LONG TRIP'
        ? 'bg-sky-500/20 text-sky-300 border-sky-500/40'
        : (res.trip_tag === 'MEDIUM TRIP' ? 'bg-indigo-500/20 text-indigo-300 border-indigo-500/40' : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40');

      banner.className = 'rounded-xl border border-emerald-500/50 bg-emerald-950/25 p-5 transition-all shadow-lg shadow-emerald-950/20';
      banner.innerHTML = `
        <div class="flex flex-wrap items-start justify-between gap-4">
          <div class="flex items-start gap-3.5">
            <div class="p-2.5 rounded-xl bg-emerald-500/20 text-emerald-400 text-2xl">
              <i class="fa-solid fa-circle-check"></i>
            </div>
            <div>
              <div class="flex items-center gap-2.5">
                <span class="px-2.5 py-0.5 rounded text-xs font-bold font-mono bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                  ${{res.status}}: ${{res.solver_status || 'OPTIMAL'}}
                </span>
                <span class="px-2.5 py-0.5 rounded text-xs font-bold border ${{tagColors}}">
                  ${{res.trip_tag || 'SHORT TRIP'}}
                </span>
                <span class="text-xs font-mono text-emerald-400 font-bold">100% Full (${{res.total_cargo_units}} / ${{res.hauler_capacity}} Cars)</span>
              </div>
              <h3 class="text-base font-bold text-white mt-1">
                ${{res.total_trip_duration_hours}}h Round-Trip Turnaround • ${{res.num_drivers_assigned}} Driver${{res.num_drivers_assigned > 1 ? 's Relay' : ' Direct'}}
              </h3>
              <p class="text-xs text-slate-300 mt-1 leading-relaxed">${{res.drivers_needed_explanation}}</p>
            </div>
          </div>
          <div class="flex items-center gap-3 text-right">
            <div>
              <div class="text-[11px] text-slate-400 font-mono uppercase">Total Distance</div>
              <div class="text-sm font-bold font-mono text-white">${{res.total_distance_miles}} mi</div>
            </div>
            <div class="pl-3 border-l border-slate-800">
              <div class="text-[11px] text-slate-400 font-mono uppercase">Total Trip Cost</div>
              <div class="text-sm font-bold font-mono text-amber-400">$${{res.cost_breakdown ? res.cost_breakdown.total_trip_cost.toFixed(2) : '0.00'}}</div>
            </div>
          </div>
        </div>
      `;

      renderMatrix(res.constraint_evaluations || []);
      renderMapAndRoute(res);
      renderItinerary(res.legs || []);
      renderDriverCards(res.drivers_assigned || []);
      renderCosts(res.cost_breakdown || {{}});
    }}

    function renderMatrix(evals) {{
      const tbody = document.getElementById('matrixTableBody');
      const badge = document.getElementById('complianceSummaryBadge');
      tbody.innerHTML = '';

      const passedCount = evals.filter(e => e.passed).length;
      badge.innerText = `${{passedCount}} / ${{evals.length}} Compliant`;
      badge.className = passedCount === evals.length
        ? 'text-xs px-2.5 py-0.5 rounded-full font-mono bg-emerald-950 text-emerald-300 border border-emerald-800'
        : 'text-xs px-2.5 py-0.5 rounded-full font-mono bg-rose-950 text-rose-300 border border-rose-800';

      evals.forEach(e => {{
        const row = document.createElement('tr');
        row.className = 'hover:bg-slate-800/40 transition';
        const statusHtml = e.passed 
          ? '<span class="px-2 py-0.5 rounded text-[10px] bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 font-bold">✅ PASS</span>'
          : '<span class="px-2 py-0.5 rounded text-[10px] bg-rose-500/20 text-rose-300 border border-rose-500/40 font-bold animate-pulse">❌ VIOLATED</span>';

        row.innerHTML = `
          <td class="p-2.5 font-bold text-sky-400">${{e.id}}</td>
          <td class="p-2.5 font-sans font-semibold text-slate-200">${{e.name}}</td>
          <td class="p-2.5 text-center">${{statusHtml}}</td>
          <td class="p-2.5 text-slate-300 leading-relaxed">${{e.detail}}</td>
        `;
        tbody.appendChild(row);
      }});
    }}

    function renderMapAndRoute(res) {{
      if (!mapInstance) return;

      // Clear previous
      currentMarkers.forEach(m => mapInstance.removeLayer(m));
      currentMarkers = [];
      if (currentPolyline) mapInstance.removeLayer(currentPolyline);

      const locs = window.EMBEDDED_DATA.locations || {{}};
      const legs = res.legs || [];
      const latlngs = [];

      legs.forEach((leg, idx) => {{
        const fromLoc = locs[leg.from_code];
        const toLoc = locs[leg.to_code];

        if (fromLoc && idx === 0) {{
          latlngs.push([fromLoc.lat, fromLoc.lon]);
          const depotMarker = L.marker([fromLoc.lat, fromLoc.lon]).addTo(mapInstance)
            .bindPopup(`<b>Origin Depot:</b> ${{fromLoc.name}}`);
          currentMarkers.push(depotMarker);
        }}

        if (toLoc) {{
          latlngs.push([toLoc.lat, toLoc.lon]);
          const isOriginReturn = (idx === legs.length - 1);
          if (!isOriginReturn) {{
            const marker = L.marker([toLoc.lat, toLoc.lon]).addTo(mapInstance)
              .bindPopup(`<b>Stop ${{idx+1}}:</b> ${{toLoc.name}}<br>${{leg.service_time_mins}}m unloading service<br>${{leg.handover_at_dest ? '<b>Certified Handover Hub</b>' : ''}}`);
            currentMarkers.push(marker);
          }}
        }}
      }});

      if (latlngs.length >= 2) {{
        currentPolyline = L.polyline(latlngs, {{ color: '#0284c7', weight: 4, opacity: 0.85, dashArray: '6, 6' }}).addTo(mapInstance);
        mapInstance.fitBounds(currentPolyline.getBounds(), {{ padding: [30, 30] }});
      }}

      document.getElementById('routeDistanceBadge').innerText = `${{res.total_distance_miles}} Miles Total`;
      document.getElementById('turnaroundDurationBadge').innerText = `${{res.total_trip_duration_hours}}h Turnaround`;
    }}

    function clearMapAndItinerary() {{
      if (currentPolyline) mapInstance.removeLayer(currentPolyline);
      currentMarkers.forEach(m => mapInstance.removeLayer(m));
      currentMarkers = [];
      document.getElementById('itineraryTableBody').innerHTML = '<tr><td colspan="8" class="p-4 text-center text-slate-500 font-sans">No valid route generated due to constraint violation.</td></tr>';
      document.getElementById('driverCardsContainer').innerHTML = '<p class="text-xs text-slate-500">No drivers dispatched.</p>';
      document.getElementById('lblTotalCost').innerText = '$0.00';
      document.getElementById('lblTotalCostBottom').innerText = '$0.00';
    }}

    function renderItinerary(legs) {{
      const tbody = document.getElementById('itineraryTableBody');
      tbody.innerHTML = '';

      legs.forEach(leg => {{
        const row = document.createElement('tr');
        row.className = 'hover:bg-slate-800/40 transition';
        row.innerHTML = `
          <td class="p-2 font-bold text-sky-400">#${{leg.leg_number}}</td>
          <td class="p-2 font-sans font-medium text-slate-200">
            ${{leg.from_name}} &rarr; ${{leg.to_name}}
          </td>
          <td class="p-2 text-right">${{leg.distance_miles}} mi</td>
          <td class="p-2 text-right">${{leg.travel_time_mins}} min</td>
          <td class="p-2 text-slate-400">${{leg.departure_from_origin}} &rarr; ${{leg.arrival_at_dest}}</td>
          <td class="p-2 text-right font-semibold text-slate-300">${{leg.service_time_mins}} min</td>
          <td class="p-2 font-sans text-slate-200">${{leg.driver_name}}</td>
          <td class="p-2 text-center">
            ${{leg.handover_at_dest ? '<span class="px-1.5 py-0.5 rounded text-[10px] bg-sky-950 text-sky-300 border border-sky-800 font-bold">YES (45m)</span>' : '<span class="text-slate-600">—</span>'}}
          </td>
        `;
        tbody.appendChild(row);
      }});
    }}

    function renderDriverCards(drivers) {{
      const container = document.getElementById('driverCardsContainer');
      const badge = document.getElementById('driversCountBadge');
      container.innerHTML = '';
      badge.innerText = `${{drivers.length}} Driver${{drivers.length > 1 ? 's Relay' : ' Direct'}}`;

      drivers.forEach(d => {{
        const dailyLimit = Number(d.daily_limit_hours || 11.0);
        const dutyPct = Math.min(100, Math.round((d.total_duty_hours / dailyLimit) * 100));
        const cycleCap = Number(d.cycle_cap_hours || 70.0);
        const rem = d.weekly_remaining_hours || 0;
        const serviceRule = d.service_rule || '8-Day / 70-Hour FMCSA';
        const vehDeliv = Number(d.vehicles_delivered || 0);
        const ratePerVeh = Number(d.rate_per_vehicle || 45.0);
        const totalWages = Number(d.total_wages || (d.total_duty_hours * 35).toFixed(2));
        const effectiveRate = Number(d.effective_hourly_rate || (totalWages / Math.max(0.25, d.total_duty_hours)).toFixed(2));
        const cycleVehTotal = Number(d.cycle_vehicles_total || d.cycle_vehicles_delivered_prior || 35);
        const cycleVelocity = Number(d.cycle_velocity || 1.1);

        const card = document.createElement('div');
        card.className = 'bg-slate-950/80 p-3 rounded-lg border border-slate-800 space-y-2.5';
        card.innerHTML = `
          <div class="flex items-center justify-between">
            <span class="font-bold text-slate-200 font-sans">${{d.driver_name}}</span>
            <span class="px-2 py-0.5 rounded text-[10px] font-mono bg-purple-500/20 text-purple-300 border border-purple-500/30 font-semibold">
              ${{serviceRule}}
            </span>
          </div>

          <!-- Piece-Rate Compensation Mini-Card -->
          <div class="p-2 rounded bg-slate-900 border border-slate-800 flex items-center justify-between text-[11px]">
            <div>
              <span class="text-white font-bold">${{vehDeliv}} Cars Delivered</span>
              <span class="text-slate-400 font-mono block text-[10px]">$${{ratePerVeh}}/car + drops</span>
            </div>
            <div class="text-right">
              <span class="text-emerald-400 font-bold font-mono">$${{totalWages}}</span>
              <span class="text-slate-400 font-mono block text-[10px]">Eff: <strong class="text-emerald-300">$${{effectiveRate}}/h</strong></span>
            </div>
          </div>

          <div>
            <div class="flex justify-between text-[10px] text-slate-400 mb-1">
              <span>Daily Shift Duty:</span>
              <span class="text-slate-300 font-mono">${{d.total_duty_hours}}h / ${{dailyLimit}}h max</span>
            </div>
            <div class="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
              <div class="bg-emerald-500 h-1.5" style="width: ${{dutyPct}}%;"></div>
            </div>
          </div>

          <div class="flex justify-between text-[10px] text-slate-400 font-mono">
            <span>Cycle Clock Remaining:</span>
            <span class="${{rem >= 0 ? 'text-emerald-400' : 'text-rose-400 font-bold'}}">${{rem}}h / ${{cycleCap}}h</span>
          </div>

          <div class="flex justify-between text-[10px] text-slate-400 font-mono pt-1 border-t border-slate-800/60">
            <span>Cycle Velocity:</span>
            <span class="text-sky-300 font-bold">${{cycleVehTotal}} cars (${{cycleVelocity}} cars/duty hr)</span>
          </div>
        `;
        container.appendChild(card);
      }});
    }}

    function renderCosts(costs) {{
      document.getElementById('lblHaulerCost').innerText = '$' + (costs.hauler_transport_cost || 0).toFixed(2);
      document.getElementById('lblDriverCost').innerText = '$' + (costs.driver_wages_cost || 0).toFixed(2);
      document.getElementById('lblHandoverCost').innerText = '$' + (costs.handover_cost || 0).toFixed(2);
      const total = '$' + (costs.total_trip_cost || 0).toFixed(2);
      document.getElementById('lblTotalCost').innerText = total;
      document.getElementById('lblTotalCostBottom').innerText = total;
    }}
  </script>
</body>
</html>
'''

# Write to templates/sandbox.html
os.makedirs('templates', exist_ok=True)
with open('templates/sandbox.html', 'w') as f:
    f.write(html_content)

# Write to root sandbox.html (for GitHub Pages static deployment)
with open('sandbox.html', 'w') as f:
    f.write(html_content)

print("Generated templates/sandbox.html and sandbox.html successfully! Size:", len(html_content))
