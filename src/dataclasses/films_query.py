from dataclasses import dataclass
from typing import List, Optional

from fastapi import Query

from src.utils.common import escape_query


@dataclass
class FilmsQuery:
    query: Optional[str] = Query(None)
    start_year: Optional[int] = Query(None)
    end_year: Optional[int] = Query(None)
    movie_types: Optional[List[str]] = Query(None)
    top_lists: Optional[List[str]] = Query(None)
    production: Optional[List[str]] = Query(None)

    def is_empty(self) -> bool:
        return self.query == "" and self.start_year is None and self.end_year is None and self.movie_types is None and self.top_lists is None and self.production is None

    def to_query(self) -> Optional[dict]:
        if self.query is None and self.start_year is None and self.end_year is None and self.movie_types is None and self.top_lists is None and self.production is None:
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
            and_conditions.append({"production": {"$in": self.production}})

        if not and_conditions:
            return {}

        query = {"$and": and_conditions}
        return query