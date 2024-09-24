import json
from typing import Any
from typing import Optional, List, Union
from typing import Set
from typing import Type, Dict

from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import and_, or_
from sqlalchemy import not_
from sqlalchemy.orm import class_mapper
from sqlalchemy.orm import relationship
from sqlalchemy.sql import ClauseElement

from datetime import datetime

import pytz
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

from config import ServeConfig

Base = declarative_base()
no_async_engine = create_engine(ServeConfig.NO_ASYNC_DB_URL)

CHINA_TZ = pytz.timezone('Asia/Shanghai')


def get_current_time():
    return datetime.now(CHINA_TZ)


class DBaseModel(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    create_at = Column(DateTime(timezone=True), default=get_current_time)
    update_at = Column(DateTime(timezone=True), default=get_current_time, onupdate=get_current_time)

    @classmethod
    def get_unique_columns(cls):
        return [col.name for col in cls.__table__.columns if col.unique]

    @classmethod
    def get_disallowed_columns(cls) -> Set[str]:
        return set()

    @classmethod
    def get_relationship(cls, exclude_relationships: list = None) -> list:
        if exclude_relationships is None:
            exclude_relationships = ["users"]
        # return [rel.key for rel in class_mapper(cls).relationships if rel.key not in exclude_relationships]
        return [rel.key for rel in class_mapper(cls).relationships]


class Partition(DBaseModel):
    __tablename__ = 'partitions'

    partition_name = Column(String, unique=True, index=True, nullable=False)

    users = relationship("User", back_populates="partition", lazy="select")
    rag_caches = relationship("RAGCache", back_populates="partition", lazy="select")
    files = relationship("File", back_populates="partition", lazy="select")
    markdowns = relationship("Markdown", back_populates="partition", lazy="select")
    documents = relationship("Document", back_populates="partition", lazy="select")
    vectors = relationship("Vector", back_populates="partition", lazy="select")
    conversations = relationship("Conversation", back_populates="partition", lazy="select")
    response_records = relationship("ResponseRecord", back_populates="partition", lazy="select")

    def __repr__(self):
        return f"<Partition(id={self.id}, partition_name='{self.partition_name}')>"


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
    "eq": EqualOperator(),
    "ne": NotEqualOperator(),
    "lt": LessThanOperator(),
    "le": LessThanOrEqualOperator(),
    "gt": GreaterThanOperator(),
    "ge": GreaterThanOrEqualOperator(),
    "in": InOperator(),
    "between": BetweenOperator(),
    "like": LikeOperator(),
    "ilike": ILikeOperator(),
    "exists": ExistsOperator(),
    "not": NotOperator(),
}


