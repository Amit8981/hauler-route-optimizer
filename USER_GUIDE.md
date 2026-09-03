# 📖 AutoHauler Dispatch Optimizer — Business User Guide

Welcome to the **AutoHauler Dispatch & Driver Schedule Optimizer**. This guide is designed for Logistics Planners, Dispatch Managers, Fleet Coordinators, and Operations Directors who manage finished vehicle transportation from Vehicle Distribution Centres (VDCs / Plants) to automotive dealerships.

---

## 🌟 Executive Overview & Business Value

Auto-hauling is one of the most operationally constrained segments in freight logistics:
1. **High Cargo Value & Vehicle Dimensions**: Multi-vehicle car haulers carry specialized loads (e.g., Toyota & Lexus sedans, SUVs, trucks) that must comply with strict weight, length, and ramp constraints.
2. **Multi-Stop Deliveries**: Haulers visit between 1 and 3 dealerships per trip before returning to the origin factory/VDC.
3. **Strict 11-Hour Driver Rule**: Under Federal Motor Carrier Safety Administration (FMCSA) and Department of Transportation (DOT) regulations, a commercial truck driver cannot exceed **11 hours of driving/duty time** without a mandatory rest break.
4. **The Long-Haul Challenge**: When a delivery route exceeds 11 hours (e.g., 14–18 hours round trip), single-driver dispatch becomes illegal and impossible. This optimizer automatically schedules a **second driver** and determines the optimal **handover hub** with a mandatory 45-minute transfer buffer, ensuring the trip remains feasible, legal, and cost-effective.

---

## 🖥️ System Architecture: How GitHub Interacts with the UI

The system utilizes a modern, **decoupled architecture**:

```
                  +----------------------------------------------+
                  |           GitHub Infrastructure              |
                  |  Repository: Amit8981/hauler-route-optimizer |
                  +----------------------------------------------+
                                         |
                       Hosts static assets & index.html
                                         v
                  +----------------------------------------------+
                  |         GitHub Pages Cloud CDN Hosting       |
                  |   https://amit8981.github.io/hauler-...      |
                  +----------------------------------------------+
                                         |
                       Loaded directly into user's browser
                                         v
+--------------------------------------------------------------------------------+
|                             USER BROWSER / CLIENT                              |
|                                                                                |
|  [Mode A: Standalone Cloud Mode]              [Mode B: Local Connected Mode]   |
|  - Instant access on any device               - Connects to local Python API   |
|  - Complete embedded 28-load dataset            at http://127.0.0.1:5050       |
|  - Pre-solved CP-SAT optimization results     - Re-solves live on custom       |
|  - Zero installation or setup needed            parameter adjustments          |
+--------------------------------------------------------------------------------+
```

### 1. Zero-Install Cloud Delivery (GitHub Pages)
- **What it does**: GitHub acts as a global Content Delivery Network (CDN) hosting `index.html`.
- **How it works**: When you open `https://amit8981.github.io/hauler-route-optimizer/`, GitHub serves the complete dashboard directly to your browser.
- **Embedded Engine**: The data bundle (28 loads, hauler configurations, vehicle specifications, and pre-computed CP-SAT solutions) is bundled inside the client app. This allows anyone (clients, executives, dispatchers) to review schedules on laptops, tablets, or phones without running Python.

### 2. Live Dynamic Solver Connection (Local Python Backend)
- **What it does**: If you run `python app.py` on your machine, the browser UI detects the local backend (`http://127.0.0.1:5050`).
- **Live Optimization**: Clicking **"SOLVE SCHEDULE (CP-SAT)"** will send dynamic parameters (e.g., custom start times, relaxed duty hours, different handover buffers) directly to the Google OR-Tools CP-SAT engine and refresh the schedule in milliseconds.
- **Decoupled Design**: The Python backend is 100% independent. If your organization decides to migrate to an enterprise frontend (React, Angular, mobile TMS app, or Streamlit), the Python solver remains completely unchanged.

---

## 🧭 Step-by-Step UI Walkthrough

### 1. The Header & System Status
Located at the top of the screen:
- **Solver Badge**: Displays `CP-SAT v9.15` and `11-Hour DOT Engine`.
- **Backend Status Pill**:
  - `Live Python CP-SAT Active` (Green): Browser is actively communicating with your local Python server.
  - `Standalone Mode (Client Ready)` (Blue): Running directly from GitHub Pages with embedded data.
- **OR Formulation Button**: Opens a reference popup detailing the mathematical variables ($y_{ijk}, x_{ijkl}$) and constraints.

---

