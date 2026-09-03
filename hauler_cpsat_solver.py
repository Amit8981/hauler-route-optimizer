"""
Hauler Route & Driver Schedule Optimization Engine using Google OR-Tools CP-SAT.
Formulation based on: Complete_OR_formulation_hauler_route_optimization.pdf
"""

import json
import math
import os
import pandas as pd
from ortools.sat.python import cp_model


VDC_CODE_TO_NAME = {
    'LA': 'LONG BEACH',
    'SF': 'BENICIA',
    'ML': 'MIRA LOMA',
    'PT': 'PORTLAND',
    'SK': 'ORILLIA',
    '04016': 'OMESA'
}


class HaulerCPSATSolver:
    def __init__(self, data_dir=None):
        if data_dir is None:
            self.data_dir = os.path.join(os.path.dirname(__file__), 'data')
        else:
            self.data_dir = data_dir
        
        self.load_data()

    def load_data(self):
        """Loads all CSV tables and distance matrices."""
        self.df_loads = pd.read_csv(os.path.join(self.data_dir, 'loads_tbl.csv'))
        self.df_haulers = pd.read_csv(os.path.join(self.data_dir, 'hauler_config.csv'))
        self.df_dealers_combo = pd.read_csv(os.path.join(self.data_dir, 'dealer_combo.csv'))
        self.df_models = pd.read_csv(os.path.join(self.data_dir, 'model_details.csv'))
        self.df_dealers = pd.read_csv(os.path.join(self.data_dir, 'dealers.csv'))
        self.df_drivers = pd.read_csv(os.path.join(self.data_dir, 'drivers.csv'))
        self.df_load_details = pd.read_csv(os.path.join(self.data_dir, 'load_details.csv'))
        
        with open(os.path.join(self.data_dir, 'distances.json'), 'r') as f:
            self.dist_data = json.load(f)

    def get_load_info(self, load_id, override_hauler_id=None):
        """Retrieves comprehensive information for a given load_id."""
        matching_load = self.df_loads[self.df_loads['id'] == int(load_id)]
        if matching_load.empty:
            raise ValueError(f"Load ID {load_id} not found in loads_tbl.csv")
        
        load_row = matching_load.iloc[0].to_dict()
        origin_code = str(load_row['origin_legal_entity']).strip()
        vdc_full_name = VDC_CODE_TO_NAME.get(origin_code, 'LONG BEACH')
        
        # Cargo items
        cargo_items = self.df_load_details[self.df_load_details['load_id'] == int(load_id)].to_dict(orient='records')
        cargo_count = len(cargo_items)

        # Hauler configuration lookup
        hauler_id = override_hauler_id if override_hauler_id is not None else load_row.get('assigned_hauler_id')
        hauler_row = None
        
        if pd.notna(hauler_id):
            matching_h = self.df_haulers[self.df_haulers['id'] == int(hauler_id)]
            if not matching_h.empty:
                hauler_row = matching_h.iloc[0].to_dict()
        
        if hauler_row is None:
            # Pick a suitable active hauler for this VDC with capacity >= cargo_count
            matching_vdc_h = self.df_haulers[
                self.df_haulers['trailer_vdc_location'].astype(str).str.contains(vdc_full_name, case=False, na=False) &
                (self.df_haulers['capacity'] >= cargo_count)
            ]
            if not matching_vdc_h.empty:
                hauler_row = matching_vdc_h.iloc[0].to_dict()
            else:
                # Fallback to any hauler with sufficient capacity
                suff_h = self.df_haulers[self.df_haulers['capacity'] >= cargo_count]
                hauler_row = suff_h.iloc[0].to_dict() if not suff_h.empty else self.df_haulers.iloc[0].to_dict()

        # Dealer combo rules
        matching_combo = self.df_dealers_combo[
            self.df_dealers_combo['vdc_location'].astype(str).str.contains(vdc_full_name, case=False, na=False)
        ]
        max_dealers = 3
        if not matching_combo.empty and pd.notna(matching_combo.iloc[0]['max_dealers']):
            max_dealers = int(matching_combo.iloc[0]['max_dealers'])
        elif pd.notna(hauler_row.get('max_dealers')):
            max_dealers = int(hauler_row['max_dealers'])

        # Destination dealerships for cargo
        dest_dealer_ids = list(set(item['destination_dealer_id'] for item in cargo_items))
        dealers_info = []
        for d_id in dest_dealer_ids:
            d_match = self.df_dealers[self.df_dealers['dealer_id'] == d_id]
            if not d_match.empty:
                d_dict = d_match.iloc[0].to_dict()
                # Count cars and weight for this dealer
                cars = [item for item in cargo_items if item['destination_dealer_id'] == d_id]
                d_dict['demand_units'] = len(cars)
                d_dict['demand_weight_kg'] = sum(float(c['weight_kg']) if pd.notna(c['weight_kg']) else 2000.0 for c in cars)
                dealers_info.append(d_dict)

        # Available drivers
        # Prioritize drivers stationed at origin VDC, plus general relief drivers
        matching_drivers = self.df_drivers[
            (self.df_drivers['home_vdc'] == origin_code) | 
            (self.df_drivers['driver_id'].isin(['DRV_08', 'DRV_09']))
        ].to_dict(orient='records')
        
        if len(matching_drivers) < 2:
            matching_drivers = self.df_drivers.to_dict(orient='records')

        return {
            'load': load_row,
            'origin_code': origin_code,
            'vdc_full_name': vdc_full_name,
            'hauler': hauler_row,
            'max_dealers': max_dealers,
            'cargo_items': cargo_items,
            'dealers': dealers_info,
            'drivers': matching_drivers
        }

    def solve_load_schedule(self, load_id, trip_start_mins=420, max_driver_duty_mins=660, 
                            handover_duration_mins=45, enforce_11hr_rule=True, 
                            override_hauler_id=None, max_solve_time_sec=15.0):
        """
        Solves the hauler routing and driver scheduling problem for a single load_id using OR-Tools CP-SAT.
        """
        info = self.get_load_info(load_id, override_hauler_id=override_hauler_id)
        origin_code = info['origin_code']
        dealers = info['dealers']
        drivers = info['drivers']
        hauler = info['hauler']
        cargo = info['cargo_items']
        total_cargo_units = len(cargo)
        hauler_capacity = int(hauler.get('capacity', 9)) if pd.notna(hauler.get('capacity')) else 9
        
        num_dealers = len(dealers)
        if num_dealers == 0:
            return {
                'status': 'ERROR', 
                'message': f'No destination dealerships found for Load {load_id}',
                'load_id': load_id,
                'origin_vdc': origin_code
            }

        # Check capacity upfront
        if total_cargo_units > hauler_capacity:
            return {
                'status': 'INFEASIBLE',
                'message': f"Capacity violation: Load has {total_cargo_units} vehicles, but hauler '{hauler.get('name')}' capacity is only {hauler_capacity} units.",
                'solver_status': 'CAPACITY_EXCEEDED',
                'load_id': load_id,
                'origin_vdc': origin_code,
                'assigned_hauler_name': hauler.get('name')
            }

        # -------------------------------------------------------------
        # 1. Location indexing
        # 0: Origin Factory (Departure depot F_start)
        # 1 .. num_dealers: Dealerships (Delivery Centres D)
        # num_dealers + 1: Origin Factory (Return depot F_end)
        # -------------------------------------------------------------
        loc_keys = [origin_code] + [d['dealer_id'] for d in dealers] + [origin_code]
        N = len(loc_keys)
        depot_start = 0
        depot_end = N - 1
        dc_indices = list(range(1, num_dealers + 1))
        
        # Distances and Travel times
        dist_matrix = self.dist_data['distances_miles']
        time_matrix = self.dist_data['travel_time_minutes']
        
        d_jk = [[0.0] * N for _ in range(N)]
        tau_jk = [[0] * N for _ in range(N)]
        
        for i in range(N):
            k1 = loc_keys[i]
            for j in range(N):
                k2 = loc_keys[j]
                if i != j:
                    d_jk[i][j] = dist_matrix.get(k1, {}).get(k2, 30.0)
                    tau_jk[i][j] = int(time_matrix.get(k1, {}).get(k2, 40))
                else:
                    d_jk[i][j] = 0.0
                    tau_jk[i][j] = 0

        # Service times
        service_times = [30] * N
        service_times[depot_start] = 30
        service_times[depot_end] = 15
        for idx, d in enumerate(dealers):
            service_times[idx + 1] = int(d.get('service_time_mins', 35))

        # Handover allowed indicator h_k
        handover_allowed = [0] * N
        handover_allowed[depot_start] = 1
        handover_allowed[depot_end] = 1
        for idx, d in enumerate(dealers):
            handover_allowed[idx + 1] = int(d.get('is_handover_allowed', 1))

        # Time windows [E_j, L_j]
        earliest_time = [0] * N
        latest_time = [2880] * N
        earliest_time[depot_start] = trip_start_mins
        latest_time[depot_start] = trip_start_mins + 60
        
        for idx, d in enumerate(dealers):
            node_idx = idx + 1
            earliest_time[node_idx] = int(d.get('earliest_arrival', 360))
            latest_time[node_idx] = int(d.get('latest_arrival', 1440))

        # Driver pool (pick top 4)
        R = drivers[:min(len(drivers), 4)]
        num_drivers = len(R)

        # -------------------------------------------------------------
        # CP-SAT MODEL INITIALIZATION
        # -------------------------------------------------------------
        model = cp_model.CpModel()

        # Valid directed arcs (j -> k)
        arcs = []
        for j in range(N):
            for k in range(N):
                if j == k:
                    continue
                if k == depot_start or j == depot_end:
                    continue
                if j == depot_start and k == depot_end and num_dealers > 0:
                    continue
                arcs.append((j, k))

        # Decision variables
        y = { (j, k): model.NewBoolVar(f"y_{j}_{k}") for j, k in arcs }
        x = { (j, k, l): model.NewBoolVar(f"x_{j}_{k}_{l}") for j, k in arcs for l in range(num_drivers) }
        z = { l: model.NewBoolVar(f"z_{l}") for l in range(num_drivers) }
        Handover = { k: model.NewBoolVar(f"Handover_{k}") for k in dc_indices }

        horizon_max = 2880  # 48 hours
        T = { j: model.NewIntVar(0, horizon_max, f"T_{j}") for j in range(N) }
        D = { j: model.NewIntVar(0, horizon_max, f"D_{j}") for j in range(N) }
        u = { j: model.NewIntVar(1, num_dealers, f"u_{j}") for j in dc_indices }
        L = { j: model.NewIntVar(0, hauler_capacity, f"L_{j}") for j in range(N) }

        # Constraints
        # 1. Departure from origin factory
        model.Add(sum(y[depot_start, k] for k in dc_indices) == 1)

        # 2. Return to origin factory
        model.Add(sum(y[j, depot_end] for j in dc_indices) == 1)

        # 3. Flow conservation & single visit per DC
        for d_idx in dc_indices:
            incoming = [y[j, d_idx] for j, k in arcs if k == d_idx]
            outgoing = [y[d_idx, k] for j, k in arcs if j == d_idx]
            model.Add(sum(incoming) == 1)
            model.Add(sum(outgoing) == 1)

        # 4. Max dealers limit
        max_allowed_dealers = info['max_dealers']
        model.Add(num_dealers <= max_allowed_dealers)

        # 5. MTZ subtour elimination
        for j in dc_indices:
            for k in dc_indices:
                if (j, k) in arcs:
                    model.Add(u[k] >= u[j] + 1).OnlyEnforceIf(y[j, k])

        # 6. Route-driver coupling
        for j, k in arcs:
            model.Add(sum(x[j, k, l] for l in range(num_drivers)) == y[j, k])

        # 7. Driver trip indicator
        for j, k in arcs:
            for l in range(num_drivers):
                model.Add(x[j, k, l] <= z[l])

        # 8. Time propagation
        model.Add(T[depot_start] == trip_start_mins)
        model.Add(D[depot_start] >= T[depot_start] + service_times[depot_start])

        for j in dc_indices:
            model.Add(D[j] >= T[j] + service_times[j])
            model.Add(D[j] >= T[j] + service_times[j] + handover_duration_mins).OnlyEnforceIf(Handover[j])
            model.Add(T[j] >= earliest_time[j])
            model.Add(T[j] <= latest_time[j])

        for j, k in arcs:
            model.Add(T[k] >= D[j] + tau_jk[j][k]).OnlyEnforceIf(y[j, k])

        # 9. Handover mechanics
        for k in dc_indices:
            if handover_allowed[k] == 0:
                model.Add(Handover[k] == 0)

            incoming_arcs = [(j, k) for j, _ in arcs if _ == k]
            outgoing_arcs = [(k, m) for _, m in arcs if _ == k]
            
            for j, _ in incoming_arcs:
                for _, m in outgoing_arcs:
                    for l1 in range(num_drivers):
                        for l2 in range(num_drivers):
                            if l1 != l2:
                                model.Add(Handover[k] >= x[j, k, l1] + x[k, m, l2] - 1)

        # 10. 11-Hour Driver Duty Limit
        for l in range(num_drivers):
            driver_duty_terms = []
            for j, k in arcs:
                duty_on_leg = tau_jk[j][k] + (service_times[k] if k != depot_end else 0)
                driver_duty_terms.append(duty_on_leg * x[j, k, l])
            
            if enforce_11hr_rule:
                model.Add(sum(driver_duty_terms) <= max_driver_duty_mins)

        # 11. Capacity & Load conservation
        model.Add(L[depot_start] == total_cargo_units)
        for idx, d in enumerate(dealers):
            node_idx = idx + 1
            demand_units = d.get('demand_units', 1)
            for j, _ in arcs:
                if _ == node_idx:
                    model.Add(L[node_idx] == L[j] - demand_units).OnlyEnforceIf(y[j, node_idx])
        model.Add(L[depot_end] == 0)

        # Objective Function
        hauler_cost_per_mile = 2
        hauler_cost_per_min = 1
        driver_cost_per_min = 1
        handover_penalty = 500
        extra_driver_penalty = 1000

        obj_terms = []
        for j, k in arcs:
            dist_cost = int(round(d_jk[j][k] * 10)) * hauler_cost_per_mile
            time_cost = tau_jk[j][k] * hauler_cost_per_min
            obj_terms.append((dist_cost + time_cost) * y[j, k])

        for l in range(num_drivers):
            obj_terms.append(extra_driver_penalty * z[l])
            for j, k in arcs:
                leg_mins = tau_jk[j][k] + service_times[k]
                obj_terms.append(leg_mins * driver_cost_per_min * x[j, k, l])

        for k in dc_indices:
            obj_terms.append(handover_penalty * Handover[k])

        model.Minimize(sum(obj_terms))

        # Solve
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = max_solve_time_sec
        solver.parameters.num_search_workers = 4
        
        status = solver.Solve(model)
        
        if status not in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            return {
                'status': 'INFEASIBLE',
                'message': 'No feasible route and driver schedule found within constraints. (Review 11-hour limit or dealer delivery windows).',
                'solver_status': solver.StatusName(status),
                'load_id': load_id,
                'origin_vdc': origin_code,
                'origin_vdc_name': self.dist_data['locations'][origin_code]['name'],
                'assigned_hauler_name': hauler.get('name')
            }

        # Schedule reconstruction
        curr_node = depot_start
        legs_output = []
        total_distance = 0.0
        total_travel_time = 0
        
        driver_duty_records = {
            l: {'driver': R[l], 'driving_mins': 0, 'service_mins': 0, 'total_duty_mins': 0, 'legs': []} 
            for l in range(num_drivers)
        }

        while curr_node != depot_end:
            next_node = None
            assigned_driver_idx = None
            for j, k in arcs:
                if j == curr_node and solver.Value(y[j, k]) == 1:
                    next_node = k
                    for l in range(num_drivers):
                        if solver.Value(x[j, k, l]) == 1:
                            assigned_driver_idx = l
                            break
                    break
            
            if next_node is None:
                break
                
            leg_dist = d_jk[curr_node][next_node]
            leg_time = tau_jk[curr_node][next_node]
            total_distance += leg_dist
            total_travel_time += leg_time
            
            from_name = self.dist_data['locations'][loc_keys[curr_node]]['name']
            to_name = self.dist_data['locations'][loc_keys[next_node]]['name']
            from_code = loc_keys[curr_node]
            to_code = loc_keys[next_node]
            
            arr_time_mins = int(solver.Value(T[next_node]))
            dep_time_mins = int(solver.Value(D[next_node]))
            service_mins = service_times[next_node]
            handover_occurred = bool(next_node in dc_indices and solver.Value(Handover[next_node]) == 1)
            remaining_load = int(solver.Value(L[next_node]))

            driver_info = R[assigned_driver_idx]
            driver_duty_records[assigned_driver_idx]['driving_mins'] += leg_time
            driver_duty_records[assigned_driver_idx]['service_mins'] += service_mins
            driver_duty_records[assigned_driver_idx]['total_duty_mins'] += (leg_time + service_mins)
            driver_duty_records[assigned_driver_idx]['legs'].append(f"{from_code} -> {to_code}")

            legs_output.append({
                'leg_number': len(legs_output) + 1,
                'from_code': from_code,
                'to_code': to_code,
                'from_name': from_name,
                'to_name': to_name,
                'distance_miles': leg_dist,
                'travel_time_mins': leg_time,
                'travel_time_formatted': f"{leg_time // 60}h {leg_time % 60}m",
                'departure_from_origin': self._format_mins(int(solver.Value(D[curr_node]))),
                'departure_from_origin_mins': int(solver.Value(D[curr_node])),
                'arrival_at_dest': self._format_mins(arr_time_mins),
                'arrival_at_dest_mins': arr_time_mins,
                'service_time_mins': service_mins,
                'departure_from_dest': self._format_mins(dep_time_mins),
                'departure_from_dest_mins': dep_time_mins,
                'driver_id': driver_info['driver_id'],
                'driver_name': driver_info['name'],
                'handover_at_dest': handover_occurred,
                'handover_duration_mins': handover_duration_mins if handover_occurred else 0,
                'remaining_cargo_units': remaining_load
            })
            
            curr_node = next_node

        active_drivers = []
        for l, rec in driver_duty_records.items():
            if rec['total_duty_mins'] > 0:
                rec['total_duty_hours'] = round(rec['total_duty_mins'] / 60.0, 2)
                rec['driving_hours'] = round(rec['driving_mins'] / 60.0, 2)
                rec['within_11hr_limit'] = bool(rec['total_duty_mins'] <= max_driver_duty_mins)
                active_drivers.append(rec)

        overall_trip_duration_mins = int(solver.Value(T[depot_end])) - trip_start_mins
        
        # Financial estimates
        hauler_transport_cost = round(total_distance * 2.10, 2)
        driver_wages_cost = round(sum(d['total_duty_hours'] * float(d['driver']['cost_per_hr']) for d in active_drivers), 2)
        handover_cost = sum(1 for leg in legs_output if leg['handover_at_dest']) * 65.0
        total_trip_cost = round(hauler_transport_cost + driver_wages_cost + handover_cost, 2)

        return {
            'status': 'OPTIMAL' if status == cp_model.OPTIMAL else 'FEASIBLE',
            'solver_status': solver.StatusName(status),
            'solve_time_sec': round(solver.WallTime(), 3),
            'objective_value': solver.ObjectiveValue(),
            'load_id': load_id,
            'load_num': info['load']['load_num'],
            'origin_vdc': origin_code,
            'origin_vdc_name': self.dist_data['locations'][origin_code]['name'],
            'assigned_hauler_id': hauler.get('id'),
            'assigned_hauler_name': hauler.get('name', 'Standard Hauler'),
            'hauler_capacity': hauler_capacity,
            'hauler_max_dealers': info['max_dealers'],
            'total_cargo_units': total_cargo_units,
            'total_cargo_weight_kg': round(sum(float(c['weight_kg']) if pd.notna(c['weight_kg']) else 2000.0 for c in cargo), 1),
            'total_distance_miles': round(total_distance, 1),
            'total_travel_time_mins': total_travel_time,
            'total_travel_time_hours': round(total_travel_time / 60.0, 2),
            'total_trip_duration_mins': overall_trip_duration_mins,
            'total_trip_duration_hours': round(overall_trip_duration_mins / 60.0, 2),
            'cost_breakdown': {
                'hauler_transport_cost': hauler_transport_cost,
                'driver_wages_cost': driver_wages_cost,
                'handover_cost': handover_cost,
                'total_trip_cost': total_trip_cost
            },
            'num_drivers_assigned': len(active_drivers),
            'drivers_assigned': active_drivers,
            'legs': legs_output,
            'handovers_count': sum(1 for leg in legs_output if leg['handover_at_dest']),
            'dealers_served': dealers,
            'cargo_manifest': cargo
        }

    def _format_mins(self, total_minutes):
        """Converts minute offset from midnight to 'HH:MM AM/PM' string."""
        hours = (total_minutes // 60) % 24
        mins = total_minutes % 60
        period = "AM" if hours < 12 else "PM"
        disp_hour = hours if 1 <= hours <= 12 else (hours - 12 if hours > 12 else 12)
        return f"{disp_hour:02d}:{mins:02d} {period}"
