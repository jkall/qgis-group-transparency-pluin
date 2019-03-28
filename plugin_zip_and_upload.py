#!/usr/bin/env python
# coding=utf-8
"""This script uploads a plugin package to the plugin repository.
        Authors: A. Pasotti, V. Picavet
        git sha              : $TemplateVCSFormat

        # Modified by Josef Källgården 2019-03-28
"""

"""
USAGE:

only  zip:
python3 plugin_zip_and_upload.py


zip and upload:
python3 plugin_zip_and_upload.py --upload group_transparency.zip


"""

import sys, os
import zipfile, zlib
import getpass
import xmlrpc.client
from optparse import OptionParser

#standard_library.install_aliases() # commented out from original code due to NameError: name 'standard_library' is not defined

# Configuration
PROTOCOL = 'https'
SERVER = 'plugins.qgis.org'
PORT = '443'
ENDPOINT = '/plugins/RPC2/'
VERBOSE = False

# JK additions:
IGNORE_FOLDERS = ['.git', 'arkiv','__pycache__','test','help','scripts']
IGNORE_FILES = ['.gitignore', 'plugin_zip_and_upload.py','Makefile','pb_tool.cfg','transparency.png']
IGNORE_FILESUFFIX = ('.pyc','.zip')
#/JK additions

def main(parameters, arguments):
    """Main entry point.

    :param parameters: Command line parameters.
    :param arguments: Command line arguments.
    """
    address = "{protocol}://{username}:{password}@{server}:{port}{endpoint}".format(
        protocol=PROTOCOL,
        username=parameters.username,
        password=parameters.password,
        server=parameters.server,
        port=parameters.port,
        endpoint=ENDPOINT)
    print("Connecting to: %s" % hide_password(address))

    server = xmlrpc.client.ServerProxy(address, verbose=VERBOSE)

    try:
        with open(arguments[0], 'rb') as handle:
            plugin_id, version_id = server.plugin.upload(
                xmlrpc.client.Binary(handle.read()))
        print("Plugin ID: %s" % plugin_id)
        print("Version ID: %s" % version_id)
    except xmlrpc.client.ProtocolError as err:
        print("A protocol error occurred")
        print("URL: %s" % hide_password(err.url, 0))
        print("HTTP/HTTPS headers: %s" % err.headers)
        print("Error code: %d" % err.errcode)
        print("Error message: %s" % err.errmsg)
    except xmlrpc.client.Fault as err:
        print("A fault occurred")
        print("Fault code: %d" % err.faultCode)
        print("Fault string: %s" % err.faultString)


def hide_password(url, start=6):
    """Returns the http url with password part replaced with '*'.

    :param url: URL to upload the plugin to.
    :type url: str

    :param start: Position of start of password.
    :type start: int
    """
    start_position = url.find(':', start) + 1
    end_position = url.find('@')
    return "%s%s%s" % (
        url[:start_position],
        '*' * (end_position - start_position),
        url[end_position:])

# JK additions:
def create_zipfile():
    file_path = os.path.realpath(__file__)
    dir_path = os.path.dirname(file_path)
    current_dir = dir_path.split(os.sep)[-1]
    zf = zipfile.ZipFile(os.path.join(dir_path, current_dir + '.zip'), mode='w')
    for root, dirs, files in os.walk(dir_path):
        dirs[:] = [d for d in dirs if d not in IGNORE_FOLDERS]
        files[:] = [f for f in files if f not in IGNORE_FILES]#exclude specific files
        files[:]= [ file for file in files if not file.endswith( IGNORE_FILESUFFIX ) ]#exclude specific file extensions
        for file in files:
            print('now adding this file {}'.format(os.path.join(root,file)))
            #print('in archive it is saved as ' + os.path.join(current_dir,file))
            print('in archive it is saved as {}'.format(os.path.relpath(os.path.join(root, file), os.path.join(dir_path, '..'))))
            #zf.write(os.path.join(root,file),os.path.join(current_dir,file), compress_type=zipfile.ZIP_DEFLATED)
            zf.write(os.path.join(root,file),os.path.relpath(os.path.join(root, file), os.path.join(dir_path, '..')), compress_type=zipfile.ZIP_DEFLATED)
    zf.close()
    return os.path.join(dir_path, current_dir + '.zip')
#/JK additions


if __name__ == "__main__":
    parser = OptionParser(usage="%prog [options] plugin.zip")
    parser.add_option(
        "-l", "--upload", dest="upload",
        help="set to True if upload",default=False)
    parser.add_option(
        "-w", "--password", dest="password",
        help="Password for plugin site", metavar="******")
    parser.add_option(
        "-u", "--username", dest="username",
        help="Username of plugin site", metavar="user")
    parser.add_option(
        "-p", "--port", dest="port",
        help="Server port to connect to", metavar="80")
    parser.add_option(
        "-s", "--server", dest="server",
        help="Specify server name", metavar="plugins.qgis.org")
    options, args = parser.parse_args()
    if len(args) != 1:
        parser.print_help()
        print("No zip file specified, therefore creating one.\n")
        zipfilename = create_zipfile()
        print('created file: ' + zipfilename)
    if options.upload:
        if not options.server:
            options.server = SERVER
        if not options.port:
            options.port = PORT
        if not options.username:
            # interactive mode
            username = getpass.getuser()
            print("Please enter user name [%s] :" % username)#, end=' ') #commented out from original code due to syntaxerror

            res = input()
            if res != "":
                options.username = res
            else:
                options.username = username
        if not options.password:
            # interactive mode
            options.password = getpass.getpass()

        main(options, args)
