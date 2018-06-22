from urllib.request import urlopen
from functools import wraps
import urllib.error


# Built originally to work in Python2 with urllib2 library
# Not actually functional
def retry(ExceptionToCheck, tries=4, delay=3, backoff=2, logger=None):
    # Retries a function or method
    # Not well tested

    if tries < 0:
        raise ValueError("tries must be 0 or greater")

    if delay <= 0:
        raise ValueError("delay must be greater than 0")

    if backoff <= 1:
        raise ValueError("backoff must be greater than 1")

    def deco_retry(f):
        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except ExceptionToCheck as e:
                    msg = "%s, Retrying in %d seconds  ..." % (str(e), mdelay)
                    if logger:
                        logger.warning(msg)
                    else:
                        print(msg)
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)

        return f_retry
    return deco_retry


@retry(urllib.error.URLError, tries=3, delay=5, backoff=2)
def urlopen_with_retry(url):
    return urllib.urlopen(url)
