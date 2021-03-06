"""This plugin provides test timings to identify which tests might be
taking the most. From this information, it might be useful to couple
individual tests nose's `--with-profile` option to profile problematic
tests.

This plugin is heavily influenced by nose's `xunit` plugin.

Add this command to the way you execute nose::

    --with-test-timer

After all tests are executed, they will be sorted in ascending order.

(c) 2011 - Mahmoud Abdelkader (http://github.com/mahmoudimus)

LICENSE:
            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
                    Version 2, December 2004

 Copyright (C) 2004 Sam Hocevar <sam@hocevar.net>

 Everyone is permitted to copy and distribute verbatim or modified
 copies of this license document, and changing it is allowed as long
 as the name is changed.

            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION

  0. You just DO WHAT THE FUCK YOU WANT TO.

"""

import logging
import operator
from time import time
from nose.plugins import Plugin

log = logging.getLogger('nose.plugins.nose_timer')

class NoseTimer(Plugin):

    enabled = False

    def _timeTaken(self):
        if hasattr(self, '_timer'):
            taken = time() - self._timer
        else:
            # test died before it ran (probably error in setup())
            # or success/failure added before test started probably
            # due to custom TestResult munging
            taken = 0.0
        return taken


    def options(self, parser, env):
        """Sets additional command line options."""
        super(NoseTimer, self).options(parser, env)
        parser.add_option(
            "--with-test-timers", action="store_true",
            dest="with_test_timers",
            help="Directory to exclude from test discovery. \
                Path can be relative to current working directory \
                or an absolute path. May be specified multiple \
                times. [NOSE_EXCLUDE_DIRS]")

    def configure(self, options, config):
        """Configures the test timer plugin based on command line options."""
        super(NoseTimer, self).configure(options, config)

        if options.with_test_timers:
            self.enabled = True
        else:
            self.enabled = False
        if not self.enabled:
            return

        self.config = config
        self._timed_tests = {}
        self._passed_tests = []
        self._failed_tests = []
        self._error_tests = []

    def startTest(self, test):
        """Initializes a timer before starting a test."""
        self._timer = time()

    def report_list_test(self, message, alist, stream):
        if not alist:
            return

        print "----------------------------------------------"
        print message
        sorted_list = sorted(alist, key=lambda x: self._timed_tests[x])
        for test in sorted_list:
            stream.writeln("%s: %0.4f" % (test, self._timed_tests[test]))

    def report(self, stream):
        """Report the test times"""
        if not self.enabled:
            return
        self.report_list_test("PASSED", self._passed_tests, stream)
        self.report_list_test("FAILED", self._failed_tests, stream)
        self.report_list_test("ERROR", self._error_tests, stream)

    def _register_time(self, test):
        self._timed_tests[test.id()] = self._timeTaken()

    def addError(self, test, err, capt=None):
        self._register_time(test)
        self._error_tests.append(test.id())

    def addFailure(self, test, err, capt=None, tb_info=None):
        self._register_time(test)
        self._failed_tests.append(test.id())

    def addSuccess(self, test, capt=None):
        self._register_time(test)
        self._passed_tests.append(test.id())
