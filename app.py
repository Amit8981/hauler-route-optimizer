"""
Local Web Application for Load-Level Hauler Route & Driver Schedule Optimization.
Flask Backend serving API and UI.
"""

import json
import os
import io
import csv
import pandas as pd
from flask import Flask, render_template, request, jsonify, Response, send_file
from hauler_cpsat_solver import HaulerCPSATSolver, VDC_CODE_TO_NAME

app = Flask(__name__)
solver = HaulerCPSATSolver()

# Cache latest solutions in memory
solutions_cache = {}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/sandbox')
def sandbox():
    """Renders the Constraint Sandbox & What-If Scenario Tester page."""
    return render_template('sandbox.html')


@app.route('/api/solve_custom', methods=['POST'])
def solve_custom():
    """Solves user-defined custom scenario with CP-SAT."""
    data = request.json or {}
    try:
        res = solver.solve_custom_scenario(data)
        return jsonify(res)
    except Exception as e:
        return jsonify({'status': 'ERROR', 'message': str(e)}), 400


@app.route('/api/loads', methods=['GET'])
def get_loads():
    """Returns list of all loads with high-level details."""
    origin_filter = request.args.get('origin')
    status_filter = request.args.get('status')
    
    df = solver.df_loads.copy()
    
    if origin_filter and origin_filter != 'ALL':
        df = df[df['origin_legal_entity'].astype(str).str.upper() == origin_filter.upper()]
    if status_filter and status_filter != 'ALL':
        df = df[df['load_status'].astype(str).str.lower() == status_filter.lower()]
    
    loads_list = []
    for _, row in df.iterrows():
        lid = int(row['id'])
        origin_code = str(row['origin_legal_entity']).strip()
        vdc_name = VDC_CODE_TO_NAME.get(origin_code, origin_code)
        
        # Cargo items count
        cargo_items = solver.df_load_details[solver.df_load_details['load_id'] == lid]
        cargo_count = len(cargo_items)
        dealers = list(cargo_items['destination_dealer_id'].unique())
        
        # Assigned hauler name
        hauler_name = row['assigned_hauler_name']
        if not hauler_name or pd.isna(hauler_name):
            hauler_name = "Auto-assigned by VDC"
            
        loads_list.append({
            'id': lid,
            'load_num': str(row['load_num']),
            'origin_legal_entity': origin_code,
            'origin_vdc_name': vdc_name,
            'load_status': str(row['load_status']),
            'cargo_count': cargo_count,
            'dealers_count': len(dealers),
            'assigned_hauler_name': hauler_name,
            'assigned_hauler_id': int(row['assigned_hauler_id']) if pd.notna(row['assigned_hauler_id']) else None,
            'assigned_driver': str(row['driver']) if pd.notna(row['driver']) else None,
            'tmw_movement_id': str(row['tmw_movement_id']) if pd.notna(row['tmw_movement_id']) else None
        })
    
    return jsonify({'loads': loads_list, 'total_count': len(loads_list)})


