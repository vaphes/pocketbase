# PocketBase Python SDK

[![Tests](https://github.com/vaphes/pocketbase/actions/workflows/tests.yml/badge.svg)](https://github.com/vaphes/pocketbase/actions/workflows/tests.yml)
[![Coverage Status](https://coveralls.io/repos/github/vaphes/pocketbase/badge.svg?branch=master)](https://coveralls.io/github/vaphes/pocketbase?branch=master)

Python client SDK for the <a href="https://pocketbase.io/">PocketBase</a> backend.

This is in early development, and at first is just a translation of <a href="https://github.com/pocketbase/js-sdk">the javascript lib</a> using <a href="https://github.com/encode/httpx/">HTTPX</a>.

---

## Installation

Install PocketBase using PIP:

```shell
python3 -m pip install pocketbase
```

## Usage

The rule of thumb here is just to use it as you would <a href="https://github.com/pocketbase/js-sdk">the javascript lib</a>, but in a pythonic way of course!

```python
from pocketbase import PocketBase  # Client also works the same
from pocketbase.client import FileUpload

client = PocketBase('http://127.0.0.1:8090')

# authenticate as regular user
user_data = client.collection("users").auth_with_password(
    "user@example.com", "0123456789")

# or as admin
admin_data = client.admins.auth_with_password("test@example.com", "0123456789")

# list and filter "example" collection records
result = client.collection("example").get_list(
    1, 20, {"filter": 'status = true && created > "2022-08-01 10:00:00"'})

# create record and upload file to image field
result = client.collection("example").create(
    {
        "status": "true",
        "image": FileUpload(("image.png", open("image.png", "rb"))),
    })

# and much more...
```
> More detailed API docs and copy-paste examples could be found in the [API documentation for each service](https://pocketbase.io/docs/api-authentication). Just remember to 'pythonize it' 🙃.

## Development

These are the requirements for local development:

* Python 3.7+
* Poetry (https://python-poetry.org/)

You can install locally:

```shell
poetry install
```

Or can build and generate a package:

```shell
poetry build
```

But if you are using only PIP, use this command:

```shell
python3 -m pip install -e .
```

## Tests

To execute the tests use this command:

```
poetry run pytest
```

## Sandbox integration testing

A lot of real-world integration test against a sandboxed pocketbase instance will be included in the pytest when the sandbox is running (on 127.0.0.1:8090)
to start the sandbox follow the following steps:
```bash
export TMP_EMAIL_DIR=`mktemp -d`  # Export temp dir used for sendmail sandbox
bash ./tests/integration/pocketbase     # Run the pocketbase sandbox (automatically downloads the latest pocketbase instance)
pytest  # Run test including sandbox API integration tests
```
## License

The PocketBase Python SDK is <a href="https://github.com/vaphes/pocketbase/blob/master/LICENCE.txt">MIT licensed</a> code.
