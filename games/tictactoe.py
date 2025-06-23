from games.game import Game
from discord import User


class TicTacToe(Game):

    def __init__(self, players: tuple[User]) -> None:
        super(self.__class__, self).__init__(players)

        self.board: list[list[str]] = [["-", "-", "-"], ["-", "-", "-"], ["-", "-", "-"]]
    
    def commands(self, sender: User, message: str) -> str:
        parts = message.split()
        command = parts[0].lower()
        if self.currentPlayer != sender:
            match command:
                case "resign":
                    self.gameOver = True
                    self.winner = self.currentPlayer
                    return self.displayFinish()
                case _:
                    return ""
        else:
            match command:
                case "resign":
                    self.gameOver = True
                    self.currentTurn += 1
                    self.winner = self.currentPlayer
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
        self.board[y][x] = "O" if self.currentTurn % 2 else "X"
        return False

    def showBoard(self) -> None:
        header = f"{self.players[0].mention} (X) vs {self.players[1].mention} (O)\n"
        board = ["   A     B     C  "]
        for row in range(3):
            board.append("      |     |     ")
            board.append(f"{row+1}  { '  |  '.join(self.board[row])}  ")
            board.append(" _____|_____|_____" if row < 2 else "      |     |      ")
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
                return

        if all(cell != '-' for row in self.board for cell in row):
            self.gameOver = True
            self.winner = None