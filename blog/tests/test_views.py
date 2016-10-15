import os
from blog import app
from blog.views import views
from test.support import EnvironmentVarGuard

from flask import url_for
import unittest
import tempfile

class AppTestCase(unittest.TestCase):

    def login(self, username, password):
        return self.test_app.post('/login', 
                            data={username: "username", password: "password"},
                            follow_redirects=True)

    def logout(self):
        return self.test_app.get('/logout', follow_redirects=True)

    def setUp(self):
        self.db_fd, app.app.config['DATABASE'] = tempfile.mkstemp()
        app.app.config['TESTING'] = True
        app.app.config['DEBUG'] = False
        app.app.config['WTF_CSRF_ENABLED'] = False
        app.app.config['SERVER_NAME']="testing"

        self.env = EnvironmentVarGuard()
        self.env.set('ADMIN_PASSWORD', 'password')

        self.app = app.app
        self.app_context = self.app.app_context()
        self.app_context.push()

        with(self.env):
            self.test_app = self.app.test_client()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(app.app.config['DATABASE'])

    def test_error_page(self):
        rv = self.test_app.get('/not_existent', follow_redirects=True)
        self.assertEqual(rv.status_code, 404)

    def test_get_index_empty_db(self):
        rv = self.test_app.get('/')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'No entries have been created yet', rv.data)

    def test_get_login_empty_db(self):
        rv = self.test_app.get('/login', follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Log in', rv.data)

    def test_get_logout_empty_db(self):
        rv = self.test_app.get('/logout', follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Log out', rv.data)

    def test_post_logout_empty_db(self):
        rv = self.test_app.post('/logout', follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Log out', rv.data)

    def test_login(self):
       with self.env:
            rv = self.test_app.post(url_for('login'), data=dict(password="password"),
                           follow_redirects=True)
            print(rv.data)

          # self.assertEqual(rv.status_code, 200)


if __name__ == '__main__':
    unittest.main()