import os

from fabric.api import cd, env, run, local
from fabric.operations import sudo
from fabric.colors import yellow

from fabric.context_managers import lcd

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

path = lambda *a: os.path.join(PROJECT_ROOT, *a)


env.proj_root = '/var/webapps/mozilla-ignite/'
git_repo = 'https://github.com/rossbruniges/mozilla-ignite.org.git'


def run_manage_cmd(cmd):
    """Run a manage.py command."""
    with cd(env.proj_root):
        run('python manage.py %s' % cmd)


def restart_celeryd():
    sudo('/etc/init.d/celeryd restart')


def restart_apache():
    sudo('/etc/init.d/apache2 restart')


def clone():
    """Create project directory and clone repository."""
    with cd(os.path.dirname(env.proj_root.rstrip('/'))):
        run('git clone --recursive %s' % (git_repo,))


def update(branch):
    """Update project source."""
    with cd(env.proj_root):
        run('git pull origin %s' % (branch,))


def syncdb():
    """Run syncdb."""
    run_manage_cmd('syncdb')


def migrate():
    """Run database migrations."""
    run_manage_cmd('migrate')


def compress():
    """Compress CSS / Javascript."""
    run_manage_cmd('compress_assets')


def new_branch(branch):
    """Checkout a new branch"""
    with cd(env.proj_root):
        run('git checkout -b %s origin/%s' % (branch, branch))
    update(branch)
    syncdb()
    migrate()
    compress()
    restart_apache()
    restart_celeryd()


def submodules():
    with cd(env.proj_root):
        run('git submodule init')
        run('git submodule sync')
        run('git submodule update')

def deploy(branch):
    """Deploy latest code from ``branch``."""
    update(branch)
    syncdb()
    migrate()
    compress()
    submodules()
    restart_apache()
    restart_celeryd()


# Local environment

def test(*args):
    """Run the tests locally takes a list of apps to test as arguments"""
    if args:
        apps = ' '.join(args)
    else:
        apps = '' # 'challenges timeslot webcast awards activity badges events users'
    print yellow('Testing: %s' % apps)
    local('python manage_test.py test %s --settings=settings_test' % apps)


def syncdb_local():
    """Syncronizes the local database"""
    print yellow('Syncing the database')
    with lcd(PROJECT_ROOT):
        local('python manage.py syncdb --noinput')
        local('python manage.py migrate --noinput')


def update_local():
    """Steps to update the local application"""
    syncdb_local()