### 2. Left Sidebar: Load Inventory Explorer
Use this panel to find and select any load:
- **Search Bar**: Type a Load ID (e.g., `244606`), load number (`L-44166`), hauler name, or status.
- **Origin VDC / Plant Filter Pills**:
  - `ALL`: View all 28 loads.
  - `LA`: Long Beach VDC (Southern California network).
  - `SF`: Benicia VDC (Northern California / Bay Area network).
  - `ML`: Mira Loma VDC (Inland Empire / Desert network).
  - `PT`: Portland VDC (Pacific Northwest / Washington / Oregon network).
  - `SK`: Orillia VDC (Eastern regional network).
  - `04016`: Omesa Logistics Hub (Southwest regional network).
- **Load Cards**: Each card displays:
  - **Load ID & Load Number**: e.g., `#244606 L-44166`.
  - **Status Badge**: `LOCKED` (yellow), `SENT` (green), `UNLOCKED` (gray).
  - **Origin Hub**: e.g., `LA (LONG BEACH)`.
  - **Cargo & Stop Count**: e.g., `8 Cars`, `2 Dealers`.
  - **Assigned Hauler**: e.g., `Test_9`.
  - *Action*: Click any card to select it.

---

### 3. Top Banner: Active Load Summary & Parameter Controls
When a load is selected, the top banner updates with its operational profile:
- **Cargo Summary**: Shows total vehicle count and total weight (e.g., `8 Vehicles (19,421 kg)`).
- **Assigned Hauler**: Displays the truck type and capacity limit (e.g., `Test_9 (9 Car Capacity)`).
- **Destination Dealerships**: Displays how many dealer drop-offs are required.

#### Dispatch Parameters Toolbar:
Before solving, you can adjust:
1. **Start Time**: Departure time from the origin factory/VDC (default: `07:00 AM`).
2. **Duty Limit ($H_{\max}$)**: Maximum allowable driver duty hours (default: `11.0 hrs`).
3. **Handover Buffer**: Duration allotted for physical vehicle inspection, paperwork, and driver swap (default: `45 min`).
4. **"SOLVE SCHEDULE (CP-SAT)" Button**: Initiates the Google OR-Tools optimization engine.

---

### 4. Key Performance Indicator (KPI) Summary Cards
Provides an instant executive summary of the dispatch plan:
- **Status**: `OPTIMAL` (optimal route and driver roster found) or `INFEASIBLE` (capacity or timing conflict).
- **Trip Duration**: Total elapsed time from departure at factory to final return.
- **Total Distance**: Total round-trip miles.
- **Drivers Needed**: Displays `1 Driver` for trips $\le 11$ hours, or `2 Drivers` for trips $> 11$ hours.
- **Handover Point**: Identifies the specific dealership/hub where Driver 1 hands over the hauler to Driver 2.
- **Capacity Load**: e.g., `8 / 9 Cars` with total cargo weight.
- **Estimated Cost**: Calculated based on hauler transit costs, driver hourly wages, and handover fees.

---

### 5. Driver 11-Hour Duty Compliance Monitor
Directly below the KPIs, you will see real-time compliance gauges for every driver assigned:
- **Driver Name & ID**: e.g., `Driver 1: Relief Driver West (DRV_08)`.
- **Duty Progress Bar**:
  - 🟩 **Green**: Duty is comfortably within the 11.0-hour limit.
  - 🟨 **Amber**: Approaching the 11.0-hour limit (e.g., $> 9$ hours).
  - 🟥 **Red**: Violation ($> 11.0$ hours).
- **Duty Breakdown**: Displays driving time vs. unloading/handover buffer time.
- **Compliance Badge**: Confirms `COMPLIANT (≤11h)`.

---

### 6. The 4 Detailed Inspection Tabs

#### Tab 1: Leg-by-Leg Schedule (Core Itinerary)
This table provides the exact operational dispatch schedule requested:
- **Leg #**: Leg sequence order (Leg 1, Leg 2, Leg 3...).
- **Origin &rarr; Destination**: Clear terminal/dealer codes and business names.
- **Distance & Travel Time**: Mileage and expected driving time.
- **Departure (Origin)**: Clock time when hauler leaves the previous stop.
- **Arrival (Dest)**: Clock time when hauler arrives at dealership/hub.
- **Service / Unload**: Scheduled unloading duration (e.g., 35–45 minutes).
- **Departure (Dest)**: Clock time when hauler departs after unloading/handover.
- **Active Driver**: Assigned driver name and employee ID.
- **Handover**: Highlights `HANDOVER (45m)` in amber badge if a driver swap occurs.
- **Onboard Cargo**: Number of vehicles remaining on the trailer after delivery.

