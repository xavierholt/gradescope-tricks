# Gradescope Tricks

## Demo

Just run `./demo.sh`!  You'll need Docker and Python installed.  The first run
will build a Docker image; subsequent runs will use the existing image.


## What's Interesting

For a thorough set of tests for an existing binary, see the `run_testcase`
function in `source/autograder.py`.

For an example of running pre-compile hygiene checks and compiling, see the
compile test cases in `source/tests.py`.  This file also contains examples of
how to use the `run_testcase` function described above.


## Other Features

- `Autograder::backtrace()`\
  Automatic backtrace generation for segfaults and heap errors.

- `Autograder::build()`\
  An easy way to compile executables from source.

- `Autograder::shellout()`\
  An easy way to run subprocesses and get their output.

- `Autograder::valgrind()`\
  Automatic detection of memory leaks and out-of-bounds accesses.


## Folder Layout

This repo is designed to mimic the default Gradescope folder layout.  Autograder
code goes in the `source` directory, and student code goes in the `submission`
directory.  JSON test results go in `results` and the `build` subdirectory is
something I added to store compiled objects.

In a real Gradescope container, these would be subdirectories of `/autograder`
(the working directory), but I always use relative paths, so it should work
wherever it ends up.

Details of the official folder layout can be found here:\
https://gradescope-autograders.readthedocs.io/en/latest/specs/#file-hierarchy`


## Folder Permissions

I add a `student` user (and group) to the container for sandboxing purposes.
The autograder runs as the `root` user by default.  I give the subfolders the
following permissions:

```
Subfolder   User  Group    Mode  Notes
source      root  root     0500  Secrets (might) live here; only root may see.
submission  root  root     0755  Public, but I never change anything in here.
build       root  student  0775  Public and writeable by student (see below).
results     root  root     0700  Only root can mess with the test results.
```

The `build` subfolder is writeable by the `student` group because student code
should always be compiled by the `student` user -- you can leak information with
`#include` statements.  Compiled code should also (obviously) be run as the
`student` user.


## Git Tricks

- Require Git by disabling other submission methods!

- I like to use a single Git repo for the class, with each assignment in its
  own subdirectory.  If you do this, use the Gradescope config (in the GUI) to
  restrict the assignment to the relevant folder(s) -- otherwise you'll get the
  entire repo in the files view, and it's extremely messy.


## Test Ordering

```python
@weight(5)
def test_02_secondtest(self):
    """The Second Test"""
    assert "Whatever!"
```

- Tests run in acsiibetical order of their function names, so use these to
  control execution order.  I usually include an ordering prefix (the `02`
  in the example) to control this.

- Gradescope will use the docstring for the test name if it's available, so
  use these to control the display names.


## Partial Credit

```python
@partial_credit(12)
def test_2d6(self, set_score=None):
    """Are you feeling lucky, punk?"""
    score  = random.randint(1, 6)
    score += random.randint(1, 6)
    print("You rolled a %d." % score)
    set_score(score)
```

- Use  `@partial_credit(42)` instead of  `@weight(42)` to set the maximum number
  of points available on that function.

- Make your function take a keyword argument `set_score=None`; the framework
  will pass in a function that you can use to set the score.

- Call `set_score(score)` at the end of a successful run to set the score.  Use
  `set_score(max(0, score))` if it's possible to deduct more points than are
  available.


## Future Work

- The compile and link functions have the compiler and some default arguments
  hard-coded.  These should probably be configurable: maybe add a few more
  class variables?

- The run_testcase function will fail on any Valgrind errors.  It should
  probably attach the Valgrind info to the result object instead, so that the
  caller can decide what to do in that case (I like to give partial credit).

- The assertNoObjects function should traverse directories and use MIME types
  to detect object files.

- GDB still prints out `Reading symbols from [whatever]...`.  It's a minor
  annoyance, but it's still an annoyance.

- It would be nice to suppress the Valgrind header as well.
