from glicko2 import Player as GlickoPlayer

# Initial ratings
players = {
    "alice": {"elo": 1500, "games": 0, "glicko": GlickoPlayer()},
    "bob": {"elo": 1500, "games": 0, "glicko": GlickoPlayer()}
}

def expected_score(r1, r2):
    return 1 / (1 + 10 ** ((r2 - r1) / 400))

def fixed_k_elo(winner, loser, k=32):
    r1, r2 = players[winner]["elo"], players[loser]["elo"]
    e1 = expected_score(r1, r2)
    players[winner]["elo"] = round(r1 + k * (1 - e1))
    players[loser]["elo"] = round(r2 - k * (1 - e1))

def dynamic_k_elo(winner, loser):
    def get_k(player):
        rating = players[player]["elo"]
        games = players[player]["games"]
        return 40 if games < 30 else 10 if rating >= 2400 else 20

    k = get_k(winner)
    r1, r2 = players[winner]["elo"], players[loser]["elo"]
    e1 = expected_score(r1, r2)
    players[winner]["elo"] = round(r1 + k * (1 - e1))
    players[loser]["elo"] = round(r2 - k * (1 - e1))

def glicko_duel(winner, loser):
    wp = players[winner]["glicko"]
    lp = players[loser]["glicko"]
    wp.update_player([lp.rating], [lp.rd], [1])
    lp.update_player([wp.rating], [wp.rd], [0])

def display():
    for name, data in players.items():
        print(f"{name.title()}: Elo = {data['elo']}, Glicko = {data['glicko'].rating:.1f} ± {data['glicko'].rd:.1f}")

# Main interaction loop
while True:
    method = input("Choose method [fix, var, gli]: ").strip().lower()
    result = input("Who won? [alice, bob, tie]: ").strip().lower()

    if result == "tie":
        print("Tie not supported in this demo.")
        continue
    elif result not in players:
        print("Invalid result.")
        continue

    winner = result
    loser = "bob" if winner == "alice" else "alice"

    players["alice"]["games"] += 1
    players["bob"]["games"] += 1

    if method == "fix":
        fixed_k_elo(winner, loser)
    elif method == "var":
        dynamic_k_elo(winner, loser)
    elif method == "gli":
        glicko_duel(winner, loser)
    else:
        print("Unknown method.")
        continue

    display()
