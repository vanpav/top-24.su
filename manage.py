# -*- coding: utf-8 -*-
import os

from flask.ext.script import Manager, Server, Command, prompt
from flask.ext.collect import Collect
from flask.ext.security.utils import encrypt_password

from app import app

class Setup(Command):

    def _create_role(self, name, description=None):
        return app.user_datastore.find_or_create_role(name=name, description=description)

    def _create_super_user(self):
        admin_role = self._create_role('admin', 'Admin role')

        username = prompt('Admin username')
        email = prompt('Admin email')
        while app.user_datastore.find_user(email=email) is not None:
            print 'Admin with email %s already exists' % email
            email = prompt('Admin email')
        password = prompt('Admin password')
        app.user_datastore.create_user(name=username,
                                       email=email,
                                       password=encrypt_password(password),
                                       roles=[admin_role])

    def run(self):
        self._create_super_user()


class ClearDB(Command):
    def run(self):
        from modules.catalog.models import Offer, Vendor, Category
        from modules.dispatcher.models import Dispatcher
        from modules.apishop.models import ApishopOffer, ApishopCategory, ApishopConfig
        from utils.filesys import delete_file_by_path, check_file_exists

        for model in (Offer, Vendor, Category, Dispatcher,
                      ApishopConfig, ApishopOffer, ApishopCategory):
            model.objects.delete()

        import shutil
        if check_file_exists('media', relative=True):
            path = os.path.join(app.config['BASE_DIR'], 'media')
            shutil.rmtree(path)

        if check_file_exists('data', relative=True):
            path = os.path.join(app.config['BASE_DIR'], 'data')
            shutil.rmtree(path)

        print 'Database cleared'

manager = Manager(app)
manager.add_command('server', Server(
    use_reloader = True,
    use_debugger = True
))
manager.add_command('setup', Setup())
manager.add_command('cleardb', ClearDB())

collect = Collect()
collect.init_app(app)
collect.init_script(manager)

if __name__ == '__main__':
    manager.run()

