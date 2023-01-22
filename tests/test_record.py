from .connection import get_client_connection
from pocketbase.utils import ClientResponseError
from pocketbase.client import FileUpload
import httpx
from random import randbytes

from uuid import uuid4
import pytest


def test_crud():
    client = get_client_connection(logged_in_as_master_admin=True)

    srv = client.collections
    # create collection
    coll = srv.create(
        {
            "name": uuid4().hex,
            "type": "base",
            "schema": [
                {
                    "name": "title",
                    "type": "text",
                    "required": True,
                },
                {
                    "name": "image",
                    "type": "file",
                    "required": True,
                    "options": {
                        "maxSelect": 3,
                        "maxSize": 5242880,
                        "mimeTypes": [
                            "application/octet-stream",
                            "text/plain",
                        ],
                    },
                },
            ],
        }
    )

    srv = client.collection(coll.id)
    # create record
    bname = uuid4().hex
    bcontent = randbytes(1024)
    record = srv.create(
        {
            "title": uuid4().hex,
            "image": FileUpload(
                ("a.txt", b"a.txt CONTENT", "text/plain"),
                (bname + ".txt", bcontent, "application/octet-stream"),
                ("c.txt", b"c.txt CONTENT", "text/plain"),
            ),
        }
    )
    # update record

    # get back record
    get_record = srv.get_one(record.id)

    # find the bname actual file name
    assert record.image == get_record.image
    for fn in get_record.image:
        if fn.startswith(bname):
            break
    assert fn.startswith(bname)
    srv.update(record.id, {"image": [fn]})

    # retrieve back the file bname
    r = httpx.get(srv.get_file_url(get_record, fn))
    assert r.status_code == 200
    assert r.content == bcontent

    # delete record
    srv.delete(record.id)
    with pytest.raises(ClientResponseError) as exc:
        srv.get_one(record.id)
    assert exc.value.status == 404


def test_crud_exceptions():
    client = get_client_connection(logged_in_as_master_admin=True)
    srv = client.collections
    with pytest.raises(ClientResponseError) as exc:
        srv.delete(uuid4().hex, uuid4().hex)
    assert exc.value.status == 404

    with pytest.raises(ClientResponseError) as exc:
        srv.get_one(uuid4().hex)
    assert exc.value.status == 404
