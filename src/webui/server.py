#! /usr/bin/env python
from __future__ import print_function

import logging
import json
import os
import posixpath
import shutil
import sys

try:
    from urllib import unquote
except Exception:
    from urllib.parse import unquote
try:
    from BaseHTTPServer import BaseHTTPRequestHandler
except ImportError:
    from http.server import BaseHTTPRequestHandler
try:
    import SocketServer as socketserver
except ImportError:
    import socketserver

from . import _project

__version__ = '0.1'

BASEPATH = os.path.abspath(os.path.dirname(__file__))

class HelperHandler(BaseHTTPRequestHandler):
    '''Based on SimpleHTTPRequestHandler'''

    server_version = "HelperHTTP/" + __version__

    def do_POST(self):
        """Serve a POST request."""
        if self.path[1:] not in ('obfuscateScripts', 'generateLicenses',
                                 'packObfuscatedScripts',
                                 'newProject', 'updateProject',
                                 'buildProject', 'removeProject',
                                 'queryProject', 'queryVersion',
                                 'newLicense', 'removeLicense'):
            self.send_error(404, "File not found")
            return

        n = int(self.headers.get('Content-Length', 0))
        t = self.headers.get('Content-Type', 'text/json;charset=UTF-8')
        if n == 0:
            arguments = ''
        else:
            arguments = self.rfile.read(n).decode()

        self.log_message("Arguments '%s'", arguments)
        result = self.run_command(self.path[1:], arguments)
        if result is not None:
            response = json.dumps(result).encode()
            self.send_response(200)
            self.send_header("Content-type", "text/json")
            self.send_header("Content-Length", str(len(response)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Last-Modified", self.date_time_string())
            self.end_headers()
            self.wfile.write(response)
        else:
            self.send_error(501, "Server internal error")

    def do_GET(self):
        """Serve a GET request."""
        f = self.send_head()
        if f:
            self.copyfile(f, self.wfile)
            f.close()

    def do_HEAD(self):
        """Serve a HEAD request."""
        f = self.send_head()
        if f:
            f.close()

    def send_head(self):
        """Common code for GET and HEAD commands.

        This sends the response code and MIME headers.

        Return value is either a file object (which has to be copied
        to the outputfile by the caller unless the command was HEAD,
        and must be closed by the caller under all circumstances), or
        None, in which case the caller has nothing further to do.

        """
        path = self.translate_path(self.path)
        f = None
        if os.path.isdir(path):
            if not self.path.endswith('/'):
                # redirect browser - doing basically what apache does
                self.send_response(301)
                self.send_header("Location", self.path + "/")
                self.end_headers()
                return None
            for index in "index.html", "index.htm":
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break
            else:
                self.send_error(404, "File not found")
                return None
        # if os.path.basename(path) not in (
        #         'bootstrap.min.css', 'bootstrap.min.js', 'jquery.min.js',
        #         'pyarmor.js', 'index.html'):
        #     self.send_error(404, "File not found")
        #     return None

        ctype = self.guess_type(path)
        try:
            # Always read in binary mode. Opening files in text mode may cause
            # newline translations, making the actual size of the content
            # transmitted *less* than the content-length!
            f = open(path, 'rb')
        except IOError:
            self.send_error(404, "File not found")
            return None
        self.send_response(200)
        self.send_header("Content-type", ctype)
        fs = os.fstat(f.fileno())
        self.send_header("Content-Length", str(fs[6]))
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.end_headers()
        return f

    def run_command(self, command, arguments):
        try:
            data = json.loads(arguments)
            result = getattr(_project, command)(data)
            errcode = 0
        except Exception as e:
            errcode = 1
            result = "Unhandle Server Error: %s" % str(e)
            logging.exception("Unhandle Server Error")
        return dict(errcode=errcode, result=result)

    def translate_path(self, path):
        """Translate a /-separated PATH to the local filename syntax.

        Components that mean special things to the local file system
        (e.g. drive or directory names) are ignored.  (XXX They should
        probably be diagnosed.)

        """
        # abandon query parameters
        path = path.split('?',1)[0]
        path = path.split('#',1)[0]
        path = posixpath.normpath(unquote(path))
        words = path.split('/')
        words = filter(None, words)
        path = BASEPATH
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir): continue
            path = os.path.join(path, word)
        return path

    def copyfile(self, source, outputfile):
        """Copy all data between two file objects.

        The SOURCE argument is a file object open for reading
        (or anything with a read() method) and the DESTINATION
        argument is a file object open for writing (or
        anything with a write() method).

        The only reason for overriding this would be to change
        the block size or perhaps to replace newlines by CRLF
        -- note however that this the default server uses this
        to copy binary data as well.

        """
        shutil.copyfileobj(source, outputfile)

    def guess_type(self, path):
        """Guess the type of a file.

        Argument is a PATH (a filename).

        Return value is a string of the form type/subtype,
        usable for a MIME Content-type header.

        The default implementation looks the file's extension
        up in the table self.extensions_map, using application/octet-stream
        as a default; however it would be permissible (if
        slow) to look inside the data to make a better guess.

        """

        base, ext = posixpath.splitext(path)
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        ext = ext.lower()
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        else:
            return self.extensions_map['']
    extensions_map = {
        '': 'application/octet-stream', # Default
        '.css': 'text/css',
        '.html': 'text/html',
        '.js': 'application/x-javascript',
        }

def main(page=''):
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)-8s %(message)s',
    )
    try:
        PORT = int(sys.argv[1])
    except Exception:
        PORT = 9096
    server = socketserver.TCPServer(("", PORT), HelperHandler)
    print("Serving HTTP on %s port %s ..." % server.server_address)
    try:
        from webbrowser import open_new_tab
        open_new_tab("http://localhost:%d/%s" % (
            server.server_address[1], page))
    except Exception:
        pass
    server.serve_forever()

if __name__ == '__main__':
    main()
