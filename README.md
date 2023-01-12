# PocketBase Python SDK

[![Tests](https://github.com/vaphes/pocketbase/actions/workflows/tests.yml/badge.svg)](https://github.com/vaphes/pocketbase/actions/workflows/tests.yml)

Python client SDK for the <a href="https://pocketbase.io/">PocketBase</a> backend.

This is in early development, and at first is just a translation of <a href="https://github.com/pocketbase/js-sdk">the javascript lib</a> using <a href="https://github.com/encode/httpx/">HTTPX</a>.

---

## Installation

Install PocketBase using pip:

```shell
$ pip install pocketbase
```

## Usage

The rule of thumb here is just to use it as you would <a href="https://github.com/pocketbase/js-sdk">the javascript lib</a>, but in a pythonic way of course!

```python
from pocketbase import PocketBase # Client also works the same

client = PocketBase('http://127.0.0.1:8090')

...

# list and filter "example" collection records
result = client.records.get_list(
    "example", 1, 20, {"filter": 'status = true && created > "2022-08-01 10:00:00"'}
)

# authenticate as regular user
user_data = client.users.auth_via_email("test@example.com", "123456")

# or as admin
admin_data = client.admins.auth_with_password("test@example.com", "123456")

# and much more...
```
> More detailed API docs and copy-paste examples could be found in the [API documentation for each service](https://pocketbase.io/docs/api-authentication). Just remember to 'pythonize it' 🙃.


<p align="center"><i>The PocketBase Python SDK is <a href="https://github.com/vaphes/pocketbase/blob/master/LICENCE.txt">MIT licensed</a> code.</p>