from typing import Type, Any, Dict

from sqlalchemy import and_, or_, not_
from sqlalchemy.orm import DeclarativeBase

from app.crud.filter_utils.operator import Operator, OPERATORS


class FilterHandler:
    def __init__(self, db_model: Type[DeclarativeBase], disallowed_fields: set = None):
        self.db_model = db_model
        self.disallowed_fields = disallowed_fields or set()
        self.operators: Dict[str, Operator] = OPERATORS

    def add_operator(self, name: str, operator: Operator):
        self.operators[name] = operator

    def handle_field_filter(self, field: str, value: Any):
        if field in self.disallowed_fields:
            raise ValueError(f"Invalid field: {field}. Disallowed fields: {', '.join(self.disallowed_fields)}")

        column = getattr(self.db_model, field)

        if isinstance(value, list):
            conditions = [self.handle_field_filter(field, v) for v in value]
            return and_(*conditions)

        if isinstance(value, dict):
            if len(value) != 1:
                raise ValueError(f"Invalid filter condition. Expected a single key but got: {value}")
            operator, filter_value = list(value.items())[0]
            if operator not in self.operators:
                raise ValueError(f"Unsupported operator: {operator}")
        else:
            operator = "="
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
                    if len(and_conditions) > 1:
                        return and_(*and_conditions)
                    elif len(and_conditions) == 1:
                        return and_conditions[0]
                    else:
                        raise ValueError("Got an empty list for and operator.")
                elif key.lower() == "or":
                    if not isinstance(value, list):
                        raise ValueError(f"Expected a list, but got {type(value)} for value: {value}")
                    or_conditions = [self.create_filter_clause(el) for el in value]
                    if len(or_conditions) > 1:
                        return or_(*or_conditions)
                    elif len(or_conditions) == 1:
                        return or_conditions[0]
                    else:
                        raise ValueError("Got an empty list for or operator.")
                elif key.lower() == "not":
                    if isinstance(value, list):
                        not_conditions = [self.create_filter_clause(el) for el in value]
                        return and_(*[not_(condition) for condition in not_conditions])
                    else:
                        return not_(self.create_filter_clause(value))
            elif len(filters) > 1:
                and_conditions = [self.create_filter_clause({k: v}) for k, v in filters.items()]
                return and_(*and_conditions)
            else:
                raise ValueError("Got an empty dictionary for filters.")
        else:
            raise ValueError(f"Invalid type: Expected a dictionary but got type: {type(filters)}")
