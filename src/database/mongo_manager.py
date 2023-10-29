from pymongo import ASCENDING, MongoClient

from src import constants


class MongoManager:
    client: MongoClient = None
    users = None
    films = None
    actors = None
    statistic = None

    def connect(self) -> None:
        self.client = MongoClient(constants.MONGO_URL)
        database = self.client[constants.MONGO_DATABASE]

        self.users = database[constants.MONGO_USERS_COLLECTION]
        self.films = database[constants.MONGO_FILMS_COLLECTION]
        self.actors = database[constants.MONGO_ACTORS_COLLECTION]
        self.statistic = database[constants.MONGO_STATISTIC_COLLECTION]

        self.films.create_index([("artists.id", ASCENDING)])
        self.films.create_index([("id", ASCENDING)], unique=True)

        self.statistic.create_index([("username", ASCENDING)])
        self.statistic.create_index(["datetime"])
        self.statistic.create_index(["question_type"])
        self.statistic.create_index(["film_id"])

    def close(self) -> None:
        self.client.close()
