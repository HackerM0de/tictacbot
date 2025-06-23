from .game import Game
from discord import User

class Reversi(Game):
    
    def __init__(self, players: tuple[User], db) -> None:
        super().__init__(players, db)
        self.board: list[list[str]] = [["-" for _ in range(8)] for _ in range(8)]
        self.board[3][3] = "O"
        self.board[3][4] = "X"
        self.board[4][3] = "X"
        self.board[4][4] = "O"

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
                            game="reversi",
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
                            game="reversi",
                            winnerId=self.winner.id,
                            loserId=loser.id,
                            isTie=False
                        )
                    return self.displayFinish()
                case "place":
                    invalid = self.placeTicker(parts[1])
                    if invalid:
                        return "Invalid position!"
                    _, _, spacesLeft = self.countPieces()
                    if spacesLeft == 0:
                        self.checkWin()
                        return self.displayFinish()
                    self.currentTurn += 1
                    if not self.hasAnyValidMove():
                        message = f"{self.currentPlayer.mention} has no moves!"
                        self.currentTurn += 1
                        if not self.hasAnyValidMove():
                            message = f"No valid moves left!"
                            self.checkWin()
                            return self.displayFinish(message)
                        return self.displayInfo(message)
                    return self.displayInfo()
                
    def showBoard(self) -> str:
        if hasattr(self, "db") and self.db is not None:
            eloX = self.db.getUserElo(self.players[0].id, "reversi") or "N/A"
            eloO = self.db.getUserElo(self.players[1].id, "reversi") or "N/A"
            header = (f"{self.players[0].mention} (X) [{eloX}] vs "
                    f"{self.players[1].mention} (O) [{eloO}]\n")
        else:
            header = (f"{self.players[0].mention} (X) vs "
                    f"{self.players[1].mention} (O)\n")
        board = ["    A   B   C   D   E   F   G   H"]
        for i, row in enumerate(self.board):
            line = f"{i+1} | " + " | ".join(row) + " |"
            board.append("  +---+---+---+---+---+---+---+---+")
            board.append(line)
        board.append("  +---+---+---+---+---+---+---+---+")
        xCount, oCount=(sum(
            cell == c for row in self.board for cell in row
            ) for c in "XO")
        footer = f"X: {xCount} O: {oCount}"
        return header + "```\n" + "\n".join(board) + "\n" + footer + "\n```"

    def placeTicker(self, place: str) -> bool:
        if len(place) != 2:
            return True
        cols = {c: i for i, c in enumerate("abcdefgh")}
        x = cols.get(place[0].lower())
        try:
            y = int(place[1]) - 1
        except ValueError:
            return True
        if x is None or not (0 <= y < 8) or self.board[y][x] != "-":
            return True
        player = "O" if self.currentTurn % 2 else "X"  
        flips = self.getFlips(player, y, x)
        if not flips:
            return True
        self.board[y][x] = player
        for fy, fx in flips:
            self.board[fy][fx] = player
        return False
    
    def getFlips(self, player: str, y: int, x: int):
        if self.board[y][x] != "-":
            return []

        opponent = "O" if player == "X" else "X"
        directions = [(-1, -1), (-1, 0), (-1, 1),
                    (0, -1),          (0, 1),
                    (1, -1),  (1, 0),  (1, 1)]
        flips = []
        for dy, dx in directions:
            ny, nx = y + dy, x + dx
            tempFlips = []
            while 0 <= ny < 8 and 0 <= nx < 8 and self.board[ny][nx] == opponent:
                tempFlips.append((ny, nx))
                ny += dy
                nx += dx
            if 0 <= ny < 8 and 0 <= nx < 8 and self.board[ny][nx] == player:
                flips.extend(tempFlips)
        return flips

    def countPieces(self) -> tuple[int]:
        return (sum(
            cell == c for row in self.board for cell in row
            ) for c in "XO-")
    
    def hasAnyValidMove(self):
        return any(
            bool(self.getFlips("XO"[self.currentTurn % 2], y, x))
            for y in range(8)
            for x in range(8)
            if self.board[y][x] == "-"
        )

    def checkWin(self):
        xCount, oCount, _ = self.countPieces()
        self.gameOver = True
        if xCount > oCount:
            self.winner = self.players[0]
            loser = self.players[1]
            isTie = False
        elif oCount > xCount:
            self.winner = self.players[1]
            loser = self.players[0]
            isTie = False
        else:
            self.winner = None
            loser = None
            isTie = True

        if hasattr(self, "db") and self.db is not None:
            if isTie:
                self.db.updateElo(
                    game="reversi",
                    winnerId=self.players[0].id,
                    loserId=self.players[1].id,
                    isTie=True
                )
            else:
                self.db.updateElo(
                    game="reversi",
                    winnerId=self.winner.id,
                    loserId=loser.id,
                    isTie=False
                )