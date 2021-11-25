import autograder
import os

from gradescope_utils.autograder_utils.decorators import partial_credit, weight

class CrasherTests(autograder.Autograder):
    @weight(5)
    def test_00_compilation(self):
        """Crasher: Compilation"""
        srcdir = 'submission'   # Student code lives here.
        refdir = 'source/code'  # Reference code lives here.

        # Make sure the folder exists.
        if not os.path.isdir(srcdir):
            relpath = os.path.relpath(srcdir, 'submission/')
            self.fail('No such directory: ' + relpath)

        # Make sure it's not full of compiled crap.
        self.assertNoObjects(srcdir, ['a', 'crasher', 'doublefree', 'memleak', 'segfault'])

        # Make sure they didn't change anything they weren't supposed to.
        self.assertUnmodified(srcdir, refdir, ['crasher.h'])

        # Compile ALL the things!
        self.build('build/crasher', [
            os.path.join(srcdir, 'crasher.cpp'),
            os.path.join(srcdir, 'doublefree.cpp'),
            os.path.join(srcdir, 'memleak.cpp'),
            os.path.join(srcdir, 'segfault.cpp')
        ])

    @weight(5)
    def test_01_doublefree(self):
        """Crasher: Double Free"""
        self.run_testcase(['build/crasher', 'doublefree'])

    @weight(5)
    def test_02_memleak(self):
        """Crasher: Memory Leak"""
        self.run_testcase(['build/crasher', 'memleak'])

    @weight(5)
    def test_03_segfault(self):
        """Crasher: Segmentation Fault"""
        self.run_testcase(['build/crasher', 'segfault'])


class PoetryTests(autograder.Autograder):
    def poetry_test(self, style):
        self.run_testcase(['build/poetry', style],
            #infile = os.path.join('source/tests', style + '.inn'), # stdin
            outfile = os.path.join('source/tests', style + '.oot'), # expected stdout
            errfile = os.path.join('source/tests', style + '.err')  # expected stderr
        )

    @weight(5)
    def test_10_hygiene(self):
        """Poetry: Hygiene"""
        srcdir = 'submission/poetry'

        if not os.path.isdir(srcdir):
            relpath = os.path.relpath(srcdir, 'submission/')
            self.fail('No such directory: ' + relpath)

        self.assertNoObjects(srcdir, ['a', 'main'])

    @weight(5)
    def test_11_compilation(self):
        """Poetry: Compilation"""
        srcdir = 'submission/poetry'

        if not os.path.isdir(srcdir):
            relpath = os.path.relpath(srcdir, 'submission/')
            self.fail('No such directory: ' + relpath)

        self.build('build/poetry', [
            os.path.join(srcdir, 'main.cpp'),
        ])

    @weight(5)
    def test_12_limmerick(self):
        """Poetry: Limerick"""
        self.poetry_test('limerick')

    @weight(5)
    def test_13_sonnet(self):
        """Poetry: Sonnet"""
        self.poetry_test('sonnet')

    @weight(5)
    def test_14_haiku(self):
        """Poetry: Haiku"""
        self.poetry_test('haiku')


if __name__ == '__main__':
    autograder.main()
