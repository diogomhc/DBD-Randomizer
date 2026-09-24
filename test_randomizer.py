"""Unit tests for randomizer.py. No display needed - run with:
    pytest test_randomizer.py
"""

import json
from unittest.mock import MagicMock

import pytest

from randomizer import RandomizerState


@pytest.fixture
def state_file(tmp_path):
    """A throwaway state file path so tests never touch the real
    randomizer_state.json in the project folder."""
    return str(tmp_path / "randomizer_state.json")


def make_fake_data():
    """A minimal GameData-like stub, no JSON files needed."""
    data = MagicMock()
    data.killers = ["Killer A", "Killer B", "Killer C"]
    data.killer_addons = {
        0: [{"name": "A1", "rarity": "Common", "img": "a1.png"},
            {"name": "A2", "rarity": "Rare", "img": "a2.png"}],
        1: [{"name": "B1", "rarity": "Common", "img": "b1.png"}],  # only 1 addon
        2: [],
    }
    data.perks_by_key = {
        0: {"name": "Perk 1", "killer": "Killer A", "image": "p1.png"},
        1: {"name": "Perk 2", "killer": "Killer A", "image": "p2.png"},
        2: {"name": "Perk 3", "killer": "Killer B", "image": "p3.png"},
        3: {"name": "Perk 4", "killer": "Killer C", "image": "p4.png"},
    }
    return data


def test_random_perks_never_duplicates(state_file):
    state = RandomizerState(make_fake_data(), state_file)
    for _ in range(200):
        perks = state.random_perks(count=4)
        assert len(perks) == len(set(perks)), f"duplicate perk in {perks}"
        assert len(perks) == 4


def test_random_perks_respects_deactivated(state_file):
    state = RandomizerState(make_fake_data(), state_file)
    state.toggle_perk(0)  # deactivate "Perk 1"
    for _ in range(50):
        perks = state.random_perks(count=4)
        assert "Perk 1" not in perks


def test_random_perks_fewer_active_than_count(state_file):
    state = RandomizerState(make_fake_data(), state_file)
    state.toggle_perk(0)
    state.toggle_perk(1)
    state.toggle_perk(2)  # only "Perk 4" left active
    perks = state.random_perks(count=4)
    assert perks == ["Perk 4"]


def test_random_perks_none_active(state_file):
    state = RandomizerState(make_fake_data(), state_file)
    for key in range(4):
        state.toggle_perk(key)
    assert state.random_perks(count=4) == []


def test_random_killer_none_active(state_file):
    state = RandomizerState(make_fake_data(), state_file)
    for name in list(state.active_killers):
        state.active_killers.remove(name)
    assert state.random_killer() is None


def test_random_killer_returns_valid_index(state_file):
    state = RandomizerState(make_fake_data(), state_file)
    for _ in range(50):
        idx = state.random_killer()
        assert idx in (0, 1, 2)


def test_random_addons_returns_none_when_fewer_than_two(state_file):
    state = RandomizerState(make_fake_data(), state_file)
    assert state.random_addons(1) == (None, None)  # Killer B has 1 addon
    assert state.random_addons(2) == (None, None)  # Killer C has 0 addons


def test_random_addons_returns_two_distinct_indices(state_file):
    state = RandomizerState(make_fake_data(), state_file)
    for _ in range(50):
        i1, i2 = state.random_addons(0)  # Killer A has 2 addons
        assert i1 != i2
        assert {i1, i2} == {0, 1}


def test_toggle_killer_round_trips(state_file):
    state = RandomizerState(make_fake_data(), state_file)
    assert state.is_killer_active(0) is True
    state.toggle_killer(0)
    assert state.is_killer_active(0) is False
    state.toggle_killer(0)
    assert state.is_killer_active(0) is True


def test_deactivate_related_perks(state_file):
    state = RandomizerState(make_fake_data(), state_file)
    state.toggle_killer(0)  # deactivate Killer A
    state.deactivate_related_perks()
    assert not state.is_perk_active(0)  # Perk 1 belongs to Killer A
    assert not state.is_perk_active(1)  # Perk 2 belongs to Killer A
    assert state.is_perk_active(2)      # Perk 3 belongs to Killer B (still active)


def test_activate_related_perks(state_file):
    state = RandomizerState(make_fake_data(), state_file)
    state.toggle_killer(0)
    state.deactivate_related_perks()
    state.toggle_killer(0) 
    state.activate_related_perks()
    assert state.is_perk_active(0)
    assert state.is_perk_active(1)


def test_state_persists_across_instances(state_file):
    state = RandomizerState(make_fake_data(), state_file)
    state.toggle_killer(0)  # deactivate Killer A
    state.toggle_perk(2)    # deactivate Perk 3

    # A fresh RandomizerState pointed at the same file should pick up
    # the saved active sets instead of the defaults.
    reloaded = RandomizerState(make_fake_data(), state_file)
    assert not reloaded.is_killer_active(0)
    assert reloaded.is_killer_active(1)
    assert not reloaded.is_perk_active(2)
    assert reloaded.is_perk_active(0)


def test_state_file_contents(state_file):
    state = RandomizerState(make_fake_data(), state_file)
    state.toggle_killer(1)
    with open(state_file, "r", encoding="utf-8") as f:
        saved = json.load(f)
    assert "Killer B" not in saved["active_killers"]
    assert saved["active_perks"] == state.active_perks


