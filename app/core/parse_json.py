import json
import re


def escape_newlines_in_json_value(json_str):
    # 将值中的换行符转义为 \\n
    in_string = False
    escaped_str = []
    for char in json_str:
        if char == '"':
            in_string = not in_string
        if char == '\n' and in_string:
            escaped_str.append('\\n')
        else:
            escaped_str.append(char)
    return ''.join(escaped_str)


def preprocess_json_string(json_str):
    # 首先转义 JSON 值中的换行符
    json_str = escape_newlines_in_json_value(json_str)

    # 移除键值对之间的多余空白字符（例如换行符、制表符等）
    json_str = re.sub(r'(?<=:|,)\s+', '', json_str)

    return json_str


def parse_json_with_stack(json_str):
    json_str = preprocess_json_string(json_str)

    json_str = json_str.strip()

    if not json_str:
        raise ValueError("EMPTY JSON")

    first_brace_index = json_str.find('{')
    first_bracket_index = json_str.find('[')

    if first_brace_index == -1 and first_bracket_index == -1:
        raise ValueError("Invalid JSON input")

    if first_brace_index != -1 and (first_bracket_index == -1 or first_brace_index < first_bracket_index):
        return parse_object_with_stack(json_str)
    else:
        return parse_array_with_stack(json_str)


def parse_object_with_stack(json_str):
    stack = []
    for i, char in enumerate(json_str):
        if char == '{':
            stack.append(i)
        elif char == '}':
            start_index = stack.pop()
            if not stack:
                data = json_str[start_index:i + 1].strip()
                if not data:
                    raise ValueError("EMPTY JSON")
                return json.loads(data)
    raise ValueError("Invalid JSON input")


def parse_array_with_stack(json_str):
    stack = []
    for i, char in enumerate(json_str):
        if char == '[':
            stack.append(i)
        elif char == ']':
            start_index = stack.pop()
            if not stack:
                data = json_str[start_index:i + 1].strip()
                if not data:
                    raise ValueError("EMPTY JSON")
                return json.loads(data)
    raise ValueError("Invalid JSON input")


if __name__ == '__main__':
    json_str = '{"name": "John",\n "age": 30, "city": "New \\nYork", "address": {"street": "123 Main St", "zip": "10001"}}'
    print(parse_json_with_stack(json_str))

    json_array_str = '[{"name": "John"}, {"name": "Jane"}]'
    print(parse_json_with_stack(json_array_str))
