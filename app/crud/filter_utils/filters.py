from typing import Type, Any, Dict
from sqlalchemy import and_, or_, not_
from app.crud.filter_utils.filter_operator import Operator, OPERATORS


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
        if isinstance(filters, dict):
            if len(filters) == 0:
                return True
            if len(filters) == 1:
                key, value = list(filters.items())[0]
                return self.handle_field_filter(key, value)
            else:
                and_conditions = [self.create_filter_clause({k: v}) for k, v in filters.items()]
                and_conditions = [cond for cond in and_conditions if cond is not None]
                return and_(*and_conditions) if and_conditions else None
        elif isinstance(filters, list):
            if len(filters) == 0:
                return True
            and_conditions = [self.create_filter_clause(f) for f in filters]
            and_conditions = [cond for cond in and_conditions if cond is not None]
            return and_(*and_conditions) if and_conditions else None
        else:
            return None