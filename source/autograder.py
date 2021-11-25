#! /usr/bin/env python3

import difflib
import os
import shlex
import subprocess
import unittest

class Autograder(unittest.TestCase):
    USER     = 'student'  # User to use for sandboxing.
    VALGRIND =  True      # Should we run Valgrind tests?
    VERBOSE  =  True      # Currently unused.

    def __init__(self, *args, **kwargs):
        super(Autograder, self).__init__(*args, **kwargs)
        self.maxDiff = None

    def assertMultiLineEqual(self, first, second, msg=None):
        """Assert that two multi-line strings are equal."""
        # From difflib, but modified to put the message at the top where you can actually find it.
        # https://github.com/python/cpython/blob/6b34d7b51e33fcb21b8827d927474ce9ed1f605c/Lib/unittest/case.py#L1201
        self.assertIsInstance(first,  str, 'First argument is not a string.')
        self.assertIsInstance(second, str, 'Second argument is not a string.')

        if first != second:
            # Don't use difflib if the strings are too long...
            if len(first) > self._diffThreshold or len(second) > self._diffThreshold:
                self._baseAssertEqual(first, second, msg)
            lhs = first.splitlines(keepends=True)
            rhs = second.splitlines(keepends=True)
            if len(lhs) == 1 and first.strip('\r\n') == first:
                lhs = [first  + '\n']
                rhs = [second + '\n']
            msg  = msg or 'Strings were not equal.'
            diff = '\n' + ''.join(difflib.ndiff(lhs, rhs))
            self.fail(self._truncateMessage(msg, diff))

    def assertNoObjects(self, srcdir, files):
        """Assert that a directory contains no compiled code."""
        # TODO: Use os.walk() and /bin/file or MIME info instead of filenames.
        objects = []
        for file in files:
            path  = os.path.join(srcdir, file)
            rpath = os.path.relpath(path, 'submission/')
            if os.path.isfile(path):
                objects.append(' - ' + rpath)
            if os.path.isfile(path + '.o'):
                objects.append(' - ' + rpath + '.o')
            if os.path.isfile(path + '.out'):
                objects.append(' - ' + rpath + '.out')
            if os.path.isfile(path + '.exe'):
                objects.append(' - ' + rpath + '.exe')
        if objects:
            self.fail('\n'.join([
                'Don\'t check compiled code into Git (consider using a .gitignore file):',
                *objects
            ]))

    def assertUnmodified(self, srcdir, refdir, files):
        """Assert that a list of files are the same in two directories."""
        for file in files:
            ref = self.readfile(os.path.join(refdir, file))
            src = self.readfile(os.path.join(srcdir, file))
            self.assertMultiLineEqual(src, ref, 'Don\'t modify ' + file + '!')

    def backtrace(self, command, infile=None, timeout=5):
        """Run a program that's known to crash in GDB and get a stack trace."""
        with open('/tmp/backtrace.gdb', 'w') as file:
            file.write('set disable-randomization off\n')
            file.write('set pagination off\n')
            file.write('set confirm off\n')
            file.write('run ')
            for arg in command[1:]:
                file.write(shlex.quote(arg))
            if infile:
                file.write('< ' + shlex.quote(infile))
            file.write('> /dev/null\n')
            file.write('backtrace\n')
            file.write('quit\n')
        prefix = ['gdb', '--silent', '--command=/tmp/backtrace.gdb', '--']
        return self.shellout(prefix + command[:1], timeout=timeout)

    def build(self, target, sources, flags=[]):
        """Compile and link a list of source files into a single executable."""
        objects = ['build/' + os.path.basename(s) + '.o' for s in sources]
        for s, o in zip(sources, objects):
            user = None if s.startswith('source/') else self.USER
            self.compile(o, s, flags=flags, user=user)
        self.link(target, objects, flags=flags, user=self.USER)

    def compile(self, target, source, flags=[], user=None):
        """Compile a single source file into an object file."""
        command = ['g++', '-c', *flags, '-g', '-o', target, '-std=c++17', '-Wall', '-Wextra', '-Werror', source]
        result  = self.shellout(command, user=user)

        if result.returncode != 0:
            self.fail('Compilation failed.\n\n%s' % (result.stdout or 'No output.'))
        return result

    def link(self, target, sources, flags=[], user=None):
        """Link a list of object files into a single executable."""
        command = ['g++', *flags, '-g', '-o', target, '-std=c++17', '-Wall', '-Wextra', '-Werror', *sources]
        result  = self.shellout(command, user=user)

        if result.returncode != 0:
            self.fail('Linking failed.\n\n%s' % (result.stdout or 'No output.'))
        return result

    def readfile(self, path, mode='r'):
        """Helper function to make reading files a one-liner."""
        if not os.path.isfile(path):
            self.fail('No such file: ' + path)
        with open(path, mode) as file:
            return file.read()

    def shellout(self, command, user=None, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, **options):
        """Run a command in a subprocess and collect the results."""
        program = os.path.basename(command[0])
        if user is not None:
            command = ['sudo', '-u', user, '--'] + command
        try:
            return subprocess.run(command, universal_newlines=True, input=stdin, stdout=stdout, stderr=stderr, **options)
        except subprocess.TimeoutExpired:
            self.fail('Timeout expired (' + program + '). Infinite loop?\n'
                ' - Make sure your code exits at the end of the input stream.\n'
                ' - Use Ctrl+D on Mac and Linux to send an EOF.\n'
                ' - Use Ctrl+Z then Enter on Windows.'
            )

    def valgrind(self, command, user=None, stdin=None, timeout=15):
        """Run a program in Valgrind and collect the output. This can be slow!"""
        prefix = ['valgrind', '--leak-check=full', '--error-exitcode=1', '--log-file=/tmp/valgrind.log', '--']
        result = self.shellout(prefix + command, stdin=stdin, user=user, timeout=timeout)
        result.valout = self.readfile('/tmp/valgrind.log')
        return result

    def run_testcase(self, command, infile=None, outfile=None, errfile=None, timeout=5):
        # A better error message in case compilation failed.
        if not os.path.isfile(command[0]):
            self.fail('No executable to test. Did compilation fail?')

        # Read the standard input file (if any).
        stdin = self.readfile(infile) if infile else None

        # Run the command once with no piping to check for infinite loops.
        # This avoids an autograder crash that happens when too much output gets buffered.
        self.shellout(command, stdin=stdin, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, user=self.USER, timeout=timeout)

        # Run it again to collect the output.
        result = self.shellout(command, stdin=stdin, stderr=subprocess.PIPE, user=self.USER, timeout=timeout)
        if result.returncode == -11:
            # Your classic segmentation fault.
            backtrace = self.backtrace(command, infile, timeout=timeout)
            self.fail('Segmentation fault.\n\n' + backtrace.stdout)
        elif result.returncode == -6:
            # Usually a double free or other heap error.
            backtrace = self.backtrace(command, infile, timeout=timeout)
            self.fail('Execution aborted.\n\n' + backtrace.stdout)
        elif result.returncode != 0:
            # Some other error; could be anything...
            self.fail('Execution failed with exit code %d.\n\n%s' % (
                result.returncode,
                result.stdout
            ))

        if outfile is not None:
            self.assertMultiLineEqual(result.stdout, self.readfile(outfile), 'Unexpected output (stdout).\n')
        if errfile is not None:
            self.assertMultiLineEqual(result.stderr, self.readfile(errfile), 'Unexpected output (stderr).\n')

        if self.VALGRIND:
            # Run it again to check for memory shenanigans.
            vgresult = self.valgrind(command, stdin=stdin, user=self.USER, timeout=10*timeout)
            if vgresult.returncode != 0:
                self.fail('Memory leak or bad memory access.\n\n' + vgresult.valout)

        # Return the non-Valgrind run.
        return result


def main(user='student', verbose=True, valgrind=True, visibility='visible'):
    from gradescope_utils.autograder_utils.json_test_runner import JSONTestRunner

    Autograder.USER     = user
    Autograder.VERBOSE  = verbose
    Autograder.VALGRIND = valgrind

    runner = JSONTestRunner(visibility=visibility)
    unittest.main(testRunner=runner)
