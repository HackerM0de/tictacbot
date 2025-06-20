from abc import ABC, abstractmethod
from discord import User
from random import shuffle


class Game(ABC):

    players: list[User] = []
    winner: User | None = None
    gameOver: bool = False
    currentTurn: int = 0

    def __init__(self, players: tuple[User]) -> None:
        [self.players.append(p) for p in players]
        shuffle(self.players)

    @property
    def currentPlayer(self) -> User:
        return self.players[self.currentTurn % len(self.players)]

    @abstractmethod
    def commands(self, sender: User, message: str) -> str:
        pass

    @abstractmethod
    def showBoard(self):
        pass

    def displayInfo(self, customInfo: str | None=None) -> str:
        info = f"{self.currentPlayer.mention}'s turn!\n\n"
        if customInfo:
            info = customInfo + " " + info
        return info + self.showBoard()
    
    def displayFinish(self, customInfo: str | None=None) -> str:
        if not self.winner:
            info = f"It is a tie!\n\n"
        else:
            info =  f"{self.winner.mention} wins!\n\n"
        if customInfo:
            info = customInfo + " " + info
        return info + self.showBoard()