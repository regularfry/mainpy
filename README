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

  import main
  import sys

  m = main.mode("run", callback)
  m.option("foo")
  main.process(sys.argv)

  def callback(params):
    print "Called with " + params['foo'].value

Called as::

  $ python b.py run --foo=bar

Outputs::

  Called with bar


TODO
====

Most of the work, including:

* Options will have default arguments.
* The top-level mode will become unnecessary.
* Non-option arguments will be respected.
* Other suggestions welcome.

License
=======

This code is in the public domain. Do as you will. Feedback and patches are
welcome but not required.

-- 
Alex Young
alex@blackkettle.org
