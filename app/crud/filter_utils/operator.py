from typing import Any

from sqlalchemy import not_
from sqlalchemy.sql import ClauseElement


class Operator:
    def apply(self, column, value: Any) -> ClauseElement:
        raise NotImplementedError


class EqualOperator(Operator):
    def apply(self, column, value: Any) -> ClauseElement:
        return column == value


class NotEqualOperator(Operator):
    def apply(self, column, value: Any) -> ClauseElement:
        return column != value


class InOperator(Operator):
    def apply(self, column, value: Any) -> ClauseElement:
        return column.in_(value)


class BetweenOperator(Operator):
    def apply(self, column, value: Any) -> ClauseElement:
        low, high = value
        return column.between(low, high)


class LessThanOperator(Operator):
    def apply(self, column, value: Any) -> ClauseElement:
        return column < value


class LessThanOrEqualOperator(Operator):
    def apply(self, column, value: Any) -> ClauseElement:
        return column <= value


class GreaterThanOperator(Operator):
    def apply(self, column, value: Any) -> ClauseElement:
        return column > value


class GreaterThanOrEqualOperator(Operator):
    def apply(self, column, value: Any) -> ClauseElement:
        return column >= value


class LikeOperator(Operator):
    def apply(self, column, value: Any) -> ClauseElement:
        return column.like(value)


class ILikeOperator(Operator):
    def apply(self, column, value: Any) -> ClauseElement:
        return column.ilike(value)


class ExistsOperator(Operator):
    def apply(self, column, value: Any) -> ClauseElement:
        return column.isnot(None) if value else column.is_(None)


class NotOperator(Operator):
    def apply(self, column, value: Any) -> ClauseElement:
        return not_(column == value)


OPERATORS = {
    "=": EqualOperator(),
    "!=": NotEqualOperator(),
    "<": LessThanOperator(),
    "<=": LessThanOrEqualOperator(),
    ">": GreaterThanOperator(),
    ">=": GreaterThanOrEqualOperator(),
    "in": InOperator(),
    "between": BetweenOperator(),
    "like": LikeOperator(),
    "ilike": ILikeOperator(),
    "exists": ExistsOperator(),
    "not": NotOperator(),
}
