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
}


class FilterHandler:
    def __init__(self, db_model: Type["DBaseModel"]):
        """
        初始化 FilterHandler，设置数据库模型、禁止字段和操作符。
        """
        self.db_model = db_model
        self.disallowed_fields = self.db_model.get_disallowed_columns()
        self.operators: Dict[str, Operator] = OPERATORS

    def add_operator(self, name: str, operator: Operator):
        """
        添加自定义操作符到操作符字典中。
        """
        self.operators[name] = operator

    def handle_field_filter(self, field: str, value: Any):
        """
        处理特定字段和值的过滤逻辑。
        """
        # 检查字段是否被禁止
        if field in self.disallowed_fields:
            raise ValueError(f"无效字段: {field}。禁止字段: {', '.join(self.disallowed_fields)}")

        column = getattr(self.db_model, field)

        # 如果值是字典，处理每个操作符及其对应的值
        if isinstance(value, dict):
            conditions = []
            for operator, filter_value in value.items():
                if filter_value is not None:
                    if operator not in self.operators and operator not in ["and", "or"]:
                        raise ValueError(f"不支持的操作符: {operator}")
                    if operator == "or" and isinstance(filter_value, list):
                        or_conditions = [self.handle_field_filter(field, v) for v in filter_value]
                        conditions.append(or_(*or_conditions))
                    elif operator == "and" and isinstance(filter_value, list):
                        and_conditions = [self.handle_field_filter(field, v) for v in filter_value]
                        conditions.append(and_(*and_conditions))
                    else:
                        conditions.append(self.operators[operator].apply(column, filter_value))
            if len(conditions) == 1:
                return conditions[0]
            return and_(*conditions) if conditions else None
        else:
            # 如果值不是字典，默认使用等于操作符
            operator = "eq"
            filter_value = value

        return self.operators[operator].apply(column, filter_value)

    def create_filter_clause(self, filters: Any) -> Any:
        """
        从提供的过滤器创建 SQLAlchemy 过滤子句。
        """
        stack = [(filters, [])]
        while stack:
            current_filters, conditions = stack.pop()
            if isinstance(current_filters, dict):
                if len(current_filters) == 0:
                    conditions.append(True)
                elif len(current_filters) == 1:
                    key, value = list(current_filters.items())[0]
                    conditions.append(self.handle_field_filter(key, value))
                else:
                    for k, v in current_filters.items():
                        stack.append(({k: v}, conditions))
            elif isinstance(current_filters, list):
                if len(current_filters) == 0:
                    conditions.append(True)
                else:
                    for f in current_filters:
                        stack.append((f, conditions))
            else:
                conditions.append(None)

        and_conditions = [cond for cond in conditions if cond is not None]
        return and_(*and_conditions) if and_conditions else None


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
