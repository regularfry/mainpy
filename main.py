"""
=======
main.py
=======

A command-line processor, loosely modeled on main.rb by Ara T. Howard.

Examples
========

a.py::

  import main
  import sys

  m = main.mode("run", callback)
  main.process(sys.argv)
  
  def callback(_):
    print "Called."

Called as::

  $ python a.py run

Outputs::

  Called.

b.py::

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

c.py::

  import main
  import sys

  m = main.mode("run", None)
  m.option("foo")
  s = m.mode("quickly", callback)
  s.option("bar")
  main.process(sys.argv)

  def callback(params):
    print "Called with %s and %s"%(params['foo'].value, params['bar'].value)

Called as::

  $ python c.py run quickly --foo=42 --bar=23

Outputs::

  Called with 42 and 23

Notes
=====

Only supports long-form options.
Mode names must precede options.
Modes can have as many submodes as you like.
There must be at least one top-level mode.
Error trapping tries to be smart.
"""
  
__docformat__ = "restructuredtext"

modes = {}

def reset():
    """
    Lose any previously-registered modes. Mainly for testing.
    """
    global modes
    modes = {}

def mode(name, callback):
    """
    Register a top-level mode. The callback registered for this mode will
    be called if the mode is specified on the command line. In the case of
    modes with submodes, *only* the lowest-level submode's callback will
    be called. A mode with submodes will never have its callback called, and
    callback should be None for those cases.

    Parameters:

    - `name`: a string that will be given on the command-line
    - `callback`: a callable that takes a single Params object parameter.
    """
    global modes

    m = Mode(name, callback)
    modes[name] = m
    return m

def usage(cmdname, mode=None):
    """
    Print a usage message created from the defined modes. Primarily internal.
    
    Parameters:
    
    - `cmdname`: sys.argv[0].
    - `mode`: A Mode.
    """
    global modes
    print "Usage:"
    
    if mode:
        mymodes = {mode.name: mode}
    else:
        mymodes = modes
    
    modenames = mymodes.keys()
    modenames.sort()

    for name in modenames:
        inmode = mymodes[name]
        print "  # %s\n      %s  %s"%(inmode.description,cmdname, inmode.usage())

def process(argv, usage_cb=usage):
    """
    Pass in the complete sys.argv to either call a mode callback,
    or print a usage message if there are not enough options passed.

    Parameters:

    - `argv`: A complete sys.argv list.
    """
    global modes

    cmdline, argv = argv[0], argv[1:]

    if len(argv)>0:
        mode_stack, rest_argv = _resolve_mode(argv, modes, [])
        supermodes, mode = mode_stack[0:-1], mode_stack[-1]

        params = mode.collect_params(rest_argv)
        if params.is_complete:
            mode.callback(params)
        else:
            usage_cb(cmdline, mode)
    else:
        usage_cb(cmdline)

def _resolve_mode(argv, context, stack):
    modename, next_argv = argv[0], argv[1:]

    if context.has_key(modename):
        mode = context[modename]
        stack.append(mode)

        if len(mode.modes)>0 and len(next_argv)>0:
            return _resolve_mode(next_argv, mode.modes, stack)

    return (stack, next_argv)


class Option(object):
    """
    An option given in the form "--foo=bar" on the command line.
    """
    def __init__(self, name):
        self.name = name
        # Are we optional?
        self.optional = True
        self.supplied = False
    
    def __repr__(self):
        return "--%s=<%s>"%(self.name,self.name)


class Param(object):
    """
    A parameter that has been resolved from an Option; in other words,
    the option was given.
    """
    def __init__(self, name):
        self.name = name
        self.is_given = False
        self.value = None
        self.values = []

class Params(object):
    """
    The collection of all parameters given on the command line. This may
    or may not be complete; the Mode is responsible for collecting its
    data, and will know if any Options were missing.
    """
    def __init__(self):
        self.param_dict = {}
        self.is_complete = False
        self.missing = []

    def __getitem__(self, key):
        return self.param_dict[key]

    def __setitem__(self, key, item):
        self.param_dict[key] = item

    def has_key(self, key):
        return self.param_dict.has_key(key)

    def add_missing(self, opt):
        self.missing.append(opt)

class Mode(object):
    def __init__(self, name, callback):
        self.name = name
        self.options = {}
        self.modes = {}
        self.callback = callback
        self.description = ""
        self.parent_mode = None

    def __repr__(self):
        return "<Mode %s>" % self.name

    def option(self, name, short=None, optional=False, argument=False):
        opt = Option(name)
        opt.short = short
        opt.optional = optional
        opt.argument = argument
        self.options["--" + name] = opt
        return opt

    def dup(self, name, callback):
        # Return a Mode with the same options as this one
        # but a different name and callback.
        submode = Mode(name, callback)
        submode.options = self.options.copy()
        return submode

    def mode(self, name, callback):
        submode = self.dup(name, callback)
        self.modes[name] = submode
        submode.parent_mode = self
        return submode

    def collect_params(self, argv):
        params = Params()
        while len(argv) > 0:
            param_str, argv = argv[0], argv[1:]
            param_name, param_val = param_str.split("=")

            if self.options.has_key(param_name):
                option = self.options[param_name]
                option.supplied = True
                param = Param(option.name)
                param.value = param_val
                params[option.name] = param

        self.check_completeness(params)

        return params
                
    def check_completeness(self, params):
        params.is_complete = True
        for name, option in self.options.items():
            if option.optional:
                continue
            if not params.has_key(option.name):
                params.is_complete = False
                params.add_missing( option )

    def usage(self):
        modenames = [self.name]
        parent = self.parent_mode
        while parent:
            modenames.append(parent.name)
            parent = parent.parent_mode

        modenames.reverse()
        modes_string = " ".join(modenames)

        if len(self.modes) > 0:
            names = self.modes.keys()
            names.sort()
            submode_str = " ("+"|".join(names) + ") "
        else:
            submode_str = ""

        options_string = " ".join([str(opt) for _,opt in self.options.items()])
        return  modes_string + submode_str + ' ' + options_string


