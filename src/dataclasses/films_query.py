from dataclasses import dataclass
from typing import List, Optional

from fastapi import Query

from src.utils.common import escape_query
from src.utils.film import production_to_query


@dataclass
class FilmsQuery:
    query: Optional[str] = Query(None)
    start_year: Optional[int] = Query(None)
    end_year: Optional[int] = Query(None)
    movie_types: Optional[List[str]] = Query(None)
    top_lists: Optional[List[str]] = Query(None)
    production: Optional[List[str]] = Query(None)

    def is_empty(self) -> bool:
        return self.query == "" and not self.__have_field()

    def __have_field(self) -> bool:
        for field in [self.start_year, self.end_year, self.movie_types, self.top_lists, self.production]:
            if field is not None:
                return True

        return False

    def to_query(self) -> Optional[dict]:
        if self.query is None and not self.__have_field():
            return None

        and_conditions = []

        if self.query:
            and_conditions.append({"name": {"$regex": escape_query(self.query), "$options": "i"}})

        if self.start_year is not None:
            and_conditions.append({"year": {"$gte": self.start_year}})

        if self.end_year is not None:
            and_conditions.append({"year": {"$gt": 0, "$lte": self.end_year}})

        if self.movie_types is not None:
            and_conditions.append({"type": {"$in": self.movie_types}})

        if self.top_lists is not None:
            and_conditions.append({"tops": {"$in": self.top_lists}})

        if self.production is not None:
            and_conditions.append({"$or": [production_to_query(production) for production in self.production]})

        if not and_conditions:
            return {}

        query = {"$and": and_conditions}
        return query
