from dcf_app.models.dcf_model import calculate_dcf

def test_calculate_dcf_basic():
    fcf = [100, 110, 120]
    discount_rate = 0.1
    terminal_growth = 0.03
    value = calculate_dcf(fcf, discount_rate, terminal_growth)
    assert value > 0
