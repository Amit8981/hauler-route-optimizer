"""
Unit tests for Custom Scenario & What-If Constraint Solver in hauler_cpsat_solver.py.
Tests custom user inputs (origin, dealers, weight in lbs, driver overrides, and edge cases).
"""

import unittest
from hauler_cpsat_solver import HaulerCPSATSolver


class TestCustomScenarioSolver(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.solver = HaulerCPSATSolver()

    def test_custom_short_haul_single_driver(self):
        """Test a custom single-drop short haul (Long Beach to Anaheim, 8 cars, 42,816 lbs)."""
        res = self.solver.solve_custom_scenario({
            'origin_code': 'LA',
            'delivery_dealer_ids': ['D_LA_01'],
            'cargo_count': 8,
            'cargo_weight_lbs': 42816.0,
            'hauler_capacity': 8,
            'trip_start_mins': 420
        })
        self.assertEqual(res['status'], 'OPTIMAL')
        self.assertEqual(res['num_drivers_assigned'], 1)
        self.assertEqual(res['handovers_count'], 0)
        self.assertEqual(res['trip_tag'], 'SHORT TRIP')
        self.assertLessEqual(res['total_trip_duration_hours'], 5.0)
        self.assertIn("1 Driver is legally sufficient", res['drivers_needed_explanation'])
        
        # Verify C-1 to C-18 evaluations
        evals = {e['id']: e['passed'] for e in res['constraint_evaluations']}
        self.assertTrue(evals.get('C-1 & C-2'))
        self.assertTrue(evals.get('C-10a'))
        self.assertTrue(evals.get('C-10b'))
        self.assertTrue(evals.get('C-12a'))

    def test_custom_long_haul_two_drivers_relay(self):
        """Test a custom long haul (Long Beach to Fresno Lexus Hub, > 11h turnaround)."""
        res = self.solver.solve_custom_scenario({
            'origin_code': 'LA',
            'delivery_dealer_ids': ['D_LA_05'],
            'cargo_count': 8,
            'cargo_weight_lbs': 42816.0,
            'hauler_capacity': 8,
            'trip_start_mins': 420
        })
        self.assertEqual(res['status'], 'OPTIMAL')
        self.assertEqual(res['num_drivers_assigned'], 2)
        self.assertEqual(res['handovers_count'], 1)
        self.assertEqual(res['trip_tag'], 'LONG TRIP')
        self.assertGreater(res['total_trip_duration_hours'], 11.0)
        self.assertIn("2 Drivers are legally mandated", res['drivers_needed_explanation'])
        for d in res['drivers_assigned']:
            self.assertTrue(d['within_11hr_limit'])
            self.assertLessEqual(d['total_duty_hours'], 11.0)

    def test_edge_case_capacity_overload_rejection(self):
        """Test Edge Case 1: 10 cars attempted onto a 7-car hauler rejected under C-10a."""
        res = self.solver.solve_custom_scenario({
            'origin_code': 'LA',
            'delivery_dealer_ids': ['D_LA_01'],
            'cargo_count': 10,
            'hauler_capacity': 7,
            'enforce_capacity': True
        })
        self.assertEqual(res['status'], 'INFEASIBLE')
        self.assertEqual(res['solver_status'], 'CAPACITY_EXCEEDED')
        evals = {e['id']: e['passed'] for e in res['constraint_evaluations']}
        self.assertFalse(evals.get('C-10a'))

    def test_edge_case_gross_weight_exceeded(self):
        """Test Edge Case 2: Federal bridge law GVWR breach (> 80,000 lbs) rejected under C-10b."""
        res = self.solver.solve_custom_scenario({
            'origin_code': 'LA',
            'delivery_dealer_ids': ['D_LA_01'],
            'cargo_count': 8,
            'cargo_weight_lbs': 60000.0,
            'hauler_tare_weight_lbs': 32000.0,  # Total gross = 92,000 lbs > 80,000 lbs
            'max_gross_weight_lbs': 80000.0,
            'enforce_weight_limit': True
        })
        self.assertEqual(res['status'], 'INFEASIBLE')
        self.assertEqual(res['solver_status'], 'GROSS_WEIGHT_EXCEEDED')
        evals = {e['id']: e['passed'] for e in res['constraint_evaluations']}
        self.assertFalse(evals.get('C-10b'))

    def test_custom_portland_trip(self):
        """Test Pacific Northwest custom scenario (Portland to Olympia)."""
        res = self.solver.solve_custom_scenario({
            'origin_code': 'PT',
            'delivery_dealer_ids': ['D_PT_03'],
            'cargo_count': 10,
            'hauler_capacity': 10,
            'cargo_weight_lbs': 45000.0,
            'trip_start_mins': 360
        })
        self.assertEqual(res['status'], 'OPTIMAL')
        self.assertEqual(res['num_drivers_assigned'], 1)
        self.assertLessEqual(res['total_trip_duration_hours'], 11.0)


if __name__ == '__main__':
    unittest.main()
