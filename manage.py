#!/usr/bin/env python
import os, random
from app import create_app, db
from app.db_models.user import User
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
from flask import g, render_template
from werkzeug.local import LocalProxy


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

def get_current_user():
	users = User.query.all()
	return random.choice(users)

current_user = LocalProxy(get_current_user)

@app.before_first_request
def setup():
	db.drop_all()
	db.create_all()
	User.generate_fake()

	
@app.teardown_appcontext
def teardown(exc = None):
	if exc is None:
		db.session.commit()
	else:
		db.session.rollback()
	db.session.remove()
	g.user = None

@app.context_processor
def template_extras():
	return {'enumerate': enumerate, 'current_user': current_user}


@app.errorhandler(404)
def page_not_found(error):
	return 'This page does not exist', 404

@app.template_filter('capitalize')
def reverse_filter(s):
	return s.capitalize()

@app.route('/users')
def users():
	users = User.query.all()
	return render_template('users.html', users = [current_user])


def make_shell_context():
    return dict(app=app, db=db, User=User)

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == '__main__':
    manager.run()
