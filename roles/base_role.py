from dataclasses import dataclass
from typing import Optional


@dataclass
class Role:
    name: str
    title: str
    emoji: str
    team: str
    description: str
    night_action: bool = False
    action_type: str = ""
    max_uses: int = -1
    passive: bool = False

    def full_name(self) -> str:
        return f"{self.emoji} {self.title} ({self.name})"

    def short_name(self) -> str:
        return f"{self.emoji} {self.title}"

    def team_label(self) -> str:
        labels = {
            "mafia": "🦈 Qora Kuchlar",
            "town": "🛡 Oq Kuchlar",
            "neutral": "🌪 Neytral",
        }
        return labels.get(self.team, "Nihol")


ROLES: dict[str, Role] = {}


def register_role(role: Role):
    ROLES[role.name] = role
    return role


def get_role(name: str) -> Optional[Role]:
    return ROLES.get(name)


def get_roles_by_team(team: str) -> list[Role]:
    return [r for r in ROLES.values() if r.team == team]


def get_all_roles() -> list[Role]:
    return list(ROLES.values())
