"""
Command-Line Interface (CLI) for Hauler Route & Driver Schedule Optimizer.
Supports C-1 to C-18 formulation, AM/PM shifts, 70-hr rolling cap, post-trip rest time, and multi-trip shift chaining.
"""

import argparse
import sys
import os
import json
import csv
from hauler_cpsat_solver import HaulerCPSATSolver


def parse_time_str(time_str):
    """Parses 'HH:MM' (24-hour) or returns integer minutes directly."""
    if ':' in time_str:
        parts = time_str.split(':')
        return int(parts[0]) * 60 + int(parts[1])
    return int(time_str)


def print_load_list(solver):
    """Prints all available loads from loads_tbl.csv."""
    print("\n" + "=" * 85)
    print(f"{'LOAD ID':<10} {'LOAD NUM':<12} {'ORIGIN':<8} {'VDC TERMINAL':<18} {'STATUS':<10} {'HAULER':<15}")
    print("=" * 85)
    for _, r in solver.df_loads.iterrows():
        lid = int(r['id'])
        lnum = str(r['load_num'])
        orig = str(r['origin_legal_entity']).strip()
        hname = str(r['assigned_hauler_name']) if str(r['assigned_hauler_name']) != 'nan' else 'Auto'
        stat = str(r['load_status'])
        
        info = solver.get_load_info(lid)
        vname = info['vdc_full_name']
        print(f"{lid:<10} {lnum:<12} {orig:<8} {vname:<18} {stat:<10} {hname:<15}")
    print("=" * 85 + "\n")


def print_solution_terminal(res):
    """Prints a formatted schedule in the terminal."""
    if res['status'] in ['INFEASIBLE', 'ERROR']:
        print("\n" + "!" * 80)
        print(f" OPTIMIZATION STATUS: {res['status']} ({res.get('solver_status', 'FAIL')})")
        print(f" REASON: {res.get('message', 'No feasible solution found.')}")
        print("!" * 80 + "\n")
        return

    print("\n" + "=" * 90)
    trip_tag = res.get('trip_tag', 'TRIP')
    print(f" DISPATCH OPTIMIZATION PLAN — LOAD #{res['load_id']} ({res['load_num']}) [{trip_tag}]")
    print("=" * 90)
    print(f" Trip Classification: {res.get('trip_type', 'Standard')} ({res.get('trip_type_desc', '')})")
    print(f" Capacity Coverage  : {res.get('capacity_coverage_status', '100% Covered (All cargo units delivered)')}")
    print(f" Turnaround Rest    : {res.get('rest_time_desc', '45 min turnaround rest buffer at origin factory (C-17)')}")
    print(f" Handover Buffer    : {res.get('handover_desc', 'None (Single Driver Direct)')}")
    print(f" Origin Terminal    : {res['origin_vdc']} ({res['origin_vdc_name']})")
    print(f" Assigned Hauler    : {res['assigned_hauler_name']} (Capacity: {res['hauler_capacity']} cars)")
    print(f" Cargo Onboard      : {res['total_cargo_units']} vehicles ({res.get('total_cargo_weight_lbs', 0):,} lbs)")
    print(f" Solver Engine      : CP-SAT (Solved in {res['solve_time_sec']*1000:.1f} ms)")
    print(f" Total Distance     : {res['total_distance_miles']} miles")
    print(f" Total Driving Time : {res['total_travel_time_hours']} hours ({res['total_travel_time_mins']} mins)")
    print(f" Trip Turnaround    : {res['total_trip_duration_hours']} hours ({res['total_trip_duration_mins']} mins)")
    print(f" Drivers Assigned   : {res['num_drivers_assigned']}")
    print(f" Total Handovers    : {res['handovers_count']}")
    if res.get('cost_breakdown'):
        cb = res['cost_breakdown']
        print(f" Estimated Trip Cost: ${cb['total_trip_cost']:,.2f} (Hauler: ${cb['hauler_transport_cost']:,.2f} | Wages (@$35/hr): ${cb['driver_wages_cost']:,.2f} | Handover: ${cb['handover_cost']:,.2f})")
    
    print("-" * 90)
    print(f" DRIVERS NEEDED RATIONALE ({res['num_drivers_assigned']} DRIVER{'S' if res['num_drivers_assigned'] > 1 else ''}):")
    print(f"  {res.get('drivers_needed_explanation', '')}")

    print("-" * 90)
    print(" DRIVER 11-HOUR & 70-HOUR/8-DAY HOS COMPLIANCE ROSTER:")
    for idx, d in enumerate(res['drivers_assigned']):
        compliance_11h = "COMPLIANT (<=11.0h)" if d['within_11hr_limit'] else "VIOLATION (>11.0h)"
        weekly_rem = d.get('weekly_remaining_hours', 0.0)
        compliance_70h = f"COMPLIANT ({weekly_rem}h left)" if d.get('within_70hr_limit', True) else "VIOLATION (>70h)"
        shift_tag = d['driver'].get('shift_type', 'AM')
        print(f"  * Driver {idx+1}: {d['driver']['name']:<22} (ID: {d['driver']['driver_id']} | Shift: {shift_tag})")
        print(f"    - Daily Duty : {d['total_duty_hours']} hrs / 11.0 hrs max [{compliance_11h}]")
        print(f"    - Weekly HOS : {d.get('weekly_hours_used', 35.0)}h used + {d['total_duty_hours']}h trip = {d.get('weekly_hours_used', 35.0)+d['total_duty_hours']}h / 70.0h [{compliance_70h}]")
        print(f"    - Driving    : {d['driving_hours']} hrs | Service/Unload: {(d['total_duty_hours']-d['driving_hours']):.2f} hrs")
        print(f"    - Segments   : {', '.join(d['legs'])}")

    print("-" * 90)
    print(" STEP-BY-STEP SCHEDULE ITINERARY:")
    header = f"{'LEG':<4} {'FROM':<10} {'TO':<10} {'DIST':<8} {'DRIVE':<7} {'DEP (ORIG)':<11} {'ARR (DEST)':<11} {'UNLOAD':<8} {'DEP (DEST)':<11} {'DRIVER':<16} {'HANDOVER'}"
    print(header)
    print("-" * len(header))
    
    for leg in res['legs']:
        handover_str = f"YES ({leg['handover_duration_mins']}m)" if leg['handover_at_dest'] else "NO"
        print(f"{leg['leg_number']:<4} {leg['from_code']:<10} {leg['to_code']:<10} {leg['distance_miles']:<6.1f}mi {leg['travel_time_mins']:<5}m {leg['departure_from_origin']:<11} {leg['arrival_at_dest']:<11} {leg['service_time_mins']:<6}m {leg['departure_from_dest']:<11} {leg['driver_name']:<16} {handover_str}")

    print("=" * 90 + "\n")


