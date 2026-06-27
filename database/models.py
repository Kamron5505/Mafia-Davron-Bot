from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class Player:
    user_id: int
    username: str = ""
    first_name: str = ""
    games_played: int = 0
    wins: int = 0
    losses: int = 0
    mafia_games: int = 0
    town_games: int = 0
    neutral_games: int = 0
    favorite_role: str = ""
    achievements: str = ""


@dataclass
class GameSession:
    game_id: int
    chat_id: int
    status: str = "lobby"
    phase: str = "lobby"
    night_count: int = 0
    roles_json: str = "[]"
    players_json: str = "[]"

    def __post_init__(self):
        self.players: List[GamePlayer] = []
        self.roles: List[str] = []

    @property
    def is_active(self):
        return self.status in ("lobby", "night", "day", "voting")


@dataclass
class GamePlayer:
    id: int = 0
    game_id: int = 0
    user_id: int = 0
    role_name: str = ""
    role_title: str = ""
    team: str = "town"
    alive: bool = True
    has_voted: bool = False
    vote_target: Optional[int] = None