def test_missing_state_file_falls_back_to_defaults(state_file):
    # state_file doesn't exist yet - should fall back to "everything active"
    state = RandomizerState(make_fake_data(), state_file)
    assert state.active_killers == ["Killer A", "Killer B", "Killer C"]
    assert len(state.active_perks) == 4


def test_corrupt_state_file_falls_back_to_defaults(state_file):
    with open(state_file, "w", encoding="utf-8") as f:
        f.write("{not valid json")
    state = RandomizerState(make_fake_data(), state_file)
    assert state.active_killers == ["Killer A", "Killer B", "Killer C"]


# -- Add-on management --------------------------------------------------


def make_fake_data_many_addons():
    """A killer with 4 add-ons (enough to test partial activation) and a
    second killer with none, to check that edge case too."""
    data = MagicMock()
    data.killers = ["Killer A", "Killer B"]
    data.killer_addons = {
        0: [
            {"name": "A1", "rarity": "Common", "img": "a1.png"},
            {"name": "A2", "rarity": "Common", "img": "a2.png"},
            {"name": "A3", "rarity": "Rare", "img": "a3.png"},
            {"name": "A4", "rarity": "Rare", "img": "a4.png"},
        ],
        1: [],
    }
    data.perks_by_key = {
        0: {"name": "Perk 1", "killer": "Killer A", "image": "p1.png"},
    }
    return data


def test_addons_all_active_by_default(state_file):
    state = RandomizerState(make_fake_data_many_addons(), state_file)
    assert all(state.is_addon_active(0, i) for i in range(4))


def test_toggle_addon_round_trips(state_file):
    state = RandomizerState(make_fake_data_many_addons(), state_file)
    assert state.is_addon_active(0, 0) is True
    state.toggle_addon(0, 0)
    assert state.is_addon_active(0, 0) is False
    state.toggle_addon(0, 0)
    assert state.is_addon_active(0, 0) is True


def test_toggle_addon_is_per_killer(state_file):
    state = RandomizerState(make_fake_data_many_addons(), state_file)
    state.toggle_addon(0, 0)  # only affects Killer A's add-on 0
    assert state.is_addon_active(0, 0) is False
    # Killer B has no add-ons, but this confirms toggling one killer
    # doesn't touch another killer's list.
    assert state.active_addon_indices(1) == []


def test_bulk_toggle_addons(state_file):
    state = RandomizerState(make_fake_data_many_addons(), state_file)
    state.bulk_toggle_addons(0, False)
    assert state.active_addon_indices(0) == []
    state.bulk_toggle_addons(0, True)
    assert state.active_addon_indices(0) == [0, 1, 2, 3]


def test_random_addons_respects_deactivated(state_file):
    state = RandomizerState(make_fake_data_many_addons(), state_file)
    state.toggle_addon(0, 2)  # deactivate A3
    state.toggle_addon(0, 3)  # deactivate A4
    for _ in range(50):
        i1, i2 = state.random_addons(0)
        assert {i1, i2} <= {0, 1}  # only A1/A2 remain active


def test_random_addons_none_when_fewer_than_two_active(state_file):
    state = RandomizerState(make_fake_data_many_addons(), state_file)
    state.toggle_addon(0, 1)
    state.toggle_addon(0, 2)
    state.toggle_addon(0, 3)  # only A1 left active
    assert state.random_addons(0) == (None, None)


def test_random_addons_none_for_killer_with_no_addons(state_file):
    state = RandomizerState(make_fake_data_many_addons(), state_file)
    assert state.random_addons(1) == (None, None)


def test_addon_state_persists_across_instances(state_file):
    state = RandomizerState(make_fake_data_many_addons(), state_file)
    state.toggle_addon(0, 0)

    reloaded = RandomizerState(make_fake_data_many_addons(), state_file)
    assert reloaded.is_addon_active(0, 0) is False
    assert reloaded.is_addon_active(0, 1) is True


def test_addon_state_file_contents(state_file):
    state = RandomizerState(make_fake_data_many_addons(), state_file)
    state.toggle_addon(0, 0)
    with open(state_file, "r", encoding="utf-8") as f:
        saved = json.load(f)
    assert "A1" not in saved["active_addons"]["0"]
    assert "A2" in saved["active_addons"]["0"]


def test_addon_state_missing_killer_entry_defaults_to_active(state_file):
    """If active_addons is saved without an entry for some killer (e.g. a
    killer added to killers.json after the state file was last written),
    that killer's add-ons should default to active rather than empty."""
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(
            {
                "active_killers": ["Killer A", "Killer B"],
                "active_perks": ["Perk 1"],
                "active_addons": {},  # no entry for killer 0 at all
            },
            f,
        )
    state = RandomizerState(make_fake_data_many_addons(), state_file)
    assert state.active_addon_indices(0) == [0, 1, 2, 3]


def test_corrupt_state_file_addons_default_to_active(state_file):
    with open(state_file, "w", encoding="utf-8") as f:
        f.write("{not valid json")
    state = RandomizerState(make_fake_data_many_addons(), state_file)
    assert state.active_addon_indices(0) == [0, 1, 2, 3]


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v"]))
