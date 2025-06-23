from .game import Game
from discord import User


class SnakeTacToe(Game):

    def __init__(self, players: tuple[User], db) -> None:
        super().__init__(players, db)

        self.board: list[list[str]] = [["-", "-", "-"], ["-", "-", "-"], ["-", "-", "-"]]
        self.age: list[list[int | None]] = [[None, None, None], [None, None, None], [None, None, None]]
    
    def commands(self, sender: User, message: str) -> str:
        parts = message.split()
        command = parts[0].lower()
        if self.currentPlayer != sender:
            match command:
                case "resign":
                    self.gameOver = True
                    self.winner = self.currentPlayer
                    self.currentTurn += 1
                    loser = self.currentPlayer
                    if hasattr(self, "db") and self.db is not None:
                         self.db.updateElo(
                            game="snaketactoe",
                            winnerId=self.winner.id,
                            loserId=loser.id,
                            isTie=False
                        )
                    return self.displayFinish()
                case _:
                    return ""
        else:
            match command:
                case "resign":
                    self.gameOver = True
                    loser = self.currentPlayer
                    self.currentTurn += 1
                    self.winner = self.currentPlayer
                    if hasattr(self, "db") and self.db is not None:
                         self.db.updateElo(
                            game="snaketactoe",
                            winnerId=self.winner.id,
                            loserId=loser.id,
                            isTie=False
                        )
                    return self.displayFinish()
                case "place":
                    if len(parts) != 2:
                        return "Invalid command!"
                    invalid = self.placeTicker(parts[1])
                    if invalid:
                        return "Invalid position!"
                    self.checkWin()
                    if self.gameOver:
                        return self.displayFinish()
                    self.currentTurn += 1
                    return self.displayInfo()
            
    def placeTicker(self, place: str) -> bool:
        if len(place) != 2:
            return True
        cols = {"a": 0, "b": 1, "c": 2}
        x = cols.get(place[0].lower())
        if x is None:
            return True
        try:
            y = int(place[1]) - 1
        except ValueError:
            return True
        if y not in range(3):
            return True
        if self.board[y][x] != "-":
            return True
        player = "O" if self.currentTurn % 2 else "X"
        self.board[y][x] = player
        for ay in range(len(self.board)):
            for ax in range(len(self.board[0])):
                if self.age[ay][ax] is not None and self.board[ay][ax] == player:
                    self.age[ay][ax] += 1
                    if self.age[ay][ax] == 4:
                        self.board[ay][ax] = "-"
                        self.age[ay][ax] = None
        self.age[y][x] = 1
        return False

    def showBoard(self) -> str:
        eloX = "N/A"
        eloO = "N/A"
        if hasattr(self, "db") and self.db is not None:
            eloX = self.db.getUserElo(self.players[0].id, "snaketactoe") or "N/A"
            eloO = self.db.getUserElo(self.players[1].id, "snaketactoe") or "N/A"
        header = (f"{self.players[0].mention} (X) [{eloX}] vs "
                  f"{self.players[1].mention} (O) [{eloO}]\n")
        board = ["   A     B     C  "]
        
        for row in range(3):
            age_line_parts = []
            for col in range(3):
                age_val = self.age[row][col]
                if age_val is None:
                    age_line_parts.append("     ")
                else:
                    age_str = f"    {age_val}"
                    age_line_parts.append(age_str)
            age_line =" " + "|".join(age_line_parts)
            board.append(age_line)
            piece_line = str(row + 1) + "  " + "  |  ".join(self.board[row]) + "  "
            board.append(piece_line)
            if row < 2:
                board.append(" _____|_____|_____")
            else:
                board.append("      |     |      ")
                
        return header + "```\n" + "\n".join(board) + "\n```"


    
    def checkWin(self) -> None:
        symbols = ['X', 'O']
        for i, player in enumerate(symbols):
            lines = (
                self.board +
                [list(col) for col in zip(*self.board)] +
                [[self.board[i][i] for i in range(3)]] +
                [[self.board[i][2 - i] for i in range(3)]]
            )
            if any(all(cell == player for cell in line) for line in lines):
                self.gameOver = True
                self.winner = self.players[i]
                loser = self.players[i - 1]

                if hasattr(self, "db") and self.db is not None:
                    self.db.updateElo(
                        game="snaketactoe",
                        winnerId=self.winner.id,
                        loserId=loser.id,
                        isTie=False
                    )