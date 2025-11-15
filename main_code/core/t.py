def _get_cards(self, player, game_table):
    # Your existing logic for showing hole cards
    if player.fold:
        return []
    if (
        isinstance(player, Human)
        or game_table.r >= game_table.skip_round
        or game_table.players_remaining > 1
        and game_table.running == False
    ):
        return player.hole_cards
    return ["card_back"] * 2

def _get_poss_actions(self, player, game_table):
    # Your existing logic for determining available actions
    return [
        (
            "Check"
            if not game_table.running
            or player.round_invested == game_table.last_bet
            else "Call"
        ),
        "Bet" if not game_table.running or not game_table.last_bet else "Raise",
    ]

def _get_profile_picture(self, i):
    return ["nature", "bot", "calvin", "daniel_n", "elliot", "teddy"][i]

def _get_action(self, player, game_table):
    # Your existing logic for formatting the action text
    action = player.action
    if action is None:
        return ""
    if action == 1:
        return "Fold"
    if action == 2:
        return "Call" if player.extra else "Check"
    else:
        word = (
            "All In"
            if player.chips == 0
            else "Bet" if game_table.bet_count < 2 else "Raise"
        )
        return f"{word} {player.extra}"

# --- Core Game Logic Methods ---

def run_bot_moves(self, game_table):
    """Handles bot turns automatically until a human or the end of the round."""
    end_round = False
    while game_table.running and isinstance(game_table.current_player, Bot):
        if game_table.can_move():
            move = game_table.current_player.get_action(game_table)
            end_round = game_table.single_move(move)
        else:
            end_round = game_table.end_move()

        if end_round:
            break
    return end_round

def get_state(self, game_table, user_seat_index):
    """Creates a standardized game state dictionary to send to a specific client."""
    state = {
        "players": [
            {
                "chips": p.chips,
                "folded": p.fold,
                "hole_cards": self._get_cards(p, game_table),
                "action": self._get_action(p, game_table),
                "round_invested": p.round_invested,
                "seat": i,
                "position_name": p.position_name,
                "poss_actions": self._get_poss_actions(p, game_table),
                "profile_picture": self._get_profile_picture(i),
            }
            for i, p in enumerate(game_table.players)
        ],
        "community": game_table.community,
        "pot": game_table.get_pot() if game_table.running else 0,
        "running": game_table.running,
        "round": game_table.r,
        "user_i": user_seat_index,  # The GUI will follow this player
        "new_player": False,
    }
    return state