from app.serves.file_processing.tokenizer_filter import TokenizerFilter

# Example usage
processor = TokenizerFilter()
documents = ["文档1内容", "文档2内容", "文档3内容", "文档1内容的副本"]
filtered_documents = processor.filter_similar_documents(documents)
print(filtered_documents)
