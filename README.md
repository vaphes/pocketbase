# PocketBase Python SDK

[![Tests](https://github.com/m29h/pocketbase/actions/workflows/tests.yml/badge.svg?branch=master)](https://github.com/m29h/pocketbase/actions/workflows/tests.yml)

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

Current code coverage statistics:  tested against a real pocketbase v0.12.2 instance
```
# pytest --cov=pocketbase  tests/

---------- coverage: platform linux, python 3.10.9-final-0 -----------
Name                                             Stmts   Miss  Cover
--------------------------------------------------------------------
pocketbase/__init__.py                               6      0   100%
pocketbase/client.py                                78      0   100%
pocketbase/models/__init__.py                        7      0   100%
pocketbase/models/admin.py                           9      0   100%
pocketbase/models/collection.py                     38      0   100%
pocketbase/models/external_auth.py                  13      5    62%
pocketbase/models/file_upload.py                    10      0   100%
pocketbase/models/log_request.py                    23      0   100%
pocketbase/models/record.py                         20      0   100%
pocketbase/models/utils/__init__.py                  4      0   100%
pocketbase/models/utils/base_model.py               22      0   100%
pocketbase/models/utils/list_result.py              10      0   100%
pocketbase/models/utils/schema_field.py             11      0   100%
pocketbase/services/__init__.py                      7      0   100%
pocketbase/services/admin_service.py                42      6    86%
pocketbase/services/collection_service.py           12      2    83%
pocketbase/services/log_service.py                  27      0   100%
pocketbase/services/realtime_service.py             88      8    91%
pocketbase/services/record_service.py              104     22    79%
pocketbase/services/settings_service.py             13      2    85%
pocketbase/services/utils/__init__.py                4      0   100%
pocketbase/services/utils/base_crud_service.py      37      0   100%
pocketbase/services/utils/base_service.py            7      0   100%
pocketbase/services/utils/crud_service.py           19      0   100%
pocketbase/services/utils/sse.py                    75      1    99%
pocketbase/stores/__init__.py                        3      0   100%
pocketbase/stores/base_auth_store.py                23      0   100%
pocketbase/stores/local_auth_store.py               46      0   100%
pocketbase/utils.py                                 26      0   100%
--------------------------------------------------------------------
TOTAL                                              784     46    94%
```

<p align="center"><i>The PocketBase Python SDK is <a href="https://github.com/m29h/pocketbase/blob/master/LICENCE.txt">MIT licensed</a> code.</p>