#### Tab 2: Driver & Hauler Timeline (Gantt Chart)
A visual Gantt bar chart displaying:
- **Hauler Transit**: Top blue bar showing the truck's overall multi-stop progression.
- **Driver Shift Bars**: Green bars showing the exact active shift window for Driver 1 and Driver 2.
- **Handover Window**: Clearly highlights where the shift handoff takes place.

#### Tab 3: Stop Circuit & Handover Diagram
A schematic node-flow diagram:
- `Factory Start Depot` &rarr; `Dealership 1` &rarr; `Handover Hub` &rarr; `Dealership 2` &rarr; `Factory Return Depot`.
- Displays arrival and departure times at each node.

#### Tab 4: Vehicle Cargo Manifest
A detailed inventory of every automobile carried on the trailer:
- **VIN**: Unique vehicle identification number.
- **Model Description**: e.g., `bZ4X AWD`, `TACOMA 4`, `TX FSPORT 350`, `COROLLA`, `TUNDRA 4`.
- **Brand / Series**: Toyota or Lexus.
- **Weight**: Exact weight in kg for road weight verification.
- **Dimensions**: Length &times; Width &times; Height in meters for ramp clearance.
- **Destination Dealer**: Specific dealership where the unit will be unloaded.

---

### 7. Exporting Dispatch Plans
Located at the top-right of the tab bar:
- **Export CSV**: Downloads `schedule_load_<ID>.csv` formatted for direct import into dispatch management systems (e.g., TMW Systems / Trimble).
- **JSON**: Opens raw structured JSON for integration with backend logistics APIs.

---

## 💡 Practical Business Use Cases

### Case A: Standard Local Route (Single Driver)
- **Select**: Load `#244861` (Mira Loma VDC).
- **Cargo**: 8 Vehicles to Ontario & San Bernardino dealers.
- **Outcome**: Round trip is 47.9 miles, taking 2.3 hours.
- **Result**: Exactly **1 Driver** (`Ravi Sushil`) assigned. 0 handovers. Total duty is 2.28 hours (well under 11 hours).

### Case B: Long-Haul Regional Route (Multi-Driver Handover)
- **Select**: Load `#244606` (Long Beach VDC).
- **Cargo**: 8 Vehicles with delivery to Anaheim and Fresno Lexus Hub.
- **Outcome**: Round trip is 598.5 miles, taking 14.5 hours.
- **Result**: A single driver cannot legally complete 14.5 hours.
  - The CP-SAT engine assigns **2 Drivers**:
    - **Driver 1** (`Relief Driver West`): Drives Long Beach &rarr; Anaheim &rarr; Fresno (7.57 hours duty $\le 11$h).
    - **Handover**: Fresno Lexus Hub ($h_k = 1$) with 45-minute handover buffer.
    - **Driver 2** (`LB764 - Robert R.`): Takes over at Fresno and returns to Long Beach (5.98 hours duty $\le 11$h).
  - Both drivers remain fully compliant with FMCSA regulations.

### Case C: Pacific Northwest Corridor
- **Select**: Load `#245356` (Portland VDC).
- **Cargo**: 8 Vehicles to Beaverton and Spokane Regional Hub.
- **Outcome**: 758.5 miles round trip.
- **Result**: Handover scheduled at Spokane Hub between Relief Driver North (9.33h) and Relief Driver West (7.67h).

---

## ❓ Frequently Asked Questions (FAQ)

**Q: Can I run this UI without any coding knowledge?**  
A: Yes! Simply open the link in any web browser: [https://amit8981.github.io/hauler-route-optimizer/](https://amit8981.github.io/hauler-route-optimizer/). All 28 loads are pre-loaded and interactive.

**Q: Where can handovers take place?**  
A: In accordance with Section 11.2 of the OR formulation ($Handover_k \le h_k$), handovers can only occur at designated dealerships or transit hubs where driver lodging and facilities exist ($h_k = 1$). Locations with $h_k = 0$ will never be assigned as handover points.

**Q: What happens if a load exceeds hauler capacity?**  
A: The system checks capacity constraints before solving ($L \le Q_i$). If a hauler with capacity 7 is assigned 8 vehicles, the UI marks the load as `INFEASIBLE: CAPACITY_EXCEEDED` and prompts the user to select an appropriate 9- or 10-car trailer.

**Q: How do we plug in our own enterprise database?**  
A: The data structure in `data/loads_tbl.csv`, `data/hauler_config.csv`, and `data/model_details.csv` matches standard vehicle dispatch schemas. The Python backend (`hauler_cpsat_solver.py`) can be connected directly to PostgreSQL, Oracle, Snowflake, or SAP TMS without any frontend rework.
