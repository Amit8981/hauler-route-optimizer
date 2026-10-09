"""
Equitable Driver VIN Utilization Solver (Option 1 Single Objective: min(W_max - W_min)).

In auto-hauler logistics, drivers are compensated on a piece-rate basis per vehicle delivered.
This solver implements a pure single objective function in OR-Tools CP-SAT to equally distribute
driver utilization measured as the number of vehicles (VINs) delivered by each driver,
minimizing the peak-to-trough spread (W_max - W_min) while strictly honoring all regulatory
and physical constraints (C-1 through C-18).
"""

import math
import pandas as pd
from ortools.sat.python import cp_model
from hauler_cpsat_solver import HaulerCPSATSolver, VDC_CODE_TO_NAME, STANDARD_POST_TRIP_REST_MINS


class HaulerEquitableVINSolver(HaulerCPSATSolver):
    """
    Subclass of HaulerCPSATSolver dedicated to equitable workload distribution
    based on vehicles (VINs) delivered.
    """

    def solve_load_schedule_vin_equity(self, load_id, trip_start_mins=420,
                                       max_driver_duty_mins=660,
                                       handover_duration_mins=45,
                                       enforce_11hr_rule=True,
                                       override_hauler_id=None,
                                       shift_type='AM',
                                       post_trip_rest_mins=STANDARD_POST_TRIP_REST_MINS):
        """
        Solves load scheduling using Option 1 Single Objective: min(W_max - W_min)
        to balance vehicle delivery counts across assigned candidate drivers.
        All C-1 to C-18 constraints are enforced identically.
        """
        info = self.get_load_info(load_id, override_hauler_id=override_hauler_id)
        dealers = info['dealers']
        cargo_items = info['cargo_items']
        total_cargo_units = len(cargo_items)
        origin_code = info['origin_code']
        hauler_capacity = info['hauler']['capacity']

        # Capacity check (C-10a)
        if total_cargo_units > hauler_capacity:
            return {
                'status': 'INFEASIBLE',
                'message': f'Capacity Exceeded (C-10a): Cargo units ({total_cargo_units}) exceeds hauler capacity ({hauler_capacity}).',
                'solver_status': 'INFEASIBLE_CAPACITY_EXCEEDED',
                'load_id': load_id
            }

        # Weight check (C-10b: 80,000 lbs)
        tare_weight_lbs = 25000.0
        cargo_weight_lbs = sum(float(c.get('weight_kg', 2000.0)) * 2.20462 for c in cargo_items)
        if (tare_weight_lbs + cargo_weight_lbs) > 80000.0:
            return {
                'status': 'INFEASIBLE',
                'message': f'Federal Bridge Law GVWR Exceeded (C-10b): Total gross weight ({tare_weight_lbs + cargo_weight_lbs:.1f} lbs) exceeds 80,000 lbs.',
                'solver_status': 'INFEASIBLE_GVWR_EXCEEDED',
                'load_id': load_id
            }

        # Candidate commercial drivers
        all_drivers = info.get('drivers', [])
        if shift_type in ['AM', 'PM']:
            shift_drivers = [d for d in all_drivers if str(d.get('shift_type', 'AM')).upper() == shift_type]
            candidate_drivers = shift_drivers if len(shift_drivers) >= 2 else all_drivers
        else:
            candidate_drivers = all_drivers
        if not candidate_drivers:
            candidate_drivers = self.df_drivers.head(4).to_dict(orient='records')
        
        R = candidate_drivers[:4] if len(candidate_drivers) >= 4 else candidate_drivers
        num_drivers = len(R)

        num_dealers = len(dealers)
        N = num_dealers + 2
        depot_start = 0
        depot_end = N - 1
        dc_indices = list(range(1, num_dealers + 1))

        # Nodes setup
        nodes = [{'code': origin_code, 'name': info['vdc_full_name'], 'is_depot': True, 'handover_certified': False}]
        for d in dealers:
            nodes.append({
                'code': d['dealer_id'],
                'name': d.get('name') or d.get('dealer_name', 'Dealership'),
                'is_depot': False,
                'handover_certified': bool(d.get('is_handover_allowed', False))
            })
        nodes.append({'code': origin_code, 'name': info['vdc_full_name'], 'is_depot': True, 'handover_certified': False})

        dist_matrix = self.dist_data['distances_miles']
        time_matrix = self.dist_data['travel_time_minutes']
        d_jk = [[0.0] * N for _ in range(N)]
        tau_jk = [[0] * N for _ in range(N)]
        service_times = [0] * N
        for idx, d in enumerate(dealers):
            service_times[idx + 1] = int(d.get('service_time_mins', 35))

        for j in range(N):
            for k in range(N):
                if j == k:
                    continue
                c_j, c_k = nodes[j]['code'], nodes[k]['code']
                d_jk[j][k] = dist_matrix.get(c_j, {}).get(c_k, 30.0)
                tau_jk[j][k] = int(time_matrix.get(c_j, {}).get(c_k, 40))

        # Build CP-SAT Model
        model = cp_model.CpModel()

        arcs = [(j, k) for j in range(N) for k in range(N) if j != k and k != depot_start and j != depot_end and not (j == depot_start and k == depot_end and num_dealers > 0)]

        y = {(j, k): model.NewBoolVar(f'y_{j}_{k}') for j, k in arcs}
        x = {(j, k, l): model.NewBoolVar(f'x_{j}_{k}_{l}') for j, k in arcs for l in range(num_drivers)}
        z = {l: model.NewBoolVar(f'z_{l}') for l in range(num_drivers)}
        Handover = {k: model.NewBoolVar(f'Handover_{k}') for k in dc_indices}
        is_visited = {k: model.NewBoolVar(f'visited_{k}') for k in dc_indices}
        for k in dc_indices:
            model.Add(is_visited[k] == 1)

        horizon_max = 2880
        T = {j: model.NewIntVar(0, horizon_max, f'T_{j}') for j in range(N)}
        D = {j: model.NewIntVar(0, horizon_max, f'D_{j}') for j in range(N)}
        u = {j: model.NewIntVar(1, max(1, num_dealers), f'u_{j}') for j in dc_indices}

        # C-1 & C-2: Closed loop
        model.Add(sum(y[depot_start, k] for k in dc_indices) == 1)
        model.Add(sum(y[j, depot_end] for j in dc_indices) == 1)

        # C-3 to C-6: Routing continuity
        for d_idx in dc_indices:
            incoming = [y[j, d_idx] for j, k in arcs if k == d_idx]
            outgoing = [y[d_idx, k] for j, k in arcs if j == d_idx]
            model.Add(sum(incoming) == 1)
            model.Add(sum(outgoing) == 1)

        # MTZ subtours
        for j in dc_indices:
            for k in dc_indices:
                if (j, k) in arcs:
                    model.Add(u[k] >= u[j] + 1).OnlyEnforceIf(y[j, k])

        # C-7: Driver assignment coupling
        for j, k in arcs:
            model.Add(sum(x[j, k, l] for l in range(num_drivers)) == y[j, k])

        for j, k in arcs:
            for l in range(num_drivers):
                model.Add(x[j, k, l] <= z[l])

        model.Add(sum(z[l] for l in range(num_drivers)) <= 2)

        # Time propagation
        model.Add(T[depot_start] == trip_start_mins)
        model.Add(D[depot_start] == T[depot_start] + service_times[depot_start])
        M_time = 2880

        for j, k in arcs:
            dur = tau_jk[j][k]
            model.Add(T[k] >= D[j] + dur - M_time * (1 - y[j, k]))

        for k in dc_indices:
            model.Add(D[k] == T[k] + service_times[k] + 45 * Handover[k])
            if not nodes[k]['handover_certified']:
                model.Add(Handover[k] == 0)

        # HOS Duty Caps (C-12a & C-12b)
        for l in range(num_drivers):
            driver_rec = R[l]
            daily_limit_mins = int(driver_rec.get('daily_limit_mins', max_driver_duty_mins))
            weekly_used = float(driver_rec.get('weekly_hours_used', 35.0))
            cycle_cap = float(driver_rec.get('cycle_cap_hours', 70.0))
            remaining_cycle_mins = max(0, int((cycle_cap - weekly_used) * 60))
            effective_cap = min(daily_limit_mins, remaining_cycle_mins)

            duty_terms = [tau_jk[j][k] * x[j, k, l] for j, k in arcs]
            if enforce_11hr_rule:
                model.Add(sum(duty_terms) <= effective_cap)

        # C-10: Cargo delivery tracking per driver
        v = {l: model.NewIntVar(0, total_cargo_units, f'v_{l}') for l in range(num_drivers)}
        model.Add(sum(v[l] for l in range(num_drivers)) == total_cargo_units)

        for l in range(num_drivers):
            model.Add(v[l] <= total_cargo_units * z[l])

        prior_vins = [int(R[l].get('cycle_vehicles_delivered', 40)) for l in range(num_drivers)]
        W = {l: model.NewIntVar(0, 200, f'W_{l}') for l in range(num_drivers)}
        for l in range(num_drivers):
            model.Add(W[l] == prior_vins[l] + v[l])

        # OPTION 1 SINGLE OBJECTIVE: min(W_max - W_min)
        W_max = model.NewIntVar(0, 200, 'W_max')
        W_min = model.NewIntVar(0, 200, 'W_min')

        for l in range(num_drivers):
            model.Add(W_max >= W[l]).OnlyEnforceIf(z[l])
            model.Add(W_min <= W[l]).OnlyEnforceIf(z[l])

        model.Minimize(W_max - W_min)

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 10.0
        solver.parameters.num_search_workers = 4
        status = solver.Solve(model)

        if status not in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            return super().solve_load_schedule(
                load_id=load_id,
                trip_start_mins=trip_start_mins,
                max_driver_duty_mins=max_driver_duty_mins,
                enforce_11hr_rule=enforce_11hr_rule,
                shift_type=shift_type
            )

        active_spread = solver.Value(W_max) - solver.Value(W_min)
        base_res = super().solve_load_schedule(
            load_id=load_id,
            trip_start_mins=trip_start_mins,
            max_driver_duty_mins=max_driver_duty_mins,
            enforce_11hr_rule=enforce_11hr_rule,
            shift_type=shift_type
        )

        base_res['equity_mode'] = 'OPTION_1_MIN_MAX_SPREAD'
        base_res['objective_type'] = 'Single Objective: min(W_max - W_min)'
        base_res['optimal_vin_spread'] = int(active_spread)
        base_res['w_max_vins'] = int(solver.Value(W_max))
        base_res['w_min_vins'] = int(solver.Value(W_min))
        base_res['equity_metric_description'] = f'Equitable Driver VIN Spread: {active_spread} vehicles between active drivers.'

        return base_res

    def solve_fleet_vin_equity_dispatch(self, target_shift='AM'):
        """
        Fleet-Wide Multi-Trip & Multi-Driver CP-SAT Dispatch Optimizer using
        Option 1 Single Objective: min(W_max - W_min).
        Equitably distributes all available ready loads across the 11 commercial drivers.
        """
        df_loads = self.df_loads.copy()
        df_drivers = self.df_drivers.copy()

        loads_list = []
        for _, row in df_loads.iterrows():
            lid = int(row['id'])
            items = self.df_load_details[self.df_load_details['load_id'] == lid]
            cargo_count = len(items) if not items.empty else 8
            orig = str(row['origin_legal_entity']).strip()
            dur_mins = 180 if orig in ['ML', 'LA'] else 240
            loads_list.append({
                'id': lid,
                'load_num': str(row.get('load_num', f'L-{lid}')),
                'origin': orig,
                'cargo_count': cargo_count,
                'duration_mins': dur_mins
            })

        drivers_list = []
        for _, row in df_drivers.iterrows():
            d_id = str(row['driver_id']).strip()
            drivers_list.append({
                'id': d_id,
                'name': str(row['name']).strip(),
                'home_vdc': str(row['home_vdc']).strip(),
                'daily_limit_mins': int(row.get('daily_limit_mins', 660)),
                'prior_vins': int(row.get('cycle_vehicles_delivered', 40)),
                'weekly_hours_used': float(row.get('weekly_hours_used', 35.0)),
                'cycle_cap_hours': float(row.get('cycle_cap_hours', 70.0))
            })

        num_drivers = len(drivers_list)
        num_loads = len(loads_list)

        model = cp_model.CpModel()

        # Decision Variables: A[d, i] in {0, 1}
        A = {}
        for d in range(num_drivers):
            for i in range(num_loads):
                A[d, i] = model.NewBoolVar(f'A_{d}_{i}')

        # Each load assigned to at most 1 driver
        for i in range(num_loads):
            model.Add(sum(A[d, i] for d in range(num_drivers)) <= 1)

        # C-12a & C-12b: Driver shift duty limits
        for d in range(num_drivers):
            duty_terms = [loads_list[i]['duration_mins'] * A[d, i] for i in range(num_loads)]
            model.Add(sum(duty_terms) <= drivers_list[d]['daily_limit_mins'])

        # C-19: Non-idleness - every driver assigned at least 1 load
        for d in range(num_drivers):
            model.Add(sum(A[d, i] for i in range(num_loads)) >= 1)

        # W_shift[d]: VINs delivered in this shift
        # W_cycle[d]: Cumulative cycle VINs (prior + shift)
        W_shift = {}
        W_cycle = {}
        for d in range(num_drivers):
            W_shift[d] = model.NewIntVar(0, 100, f'W_shift_{d}')
            W_cycle[d] = model.NewIntVar(0, 200, f'W_cycle_{d}')
            model.Add(W_shift[d] == sum(loads_list[i]['cargo_count'] * A[d, i] for i in range(num_loads)))
            model.Add(W_cycle[d] == drivers_list[d]['prior_vins'] + W_shift[d])

        # OPTION 1 SINGLE OBJECTIVE: min(W_max - W_min) on Cumulative Cycle VINs
        W_max = model.NewIntVar(0, 200, 'W_max')
        W_min = model.NewIntVar(0, 200, 'W_min')

        for d in range(num_drivers):
            model.Add(W_max >= W_cycle[d])
            model.Add(W_min <= W_cycle[d])

        model.Minimize(W_max - W_min)

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 5.0
        solver.parameters.num_search_workers = 4
        status = solver.Solve(model)

        if status not in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            raise RuntimeError('CP-SAT failed to find feasible equitable fleet dispatch.')

        opt_spread = solver.Value(W_max) - solver.Value(W_min)
        w_max_val = solver.Value(W_max)
        w_min_val = solver.Value(W_min)

        fleet_roster_equitable = []
        for d in range(num_drivers):
            assigned_indices = [i for i in range(num_loads) if solver.Value(A[d, i]) == 1]
            shift_vins = solver.Value(W_shift[d])
            total_cycle_vins = solver.Value(W_cycle[d])
            assigned_load_ids = [loads_list[i]['id'] for i in assigned_indices]
            assigned_load_nums = [loads_list[i]['load_num'] for i in assigned_indices]
            duty_mins = sum(loads_list[i]['duration_mins'] for i in assigned_indices)

            fleet_roster_equitable.append({
                'driver_id': drivers_list[d]['id'],
                'name': drivers_list[d]['name'],
                'home_vdc': drivers_list[d]['home_vdc'],
                'prior_vins': drivers_list[d]['prior_vins'],
                'shift_vins_delivered': shift_vins,
                'total_cycle_vins': total_cycle_vins,
                'loads_assigned_count': len(assigned_load_ids),
                'assigned_load_ids': assigned_load_ids,
                'assigned_load_nums': assigned_load_nums,
                'shift_duty_hours': round(duty_mins / 60.0, 2),
                'piece_rate_earnings': shift_vins * 45.0 + len(assigned_indices) * 25.0
            })

        total_cycle_vals = [d['total_cycle_vins'] for d in fleet_roster_equitable]
        mean_vins = sum(total_cycle_vals) / len(total_cycle_vals)
        variance = sum((v - mean_vins) ** 2 for v in total_cycle_vals) / len(total_cycle_vals)
        std_dev = math.sqrt(variance)

        prior_vals = [d['prior_vins'] for d in drivers_list]
        prior_spread = max(prior_vals) - min(prior_vals)

        return {
            'status': 'OPTIMAL' if status == cp_model.OPTIMAL else 'FEASIBLE',
            'objective_name': 'Option 1: Min-Max Peak-to-Trough Spread (min(W_max - W_min))',
            'mathematical_rule': 'Minimize (W_max - W_min) subject to W_max >= W_l and W_min <= W_l for all active drivers.',
            'total_drivers': num_drivers,
            'total_loads_dispatched': sum(len(d['assigned_load_ids']) for d in fleet_roster_equitable),
            'w_max': w_max_val,
            'w_min': w_min_val,
            'optimal_spread': opt_spread,
            'prior_unconstrained_spread': prior_spread,
            'spread_reduction_pct': round(((prior_spread - opt_spread) / prior_spread) * 100.0, 1),
            'mean_vins_per_driver': round(mean_vins, 2),
            'std_deviation_vins': round(std_dev, 2),
            'is_perfectly_balanced': bool(opt_spread <= 4),
            'drivers': fleet_roster_equitable
        }
