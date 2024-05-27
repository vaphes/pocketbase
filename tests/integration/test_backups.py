import datetime
import errno
import http
import time
from typing import Iterator
from uuid import uuid4

import pytest

from pocketbase import PocketBase
from pocketbase.models import FileUpload
from pocketbase.models.collection import Collection
from pocketbase.utils import ClientResponseError

def cleanup_backup(client: PocketBase, backup_name: str):
    # Cleanup
    print("Cleaning up uploaded backup %s" % (backup_name,))
    client.backups.delete(backup_name)

    # Check that it was deleted
    for backup in client.backups.get_full_list():
        if backup.key == backup_name:
            pytest.fail("Backup %s still found in list of all backups" % (backup_name,))

@pytest.fixture
def backup_name(client: PocketBase) -> Iterator[str]:
    backup_name = "%s.zip" % (uuid4().hex[:16],)
    client.backups.create(backup_name)
    try:
        yield backup_name
    finally:
        cleanup_backup(client, backup_name)


@pytest.fixture
def target_collection(client: PocketBase) -> Collection:
    collection = client.collections.create(
        {
            "name": uuid4().hex,
            "type": "base",
            "schema": [
                {
                    "name": "title",
                    "type": "text",
                    "required": True,
                    "options": {
                        "min": 10,
                    },
                },
            ],
        }
    )
    try:
        yield collection
    finally:
        client.collections.delete(collection.id)


class TestBackupsService:
    def test_create_list_download_and_delete(self, client: PocketBase, state, backup_name):
        # Find new backup in list of all backups
        for backup in client.backups.get_full_list():
            if backup.key == backup_name:
                state.backup = backup
                assert isinstance(backup.modified, datetime.datetime)
                assert backup.size > 0
                break
        else:
            pytest.fail("Backup %s not found in list of all backups" % (state.backup_name,))

            # Download the backup
        data = client.backups.download(backup_name)
        assert isinstance(data, bytes)
        assert len(data) == state.backup.size

    def test_restore(self, client: PocketBase, state, backup_name, target_collection):
        # Create a record that will be deleted with backup is restored.
        collection = client.collection(target_collection.id)
        state.record = collection.create({"title": "Test record"})
        client.backups.restore(backup_name)
        until = time.time() + 10
        while time.time() < until:  # Wait maximum of 10 seconds
            try:
                collection.get_one(state.record.id)
            except ClientResponseError as e:
                # Restore causes the service to restart. This will cause a connection error.
                # This loop will wait until the service is back up.
                if f"[Errno {errno.ECONNREFUSED}]" in str(e):
                    continue
                # This may also occur if server shuts down in the middle of collection check request.
                if "Server disconnected without sending a response" in str(e):
                    continue
                if e.status == http.HTTPStatus.NOT_FOUND:
                    break
                raise

    def test_upload(self, client: PocketBase, state, backup_name):
        state.downloaded_backup = client.backups.download(backup_name)

        state.new_backup_name = "%s.zip" % (uuid4().hex[:16],)
        upload = FileUpload(state.new_backup_name, state.downloaded_backup, "application/zip")
        client.backups.upload(upload)
        try:
            state.downloaded_new_backup = client.backups.download(state.new_backup_name)
            assert state.downloaded_new_backup == state.downloaded_backup
        finally:
            cleanup_backup(client, state.new_backup_name)
