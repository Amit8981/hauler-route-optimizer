from hauler_cpsat_solver import HaulerCPSATSolver

solver = HaulerCPSATSolver()
test_loads = [244861, 245516, 245356, 245060, 228409]

print("="*70)
print("TESTING ACROSS MULTIPLE LOAD IDs AND VDCs")
print("="*70)

for lid in test_loads:
    try:
        res = solver.solve_load_schedule(lid, trip_start_mins=420)
        print(f"\n[LOAD {lid} - {res['origin_vdc']} ({res['origin_vdc_name']})]")
        print(f"Status: {res['status']} | Hauler: {res['assigned_hauler_name']} | Distance: {res['total_distance_miles']} mi | Travel Time: {res['total_travel_time_hours']} h")
        print(f"Drivers: {res['num_drivers_assigned']} | Handovers: {res['handovers_count']}")
        for d in res['drivers_assigned']:
            print(f"  * {d['driver']['name']}: Duty {d['total_duty_hours']} h (<=11h: {d['within_11hr_limit']})")
        for leg in res['legs']:
            handover_str = f" [HANDOVER -> {leg['driver_name']}]" if leg['handover_at_dest'] else ""
            print(f"  Leg {leg['leg_number']}: {leg['from_code']} -> {leg['to_code']} | Driver: {leg['driver_name']} | Arr: {leg['arrival_at_dest']} | Dep: {leg['departure_from_dest']}{handover_str}")
    except Exception as e:
        print(f"Error on load {lid}: {e}")

print("\nAll solver tests completed.")
