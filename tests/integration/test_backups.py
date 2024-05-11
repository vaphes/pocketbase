import datetime
from uuid import uuid4

from pocketbase import PocketBase


class TestBackupsService:
    def test_create_list_download_and_delete(self, client: PocketBase, state):
        state.backup_name = "%s.zip" % (uuid4().hex[:16],)
        client.backups.create(state.backup_name)

        try:
            # Find new backup in list of all backups
            for backup in client.backups.get_full_list():
                if backup.key == state.backup_name:
                    state.backup = backup
                    assert isinstance(backup.modified, datetime.datetime)
                    assert backup.size > 0
                    break
            else:
                self.fail("Backup %s not found in list of all backups" % (state.backup_name,))

            # Download the backup
            data = client.backups.download(state.backup_name)
            assert isinstance(data, bytes)
            assert len(data) == state.backup.size
        finally:
            # Cleanup
            client.backups.delete(state.backup_name)

            # Check that it was deleted
            for backup in client.backups.get_full_list():
                if backup.key == state.backup_name:
                    self.fail("Backup %s still found in list of all backups" % (state.backup_name,))
                    break

