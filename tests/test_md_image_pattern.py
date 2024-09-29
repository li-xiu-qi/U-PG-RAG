import re

md_image_pattern = re.compile(r'\[([^\]]+)\]\(([a-zA-Z0-9:/._~#-]+)?\)')

markdown_text = """
![Alt text](http://example.com/image1.png)
![Another image](https://example.com/image2.jpg)
![Image without URL]()
### test
http://example.com/image1.png
"""

matches = md_image_pattern.findall(markdown_text)

for match in matches:
    print(f"Alt text: {match[0]}, URL: {match[1]}")


# 写一个清除所有图片链接的函数
def remove_image_links(markdown_text: str) -> str:
    return md_image_pattern.sub('', markdown_text)


# 测试看看
cleaned_text = remove_image_links(markdown_text)
print(cleaned_text)

# 发现感叹号没有去除，所以我们需要修改正则表达式
md_image_pattern = re.compile(r'!\[([^\]]+)\]\(([a-zA-Z0-9:/._~#-]+)?\)')
cleaned_text = remove_image_links(markdown_text)
print(cleaned_text)

# 还有一种带有html的图片链接，我们也需要处理
html_image_pattern = re.compile(r'<img\s+[^>]*?src=["\']([^"\']*)["\'][^>]*>')

html_text = """
<img src="http://example.com/image1.png" alt="Alt text">
<img src='https://example.com/image2.jpg' alt='Another image'>
<img src="image.png" alt="Image without URL">
"""


# 写一个清除所有图片链接的函数
def remove_image_links(html_text: str) -> str:
    html_text = html_image_pattern.sub('', html_text)
    return html_text


# 测试看看
cleaned_text = remove_image_links(html_text)
print(cleaned_text)
