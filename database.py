from pymongo import MongoClient
import glicko2

import time


class DataBase:
    DEFAULT_RATING = 1000
    DEFAULT_RD = 250
    DEFAULT_VOLATILITY = 0.06
    
    def __init__(self, uri: str, dbName="gameratings"):
        self.client = MongoClient(uri)
        self.db = self.client[dbName]
        self.users = self.db["users"]

    def getUserRatings(self, userId: int) -> dict:
        user = self.users.find_one({"_id": userId})
        if not user:
            return {}
        return user.get("ratings", {})
    
    def initializeUserGame(self, userId: int, game: str) -> None:
        user = self.users.find_one({"_id": userId})
        if not user or game not in user.get("ratings", {}):
            self.users.update_one(
                {"_id": userId},
                {"$set": {
                    f"ratings.{game}": {
                        "rating": self.DEFAULT_RATING,
                        "rd": self.DEFAULT_RD,
                        "volatility": self.DEFAULT_VOLATILITY,
                        "lastUpdated": int(time.time())
                    }
                }},
                upsert=True
            )

    def updateRating(self, userId: int, game: str, rating: int, rd: int=None, volatility: float=None) -> None:
        rating = int(rating)
        rd = int(rd)
        updateData = {
            f"ratings.{game}.rating": rating,
            f"ratings.{game}.lastUpdated": int(time.time())
        }
        if rd is not None:
            updateData[f"ratings.{game}.rd"] = rd
        if volatility is not None:
            updateData[f"ratings.{game}.volatility"] = volatility
        
        self.users.update_one(
            {"_id": userId},
            {"$set": updateData},
            upsert=True
        )
    
    def getLeaderboard(self, game: str, startingPos: int=1, numberOfUsers: int=10) -> list[tuple[str, int]]:
        cursor = self.users.find(
            {f"ratings.{game}": {"$exists": True}},
            {"ratings." + game + ".rating": 1}
        ).sort([(f"ratings.{game}.rating", -1)]).skip(startingPos - 1).limit(numberOfUsers)

        leaderboard = []
        for doc in cursor:
            rating_data = doc.get("ratings", {}).get(game)
            if rating_data is None:
                continue 
            rating = rating_data.get("rating")
            leaderboard.append((doc["_id"], rating))
        return leaderboard
    
    def getUserElo(self, userId: int, game: str) -> int | None:
        userData = self.getUserRatings(userId)
        gameData = userData.get(game)
        if gameData and "rating" in gameData:
            return gameData["rating"]
        return None
    
    def getUserGlicko(self, userId: int, game: str):
        self.initializeUserGame(userId, game)
        allRatings = self.getUserRatings(userId)
        gameRatings = allRatings.get(game, {})
        return {
            "rating": gameRatings.get("rating"),
            "rd": gameRatings.get("rd"),
            "volatility": gameRatings.get("volatility")
        }
    
    def updateElo(self, winnerId: int, loserId: int, game: str, isTie: bool=False) -> None:
        winnerData = self.getUserGlicko(winnerId, game)
        loserData = self.getUserGlicko(loserId, game)

        winner = glicko2.Player(
            rating=winnerData["rating"],
            rd=winnerData["rd"],
            vol=winnerData["volatility"]
        )
        loser = glicko2.Player(
            rating=loserData["rating"],
            rd=loserData["rd"],
            vol=loserData["volatility"]
        )

        if isTie:
            winner.update_player([loser.getRating()], [loser.getRd()], [0.5])
            loser.update_player([winner.getRating()], [winner.getRd()], [0.5])
        else:
            winner.update_player([loser.getRating()], [loser.getRd()], [1])
            loser.update_player([winner.getRating()], [winner.getRd()], [0])

        self.updateRating(
            winnerId,
            game,
            winner.rating,
            winner.rd,
            winner.vol
        )
        self.updateRating(
            loserId,
            game,
            loser.rating,
            loser.rd,
            loser.vol
        )