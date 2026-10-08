"""
Comprehensive Unit Tests for Updated Operations Research Formulation (C-1 to C-18)
and Multi-Trip Shift Operations.
"""

import unittest
from hauler_cpsat_solver import HaulerCPSATSolver


class TestNewFormulation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.solver = HaulerCPSATSolver()

    def test_short_trip_single_driver(self):
        """Test short trip (Load 244861 Mira Loma) assigns exactly 1 driver and 0 handovers."""
        res = self.solver.solve_load_schedule(244861, trip_start_mins=360, shift_type='AM')
        self.assertEqual(res['status'], 'OPTIMAL')
        self.assertEqual(res['num_drivers_assigned'], 1)
        self.assertEqual(res['handovers_count'], 0)
        self.assertLessEqual(res['total_trip_duration_hours'], 11.0)
        self.assertIn("1 Driver is legally sufficient", res['drivers_needed_explanation'])

    def test_long_trip_two_drivers_handover(self):
        """Test long-haul trip (Load 244606 Long Beach to Fresno) legally mandates 2 drivers under C-13."""
        res = self.solver.solve_load_schedule(244606, trip_start_mins=360, shift_type='AM')
        self.assertEqual(res['status'], 'OPTIMAL')
        self.assertEqual(res['num_drivers_assigned'], 2)
        self.assertEqual(res['handovers_count'], 1)
        self.assertGreater(res['total_trip_duration_hours'], 11.0)
        self.assertIn("2 Drivers are legally mandated", res['drivers_needed_explanation'])
        # Verify both drivers remain <= 11.0h
        for driver in res['drivers_assigned']:
            self.assertTrue(driver['within_11hr_limit'])
            self.assertLessEqual(driver['total_duty_hours'], 14.0)

    def test_flat_driver_cost_calculation(self):
        """Test that driver wages track both per-vehicle delivered piece-rate and flat comparison."""
        res = self.solver.solve_load_schedule(244861)
        total_duty_hours = sum(d['total_duty_hours'] for d in res['drivers_assigned'])
        expected_hourly = round(total_duty_hours * 35.0, 2)
        self.assertEqual(res['cost_breakdown']['driver_flat_hourly_comparison'], expected_hourly)
        
        # Test per-vehicle piece-rate compensation
        expected_piece_rate = sum(d['total_wages'] for d in res['drivers_assigned'])
        self.assertEqual(res['cost_breakdown']['driver_wages_cost'], expected_piece_rate)
        self.assertIn('Per-Vehicle Delivered', res['cost_breakdown']['wage_model'])

    def test_service_rules_variety(self):
        """Test that solver assigns drivers with varied regulatory service rules."""
        res = self.solver.solve_load_schedule(244606)
        rules = [d.get('service_rule') for d in res['drivers_assigned']]
        self.assertTrue(any('FMCSA' in r or 'Intrastate' in r or 'Canada' in r for r in rules))

    def test_weekly_cap_compliance(self):
        """Test that weekly/cycle remaining hours are tracked and within the cycle cap (C-12b)."""
        res = self.solver.solve_load_schedule(244606)
        for d in res['drivers_assigned']:
            self.assertTrue(d['within_70hr_limit'])
            self.assertGreaterEqual(d['weekly_remaining_hours'], 0)

    def test_multitrip_shift_chaining_with_rest(self):
        """Test a single driver executing 3 short Mira Loma trips in 1 AM shift with 45m turnaround rest."""
        res = self.solver.solve_multitrip_driver_shift(
            driver_id="DRV_07",
            load_ids=[244861, 188377, 188384],
            shift_start_mins=360,
            post_trip_rest_mins=45
        )
        self.assertTrue(res['overall_shift_feasible'])
        self.assertEqual(res['total_trips_completed'], 3)
        self.assertLessEqual(res['total_shift_duty_hours'], 11.0)
        self.assertLessEqual(res['total_shift_span_hours'], 12.0)
        self.assertEqual(res['post_trip_rest_mins'], 45)
        self.assertEqual(len(res['trips']), 3)

    def test_capacity_exceeded_rejection(self):
        """Test C-10 capacity constraint rejects load if hauler is too small."""
        res = self.solver.solve_load_schedule(244606, override_hauler_id=63)  # Hauler 63 has cap 7, load has 8
        self.assertEqual(res['status'], 'INFEASIBLE')
        self.assertEqual(res['solver_status'], 'CAPACITY_EXCEEDED')


    def test_manager_fleet_roster_generation(self):
        """Test that get_manager_fleet_roster generates all 11 commercial drivers under Constraint C-19 Non-Idleness."""
        roster = self.solver.get_manager_fleet_roster()
        summary = roster['summary']
        drivers = roster['drivers']
        
        self.assertEqual(summary['total_drivers'], 11)
        # Constraint C-19a: Zero idle drivers (all 11 actively dispatched)
        self.assertEqual(summary['active_dispatched'], 11)
        self.assertEqual(summary['standby_count'], 0)
        self.assertEqual(summary['multitrip_chained_count'], 4)
        self.assertEqual(summary['fleet_compliance_pct'], 100.0)
        self.assertGreater(summary['total_shift_vehicles_delivered'], 100)
        self.assertGreater(summary['total_shift_wages'], 5000.0)
        
        # Verify each driver has real-time location and coordinates
        for d in drivers:
            self.assertIn('current_location', d)
            loc = d['current_location']
            self.assertIn('name', loc)
            self.assertIn('description', loc)
            self.assertIsInstance(loc['lat'], (int, float))
            self.assertIsInstance(loc['lon'], (int, float))
            self.assertIn('hos_validation', d)
            self.assertTrue(d['hos_validation']['is_fully_compliant'])

    def test_multitrip_shift_validations(self):
        """Test that all multi-trip chained drivers validate multiple trips within shift limits with C-17 rest."""
        roster = self.solver.get_manager_fleet_roster()
        multitrip_drivers = [d for d in roster['drivers'] if d['is_multitrip']]
        self.assertEqual(len(multitrip_drivers), 4)

        for d in multitrip_drivers:
            # Must have at least 2 trips
            self.assertGreaterEqual(d['trips_count'], 2)
            self.assertGreater(d['vehicles_delivered'], 0)
            self.assertGreater(d['total_wages'], 0)
            self.assertGreater(d['effective_hourly_yield'], 50.0)
            
            # Mathematical HOS limits
            self.assertLessEqual(d['shift_duty_hours'], d['daily_limit_hours'])
            self.assertLessEqual(d['shift_span_hours'], 14.0)
            self.assertGreaterEqual(d['cycle_remaining_hours'], 0)
            
            # C-17 turnaround rest proof
            self.assertTrue(d['hos_validation']['turnaround_rest']['passed'])
            self.assertIn("45 min", d['hos_validation']['turnaround_rest']['used'])

    def test_constraint_c19_workload_equity_band(self):
        """Test Constraint C-19: utilization percentage across all active drivers is tightly clustered (<=25% spread)."""
        roster = self.solver.get_manager_fleet_roster()
        summary = roster['summary']
        spread = summary['c19_workload_equity_spread_pct']
        self.assertTrue(summary['c19_equity_satisfied'])
        self.assertLessEqual(spread, 25.0)
        self.assertGreater(summary['min_utilization_pct'], 45.0)
        self.assertLess(summary['max_utilization_pct'], 75.0)

    def test_driver_shortage_analysis_audit(self):
        """Test Fleet Driver Shortage & Backlogged Inventory Audit in manager roster."""
        roster = self.solver.get_manager_fleet_roster()
        self.assertIn('driver_shortage_analysis', roster)
        shortage = roster['driver_shortage_analysis']
        
        self.assertEqual(shortage['total_active_drivers_pool'], 11)
        self.assertEqual(shortage['total_daily_loads_ready'], 28)
        self.assertEqual(shortage['backlogged_loads_count'], 12)
        self.assertEqual(shortage['driver_deficit_count'], 9)
        self.assertGreater(shortage['backlogged_vehicles_count'], 80)
        self.assertGreater(shortage['backlogged_inventory_value_usd'], 3000000.0)
        self.assertTrue(len(shortage['terminal_breakdown']) >= 5)

    def test_soft_coverage_full_trip(self):
        """Test resilient soft-coverage engine achieves 100% full coverage when constraints permit."""
        res = self.solver.solve_load_schedule(244861)
        self.assertEqual(res['status'], 'OPTIMAL')
        self.assertEqual(res['trip_coverage_status'], 'FULL_COVERAGE')
        self.assertEqual(res['completion_rate_pct'], 100.0)
        self.assertFalse(res['is_partial_trip'])
        self.assertEqual(len(res['uncovered_locations']), 0)
        self.assertEqual(res['cargo_delivery_audit']['returned_to_depot_undelivered'], 0)
        self.assertTrue(res['cargo_delivery_audit']['return_trailer_empty'])

    def test_soft_coverage_partial_trip_with_cargo_return(self):
        """Test soft-coverage gracefully handles tight duty constraint by dropping unreachable stop and returning cargo."""
        # Custom scenario with 2 dealers (one local, one far in Fresno) and single driver capped at 6.0 hours (360 mins)
        # Using 8 cars to remain within 80,000 lbs Federal Bridge Law GVWR limit
        scenario = {
            'origin_code': 'LA',
            'delivery_dealer_ids': ['D_LA_01', 'D_LA_05'],  # D_LA_05 is Fresno (>250 miles)
            'cargo_count': 8,
            'hauler_capacity': 8,
            'max_driver_duty_mins': 360,
            'enforce_11hr_rule': True
        }
        res = self.solver.solve_custom_scenario(scenario)
        self.assertIn(res['status'], ['OPTIMAL', 'FEASIBLE'])
        # Single driver with 360 mins cannot reach Fresno and return, so D_LA_05 is dropped!
        self.assertEqual(res['trip_coverage_status'], 'PARTIAL_INCOMPLETE')
        self.assertTrue(res['is_partial_trip'])
        self.assertGreater(len(res['uncovered_locations']), 0)
        self.assertGreater(res['cargo_delivery_audit']['returned_to_depot_undelivered'], 0)
        self.assertFalse(res['cargo_delivery_audit']['return_trailer_empty'])
        self.assertEqual(res['uncovered_locations'][0]['dealer_id'], 'D_LA_05')
        self.assertIn("Fresno", res['uncovered_locations'][0]['dealer_name'])
        self.assertIn("HOS", res['uncovered_locations'][0]['root_cause'])

    def test_complete_constraint_evaluations_report(self):
        """Test that CP-SAT solver generates formal mathematical audit report for all 20 constraints (C-1 to C-20)."""
        res = self.solver.solve_load_schedule(244606, trip_start_mins=360, shift_type='AM')
        self.assertIn('constraint_evaluations', res)
        evals = res['constraint_evaluations']
        self.assertEqual(len(evals), 20)
        
        # Verify all 20 constraints passed
        all_passed = all(e['passed'] for e in evals)
        self.assertTrue(all_passed, f"Failed constraints: {[e['id'] for e in evals if not e['passed']]}")
        
        # Verify required keys
        required_keys = {
            'id', 'name', 'category', 'status', 'passed', 'formula',
            'observed_value', 'regulatory_limit', 'safety_slack',
            'proof_detail', 'governing_regulation'
        }
        for e in evals:
            self.assertTrue(required_keys.issubset(e.keys()), f"Missing keys in {e.get('id')}: {required_keys - set(e.keys())}")
            self.assertEqual(e['status'], 'PASS')
            self.assertTrue(len(e['observed_value']) > 0)
            self.assertTrue(len(e['regulatory_limit']) > 0)
            self.assertTrue(len(e['safety_slack']) > 0)
            self.assertTrue(len(e['proof_detail']) > 0)

        # Verify all expected constraint IDs are present
        expected_ids = {
            'C-1 & C-2', 'C-3', 'C-4', 'C-5', 'C-6', 'C-7', 'C-8 & C-9',
            'C-10a', 'C-10b', 'C-11', 'C-12a', 'C-12b', 'C-13', 'C-14',
            'C-15', 'C-16', 'C-17', 'C-18', 'C-19', 'C-20'
        }
        eval_ids = {e['id'] for e in evals}
        self.assertEqual(eval_ids, expected_ids)


if __name__ == '__main__':
    unittest.main()