def print_multitrip_terminal(res):
    """Prints a multi-trip shift tour summary in the terminal."""
    print("\n" + "=" * 90)
    print(f" MULTI-TRIP SINGLE-DRIVER SHIFT TOUR — {res['driver_name']} ({res['driver_id']})")
    print("=" * 90)
    print(f" Shift Schedule     : {res['shift_type']} Shift ({res['shift_start']} to {res['shift_end']})")
    print(f" Total Trips Run    : {res['total_trips_completed']} complete round-trips")
    print(f" Total Shift Duty   : {res['total_shift_duty_hours']} hours (Limit: 11.0 hours) [{'COMPLIANT' if res['daily_11h_compliant'] else 'VIOLATION'}]")
    print(f" Total Shift Span   : {res['total_shift_span_hours']} hours (Shift Window: 12.0 hours) [{'COMPLIANT' if res['shift_12h_span_compliant'] else 'VIOLATION'}]")
    print(f" Total Distance     : {res['total_distance_miles']} miles")
    print(f" Turnaround Rest    : {res['post_trip_rest_mins']} minutes standard rest at factory between trips")
    print(f" Weekly HOS Status  : 70.0h Cap [{'COMPLIANT (' + str(res['weekly_remaining_hours']) + 'h remaining)' if res['weekly_70h_compliant'] else 'VIOLATION'}]")
    print(f" Overall Feasibility: {'FEASIBLE & COMPLIANT' if res['overall_shift_feasible'] else 'INFEASIBLE'}")
    print("-" * 90)
    print(" SEQUENTIAL TRIP BREAKDOWN:")
    for trip in res['trips']:
        print(f"  * Trip {trip['trip_sequence']} (Load #{trip['load_id']} - {trip['load_num']}):")
        print(f"    - Schedule : Depart {trip['start_time']} -> Return {trip['finish_time']} (Duration: {trip['trip_duration_hours']}h | Duty: {trip['trip_duty_hours']}h)")
        print(f"    - Mileage  : {trip['distance_miles']} miles")
        if trip['trip_sequence'] < res['total_trips_completed']:
            print(f"    - Buffer   : {res['post_trip_rest_mins']} min mandatory post-trip turnaround rest at factory depot")
    print("=" * 90 + "\n")


def export_schedule_csv(res, filename):
    """Exports schedule to a CSV file."""
    if res['status'] in ['INFEASIBLE', 'ERROR']:
        print(f"Cannot export: solution is {res['status']}")
        return
    
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Leg', 'From_Code', 'From_Name', 'To_Code', 'To_Name', 'Distance_Miles', 
                         'Drive_Mins', 'Dep_Origin', 'Arr_Dest', 'Service_Mins', 'Dep_Dest', 
                         'Driver_Name', 'Driver_ID', 'Handover_Occurred', 'Cargo_Remaining'])
        for leg in res['legs']:
            writer.writerow([
                leg['leg_number'], leg['from_code'], leg['from_name'], leg['to_code'], leg['to_name'],
                leg['distance_miles'], leg['travel_time_mins'], leg['departure_from_origin'],
                leg['arrival_at_dest'], leg['service_time_mins'], leg['departure_from_dest'],
                leg['driver_name'], leg['driver_id'], 'YES' if leg['handover_at_dest'] else 'NO',
                leg['remaining_cargo_units']
            ])
    print(f"Successfully exported schedule to: {filename}")


