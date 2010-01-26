=======
main.py
=======

A quick and dirty command-line processor.  See main.py for more.

INSTALL
=======

1. Copy main.py into your project.
2. There is no step 2.

USAGE
=====

See main.py, but in brief:

b.py::

  import main
  import sys

  def callback(params):
    print "Called with " + params['foo'].value

  m = main.mode("run", callback)
  m.option("foo")
  m.description="How not to be seen"
  main.process(sys.argv)


Called as::

  $ python b.py

Outputs::

  Usage:
    # How not to be seen
          b.py  run --foo=<foo>

Called as::

  $ python b.py run --foo=bar

Outputs::

  Called with bar


TODO
====

Most of the work, including:

* Errors will be caught and redirected to usage messages better
* Options will have default arguments.
* The top-level mode will become unnecessary.
* Non-option arguments will be respected.
* Param objects will support more information.
* Cheese will be eaten.

License
=======

This code is in the public domain. Do as you will. Feedback and patches are
welcome but not required.

-- 
Alex Young
alex@blackkettle.org
