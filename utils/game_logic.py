import random
from typing import Optional
from roles.base_role import Role, get_all_roles, get_role


def check_win_condition(alive_players: list) -> Optional[str]:
    mafia_count = sum(1 for p in alive_players if p["team"] == "mafia" and p["alive"])
    town_count = sum(1 for p in alive_players if p["team"] == "town" and p["alive"])
    neutral_count = sum(1 for p in alive_players if p["team"] == "neutral" and p["alive"])

    if mafia_count >= town_count + neutral_count:
        return "mafia"

    if mafia_count == 0 and neutral_count == 0:
        return "town"

    return None


def resolve_night_actions(actions: list, players: dict) -> list:
    deaths = []
    heals = set()
    blocks = set()

    for action in actions:
        action_type = action.get("action_type", "")
        target_id = action.get("target_id")
        user_id = action.get("user_id")

        if action_type == "kill" and target_id:
            deaths.append(target_id)
        elif action_type == "heal" and target_id:
            heals.add(target_id)
        elif action_type == "block" and target_id:
            blocks.add(target_id)

    saved = deaths.copy()
    for d in deaths:
        if d in heals:
            saved.remove(d)

    return saved


def get_winning_team_text(winner: str) -> str:
    texts = {
        "mafia": ("🦈 Qora Kuchlar", "O'yin nihoyasiga yetdi! Mafiya barcha fuqarolarni yo'q qildi!"),
        "town": ("🛡 Oq Kuchlar", "O'yin nihoyasiga yetdi! Fuqarolar shaharni tozaladi!"),
        "neutral": ("🌪 Neytral kuch", "Neytral kuch o'z maqsadiga erishdi!"),
    }
    return texts.get(winner, ("Nihol", ""))


def generate_death_story(role_name: str, killer_role: str = None) -> str:
    stories = {
        "mafia": "Tunuk suvda akulaning soyasi paydo bo'ldi... Jabrlanganning baqirig'i kecha sukutini bo'ldi.",
        "don": "Mafiya doni o'z jazosini oldi. Endi uning hukmronligi tugadi.",
        "doctor": "Tabib o'z bemorini davolashga ulgurmadi... Uning qo'llari zaiflashdi.",
        "detective": "Tergovchi haqiqatni bilishga yaqin edi... Lekin sir u bilan birga ketdi.",
        "townsfolk": "Begunoh fuqaro mafiya qurboni bo'ldi. Uning qoni ertangi kun uchun yonadi.",
    }
    return stories.get(role_name, "Dengiz to'lqinlari yana bir jonni olib ketdi. Uning ruhi endi ummon qa'rida.")


def format_player_list(players: list, show_roles: bool = False) -> str:
    lines = []
    for p in players:
        name = p.get("username") or p.get("first_name") or f"ID{p['user_id']}"
        if show_roles:
            role_name = p.get("role_title") or p.get("role_name", "")
            lines.append(f"• {name} — {role_name}")
        else:
            lines.append(f"• {name}")
    return "\n".join(lines)


def validate_player_count(count: int) -> tuple:
    if count < 6:
        return False, "Kamida 6 o'yinchi kerak."
    if count > 30:
        return False, "Maksimum 30 o'yinchi."
    return True, "OK"