class FilterHandler:
    def __init__(self, db_model: Type["DBaseModel"]):
        self.db_model = db_model
        self.disallowed_fields = self.db_model.get_disallowed_columns()
        self.operators: Dict[str, Operator] = OPERATORS

    def add_operator(self, name: str, operator: Operator):
        self.operators[name] = operator

    def handle_field_filter(self, field: str, value: Any):
        if field in self.disallowed_fields:
            raise ValueError(f"Invalid field: {field}. Disallowed fields: {', '.join(self.disallowed_fields)}")

        column = getattr(self.db_model, field)

        if isinstance(value, list):
            conditions = [self.handle_field_filter(field, v) for v in value]
            return and_(*conditions) if conditions else None

        if isinstance(value, dict):
            conditions = []
            for operator, filter_value in value.items():
                if filter_value is not None:
                    if operator not in self.operators:
                        raise ValueError(f"Unsupported operator: {operator}")
                    conditions.append(self.operators[operator].apply(column, filter_value))
            if len(conditions) == 1:
                return conditions[0]
            return and_(*conditions) if conditions else None
        else:
            operator = "eq"
            filter_value = value

        return self.operators[operator].apply(column, filter_value)

    def create_filter_clause(self, filters: Any) -> Any:
        if isinstance(filters, dict):
            if len(filters) == 0:
                return True
            if len(filters) == 1:
                key, value = list(filters.items())[0]
                if key.startswith("$"):
                    if key.lower() not in ["and", "or", "not"]:
                        raise ValueError(f"Invalid filter condition. Expected and, or or not but got: {key}")
                else:
                    return self.handle_field_filter(key, filters[key])

                if key.lower() == "and":
                    if not isinstance(value, list):
                        raise ValueError(f"Expected a list, but got {type(value)} for value: {value}")
                    and_conditions = [self.create_filter_clause(el) for el in value]
                    and_conditions = [cond for cond in and_conditions if cond is not None]
                    if len(and_conditions) > 1:
                        return and_(*and_conditions)
                    elif len(and_conditions) == 1:
                        return and_conditions[0]
                    else:
                        return None
                elif key.lower() == "or":
                    if not isinstance(value, list):
                        raise ValueError(f"Expected a list, but got {type(value)} for value: {value}")
                    or_conditions = [self.create_filter_clause(el) for el in value]
                    or_conditions = [cond for cond in or_conditions if cond is not None]
                    if len(or_conditions) > 1:
                        return or_(*or_conditions)
                    elif len(or_conditions) == 1:
                        return or_conditions[0]
                    else:
                        return None
                elif key.lower() == "not":
                    if isinstance(value, list):
                        not_conditions = [self.create_filter_clause(el) for el in value]
                        not_conditions = [cond for cond in not_conditions if cond is not None]
                        return and_(*[not_(condition) for condition in not_conditions])
                    else:
                        return not_(self.create_filter_clause(value))
            elif len(filters) > 1:
                and_conditions = [self.create_filter_clause({k: v}) for k, v in filters.items()]
                and_conditions = [cond for cond in and_conditions if cond is not None]
                return and_(*and_conditions) if and_conditions else None
            else:
                raise ValueError("Got an empty dictionary for filters.")
        elif isinstance(filters, list):
            if len(filters) == 0:
                return True
            and_conditions = [self.create_filter_clause(f) for f in filters]
            and_conditions = [cond for cond in and_conditions if cond is not None]
            return and_(*and_conditions) if and_conditions else None
        else:
            return None


from typing import Any, Optional, List, Union, Dict
from pydantic import BaseModel, Field


class FilterCondition(BaseModel):
    like: Optional[Any] = None
    ilike: Optional[Any] = None
    in_: Optional[List[Any]] = Field(None, alias='in')
    between: Optional[List[Any]] = None
    exists: Optional[bool] = None
    not_: Optional[Any] = Field(None, alias='not')
    eq: Optional[Any] = Field(None, alias='=')
    ne: Optional[Any] = Field(None, alias='!=')
    lt: Optional[Any] = Field(None, alias='<')
    lte: Optional[Any] = Field(None, alias='<=')
    gt: Optional[Any] = Field(None, alias='>')
    gte: Optional[Any] = Field(None, alias='>=')


class FilterModel(BaseModel):
    filters: Dict[str, FilterCondition]


class ModelRead(BaseModel):
    id: int
    filters: Optional[FilterModel] = None


class ModelReads(BaseModel):
    filters: Optional[FilterModel] = None


def filter_model_to_dict(filter_model: FilterModel) -> Dict[str, Any]:
    return filter_model.model_dump(by_alias=True)


# 示例数据
data = {
    "partition_name": "东北石油大学",
    "id": 8,
    "create_at": "2024-09-24T02:13:07.863979Z",
    "update_at": "2024-09-24T02:13:07.864015Z"
}

# 创建 FilterCondition 实例
filter_conditions = {
    "partition_name": {"like": data["partition_name"]},
    "id": {"in": [data["id"]]},
    "create_at": {"between": [data["create_at"], data["update_at"]]}
}

# 创建 FilterHandler 实例
filter_handler = FilterHandler(Partition)
filters = filter_conditions
filter_clause = filter_handler.create_filter_clause(filters)

print(filter_clause)
