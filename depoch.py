#!/usr/bin/env python

import re
from time import gmtime, localtime, strftime

from cement.core import foundation, controller, handler

class BaseController(controller.CementBaseController):
    class Meta:
        label='base'
        description = 'Convert unix epoch timestamps to human readable format'
        arguments = [
            (['--regex', '-r'], {
                'action': 'store',
                'help': 'Regex to use to extract the timestamp from input',
                'type': re.compile,
                'default': r'^(\d+)',
            }),
            (['--format', '-f'], {
                'action': 'store',
                'help': 'Output date string in strftime(2) format',
                'default': '%Y-%m-%d %H:%M:%S',
            }),
            (['--local'], {
                'action': 'store_true',
                'help': 'Treat timestamp as in local timezone (default is UTC)',
            }),
            (['input'], {
                'nargs': '*',
                'help': 'Files to process',
            }),
        ]

    def format_line(self, line):
        pattern = self.app.pargs.regex
        match = pattern.search(line)
        if match:
            timestamp = int(match.group(1))
            if self.app.pargs.local:
                timestamp = localtime(timestamp)
            else:
                timestamp = gmtime(timestamp)
            line = pattern.sub(strftime(self.app.pargs.format, timestamp), line)
        return line

    def input_lines(self, file_name):
        with open(file_name, 'r') as input_file:
            for line in input_file:
                yield self.format_line(line.strip('\n'))

    def input(self, files):
        self.app.log.debug('Processing files: %r' % files)
        for input_file in files:
            for line in self.input_lines(input_file):
                yield line

    @controller.expose(hide=True)
    def default(self):
        files = []
        if self.app.pargs.input:
            self.app.log.debug('Input files: %r' % self.app.pargs.input)
            files.extend(self.app.pargs.input)
        else:
            files.append('/dev/stdin')
        for line in self.input(files):
            print line

def run():
    app = foundation.CementApp('depoch', base_controller=BaseController)
    try:
        app.setup()
        app.run()
    finally:
        app.close()

if __name__ == '__main__':
    run()
