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


if __name__ == '__main__':
    unittest.main()
