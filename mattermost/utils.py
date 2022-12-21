from requests.api import delete, get, head, options, patch, post, put


class FakeResponse:
    # def __init__(self, e):
    #     self.error = e

    @property
    def headers(self):
        return {}

    def json(self):
        # raise self.error
        return {}


def request_wrapper(func, headers: dict = {}, timeout: int = None):
    def wrapper(*args, **kwargs):
        if headers:
            kwargs["headers"] = headers
        if timeout:
            kwargs["timeout"] = timeout
        try:
            resp = func(*args, **kwargs)
        except Exception as e:
            # TODO 自定义异常
            raise e
        return resp
    return wrapper


class InnerRequest:
    TIME_OUT = 3

    def __init__(self, headers: dict = {}, timeout=TIME_OUT):
        self.delete = request_wrapper(delete, headers=headers, timeout=timeout)
        self.get = request_wrapper(get, headers=headers, timeout=timeout)
        self.head = request_wrapper(head, headers=headers, timeout=timeout)
        self.options = request_wrapper(options, headers=headers, timeout=timeout)
        self.patch = request_wrapper(patch, headers=headers, timeout=timeout)
        self.post = request_wrapper(post, headers=headers, timeout=timeout)
        self.put = request_wrapper(put, headers=headers, timeout=timeout)