def main():
    parser = argparse.ArgumentParser(
        description="AutoHauler Route & Driver Schedule Optimizer (CP-SAT CLI)",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Examples:
  1. Solve default load #244606 (LA Long Beach):
     python cli_run.py --load 244606

  2. Solve with PM shift preference (18:00 start):
     python cli_run.py --load 244861 --shift PM --start 18:00

  3. Simulate multi-trip shift chaining (3 short trips by Driver 7 with 45m turnaround rest):
     python cli_run.py --multitrip DRV_07 --loads 244861 188377 188384

  4. List all available loads in inventory:
     python cli_run.py --list

  5. Batch solve all loads:
     python cli_run.py --batch
        """
    )
    
    parser.add_argument('--load', '-l', type=int, help="Load ID to solve (e.g. 244606, 244861, 245516, 245356)")
    parser.add_argument('--start', '-s', type=str, default="06:00", help="Trip start time at factory, format HH:MM (default: 06:00)")
    parser.add_argument('--shift', type=str, choices=['AM', 'PM'], default="AM", help="Driver shift preference: AM (06:00-18:00) or PM (18:00-06:00)")
    parser.add_argument('--max_duty', '-d', type=float, default=11.0, help="Max driver daily duty hours (default: 11.0)")
    parser.add_argument('--buffer', '-b', type=int, default=45, help="Handover buffer duration in minutes (default: 45)")
    parser.add_argument('--rest', '-r', type=int, default=45, help="Standard post-trip turnaround rest in minutes (default: 45)")
    parser.add_argument('--hauler_id', '-H', type=int, default=None, help="Override assigned hauler ID")
    parser.add_argument('--list', action='store_true', help="List all 28 loads in inventory")
    parser.add_argument('--batch', action='store_true', help="Batch solve all loads in inventory")
    parser.add_argument('--multitrip', type=str, help="Driver ID for multi-trip shift tour simulation (e.g. DRV_07)")
    parser.add_argument('--loads', nargs='+', type=int, help="List of load IDs for multi-trip shift tour simulation")
    parser.add_argument('--export', '-e', type=str, help="Export itinerary to CSV file path")
    parser.add_argument('--json', action='store_true', help="Output raw JSON response")

    args = parser.parse_args()
    solver = HaulerCPSATSolver()

    if args.list:
        print_load_list(solver)
        return

    if args.multitrip:
        driver_id = args.multitrip
        load_ids = args.loads or [244861, 188377, 188384]
        res = solver.solve_multitrip_driver_shift(
            driver_id=driver_id,
            load_ids=load_ids,
            shift_start_mins=parse_time_str(args.start),
            post_trip_rest_mins=args.rest
        )
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print_multitrip_terminal(res)
        return

    if args.batch:
        print("\n" + "=" * 85)
        print(" BATCH RUNNING OPTIMIZATION ACROSS ALL 28 LOADS (C-1 TO C-18 ENGINE)")
        print("=" * 85)
        success_count = 0
        total_count = len(solver.df_loads)
        
        for idx, row in solver.df_loads.iterrows():
            lid = int(row['id'])
            res = solver.solve_load_schedule(
                lid, 
                trip_start_mins=parse_time_str(args.start), 
                max_driver_duty_mins=int(round(args.max_duty * 60)),
                shift_type=args.shift,
                post_trip_rest_mins=args.rest
            )
            stat = res['status']
            if stat in ['OPTIMAL', 'FEASIBLE']:
                success_count += 1
                handover_str = f"{res['handovers_count']} handover(s)" if res['handovers_count'] > 0 else "single driver"
                print(f" [OK] Load #{lid:<7} ({res['origin_vdc']}): {stat} | {res['total_distance_miles']:>5.1f} mi | {res['total_trip_duration_hours']:>4.1f}h | {res['num_drivers_assigned']} driver(s) ({handover_str})")
            else:
                print(f" [FAIL] Load #{lid:<7}: {stat} — {res.get('message')}")
                
        print("=" * 85)
        print(f" Batch Complete: {success_count}/{total_count} loads successfully solved.\n")
        return

    # If no load specified, prompt user or use default 244606
    load_id = args.load
    if load_id is None:
        print_load_list(solver)
        try:
            val = input("Enter Load ID to optimize (or press Enter for default 244606): ").strip()
            load_id = int(val) if val else 244606
        except (ValueError, KeyboardInterrupt):
            print("\nExiting.")
            return

    start_mins = parse_time_str(args.start)
    duty_mins = int(round(args.max_duty * 60))

    res = solver.solve_load_schedule(
        load_id=load_id,
        trip_start_mins=start_mins,
        max_driver_duty_mins=duty_mins,
        handover_duration_mins=args.buffer,
        override_hauler_id=args.hauler_id,
        shift_type=args.shift,
        post_trip_rest_mins=args.rest
    )

    if args.json:
        print(json.dumps(res, indent=2))
    else:
        print_solution_terminal(res)

    if args.export:
        export_schedule_csv(res, args.export)


if __name__ == '__main__':
    main()
