from app.sensitivity import run_sensitivity_analysis

def test_run_sensitivity_analysis():
    base_inputs = {
        'revenue': 100,
        'growth_rate': 0.05,
        'wacc': 0.1,
        'terminal_growth': 0.02
    }

    values = [0.09, 0.1, 0.11]
    results = run_sensitivity_analysis(base_inputs, 'wacc', values)
    assert len(results) == 3
    assert all(isinstance(v, float) for v in results.values())
