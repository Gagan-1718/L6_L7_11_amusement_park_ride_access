"""Lab 6 - Step 7: test cases targeting >= 90% BRANCH coverage.

Includes every line-coverage test plus extra tests so each decision
(and each loop entry / loop exit) is taken both ways.
"""
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


# ---------- process_ride_admissions: validation ----------

def test_single_adult_family_ride():
    result = process_ride_admissions([make_group(patrons=[patron()])], 5.0)
    assert result == {"total_revenue": 10.0, "status": "COMPLETED"}


def test_groups_not_a_list_raises():
    with pytest.raises(ValueError):
        process_ride_admissions("not a list", 5.0)


def test_negative_fee_raises():
    with pytest.raises(ValueError):
        process_ride_admissions([], -1)


def test_zero_fee_is_valid():
    assert process_ride_admissions([], 0)["status"] == "ZERO_ADMISSIONS"


# ---------- groups loop / is_open ----------

def test_empty_groups_list():
    assert process_ride_admissions([], 5.0) == {"total_revenue": 0.0, "status": "ZERO_ADMISSIONS"}


def test_closed_group_is_skipped():
    result = process_ride_admissions([make_group(is_open=False, patrons=[patron()])], 5.0)
    assert result["status"] == "ZERO_ADMISSIONS"


def test_missing_is_open_defaults_to_closed():
    result = process_ride_admissions([{"ride_type": "family", "patrons": [patron()]}], 0)
    assert result["status"] == "ZERO_ADMISSIONS"


def test_missing_ride_type_defaults_to_family():
    result = process_ride_admissions([{"is_open": True, "patrons": [patron()]}], 0)
    assert result["total_revenue"] == 10.0


# ---------- ride types ----------

def test_roller_coaster_adult():
    assert process_ride_admissions([make_group("roller_coaster", [patron()])], 0)["total_revenue"] == 25.0


def test_water_ride_adult():
    assert process_ride_admissions([make_group("water_ride", [patron()])], 0)["total_revenue"] == 18.0


def test_unknown_ride_type_rejected():
    result = process_ride_admissions([make_group("zipline", [patron()])], 0)
    assert result["status"] == "ZERO_ADMISSIONS"


# ---------- patrons loop ----------

def test_open_group_with_no_patrons():
    result = process_ride_admissions([make_group(patrons=[])], 0)
    assert result["status"] == "ZERO_ADMISSIONS"


def test_missing_patrons_key():
    result = process_ride_admissions([{"is_open": True, "ride_type": "family"}], 0)
    assert result["status"] == "ZERO_ADMISSIONS"


def test_zero_height_rejected():
    result = process_ride_admissions([make_group(patrons=[patron(height=0)])], 0)
    assert result["status"] == "ZERO_ADMISSIONS"


def test_negative_height_rejected():
    result = process_ride_admissions([make_group(patrons=[patron(height=-5)])], 0)
    assert result["status"] == "ZERO_ADMISSIONS"


def test_missing_height_rejected():
    result = process_ride_admissions([make_group(patrons=[{}])], 0)
    assert result["status"] == "ZERO_ADMISSIONS"


def test_too_short_rejected():
    result = process_ride_admissions([make_group(patrons=[patron(height=119)])], 0)
    assert result["status"] == "ZERO_ADMISSIONS"


def test_exactly_minimum_height_admitted():
    assert process_ride_admissions([make_group(patrons=[patron(height=120)])], 0)["total_revenue"] == 10.0


def test_child_discount():
    result = process_ride_admissions([make_group("roller_coaster", [patron(child=True)])], 0)
    assert result["total_revenue"] == 15.0


def test_adult_full_price():
    result = process_ride_admissions([make_group("water_ride", [patron(child=False)])], 0)
    assert result["total_revenue"] == 18.0


# ---------- health warning ----------

def test_health_warning_roller_coaster_cancels_group_and_breaks():
    group = make_group("roller_coaster", [patron(), patron(health=True), patron()])
    result = process_ride_admissions([group], 0)
    assert result["status"] == "ZERO_ADMISSIONS"


def test_health_warning_family_ride_continues():
    group = make_group("family", [patron(health=True), patron()])
    assert process_ride_admissions([group], 0) == {"total_revenue": 10.0, "status": "COMPLETED"}


# ---------- fast lane ----------

def test_fast_lane_fee_added():
    result = process_ride_admissions([make_group(patrons=[patron()], fast_lane=True)], 5.0)
    assert result["total_revenue"] == 15.0


def test_no_fast_lane_no_fee():
    result = process_ride_admissions([make_group(patrons=[patron()], fast_lane=False)], 5.0)
    assert result["total_revenue"] == 10.0


def test_missing_fast_lane_key_means_no_fee():
    result = process_ride_admissions([{"is_open": True, "patrons": [patron()]}], 5.0)
    assert result["total_revenue"] == 10.0


# ---------- final status ----------

def test_exactly_four_rejections_not_audit():
    group = make_group("family", [patron(height=50)] * 4 + [patron()])
    assert process_ride_admissions([group], 0)["status"] == "COMPLETED"


def test_five_rejections_triggers_audit():
    group = make_group("family", [patron(height=50)] * 5 + [patron()])
    assert process_ride_admissions([group], 0) == {"total_revenue": 10.0, "status": "SAFETY_AUDIT"}


def test_multiple_groups_accumulate():
    groups = [make_group("family", [patron()]), make_group("water_ride", [patron()])]
    assert process_ride_admissions(groups, 0)["total_revenue"] == 28.0


# ---------- inspect_safety_restraints ----------

def test_no_data_empty_list():
    assert inspect_safety_restraints([]) == "NO_DATA"


def test_no_data_none():
    assert inspect_safety_restraints(None) == "NO_DATA"


def test_emergency_lock():
    assert inspect_safety_restraints([[1, 0, 0]]) == "EMERGENCY_LOCK"


def test_emergency_lock_in_second_stream():
    assert inspect_safety_restraints([[1, 1], [0, 0]]) == "EMERGENCY_LOCK"


def test_single_unlatched_is_safe():
    assert inspect_safety_restraints([[1, 0, 1]]) == "SAFE"


def test_streak_reset_then_unlatched_is_safe():
    assert inspect_safety_restraints([[0, 1, 0, 1]]) == "SAFE"


def test_all_latched_is_safe():
    assert inspect_safety_restraints([[1, 1, 1]]) == "SAFE"


def test_empty_sensor_stream_is_safe():
    assert inspect_safety_restraints([[]]) == "SAFE"
