import unittest
import re
import main

class testMain(unittest.TestCase):
    def setUp(self):
        main.reset()

    def testModeName(self):
        class ns: pass

        ns.called = False
        def callback(params=[]): ns.called = True
        test_mode = main.mode("foo", callback)

        main.process(["main", "foo"])

        self.assertTrue(ns.called)

    def testNoMode(self):
        class ns: pass
        ns.called=False
        def usage_cb(_): ns.called=True

        main.process(['main'], usage_cb)
        
        self.assert_(ns.called)

    def testOption(self):
        class ns: pass
        ns.params=None
        
        def callback(params): ns.params = params
        test_mode = main.mode("foo", callback)
        test_mode.option("bar")

        main.process(["main", "foo","--bar=qux"])
        
        self.assert_(ns.params, "No params object was created")

    def testSubModeWithOptions(self):
        class ns: pass
        ns.params = None

        def cb(params): ns.params = params
        m = main.mode("foo", None)
        m.option("qux")
        s = m.mode("bar", cb)
        s.option("abed")

        main.process(["main", "foo", "bar", "--qux=23", "--abed=not"])

        self.assert_(ns.params, "No params object was created")
        self.assertEqual(ns.params['qux'].value, "23")
        self.assertEqual(ns.params['abed'].value, "not")

    def testResolvePartialSpec(self):
        m = main.mode("foo", None)
        s = m.mode("sub", None)

        in_argv = ["foo"]
        stack, argv = main._resolve_mode(in_argv, main.modes, [])

        self.assertEqual([m], stack)
        self.assertEqual([], argv)

    def testResolvePartialSpecWithOptions(self):
        m = main.mode("foo", None)
        m.option("bar")
        s = m.mode("sub", None)

        in_argv = ["foo", "--bar=bar"]
        stack, argv = main._resolve_mode(in_argv, main.modes, [])

        self.assertEqual([m], stack)

class testMode(unittest.TestCase):
    def testCollectOption(self):
        mode = main.Mode("foo", None)
        mode.option("bar")

        params = mode.collect_params(["--bar=qux"])
        
        self.assertTrue(params.has_key("bar"))
        self.assertEqual("qux", params['bar'].value)

        
class testSubMode(unittest.TestCase):
    def testSubModeCallback(self):
        class ns: pass
        ns.outer = False
        ns.inner = False
        def outercb(params): ns.outer = True
        def innercb(params): ns.inner = True

        mode = main.mode("foo", outercb)
        submode = mode.mode("bar", innercb)
        
        main.process(["main", "foo", "bar"])

        self.assertFalse(ns.outer)
        self.assert_(ns.inner)

    def testSubModeParams(self):
        mode = main.mode("foo", None)
        mode.option("qux")

        submode = mode.mode("bar", None)
        submode.option("abednigo")

        params = submode.collect_params(["--qux=fnord", "--abednigo=farley"])

        self.assert_(params.has_key("qux"))
        self.assertEqual(params['qux'].value, "fnord")

        self.assert_(params.has_key("abednigo"))
        self.assertEqual(params['abednigo'].value, "farley")

class testRequirements(unittest.TestCase):
    def testOptionRequirement(self):
        mode = main.mode("foo", None)
        option = mode.option("qux")
        params = mode.collect_params([])

        self.assertFalse(params.is_complete)
        self.assertEqual(params.missing, [option])

    def testSubmodeUsage(self):
        mode = main.mode("foo", None)
        mode.option("foo")
        sub = mode.mode("bar", None)
        sub.option("bar")

        usage_str = sub.usage()
        self.assert_(re.search(r"^foo bar ", usage_str))
        self.assert_(re.search(r"--foo=<foo>", usage_str), "\"%s\" not matched" % usage_str)
        self.assert_(re.search(r"--bar=<bar>", usage_str), "\"%s\" not matched" % usage_str)

    def testModeUsage(self):
        mode = main.mode("foo", None)
        mode.option("foo")
        sub = mode.mode("bar", None)
        sub.option("bar")
        subb = mode.mode("qux", None)
        subb.option("qux")

        usage_str = mode.usage()

        self.assert_(re.search(r"^foo \(bar|qux\) ", usage_str), "\"%s\" not matched" % usage_str)
        self.assert_(re.search(r"--foo=<foo>", usage_str), "\"%s\" not matched" % usage_str)    
        self.assertFalse(re.search(r"--bar=<bar>", usage_str))
        

if __name__=="__main__":
    unittest.main()
