from blog import create_app, database
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell

app = create_app()
manager = Manager(app)
migrate = Migrate(app, database)

def make_shell_context():
    return dict(app=app, database=database)

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
