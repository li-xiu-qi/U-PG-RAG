import hashlib
import json


def dict_to_json_str(d):
    return json.dumps(d, sort_keys=True)


def hash_dict(json_str):
    sha256_hash = hashlib.sha256()
    sha256_hash.update(json_str.encode())
    return sha256_hash.hexdigest()


def sort_dict_list(dict_list):
    return [dict_to_json_str(message) for message in sorted(dict_list, key=lambda x: json.dumps(x, sort_keys=True))]


def create_sorted_messages_str(messages):
    sorted_messages = sort_dict_list(messages)
    return str(sorted_messages)


def create_hash_key(task: str, messages: list[dict], parameters: dict) -> str:
    sorted_messages_str = create_sorted_messages_str(messages)
    llm_string = dict_to_json_str(parameters)
    return f"{task}-{hash_dict(sorted_messages_str + llm_string)}"