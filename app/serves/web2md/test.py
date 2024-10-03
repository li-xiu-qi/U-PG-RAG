from web2md import Web2md

if __name__ == "__main__":
    service = Web2md(convert_to_absolute=True, remove_links=True)

    # Convert HTML content directly
    html_content = """
    <html>
    <body>
    <img src="/path/to/image.jpg" alt="示例图片">
    <img src="/path/to/image2.jpg" alt="aljfkajd">
    <a href="/path/to/page">示例链接</a>
    <a href="/path/to/page2">aljfkajd</a>
    <a href="/path/to/file.pdf">文件链接</a>
    <table>
        <tr>
            <td colspan="2">Cell with colspan</td>
        </tr>
        <tr>
            <td>Cell 1</td>
            <td>Cell 2</td>
        </tr>
    </table>
    </body>
    </html>
    """
    current_url = "https://example.com/some/page.html"
    markdown_content, link_resources = service.convert_html_to_markdown(html_content, current_url)
    print(link_resources)
    print(markdown_content)

    # Fetch and convert HTML content from a URL
    url = "https://example.com/some/page.html"
    markdown_content, link_resources = service.fetch_and_convert(url)
    print(link_resources)
    print(markdown_content)
