"""
Simple "installation" script copying the files into the required folders
"""
import os
import shutil

copy_destinations = [{
    'src': 'conf/web.ini',
    'target': '../conf/',
    'file': 'web.ini',
    'overwrite': False
},{
    'src': 'conf/log.ini',
    'target': '../conf/',
    'file': 'log.ini',
    'overwrite': False
}, {
    'src': 'src/KI4MailWS/wsdl.py',
    'target': '../src/KI4MailWS/',
    'file': 'wsdl.py',
    'overwrite': True
}, {
    'src': 'src/KI4MailWS/handler.py',
    'target': '../src/KI4MailWS/',
    'file': 'handler.py',
    'overwrite': True
}, {
    'src': 'web.py',
    'target': '../',
    'file': 'web.py',
    'overwrite': True
}]

file_name = os.path.basename(__file__)
folder = os.path.realpath(__file__).replace(file_name, '')

for copy in copy_destinations:
    if os.path.isfile(folder + copy['target'] + copy['file']):
        if copy['overwrite']:
            os.remove(folder + copy['target'] + copy['file'])
        else:
            next()

    required_folders = os.path.realpath(os.path.join(folder, copy['target'])).split('/')
    full_path = '/'
    for path_folder in required_folders:
        if path_folder != "":
            full_path = full_path + "/" + path_folder
        if not os.path.isdir(full_path):
            os.mkdir(full_path)

    os.rename(folder + copy['src'], os.path.realpath(os.path.join(folder, copy['target'])) + "/" + copy['file'])

# remove self
shutil.rmtree(folder)
