import hashlib


def sanitize_filename(filename):
    """
    对文件名进行处理，确保文件名安全。
    去除空格，保留字母、数字、下划线、点号、破折号和中文字符。
    """
    # 替换空格为下划线
    sanitized = filename.replace(" ", "_")

    # 保留字母、数字、下划线、点号、破折号和中文字符
    allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.-')
    sanitized = ''.join(c for c in sanitized if c in allowed_chars or '\u4e00' <= c <= '\u9fff')

    return sanitized


def generate_hash(content: str) -> str:
    """
    生成内容的SHA-256哈希值。
    """
    hash_object = hashlib.sha256(content.encode('utf-8'))
    return hash_object.hexdigest()