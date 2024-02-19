"""

Utility functions for output APIs

"""

def check_outfile_sanity(im: tuple, ip: tuple, method: str, props: tuple) -> bool:
    if method not in im:
        return False
    for p in props:
        if p not in ip:
            return False
    return True

