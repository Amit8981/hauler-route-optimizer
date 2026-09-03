"""
Helper to export all 28 loads with full CP-SAT solutions and metadata into a JSON object.
Does NOT modify any existing python files.
"""

import json
from hauler_cpsat_solver import HaulerCPSATSolver

solver = HaulerCPSATSolver()
loads = solver.df_loads['id'].tolist()

data_bundle = {
    'loads': [],
    'load_details': {},
    'solutions': {},
    'dealers': solver.df_dealers.to_dict(orient='records'),
    'drivers': solver.df_drivers.to_dict(orient='records'),
    'haulers': solver.df_haulers.to_dict(orient='records')
}

for idx, row in solver.df_loads.iterrows():
    lid = int(row['id'])
    info = solver.get_load_info(lid)
    
    cargo = info['cargo_items']
    dealers = list(set(c['destination_dealer_id'] for c in cargo))
    
    data_bundle['loads'].append({
        'id': lid,
        'load_num': str(row['load_num']),
        'origin_legal_entity': info['origin_code'],
        'origin_vdc_name': info['vdc_full_name'],
        'load_status': str(row['load_status']),
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
            'hauler': {
                'id': int(info['hauler']['id']) if info['hauler'].get('id') else None,
                'name': info['hauler'].get('name', 'Standard Hauler'),
                'capacity': int(info['hauler'].get('capacity', 9)),
                'gross_weight': float(info['hauler'].get('gross_weight', 36000.0)),
                'max_dealers': info['max_dealers']
            },
            'dealers': info['dealers'],
            'cargo_items': cargo,
            'total_cargo_units': len(cargo),
            'total_weight_kg': sum(float(c['weight_kg']) if c['weight_kg'] and str(c['weight_kg']) != 'nan' else 2000.0 for c in cargo)
        }
    }
    
    # Solve with CP-SAT
    sol = solver.solve_load_schedule(lid, trip_start_mins=420)
    data_bundle['solutions'][str(lid)] = sol

with open('data/embedded_data.json', 'w') as f:
    json.dump(data_bundle, f)

print("Exported embedded_data.json successfully! Total loads solved:", len(data_bundle['solutions']))
