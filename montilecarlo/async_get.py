import asyncio

from aiohttp import ClientSession


async def afetch(url, sem, pause):
    """Get a url
    Parameters
    ----------
    url: string, URL to get
    sem: asyncio.Semaphore, defines the max concurrent connections
    pause: seconds to pause between requests
    Returns
    -------
    tuple: (URL, contents)
    """
    async with sem:
        async with ClientSession() as session:
            async with session.get(url) as response:
                await asyncio.sleep(pause)
                if response.status != 200:
                    return (response.url, None)
                else:
                    contents = await response.read()
                    return (response.url, contents)


async def get_urls(urls, callback=None, concurrent=5, pause=0):
    """Get contents of urls asyncronously
    Required Parameters
    -------------------
    urls: iterable of URLs
    Optional Parameters
    -------------------
    callback: a function to handle the future returned from afetch
    concurrent: number of concurrent connections (default: 5)
    pause: seconds to pause after getting url, throttle (default: 0)
    Returns
    -------
    list of (URL, contents) tuples
    """
    sem = asyncio.Semaphore(concurrent)
    tasks = []
    for url in urls:
        task = asyncio.ensure_future(afetch(url, sem, pause))
        if callback:
            task.add_done_callback(callback)
        tasks.append(task)
    responses = await asyncio.gather(*tasks)
    return responses


def process_urls(*args, **kwargs):
    """
    Syncronous wrapper for get_urls
    Takes same parameters as get_urls
    """
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(get_urls(*args, **kwargs))

