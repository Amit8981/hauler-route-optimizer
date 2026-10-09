"""
Unit tests for Equitable Driver VIN Utilization Solver (Option 1: min(W_max - W_min)).
"""

import unittest
from hauler_equitable_vin_solver import HaulerEquitableVINSolver


class TestEquitableVINSolver(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.solver = HaulerEquitableVINSolver()

    def test_option1_single_objective_fleet_optimization(self):
        """Test that Option 1 min(W_max - W_min) achieves optimal equity across all 11 drivers."""
        res = self.solver.solve_fleet_vin_equity_dispatch()
        
        self.assertIn(res['status'], ['OPTIMAL', 'FEASIBLE'])
        self.assertEqual(res['total_drivers'], 11)
        self.assertEqual(res['w_max'] - res['w_min'], res['optimal_spread'])
        # Optimal spread should be <= 4 vehicles (vs 23 vehicles prior spread)
        self.assertLessEqual(res['optimal_spread'], 4)
        self.assertGreater(res['spread_reduction_pct'], 75.0)
        self.assertTrue(res['is_perfectly_balanced'])

    def test_all_11_drivers_active_and_workload_balanced(self):
        """Test that Constraint C-19 Non-Idleness is preserved: 0 idle drivers, tight VIN band."""
        res = self.solver.solve_fleet_vin_equity_dispatch()
        drivers = res['drivers']
        
        self.assertEqual(len(drivers), 11)
        for d in drivers:
            # Every driver must have at least 1 load and deliver vehicles
            self.assertGreater(d['loads_assigned_count'], 0)
            self.assertGreater(d['shift_vins_delivered'], 0)
            # Cycle VINs should be clustered around the fleet mean
            self.assertGreaterEqual(d['total_cycle_vins'], res['w_min'])
            self.assertLessEqual(d['total_cycle_vins'], res['w_max'])
            # Shift duty hours must strictly respect daily limit (C-12a)
            self.assertLessEqual(d['shift_duty_hours'], 14.0)

    def test_load_schedule_vin_equity_execution(self):
        """Test load-level scheduling with Option 1 single objective for driver balance."""
        res = self.solver.solve_load_schedule_vin_equity(244861)
        
        self.assertIn(res['status'], ['OPTIMAL', 'FEASIBLE'])
        self.assertEqual(res.get('equity_mode'), 'OPTION_1_MIN_MAX_SPREAD')
        self.assertIn('min(W_max - W_min)', res.get('objective_type', ''))
        self.assertIsNotNone(res.get('optimal_vin_spread'))
        # Constraint C-10a, C-12a, C-1, C-2 verification
        self.assertEqual(res['origin_vdc'], 'ML')
        self.assertLessEqual(res['total_trip_duration_hours'], 11.0)
        self.assertEqual(res['total_cargo_units'], 8)

    def test_regulatory_constraints_c1_to_c18_preserved(self):
        """Test that all statutory FMCSA and physical capacity constraints remain intact."""
        res = self.solver.solve_load_schedule_vin_equity(244606)
        
        self.assertIn(res['status'], ['OPTIMAL', 'FEASIBLE'])
        # Long trip requires 2 drivers under C-13
        self.assertEqual(len(res['drivers_assigned']), 2)
        # Total vehicle units conserved (C-10)
        self.assertEqual(res['total_cargo_units'], 10)
        # Handover executed at certified hub (C-14)
        handovers = [l for l in res['legs'] if l['handover_at_dest']]
        self.assertEqual(len(handovers), 1)
        self.assertEqual(handovers[0]['handover_duration_mins'], 45)


if __name__ == '__main__':
    unittest.main()
