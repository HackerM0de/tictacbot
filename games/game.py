from abc import ABC, abstractmethod
from discord import User
from random import shuffle
from typing import TYPE_CHECKING
from database import DataBase


class Game(ABC):

    def __init__(self, players: tuple[User], db: DataBase | None=None) -> None:
        self.players: list[User] = []
        self.db = db
        self.winner: User | None = None
        self.gameOver: bool = False
        self.currentTurn: int = 0
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