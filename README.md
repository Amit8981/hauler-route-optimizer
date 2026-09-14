# 🚛 AutoHauler Route & Driver Schedule Optimization System

[![Live Demo](https://img.shields.io/badge/Live%20Demo-GitHub%20Pages-success?style=for-the-badge&logo=github)](https://amit8981.github.io/hauler-route-optimizer/)
[![OR-Tools](https://img.shields.io/badge/OR--Tools-CP--SAT%20v9.15-blue.svg)](https://developers.google.com/optimization)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> 🚀 **Live Interactive Web UI**: **[https://amit8981.github.io/hauler-route-optimizer/](https://amit8981.github.io/hauler-route-optimizer/)**
> 
> 🏛️ **System Architecture & Workflow**: **[architecture/README.md](architecture/README.md)** &mdash; Detailed architectural diagrams, sequence data flow, CP-SAT mathematical formulation, REST APIs, and UI layer breakdown.

An enterprise-grade Operations Research solution for **Finished Vehicle Logistics (Auto-Hauling)**, solving multi-stop Factory $\to$ Dealership $\to$ Factory routing with hauler continuity, driver assignment, **11-hour driver limits**, and **multi-driver handover mechanics** using **Google OR-Tools CP-SAT**.

The problem is solved at the **`load_ID` level**: for any given load, it determines the vehicle cargo manifest, hauler assignment, optimal route sequence, stop-by-stop schedule with arrival/departure times, and driver shifts respecting individual 11-hour FMCSA/DOT limits.

---

## 📑 Mathematical Problem Formulation

The system implements the formulation from [`docs/Complete_OR_formulation_hauler_route_optimization.pdf`](docs/Complete_OR_formulation_hauler_route_optimization.pdf):

### 1. Decision Variables
- **Hauler Movement**: $y_{ijk} \in \{0, 1\}$ &mdash; selects whether hauler $i$ travels on directed arc $j \to k$.
- **Driver Assignment**: $x_{ijkl} \in \{0, 1\}$ &mdash; assigns driver $l \in R$ to operate hauler $i$ on segment $j \to k$.
- **Driver Trip Indicator**: $z_{il} \in \{0, 1\}$ &mdash; tracks whether driver $l$ is utilized on the trip.
- **Timing & Schedule**: $T_{ij}$ (arrival time) and $D_{ij}$ (departure time).
- **Subtour Elimination**: $u_{id} \in [1, |D|]$ (Miller-Tucker-Zemlin rank).
- **Load Tracking**: $L_{ij} \in [0, Q_i]$ (onboard vehicle units).
- **Handover Indicator**: $Handover_k \in \{0, 1\}$ &mdash; marks a driver swap at delivery centre $k$.

### 2. Core Constraints
1. **Allowed Routes & Flow Continuity**: $\sum_{j} y_{ijk} = \sum_{m} y_{ikm} \quad \forall k \in D$.
2. **Same Factory Return**: Hauler departs from origin VDC/factory $F$ and returns to the same factory $F$.
3. **Mandatory Delivery**: Each delivery centre (dealer) in the load manifest is served exactly once.
4. **Subtour Elimination**: MTZ formulation $u_k \ge u_j + 1$ if $y_{jk} = 1$.
5. **Route-Driver Coupling**: $\sum_{l \in R} x_{jkl} = y_{jk}$. Every active segment is assigned exactly one driver.
6. **11-Hour Driver Duty Limit**:
   $$\sum_{(j, k)} (\tau_{jk} + s_k) \cdot x_{jkl} \le 660 \text{ minutes (11.0 hours)} \quad \forall l \in R$$
7. **Driver Handover Mechanics**:
   - If driver on incoming leg $(j \to k) \ne$ driver on outgoing leg $(k \to m)$, then $Handover_k = 1$.
   - Handover is only allowed at designated locations ($Handover_k \le h_k$).
   - Mandatory handover buffer (default 45 mins) is enforced before departure:
     $$D_k \ge T_k + s_k + \text{HandoverTime}_k$$
8. **Hauler Capacity & Max Dealers**: Onboard units $\le Q_i$ and number of visited dealers $\le \text{max\_dealers}$ from `dealer_combo.csv` & `hauler_config.csv`.
9. **Time Windows**: Arrival at dealer $d$ satisfies $E_d \le T_d \le L_d$.

---

## 📂 Data Architecture

The system integrates four core datasets transcribed from enterprise distribution databases:

| Dataset | File | Description |
| :--- | :--- | :--- |
| **Loads Table** | [`data/loads_tbl.csv`](data/loads_tbl.csv) | Load ID, load number, origin legal entity (LA, SF, ML, PT, SK, 04016), status (locked, sent, unlocked), assigned hauler |
| **Hauler Config** | [`data/hauler_config.csv`](data/hauler_config.csv) | Hauler capacities (7 to 11 cars), gross weight, ramp configurations (head, top, bottom), max dealers |
| **Dealer Combo** | [`data/dealer_combo.csv`](data/dealer_combo.csv) | Minimum/maximum load thresholds, split delivery limits, and max dealers per VDC |
| **Model Details** | [`data/model_details.csv`](data/model_details.csv) | Vehicle specifications (Toyota & Lexus models), weights (kg), dimensions (L &times; W &times; H), brand, tier |
| **Dealers Network** | [`data/dealers.csv`](data/dealers.csv) | Dealership delivery locations per VDC network with coordinates, time windows, and handover eligibility |
| **Driver Roster** | [`data/drivers.csv`](data/drivers.csv) | Certified drivers with shift windows, duty limits (660 mins), and hourly wages |
| **Load Manifests** | [`data/load_details.csv`](data/load_details.csv) | Detailed vehicle manifests linking VINs and model IDs to destination dealers |

---

## 🖥️ Local Web UI Dashboard

The application includes an interactive local web dashboard:

- **Load Explorer**: Filter by VDC (`LA`, `SF`, `ML`, `PT`, `SK`, `04016`) or status (`locked`, `sent`, `unlocked`), and search by Load ID.
- **Parameter Controls**: Adjust departure time, driver duty limit ($H_{\max}$), handover buffer duration, and hauler overrides.
- **KPI Summary**: Live solve status (`OPTIMAL`/`FEASIBLE`), total distance, complete trip duration, drivers needed, and cost breakdown.
- **Driver Duty Compliance Bar**: Visual progress bars showing each driver's total duty vs the 11.0h limit.
- **Leg-by-Leg Itinerary Table**: Sequential breakdown of each leg with departure, arrival, service duration, active driver, handover flag, and remaining onboard cargo.
- **Gantt / Timeline Chart**: Visual timeline representing hauler movement, Driver 1 shift, handover window, and Driver 2 shift.
- **Stop Circuit Sequence Diagram**: Interactive node-flow diagram of Factory $\to$ Dealer 1 $\to$ Handover Hub $\to$ Factory.
- **Export**: One-click download of schedule as CSV or JSON.

---

## 🚀 Quickstart & Installation

### Prerequisites
- Python 3.9 or higher
- pip

### 1. Clone the Repository
```bash
git clone https://github.com/Amit8981/hauler-route-optimizer.git
cd hauler-route-optimizer
```

### 2. Create and Activate Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Local Web Dashboard
```bash
python app.py
```
Open your browser at: **`http://127.0.0.1:5050`**

---

## 🧪 Running Automated Tests

Run the unit test suite covering single-driver, multi-driver handover, long-haul PNW routes, and capacity constraint enforcement:

```bash
python -m unittest discover -s tests
```

Output:
```
....
----------------------------------------------------------------------
Ran 4 tests in 0.030s

OK
```

---

## 📊 Sample Output for Load #244606 (Long Beach VDC)

```
======================================================================
OPTIMIZATION RESULTS - LOAD #244606 (LA / Long Beach VDC)
======================================================================
Status: OPTIMAL (18 ms)
Hauler: Test_9 (Capacity: 9 cars) | Cargo: 8 vehicles (19,421 kg)
Total Distance: 598.5 miles | Duration: 14.5 hours | Drivers: 2
Handovers Required: 1 (Fresno Lexus Hub)

DRIVER DUTY SUMMARY:
 - Driver 1 (Relief Driver West): 7.57 hours (COMPLIANT <= 11.0h)
 - Driver 2 (LB764 - Robert R.): 5.98 hours (COMPLIANT <= 11.0h)

ITINERARY:
 Leg 1: LA -> D_LA_01 (Toyota of Anaheim)
        Dep: 07:30 AM | Arr: 07:56 AM | Driver: Relief Driver West
 Leg 2: D_LA_01 -> D_LA_05 (Fresno Lexus Hub)
        Dep: 08:31 AM | Arr: 02:19 PM | Driver: Relief Driver West
        *** DRIVER HANDOVER (45 min buffer) ***
 Leg 3: D_LA_05 -> LA (Long Beach VDC)
        Dep: 03:49 PM | Arr: 12:00 AM | Driver: LB764 (Robert R.)
======================================================================
```

---

## 📄 License
MIT License. Developed for Finished Vehicle Logistics & Hauler Route Optimization.
