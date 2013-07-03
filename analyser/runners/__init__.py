import re
import sys
import os

"""
runner helpers
contains functions for creating runners (like parser runner, updater runner)
"""

def get_available_commands(all_functions, prefix):
    "returns list of commands that starts with prefix"
    available_commands = []
    for function in all_functions:
        match = re.match('^%s([A-z0-9_]+)$' % prefix, function)
        if match:
            command = match.groups()[0]
            available_commands.append(command)
    return available_commands

def print_info(commands, prefix='', get_doc=None):
    "nicely prints  info about functions and their documentation"
    print 'following commands are available:'
    for cmd in commands:
        print ' * ' + cmd
        if get_doc:
            doc = get_doc("%s%s.__doc__" % (prefix, cmd) )
            if doc:
                print '%s%s' % (" "*5, doc)
    if not commands:
        print 'sorry, no commands are available'

def get_command(all_functions, argv, prefix, usage_filename, get_doc=None):
    "get command from user, showing to him info about commands if necessary"
    commands = get_available_commands(all_functions, prefix)
    if len(argv) >= 1:
        command = argv[0]
    else:
        print '\nUSAGE: manage.py %s <COMMAND>\n' % usage_filename
        print_info(commands, prefix, get_doc)
        if not commands:
            exit()
        command = raw_input('Enter command (leave blank to cancel) --> ')
    if command not in commands:
        print "there's not that command!"
        if len(sys.argv) >= 1:
            print_info(commands, prefix ,get_doc)
        return '', []
    print 'executing command: %s' % command
    print '-'*80+'\n'
    return command, argv[1:]


def get_runner(argv):
    "get runners from user, showing to him info about runners if necessary"
    import analyser.settings as settings
    runners_folder = os.path.join(settings.path_to_project, 'analyser','runners')
    files = filter ( lambda d: re.match(r'^[a-z][a-z_-]+.py$',d) , os.listdir( runners_folder ) )
    commands = map ( lambda d: d[:-len('.py')], files)
    if len(argv) >= 1:
        command = argv[0]
    else:
        print '\nUSAGE: manage.py <RUNNER>\n'
        print_info(commands)
        if not commands:
            exit()
        command = raw_input('Enter command (leave blank to cancel) --> ')
    if command not in commands:
        print "there's not that command!"
        if len(sys.argv) >= 2:
            print_info(commands)
        return ''
    print 'choosed runner: %s' % command
    print '-'*80+'\n'
    return command

def get_project_dir(filename):
    project_directory, settings_filename = os.path.split(filename)
    if project_directory == os.curdir or not project_directory:
       project_directory = os.getcwd()
    return os.path.split(project_directory)[0]

def setup_sys_path(settings_mod):
    path_to_project = settings_mod.path_to_project
    paths = [ path_to_project ]
    for path in settings_mod.ADD_TO_PATH:
        paths.append( os.path.join(path_to_project,path) )
    sys.path = paths + sys.path

def setup_django_orm():
    from server.django.core.management import setup_environ
    from server import settings
    setup_environ(settings)
