"""Lab 6 - Step 5: test cases targeting >= 90% LINE (code) coverage."""
import pytest
from amusement_park_ride_access import process_ride_admissions, inspect_safety_restraints


def make_group(ride_type="family", patrons=None, is_open=True, fast_lane=False):
    return {
        "is_open": is_open,
        "ride_type": ride_type,
        "has_fast_lane": fast_lane,
        "patrons": patrons if patrons is not None else [],
    }


def patron(height=150, health=False, child=False):
    return {"height_cm": height, "health_warning": health, "is_child": child}


# ---------- process_ride_admissions ----------

def test_single_adult_family_ride():
    result = process_ride_admissions([make_group(patrons=[patron()])], 5.0)
    assert result == {"total_revenue": 10.0, "status": "COMPLETED"}


def test_invalid_input_raises():
    with pytest.raises(ValueError):
        process_ride_admissions("not a list", 5.0)


def test_closed_group_is_skipped():
    result = process_ride_admissions([make_group(is_open=False, patrons=[patron()])], 5.0)
    assert result["status"] == "ZERO_ADMISSIONS"


def test_roller_coaster_adult_and_child_with_fast_lane():
    group = make_group("roller_coaster", [patron(), patron(child=True)], fast_lane=True)
    result = process_ride_admissions([group], 5.0)
    assert result["total_revenue"] == 25.0 + 15.0 + 5.0
    assert result["status"] == "COMPLETED"


def test_water_ride_price():
    result = process_ride_admissions([make_group("water_ride", [patron()])], 0)
    assert result["total_revenue"] == 18.0


def test_unknown_ride_type_rejected():
    result = process_ride_admissions([make_group("zipline", [patron()])], 0)
    assert result["status"] == "ZERO_ADMISSIONS"


def test_invalid_height_rejected():
    result = process_ride_admissions([make_group(patrons=[patron(height=0)])], 0)
    assert result["status"] == "ZERO_ADMISSIONS"


def test_too_short_rejected():
    result = process_ride_admissions([make_group(patrons=[patron(height=100)])], 0)
    assert result["status"] == "ZERO_ADMISSIONS"


def test_health_warning_roller_coaster_cancels_group():
    group = make_group("roller_coaster", [patron(), patron(health=True), patron()])
    result = process_ride_admissions([group], 0)
    assert result["status"] == "ZERO_ADMISSIONS"


def test_health_warning_family_ride_only_rejects_that_patron():
    group = make_group("family", [patron(health=True), patron()])
    result = process_ride_admissions([group], 0)
    assert result == {"total_revenue": 10.0, "status": "COMPLETED"}


def test_safety_audit_when_more_than_four_rejections():
    group = make_group("family", [patron(height=50)] * 5 + [patron()])
    result = process_ride_admissions([group], 0)
    assert result == {"total_revenue": 10.0, "status": "SAFETY_AUDIT"}


# ---------- inspect_safety_restraints ----------

def test_no_data():
    assert inspect_safety_restraints([]) == "NO_DATA"


def test_emergency_lock_on_two_consecutive_unlatched():
    assert inspect_safety_restraints([[1, 0, 0]]) == "EMERGENCY_LOCK"


def test_safe_when_streak_is_reset():
    assert inspect_safety_restraints([[0, 1, 0, 1]]) == "SAFE"