@app.route('/api/load/<int:load_id>', methods=['GET'])
def get_load_detail(load_id):
    """Returns complete details for a single load."""
    try:
        info = solver.get_load_info(load_id)
        
        # Format cargo items
        cargo_list = []
        for c in info['cargo_items']:
            cargo_list.append({
                'vin': c['vin'],
                'model_name': c['model_name'],
                'brand': c['brand'],
                'series': c['series'],
                'weight_kg': c['weight_kg'],
                'length_m': c['length_m'],
                'width_m': c['width_m'],
                'height_m': c['height_m'],
                'destination_dealer_id': c['destination_dealer_id']
            })
            
        # Available haulers suitable for this load
        cargo_count = len(cargo_list)
        vdc_name = info['vdc_full_name']
        matching_haulers = solver.df_haulers[
            solver.df_haulers['trailer_vdc_location'].astype(str).str.contains(vdc_name, case=False, na=False)
        ].to_dict(orient='records')
        
        if not matching_haulers:
            matching_haulers = solver.df_haulers.head(10).to_dict(orient='records')

        clean_haulers = []
        for h in matching_haulers:
            clean_haulers.append({
                'id': int(h['id']),
                'name': str(h['name']),
                'capacity': int(h['capacity']) if pd.notna(h['capacity']) else 9,
                'gross_weight': float(h['gross_weight']) if pd.notna(h['gross_weight']) else 36000.0,
                'max_dealers': int(h['max_dealers']) if pd.notna(h['max_dealers']) else 2,
                'is_compatible': bool(pd.notna(h['capacity']) and int(h['capacity']) >= cargo_count)
            })

        return jsonify({
            'success': True,
            'load_id': load_id,
            'load_num': info['load']['load_num'],
            'origin_code': info['origin_code'],
            'origin_name': info['vdc_full_name'],
            'load_status': info['load']['load_status'],
            'hauler': {
                'id': int(info['hauler']['id']) if pd.notna(info['hauler'].get('id')) else None,
                'name': info['hauler'].get('name', 'Standard Hauler'),
                'capacity': int(info['hauler']['capacity']) if pd.notna(info['hauler'].get('capacity')) else 9,
                'gross_weight': float(info['hauler']['gross_weight']) if pd.notna(info['hauler'].get('gross_weight')) else 36000.0,
                'max_dealers': info['max_dealers']
            },
            'candidate_haulers': clean_haulers,
            'dealers': info['dealers'],
            'cargo_items': cargo_list,
            'total_cargo_units': len(cargo_list),
            'total_weight_kg': sum(float(c['weight_kg']) if pd.notna(c['weight_kg']) else 2000.0 for c in cargo_list),
            'cached_solution': solutions_cache.get(load_id)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 404


@app.route('/api/solve', methods=['POST'])
def solve_schedule():
    """Optimizes the schedule for a given load using CP-SAT."""
    data = request.json or {}
    load_id = data.get('load_id')
    if not load_id:
        return jsonify({'success': False, 'error': 'load_id is required'}), 400
    
    # Parse parameters
    trip_start_str = data.get('trip_start_time', '07:00')
    try:
        parts = trip_start_str.split(':')
        start_mins = int(parts[0]) * 60 + int(parts[1])
    except Exception:
        start_mins = 420  # default 07:00 AM
        
    duty_limit_hours = float(data.get('max_driver_duty_hours', 11.0))
    duty_limit_mins = int(round(duty_limit_hours * 60))
    
    handover_mins = int(data.get('handover_duration_mins', 45))
    enforce_11h = bool(data.get('enforce_11hr_rule', True))
    
    override_hauler_id = data.get('override_hauler_id')
    if override_hauler_id is not None and override_hauler_id != '':
        override_hauler_id = int(override_hauler_id)
    else:
        override_hauler_id = None
        
    shift_type = data.get('shift_type', 'AM')
    post_trip_rest_mins = int(data.get('post_trip_rest_mins', 45))
        
    res = solver.solve_load_schedule(
        load_id=int(load_id),
        trip_start_mins=start_mins,
        max_driver_duty_mins=duty_limit_mins,
        handover_duration_mins=handover_mins,
        enforce_11hr_rule=enforce_11h,
        override_hauler_id=override_hauler_id,
        shift_type=shift_type,
        post_trip_rest_mins=post_trip_rest_mins
    )
    
    # Cache result
    if res['status'] in ['OPTIMAL', 'FEASIBLE']:
        solutions_cache[int(load_id)] = res
        
    return jsonify(res)


@app.route('/api/multitrip', methods=['POST'])
def solve_multitrip():
    """Solves multi-trip shift chaining for a single driver performing short trips."""
    data = request.json or {}
    driver_id = data.get('driver_id', 'DRV_07')
    load_ids = data.get('load_ids', [244861, 188377, 188384])
    start_str = data.get('start_time', '06:00')
    try:
        parts = start_str.split(':')
        start_mins = int(parts[0]) * 60 + int(parts[1])
    except Exception:
        start_mins = 360
    rest_mins = int(data.get('post_trip_rest_mins', 45))
    
    res = solver.solve_multitrip_driver_shift(
        driver_id=driver_id,
        load_ids=load_ids,
        shift_start_mins=start_mins,
        post_trip_rest_mins=rest_mins
    )
    return jsonify(res)


@app.route('/api/dealers', methods=['GET'])
def get_dealers():
    return jsonify({'dealers': solver.df_dealers.to_dict(orient='records')})


@app.route('/api/drivers', methods=['GET'])
def get_drivers():
    return jsonify({'drivers': solver.df_drivers.to_dict(orient='records')})


@app.route('/api/manager_roster', methods=['GET'])
def get_manager_roster():
    """Returns the complete fleet driver roster from a Manager's Operational POV."""
    roster = solver.get_manager_fleet_roster()
    return jsonify(roster)



@app.route('/api/haulers', methods=['GET'])
def get_haulers():
    return jsonify({'haulers': solver.df_haulers.to_dict(orient='records')})


@app.route('/api/export/csv/<int:load_id>')
def export_csv(load_id):
    """Exports the optimized schedule as a CSV file."""
    res = solutions_cache.get(load_id)
    if not res or 'legs' not in res:
        # Solve on the fly
        res = solver.solve_load_schedule(load_id)
        if res['status'] not in ['OPTIMAL', 'FEASIBLE']:
            return "No valid schedule to export", 400

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Leg #', 'From Code', 'From Name', 'To Code', 'To Name', 'Distance (Miles)', 
                     'Driving Time (Mins)', 'Departure (Origin)', 'Arrival (Dest)', 'Service (Mins)', 
                     'Departure (Dest)', 'Assigned Driver', 'Handover Occurred', 'Remaining Cargo Units'])
    
    for leg in res['legs']:
        writer.writerow([
            leg['leg_number'],
            leg['from_code'],
            leg['from_name'],
            leg['to_code'],
            leg['to_name'],
            leg['distance_miles'],
            leg['travel_time_mins'],
            leg['departure_from_origin'],
            leg['arrival_at_dest'],
            leg['service_time_mins'],
            leg['departure_from_dest'],
            leg['driver_name'],
            'YES' if leg['handover_at_dest'] else 'NO',
            leg['remaining_cargo_units']
        ])
        
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename=schedule_load_{load_id}.csv"}
    )


@app.route('/api/export/json/<int:load_id>')
def export_json(load_id):
    """Exports the optimized schedule as JSON."""
    res = solutions_cache.get(load_id)
    if not res:
        res = solver.solve_load_schedule(load_id)
    return jsonify(res)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5050))
    print(f"Starting Hauler Route & Schedule Optimizer UI on http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
