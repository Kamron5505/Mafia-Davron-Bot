import aiosqlite
from config import DB_PATH


class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.conn = None
        return cls._instance

    async def connect(self):
        if self.conn is None:
            self.conn = await aiosqlite.connect(DB_PATH)
            self.conn.row_factory = aiosqlite.Row
            await self._create_tables()
        return self.conn

    async def _create_tables(self):
        await self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS players (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                games_played INTEGER DEFAULT 0,
                wins INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0,
                mafia_games INTEGER DEFAULT 0,
                town_games INTEGER DEFAULT 0,
                neutral_games INTEGER DEFAULT 0,
                favorite_role TEXT DEFAULT '',
                achievements TEXT DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS games (
                game_id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                status TEXT DEFAULT 'lobby',
                phase TEXT DEFAULT 'lobby',
                night_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                roles_json TEXT DEFAULT '[]',
                players_json TEXT DEFAULT '[]'
            );

            CREATE TABLE IF NOT EXISTS game_players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id INTEGER,
                user_id INTEGER,
                role_name TEXT,
                role_title TEXT DEFAULT '',
                team TEXT DEFAULT 'town',
                alive INTEGER DEFAULT 1,
                has_voted INTEGER DEFAULT 0,
                vote_target INTEGER DEFAULT NULL,
                FOREIGN KEY (game_id) REFERENCES games(game_id)
            );

            CREATE TABLE IF NOT EXISTS game_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id INTEGER,
                event_type TEXT,
                description TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (game_id) REFERENCES games(game_id)
            );

            CREATE TABLE IF NOT EXISTS night_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id INTEGER,
                night INTEGER DEFAULT 0,
                user_id INTEGER,
                action_type TEXT,
                target_id INTEGER DEFAULT NULL,
                resolved INTEGER DEFAULT 0,
                FOREIGN KEY (game_id) REFERENCES games(game_id)
            );
        """)
        await self.conn.commit()

        await self._migrate_schema()

    async def _migrate_schema(self):
        columns = {
            "stars_balance": "INTEGER DEFAULT 0",
            "is_banned": "INTEGER DEFAULT 0",
            "ban_reason": "TEXT DEFAULT ''",
            "registered_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
        }
        for col, col_type in columns.items():
            try:
                await self.conn.execute(f"ALTER TABLE players ADD COLUMN {col} {col_type}")
            except Exception:
                pass

        new_tables = {
            "blocked_groups": "group_id INTEGER PRIMARY KEY, reason TEXT DEFAULT '', blocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "bot_groups": "group_id INTEGER PRIMARY KEY, title TEXT DEFAULT '', members_count INTEGER DEFAULT 0, games_played INTEGER DEFAULT 0, added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "stars_log": "id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, amount INTEGER NOT NULL, action_type TEXT NOT NULL, reason TEXT DEFAULT '', admin_id INTEGER DEFAULT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "payments": "id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, telegram_payment_id TEXT DEFAULT '', stars_amount INTEGER NOT NULL, price_amount INTEGER NOT NULL, currency TEXT DEFAULT 'XTR', status TEXT DEFAULT 'completed', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "settings": "key TEXT PRIMARY KEY, value TEXT NOT NULL",
            "purchased_roles": "id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, role_name TEXT NOT NULL, used INTEGER DEFAULT 0, purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
        }
        for name, schema in new_tables.items():
            try:
                await self.conn.execute(f"CREATE TABLE IF NOT EXISTS {name} ({schema})")
            except Exception:
                pass
        await self.conn.commit()

    async def get_player(self, user_id: int):
        cur = await self.conn.execute(
            "SELECT * FROM players WHERE user_id = ?", (user_id,)
        )
        return await cur.fetchone()

    async def create_player(self, user_id: int, username: str = "", first_name: str = ""):
        await self.conn.execute(
            """INSERT OR IGNORE INTO players (user_id, username, first_name)
               VALUES (?, ?, ?)""",
            (user_id, username, first_name),
        )
        await self.conn.commit()

    async def update_player_stats(self, user_id: int, won: bool, role_team: str, role_name: str):
        player = await self.get_player(user_id)
        if not player:
            return

        games = player["games_played"] + 1
        wins = player["wins"] + (1 if won else 0)
        losses = player["losses"] + (0 if won else 1)
        mafia = player["mafia_games"] + (1 if role_team == "mafia" else 0)
        town = player["town_games"] + (1 if role_team == "town" else 0)
        neutral = player["neutral_games"] + (1 if role_team == "neutral" else 0)

        await self.conn.execute(
            """UPDATE players SET games_played=?, wins=?, losses=?,
               mafia_games=?, town_games=?, neutral_games=?,
               favorite_role=?
               WHERE user_id=?""",
            (games, wins, losses, mafia, town, neutral, role_name, user_id),
        )
        await self.conn.commit()

    async def add_achievement(self, user_id: int, achievement: str):
        player = await self.get_player(user_id)
        if not player:
            return
        current = player["achievements"] or ""
        if achievement in current:
            return
        new_ach = f"{current}|{achievement}" if current else achievement
        await self.conn.execute(
            "UPDATE players SET achievements=? WHERE user_id=?",
            (new_ach, user_id),
        )
        await self.conn.commit()

    async def create_game(self, chat_id: int):
        cur = await self.conn.execute(
            "INSERT INTO games (chat_id, status, phase) VALUES (?, 'lobby', 'lobby')",
            (chat_id,),
        )
        await self.conn.commit()
        return cur.lastrowid

    async def get_active_game(self, chat_id: int):
        cur = await self.conn.execute(
            "SELECT * FROM games WHERE chat_id=? AND status IN ('lobby','night','day','voting') ORDER BY game_id DESC LIMIT 1",
            (chat_id,),
        )
        return await cur.fetchone()

    async def get_game(self, game_id: int):
        cur = await self.conn.execute(
            "SELECT * FROM games WHERE game_id=?", (game_id,)
        )
        return await cur.fetchone()

    async def update_game_status(self, game_id: int, status: str, phase: str = None):
        if phase:
            await self.conn.execute(
                "UPDATE games SET status=?, phase=? WHERE game_id=?",
                (status, phase, game_id),
            )
        else:
            await self.conn.execute(
                "UPDATE games SET status=? WHERE game_id=?",
                (status, game_id),
            )
        await self.conn.commit()

    async def add_player_to_game(self, game_id: int, user_id: int, role_name: str = "", role_title: str = "", team: str = "town"):
        await self.conn.execute(
            """INSERT OR IGNORE INTO game_players (game_id, user_id, role_name, role_title, team)
               VALUES (?, ?, ?, ?, ?)""",
            (game_id, user_id, role_name, role_title, team),
        )
        await self.conn.commit()

    async def get_game_players(self, game_id: int):
        cur = await self.conn.execute(
            "SELECT * FROM game_players WHERE game_id=?", (game_id,)
        )
        return await cur.fetchall()

    async def get_alive_players(self, game_id: int):
        cur = await self.conn.execute(
            "SELECT * FROM game_players WHERE game_id=? AND alive=1", (game_id,)
        )
        return await cur.fetchall()

    async def get_player_in_game(self, game_id: int, user_id: int):
        cur = await self.conn.execute(
            "SELECT * FROM game_players WHERE game_id=? AND user_id=?",
            (game_id, user_id),
        )
        return await cur.fetchone()

    async def kill_player(self, game_id: int, user_id: int):
        await self.conn.execute(
            "UPDATE game_players SET alive=0 WHERE game_id=? AND user_id=?",
            (game_id, user_id),
        )
        await self.conn.commit()

    async def record_event(self, game_id: int, event_type: str, description: str):
        await self.conn.execute(
            "INSERT INTO game_events (game_id, event_type, description) VALUES (?, ?, ?)",
            (game_id, event_type, description),
        )
        await self.conn.commit()

    async def get_events(self, game_id: int):
        cur = await self.conn.execute(
            "SELECT * FROM game_events WHERE game_id=? ORDER BY timestamp", (game_id,)
        )
        return await cur.fetchall()

    async def save_night_action(self, game_id: int, night: int, user_id: int, action_type: str, target_id: int = None):
        await self.conn.execute(
            "INSERT INTO night_actions (game_id, night, user_id, action_type, target_id) VALUES (?, ?, ?, ?, ?)",
            (game_id, night, user_id, action_type, target_id),
        )
        await self.conn.commit()

    async def get_night_actions(self, game_id: int, night: int):
        cur = await self.conn.execute(
            "SELECT * FROM night_actions WHERE game_id=? AND night=? AND resolved=0",
            (game_id, night),
        )
        return await cur.fetchall()

    async def resolve_night_action(self, action_id: int):
        await self.conn.execute(
            "UPDATE night_actions SET resolved=1 WHERE id=?", (action_id,)
        )
        await self.conn.commit()

    async def end_game(self, game_id: int):
        await self.conn.execute(
            "UPDATE games SET status='ended', phase='ended' WHERE game_id=?",
            (game_id,),
        )
        await self.conn.commit()

    async def get_active_games_for_recovery(self):
        cur = await self.conn.execute(
            "SELECT * FROM games WHERE status IN ('night','day','voting')"
        )
        return await cur.fetchall()

    async def close(self):
        if self.conn:
            await self.conn.close()
            self.conn = None

    async def set_vote(self, game_id: int, user_id: int, target_id: int):
        await self.conn.execute(
            "UPDATE game_players SET has_voted=1, vote_target=? WHERE game_id=? AND user_id=?",
            (target_id, game_id, user_id),
        )
        await self.conn.commit()

    async def reset_votes(self, game_id: int):
        await self.conn.execute(
            "UPDATE game_players SET has_voted=0, vote_target=NULL WHERE game_id=?",
            (game_id,),
        )
        await self.conn.commit()

    async def is_banned(self, user_id: int) -> bool:
        cur = await self.conn.execute(
            "SELECT is_banned FROM players WHERE user_id=?", (user_id,)
        )
        row = await cur.fetchone()
        return row is not None and row["is_banned"] == 1

    async def ban_user(self, user_id: int, reason: str = ""):
        await self.conn.execute(
            "UPDATE players SET is_banned=1, ban_reason=? WHERE user_id=?",
            (reason, user_id),
        )
        await self.conn.commit()

    async def unban_user(self, user_id: int):
        await self.conn.execute(
            "UPDATE players SET is_banned=0, ban_reason='' WHERE user_id=?",
            (user_id,),
        )
        await self.conn.commit()

    async def get_all_players(self):
        cur = await self.conn.execute("SELECT * FROM players ORDER BY user_id")
        return await cur.fetchall()

    async def get_players_count(self) -> int:
        cur = await self.conn.execute("SELECT COUNT(*) as cnt FROM players")
        row = await cur.fetchone()
        return row["cnt"] if row else 0

    async def get_banned_count(self) -> int:
        cur = await self.conn.execute("SELECT COUNT(*) as cnt FROM players WHERE is_banned=1")
        row = await cur.fetchone()
        return row["cnt"] if row else 0

    async def add_stars(self, user_id: int, amount: int):
        await self.conn.execute(
            "UPDATE players SET stars_balance = stars_balance + ? WHERE user_id=?",
            (amount, user_id),
        )
        await self.conn.commit()

    async def remove_stars(self, user_id: int, amount: int):
        await self.conn.execute(
            "UPDATE players SET stars_balance = MAX(0, stars_balance - ?) WHERE user_id=?",
            (amount, user_id),
        )
        await self.conn.commit()

    async def get_stars_balance(self, user_id: int) -> int:
        cur = await self.conn.execute(
            "SELECT stars_balance FROM players WHERE user_id=?", (user_id,)
        )
        row = await cur.fetchone()
        return row["stars_balance"] if row else 0

    async def add_stars_log(self, user_id: int, amount: int, action_type: str, reason: str = "", admin_id: int = None):
        await self.conn.execute(
            "INSERT INTO stars_log (user_id, amount, action_type, reason, admin_id) VALUES (?, ?, ?, ?, ?)",
            (user_id, amount, action_type, reason, admin_id),
        )
        await self.conn.commit()

    async def get_stars_log(self, user_id: int, limit: int = 50):
        cur = await self.conn.execute(
            "SELECT * FROM stars_log WHERE user_id=? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit),
        )
        return await cur.fetchall()

    async def get_total_stars_sold(self) -> int:
        cur = await self.conn.execute(
            "SELECT COALESCE(SUM(amount), 0) as total FROM stars_log WHERE action_type='purchase' OR action_type='admin_add'"
        )
        row = await cur.fetchone()
        return row["total"] if row else 0

    async def add_payment(self, user_id: int, telegram_payment_id: str, stars_amount: int, price_amount: int, status: str = "completed"):
        cur = await self.conn.execute(
            "INSERT INTO payments (user_id, telegram_payment_id, stars_amount, price_amount, status) VALUES (?, ?, ?, ?, ?)",
            (user_id, telegram_payment_id, stars_amount, price_amount, status),
        )
        await self.conn.commit()
        return cur.lastrowid

    async def get_pending_payments(self):
        cur = await self.conn.execute(
            "SELECT * FROM payments WHERE status='pending' ORDER BY created_at DESC"
        )
        return await cur.fetchall()

    async def update_payment_status(self, payment_id: int, status: str):
        await self.conn.execute(
            "UPDATE payments SET status=? WHERE id=?", (status, payment_id),
        )
        await self.conn.commit()

    async def get_total_revenue(self) -> int:
        cur = await self.conn.execute(
            "SELECT COALESCE(SUM(price_amount), 0) as total FROM payments WHERE status='completed'"
        )
        row = await cur.fetchone()
        return row["total"] if row else 0

    async def is_group_blocked(self, group_id: int) -> bool:
        cur = await self.conn.execute(
            "SELECT group_id FROM blocked_groups WHERE group_id=?", (group_id,)
        )
        return await cur.fetchone() is not None

    async def block_group(self, group_id: int, reason: str = ""):
        await self.conn.execute(
            "INSERT OR REPLACE INTO blocked_groups (group_id, reason) VALUES (?, ?)",
            (group_id, reason),
        )
        await self.conn.commit()

    async def unblock_group(self, group_id: int):
        await self.conn.execute(
            "DELETE FROM blocked_groups WHERE group_id=?", (group_id,)
        )
        await self.conn.commit()

    async def get_blocked_groups(self):
        cur = await self.conn.execute("SELECT * FROM blocked_groups")
        return await cur.fetchall()

    async def add_bot_group(self, group_id: int, title: str = "", members_count: int = 0):
        await self.conn.execute(
            "INSERT OR IGNORE INTO bot_groups (group_id, title, members_count) VALUES (?, ?, ?)",
            (group_id, title, members_count),
        )
        await self.conn.commit()

    async def update_bot_group(self, group_id: int, title: str = None, members_count: int = None, games_played: int = None):
        sets = []
        vals = []
        if title is not None:
            sets.append("title=?")
            vals.append(title)
        if members_count is not None:
            sets.append("members_count=?")
            vals.append(members_count)
        if games_played is not None:
            sets.append("games_played=?")
            vals.append(games_played)
        if sets:
            vals.append(group_id)
            await self.conn.execute(
                f"UPDATE bot_groups SET {', '.join(sets)} WHERE group_id=?",
                vals,
            )
            await self.conn.commit()

    async def remove_bot_group(self, group_id: int):
        await self.conn.execute(
            "DELETE FROM bot_groups WHERE group_id=?", (group_id,)
        )
        await self.conn.commit()

    async def get_all_groups(self):
        cur = await self.conn.execute("SELECT * FROM bot_groups")
        return await cur.fetchall()

    async def get_groups_count(self) -> int:
        cur = await self.conn.execute("SELECT COUNT(*) as cnt FROM bot_groups")
        row = await cur.fetchone()
        return row["cnt"] if row else 0

    async def get_setting(self, key: str, default: str = ""):
        cur = await self.conn.execute(
            "SELECT value FROM settings WHERE key=?", (key,)
        )
        row = await cur.fetchone()
        return row["value"] if row else default

    async def set_setting(self, key: str, value: str):
        await self.conn.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            (key, value),
        )
        await self.conn.commit()

    async def get_active_users_today(self) -> int:
        cur = await self.conn.execute(
            "SELECT COUNT(DISTINCT user_id) as cnt FROM game_events WHERE date(timestamp)=date('now')"
        )
        row = await cur.fetchone()
        return row["cnt"] if row else 0

    async def get_total_games_played(self) -> int:
        cur = await self.conn.execute(
            "SELECT COUNT(*) as cnt FROM games WHERE status='ended'"
        )
        row = await cur.fetchone()
        return row["cnt"] if row else 0

    async def reset_player_stats(self, user_id: int):
        await self.conn.execute(
            """UPDATE players SET games_played=0, wins=0, losses=0,
               mafia_games=0, town_games=0, neutral_games=0,
               favorite_role='', achievements=''
               WHERE user_id=?""",
            (user_id,),
        )
        await self.conn.commit()

    async def buy_role(self, user_id: int, role_name: str) -> bool:
        cur = await self.conn.execute(
            "SELECT id FROM purchased_roles WHERE user_id=? AND role_name=? AND used=0",
            (user_id, role_name),
        )
        if await cur.fetchone():
            return False
        await self.conn.execute(
            "INSERT INTO purchased_roles (user_id, role_name) VALUES (?, ?)",
            (user_id, role_name),
        )
        await self.conn.commit()
        return True

    async def use_purchased_role(self, user_id: int, role_name: str) -> bool:
        cur = await self.conn.execute(
            "UPDATE purchased_roles SET used=1 WHERE user_id=? AND role_name=? AND used=0 LIMIT 1",
            (user_id, role_name),
        )
        await self.conn.commit()
        return cur.rowcount > 0

    async def get_purchased_role_names(self, user_id: int) -> list:
        cur = await self.conn.execute(
            "SELECT role_name FROM purchased_roles WHERE user_id=? AND used=0",
            (user_id,),
        )
        rows = await cur.fetchall()
        return [row["role_name"] for row in rows]
