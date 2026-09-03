"""
Command-Line Interface (CLI) for Hauler Route & Driver Schedule Optimizer.
Allows running the optimizer directly from VS Code terminal / cmd with a variety of inputs.
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
    print("\n" + "=" * 80)
    print(f"{'LOAD ID':<10} {'LOAD NUM':<12} {'ORIGIN':<8} {'VDC TERMINAL':<18} {'STATUS':<10} {'HAULER':<15}")
    print("=" * 80)
    for _, r in solver.df_loads.iterrows():
        lid = int(r['id'])
        lnum = str(r['load_num'])
        orig = str(r['origin_legal_entity']).strip()
        hname = str(r['assigned_hauler_name']) if str(r['assigned_hauler_name']) != 'nan' else 'Auto'
        stat = str(r['load_status'])
        
        info = solver.get_load_info(lid)
        vname = info['vdc_full_name']
        print(f"{lid:<10} {lnum:<12} {orig:<8} {vname:<18} {stat:<10} {hname:<15}")
    print("=" * 80 + "\n")


def print_solution_terminal(res):
    """Prints a beautiful, formatted schedule in the terminal."""
    if res['status'] in ['INFEASIBLE', 'ERROR']:
        print("\n" + "!" * 75)
        print(f" OPTIMIZATION STATUS: {res['status']} ({res.get('solver_status', 'FAIL')})")
        print(f" REASON: {res.get('message', 'No feasible solution found.')}")
        print("!" * 75 + "\n")
        return

    print("\n" + "=" * 85)
    print(f" DISPATCH OPTIMIZATION PLAN — LOAD #{res['load_id']} ({res['load_num']})")
    print("=" * 85)
    print(f" Origin Terminal    : {res['origin_vdc']} ({res['origin_vdc_name']})")
    print(f" Assigned Hauler    : {res['assigned_hauler_name']} (Capacity: {res['hauler_capacity']} cars)")
    print(f" Cargo Onboard      : {res['total_cargo_units']} vehicles ({res['total_cargo_weight_kg']:,.1f} kg)")
    print(f" Solver Status      : {res['status']} (Solved in {res['solve_time_sec']*1000:.1f} ms)")
    print(f" Total Distance     : {res['total_distance_miles']} miles")
    print(f" Total Driving Time : {res['total_travel_time_hours']} hours ({res['total_travel_time_mins']} mins)")
    print(f" Trip Turnaround    : {res['total_trip_duration_hours']} hours ({res['total_trip_duration_mins']} mins)")
    print(f" Drivers Assigned   : {res['num_drivers_assigned']}")
    print(f" Total Handovers    : {res['handovers_count']}")
    if res.get('cost_breakdown'):
        cb = res['cost_breakdown']
        print(f" Estimated Trip Cost: ${cb['total_trip_cost']:,.2f} (Hauler: ${cb['hauler_transport_cost']:,.2f} | Wages: ${cb['driver_wages_cost']:,.2f} | Handover: ${cb['handover_cost']:,.2f})")
    
    print("-" * 85)
    print(" DRIVER 11-HOUR COMPLIANCE ROSTER:")
    for idx, d in enumerate(res['drivers_assigned']):
        compliance_str = "COMPLIANT (<=11.0h)" if d['within_11hr_limit'] else "VIOLATION (>11.0h)"
        print(f"  * Driver {idx+1}: {d['driver']['name']:<22} (ID: {d['driver']['driver_id']})")
        print(f"    - Total Duty : {d['total_duty_hours']} hrs / 11.0 hrs limit [{compliance_str}]")
        print(f"    - Driving    : {d['driving_hours']} hrs | Unloading/Buffer: {(d['total_duty_hours']-d['driving_hours']):.2f} hrs")
        print(f"    - Segments   : {', '.join(d['legs'])}")

    print("-" * 85)
    print(" STEP-BY-STEP SCHEDULE ITINERARY:")
    header = f"{'LEG':<4} {'FROM':<10} {'TO':<10} {'DIST':<8} {'DRIVE':<7} {'DEP (ORIG)':<11} {'ARR (DEST)':<11} {'UNLOAD':<8} {'DEP (DEST)':<11} {'DRIVER':<16} {'HANDOVER'}"
    print(header)
    print("-" * len(header))
    
    for leg in res['legs']:
        handover_str = f"YES ({leg['handover_duration_mins']}m)" if leg['handover_at_dest'] else "NO"
        print(f"{leg['leg_number']:<4} {leg['from_code']:<10} {leg['to_code']:<10} {leg['distance_miles']:<6.1f}mi {leg['travel_time_mins']:<5}m {leg['departure_from_origin']:<11} {leg['arrival_at_dest']:<11} {leg['service_time_mins']:<6}m {leg['departure_from_dest']:<11} {leg['driver_name']:<16} {handover_str}")

    print("=" * 85 + "\n")


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

  2. Solve with custom start time (06:30 AM) and 10.5 hour duty limit:
     python cli_run.py --load 244606 --start 06:30 --max_duty 10.5

  3. Solve and export schedule to CSV:
     python cli_run.py --load 244861 --export output_schedule.csv

  4. Run short-haul Mira Loma load:
     python cli_run.py --load 244861

  5. List all available loads in inventory:
     python cli_run.py --list

  6. Batch solve all loads:
     python cli_run.py --batch
        """
    )
    
    parser.add_argument('--load', '-l', type=int, help="Load ID to solve (e.g. 244606, 244861, 245516, 245356)")
    parser.add_argument('--start', '-s', type=str, default="07:00", help="Trip start time at factory, format HH:MM (default: 07:00)")
    parser.add_argument('--max_duty', '-d', type=float, default=11.0, help="Max driver duty hours before mandatory handover (default: 11.0)")
    parser.add_argument('--buffer', '-b', type=int, default=45, help="Handover buffer duration in minutes (default: 45)")
    parser.add_argument('--hauler_id', '-H', type=int, default=None, help="Override assigned hauler ID (e.g. 64 for 10-car hauler)")
    parser.add_argument('--list', action='store_true', help="List all 28 loads in inventory")
    parser.add_argument('--batch', action='store_true', help="Batch solve all loads in inventory")
    parser.add_argument('--export', '-e', type=str, help="Export itinerary to CSV file path")
    parser.add_argument('--json', action='store_true', help="Output raw JSON response")

    args = parser.parse_args()
    solver = HaulerCPSATSolver()

    if args.list:
        print_load_list(solver)
        return

    if args.batch:
        print("\n" + "=" * 80)
        print(" BATCH RUNNING OPTIMIZATION ACROSS ALL 28 LOADS")
        print("=" * 80)
        success_count = 0
        total_count = len(solver.df_loads)
        
        for idx, row in solver.df_loads.iterrows():
            lid = int(row['id'])
            res = solver.solve_load_schedule(lid, trip_start_mins=parse_time_str(args.start), max_driver_duty_mins=int(round(args.max_duty * 60)))
            stat = res['status']
            if stat in ['OPTIMAL', 'FEASIBLE']:
                success_count += 1
                handover_str = f"{res['handovers_count']} handover(s)" if res['handovers_count'] > 0 else "single driver"
                print(f" [OK] Load #{lid:<7} ({res['origin_vdc']}): {stat} | {res['total_distance_miles']:>5.1f} mi | {res['total_trip_duration_hours']:>4.1f}h | {res['num_drivers_assigned']} driver(s) ({handover_str})")
            else:
                print(f" [FAIL] Load #{lid:<7}: {stat} — {res.get('message')}")
                
        print("=" * 80)
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
        override_hauler_id=args.hauler_id
    )

    if args.json:
        print(json.dumps(res, indent=2))
    else:
        print_solution_terminal(res)

    if args.export:
        export_schedule_csv(res, args.export)


if __name__ == '__main__':
    main()
