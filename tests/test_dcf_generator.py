from app.models.dcf_generator import mock_dcf_valuation

def test_dcf_output_range():
    val = mock_dcf_valuation("Cloud service company")
    assert 80 <= val <= 150
