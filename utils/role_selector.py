import random
from typing import List, Dict
from roles.base_role import ROLES, get_roles_by_team, get_role
from database.db import Database


def select_roles(count: int = 6) -> list:
    mafia_roles = get_roles_by_team("mafia")
    town_roles = get_roles_by_team("town")
    neutral_roles = get_roles_by_team("neutral")

    mafia_count = random.choices([1, 2], weights=[0.4, 0.6])[0]
    neutral_count = random.choices([0, 1], weights=[0.7, 0.3])[0]
    town_count = count - mafia_count - neutral_count

    if town_count < 2:
        neutral_count = 0
        town_count = count - mafia_count

    selected = []

    picked_mafia = random.sample(mafia_roles, min(mafia_count, len(mafia_roles)))
    selected.extend(picked_mafia)

    if neutral_count > 0:
        picked_neutral = random.sample(neutral_roles, min(neutral_count, len(neutral_roles)))
        selected.extend(picked_neutral)

    has_townsfolk = any(r.name == "townsfolk" for r in selected)
    available_town = [r for r in town_roles]
    if not has_townsfolk and town_count > 1:
        town_count -= 1
        selected.append(next(r for r in town_roles if r.name == "townsfolk"))

    needed = count - len(selected)
    if needed > 0:
        exclude_names = {r.name for r in selected}
        pool = [r for r in available_town if r.name not in exclude_names]
        if len(pool) < needed:
            pool = town_roles
        picked_town = random.sample(pool, min(needed, len(pool)))
        selected.extend(picked_town)

    selected = selected[:count]
    random.shuffle(selected)
    return selected


def assign_roles(players: list, selected_roles: list, purchased_roles: Dict[int, str] = None) -> dict:
    if purchased_roles is None:
        purchased_roles = {}

    if len(players) < len(selected_roles):
        diff = len(players) - len(selected_roles)
        townsfolk_roles = [r for r in selected_roles if r.name == "townsfolk"]
        for _ in range(diff):
            if townsfolk_roles:
                selected_roles.append(townsfolk_roles[0])
            else:
                from roles.town_roles import register_role
                selected_roles.append(get_roles_by_team("town")[0])

    random.shuffle(players)
    assignments = {}
    assigned_roles = list(selected_roles)

    # First, assign purchased roles to their buyers
    for player in list(players):
        if player in purchased_roles:
            role_name = purchased_roles[player]
            role = get_role(role_name)
            if role and role in assigned_roles:
                assignments[player] = role
                assigned_roles.remove(role)
                players.remove(player)
            elif role:
                # Role not in selected list, add it and remove another
                assignments[player] = role
                players.remove(player)
                if assigned_roles:
                    assigned_roles.pop()

    # Then assign remaining roles to remaining players
    for i, player in enumerate(players):
        role = assigned_roles[i % len(assigned_roles)]
        assignments[player] = role

    return assignments
