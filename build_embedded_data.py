"""
Helper to export all 28 loads with updated C-1 to C-18 CP-SAT solutions and metadata into a JSON object.
"""

import json
from hauler_cpsat_solver import HaulerCPSATSolver

solver = HaulerCPSATSolver()
loads = solver.df_loads['id'].tolist()

data_bundle = {
    'loads': [],
    'load_details': {},
    'solutions': {},
    'multitrip_shifts': {},
    'dealers': solver.df_dealers.to_dict(orient='records'),
    'drivers': solver.df_drivers.to_dict(orient='records'),
    'haulers': solver.df_haulers.to_dict(orient='records'),
    'locations': solver.dist_data.get('locations', {}),
    'distances_miles': solver.dist_data.get('distances_miles', {}),
    'travel_time_minutes': solver.dist_data.get('travel_time_minutes', {})
}

for idx, row in solver.df_loads.iterrows():
    lid = int(row['id'])
    info = solver.get_load_info(lid)
    
    cargo = info['cargo_items']
    dealers = list(set(c['destination_dealer_id'] for c in cargo))
    
    # Solve with updated CP-SAT engine
    sol = solver.solve_load_schedule(lid, trip_start_mins=360, shift_type='AM')
    data_bundle['solutions'][str(lid)] = sol

    data_bundle['loads'].append({
        'id': lid,
        'load_num': str(row['load_num']),
        'origin_legal_entity': info['origin_code'],
        'origin_vdc_name': info['vdc_full_name'],
        'load_status': str(row['load_status']),
        'trip_type': sol.get('trip_type', 'Short Trip'),
        'trip_tag': sol.get('trip_tag', 'SHORT TRIP'),
        'trip_type_desc': sol.get('trip_type_desc', ''),
        'capacity_coverage_pct': 100.0,
        'turnaround_duration_hours': sol.get('total_trip_duration_hours', 0.0),
        'drivers_required': sol.get('num_drivers_assigned', 1),
        'rest_time_mins': sol.get('rest_time_mins', 45),
        'handover_time_mins': sol.get('handover_time_mins', 0),
        'handover_desc': sol.get('handover_desc', 'None'),
        'cargo_count': len(cargo),
        'dealers_count': len(dealers),
        'assigned_hauler_name': info['hauler'].get('name', 'Standard Hauler'),
        'assigned_hauler_id': int(info['hauler']['id']) if info['hauler'].get('id') else None,
        'driver': str(row['driver']) if str(row['driver']) != 'nan' else None
    })
    
    data_bundle['load_details'][str(lid)] = {
        'info': {
            'origin_code': info['origin_code'],
            'origin_name': info['vdc_full_name'],
            'load_num': str(row['load_num']),
            'load_status': str(row['load_status']),
            'trip_type': sol.get('trip_type', 'Short Trip'),
            'trip_tag': sol.get('trip_tag', 'SHORT TRIP'),
            'capacity_coverage_pct': 100.0,
            'rest_time_mins': sol.get('rest_time_mins', 45),
            'handover_time_mins': sol.get('handover_time_mins', 0),
            'handover_desc': sol.get('handover_desc', 'None'),
            'hauler': {
                'id': int(info['hauler']['id']) if info['hauler'].get('id') else None,
                'name': info['hauler'].get('name', 'Standard Hauler'),
                'capacity': int(info['hauler'].get('capacity', 9)),
                'gross_weight': float(info['hauler'].get('gross_weight', 80000.0)),
                'max_dealers': info['max_dealers']
            },
            'dealers': info['dealers'],
            'cargo_items': cargo,
            'total_cargo_units': len(cargo),
            'total_weight_lbs': sum(int(round(float(c.get('weight_lb', float(c.get('weight_kg', 2000.0)) * 2.20462)))) for c in cargo),
            'total_weight_kg': sum(float(c['weight_kg']) if c.get('weight_kg') and str(c['weight_kg']) != 'nan' else 2000.0 for c in cargo)
        }
    }

# Pre-solve multi-trip shift tour (Driver 7 SoCal performing short Mira Loma trips in AM shift)
multi_trip_res = solver.solve_multitrip_driver_shift("DRV_07", [244861, 188384], shift_start_mins=360, post_trip_rest_mins=45)
data_bundle['multitrip_shifts']['DRV_07'] = multi_trip_res

# Export complete Manager Fleet Roster with location tracking and multi-trip shift validations
print("Generating complete Manager Fleet Roster with multi-trip validations...")
data_bundle['manager_roster'] = solver.get_manager_fleet_roster()

with open('data/embedded_data.json', 'w') as f:
    json.dump(data_bundle, f)

print("Exported updated embedded_data.json successfully! Total loads solved:", len(data_bundle['solutions']))

