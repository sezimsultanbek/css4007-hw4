from tools import lookup, calculate


def test_lookup_population():
    result = lookup("Ossbridge", "population_2025")
    assert result["value"] == 52904
    assert result["sources"] == ["NR-01"]


def test_lookup_corrected_area():
    result = lookup("Brightwater", "area_km2")
    assert result["value"] == 921.4


def test_lookup_water_conversion():
    result = lookup("Lindenmoor", "water_2025_m3")
    assert result["value"] == 2151400


def test_calculate():
    result = calculate("10 + 5 * 2")
    assert result["result"] == 20


def test_calculate_rejects_unsafe_code():
    result = calculate("__import__('os').system('echo unsafe')")
    assert "error" in result