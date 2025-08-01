import unittest
from app.models.dcf_generator import generate_forecasted_fcfs, run_dcf_from_inputs

class TestDCFGenerator(unittest.TestCase):
    def setUp(self):
        self.inputs = {
            "revenue_base": 1000.0,
            "revenue_growth": 0.05,
            "ebitda_margin": 0.25,
            "depreciation_pct": 0.05,
            "capex_pct": 0.10,
            "nwc_pct": 0.04,
            "tax_rate": 0.25,
            "interest_expense": 20.0,
            "debt": 500.0,
            "years": 5
        }

    def test_generate_forecasted_fcfs(self):
        fcfs = generate_forecasted_fcfs(self.inputs)

        # Basic checks
        self.assertIsInstance(fcfs, list)
        self.assertEqual(len(fcfs), self.inputs["years"])
        for fcf in fcfs:
            self.assertIsInstance(fcf, (float, int))

    def test_run_dcf_from_inputs_returns_float(self):
        value = run_dcf_from_inputs(self.inputs)
        self.assertIsInstance(value, float)
        self.assertGreater(value, 0.0)  # optional: basic reasonableness check

if __name__ == "__main__":
    unittest.main()
