import os

_allowed_extensions = [
    ".pdf",  # PDF 文件
    ".doc",  # Microsoft Word 文档
    ".docx",  # Microsoft Word 文档 (新版)
    ".xls",  # Microsoft Excel 表格
    ".xlsx",  # Microsoft Excel 表格 (新版)
    ".ppt",  # Microsoft PowerPoint 演示文稿
    ".pptx",  # Microsoft PowerPoint 演示文稿 (新版)
    ".txt",  # 文本文件
    ".csv",  # 逗号分隔值文件
    ".rtf",  # 富文本文件
    ".odt",  # OpenDocument 文本
    ".ods",  # OpenDocument 电子表格
    ".odp",  # OpenDocument 演示文稿
    ".epub",  # 电子书格式
    ".md",  # Markdown 文档
    ".tex"  # LaTeX 文件
]
DOWNLOAD_URL_EXPIRY = int(os.getenv("DOWNLOAD_URL_EXPIRY", 3600))
minio_endpoint = os.getenv('MINIO_ENDPOINT', 'localhost:9000')

access_key = os.getenv('MINIO_ACCESS_KEY')
secret_key = os.getenv('MINIO_SECRET_KEY')

minio_region = os.getenv('MINIO_REGION', 'cn-beijing-1')

bucket_name = os.getenv("MINIO_BUCKET_NAME", "file-storage")
