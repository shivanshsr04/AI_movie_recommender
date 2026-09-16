import hashlib
import sqlite3
from utils import auth


def test_salted_hashes_and_legacy_upgrade(tmp_path, monkeypatch):
    monkeypatch.setattr(auth, 'DATABASE_FILE', str(tmp_path / 'users.db'))
    assert auth.make_hashes('correct password') != auth.make_hashes('correct password')
    assert auth.add_user('person', 'correct password')[0]
    assert auth.login_user('person', 'correct password')[0]
    assert not auth.login_user('person', 'incorrect')[0]
    assert not auth.add_user('person', 'another password')[0]
    with sqlite3.connect(auth.DATABASE_FILE) as conn:
        conn.execute('UPDATE userstable SET password=? WHERE username=?',
                     (hashlib.sha256(b'legacy password').hexdigest(), 'person'))
    assert auth.login_user('person', 'legacy password')[0]
    with sqlite3.connect(auth.DATABASE_FILE) as conn:
        assert conn.execute('SELECT password FROM userstable').fetchone()[0].startswith('pbkdf2_sha256$')
