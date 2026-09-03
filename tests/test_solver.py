import unittest
import os
import sys

# Add project directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from hauler_cpsat_solver import HaulerCPSATSolver


class TestHaulerCPSATSolver(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.solver = HaulerCPSATSolver()

    def test_short_haul_single_driver(self):
        """Test a short haul load (< 11h) correctly assigns exactly 1 driver with 0 handovers."""
        res = self.solver.solve_load_schedule(244861, trip_start_mins=420)
        self.assertIn(res['status'], ['OPTIMAL', 'FEASIBLE'])
        self.assertEqual(res['num_drivers_assigned'], 1)
        self.assertEqual(res['handovers_count'], 0)
        self.assertTrue(res['drivers_assigned'][0]['within_11hr_limit'])
        self.assertLessEqual(res['drivers_assigned'][0]['total_duty_hours'], 11.0)
        # Check factory departure and return
        self.assertEqual(res['legs'][0]['from_code'], res['origin_vdc'])
        self.assertEqual(res['legs'][-1]['to_code'], res['origin_vdc'])

    def test_long_haul_two_drivers_handover(self):
        """Test a long haul load (> 11h) triggers 2 drivers and 1 handover within 11h rule."""
        res = self.solver.solve_load_schedule(244606, trip_start_mins=420)
        self.assertIn(res['status'], ['OPTIMAL', 'FEASIBLE'])
        self.assertEqual(res['num_drivers_assigned'], 2)
        self.assertEqual(res['handovers_count'], 1)
        for d in res['drivers_assigned']:
            self.assertTrue(d['within_11hr_limit'])
            self.assertLessEqual(d['total_duty_hours'], 11.0)

    def test_portland_long_haul(self):
        """Test Portland Pacific Northwest long-haul load (> 11h)."""
        res = self.solver.solve_load_schedule(245356, trip_start_mins=420)
        self.assertIn(res['status'], ['OPTIMAL', 'FEASIBLE'])
        self.assertGreater(res['total_travel_time_hours'], 11.0)
        self.assertEqual(res['num_drivers_assigned'], 2)
        for d in res['drivers_assigned']:
            self.assertLessEqual(d['total_duty_hours'], 11.0)

    def test_capacity_exceeded_rejection(self):
        """Test that attempting to put 8 cars onto a 7-car hauler triggers capacity exceeded."""
        # Hauler 63 has capacity 7
        res = self.solver.solve_load_schedule(244606, override_hauler_id=63)
        self.assertEqual(res['status'], 'INFEASIBLE')
        self.assertEqual(res['solver_status'], 'CAPACITY_EXCEEDED')


if __name__ == '__main__':
    unittest.main()
