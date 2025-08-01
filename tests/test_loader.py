import unittest
import numpy as np
from app.data.loader import get_financials
from app.utils.loader import create_company_vector

class TestLoader(unittest.TestCase):
    def test_get_financials_returns_data(self):
        result = get_financials("AAPL")
        assert "ticker" in result
        assert result["ticker"] == "AAPL"
        assert result["cashflow"] is not None

class TestCreateCompanyVector(unittest.TestCase):
    def setUp(self):
        self.sample_company = {
            "description": "AI-powered accounting software for small businesses.",
            "revenue_growth": 0.12,
            "ebitda_margin": 0.30,
            "capex_pct": 0.05
        }

    def test_output_is_numpy_array(self):
        vec = create_company_vector(self.sample_company)
        self.assertIsInstance(vec, np.ndarray)
        self.assertGreater(len(vec), 0)

    def test_vector_length_differs_with_numerics(self):
        vec_text_only = create_company_vector(self.sample_company, use_numerics=False)
        vec_with_numerics = create_company_vector(self.sample_company, use_numerics=True)
        self.assertNotEqual(len(vec_text_only), len(vec_with_numerics))
        self.assertEqual(len(vec_with_numerics), len(vec_text_only) + 3)

    def test_missing_description_fallback(self):
        incomplete = {**self.sample_company, "description": ""}
        vec = create_company_vector(incomplete)
        self.assertIsInstance(vec, np.ndarray)

    def test_target_is_excluded_from_peers(self):
        from app.utils.loader import load_company_data

        # Assume your peers.json includes a company named "TestCorp"
        target_name = "Sample Peer A"
        target, peers = load_company_data(target_name)

        # Check the target was found
        assert target is not None
        assert target.get("name") == target_name

        # Ensure no peer has the same name as the target
        peer_names = [p.get("name") for p in peers]
        assert target_name not in peer_names


if __name__ == "__main__":
    unittest.main()
