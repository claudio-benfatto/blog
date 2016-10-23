import os
import blog
from blog import app
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
        
        APP_DIR = os.path.dirname(os.path.realpath(__file__))

        config =dict(
            SERVER_NAME = "localhost",
            SQLALCHEMY_DATABASE_URI='sqlite:///%s' % os.path.join(APP_DIR, 'test_blog.db'),
            SQLALCHEMY_COMMIT_ON_TEARDOWN=False,
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            TESTING=True,
            DEBUG=False,
            SECRET_KEY='shhh, secret!',
            USERNAME='admin',
            PASSWORD='default',
            APP_ADMIN_PASSWORD='password'
        )

        blog.config_app(config)

        self.env = EnvironmentVarGuard()
        self.env.set('ADMIN_PASSWORD', 'password')

        app_context = app.app_context()
        app_context.push()

        with(self.env):
            self.test_app = app.test_client()

    def tearDown(self):
        pass

    def test_error_page(self):
        rv = self.test_app.get('/not_existent', follow_redirects=True)
        self.assertEqual(rv.status_code, 404)

    def test_get_index_empty_db(self):
        rv = self.test_app.get('/')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'No entries have been created yet', rv.data)

    def test_get_login_empty_db(self):
        print(url_for('login'))
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
            self.assertEqual(rv.status_code, 200)


if __name__ == '__main__':
    unittest.main()