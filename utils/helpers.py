import re

pattern = re.compile('\d+$')


async def get_page(path: str) -> str:
    """
    We can`t pass full page to callback because it will be to long and will raise an error
    So, we have to get page number from path and passed it to url
    If path doesnt have number at the end - returns '1'
    :param path: Example 'http://188.225.43.69/main/posts_public/?page=2'
    """
    if path:
        result = pattern.findall(path)
        if result:
            return result[-1]
        return '1'
