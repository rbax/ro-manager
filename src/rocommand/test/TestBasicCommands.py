#!/usr/bin/python

"""
Module to test basic RO manager commands

See: http://www.wf4ever-project.org/wiki/display/docs/RO+management+tool
"""

import os, os.path
import sys
import re
import shutil
import unittest
import logging
import datetime
import StringIO
try:
    # Running Python 2.5 with simplejson?
    import simplejson as json
except ImportError:
    import json

if __name__ == "__main__":
    # Add main project directory and ro manager directories at start of python path
    sys.path.insert(0, "../..")
    sys.path.insert(0, "..")

from MiscLib import TestUtils

from rocommand import ro, ro_utils, ro_manifest

from TestConfig import ro_test_config
from StdoutContext import SwitchStdout

import TestROSupport

class TestBasicCommands(TestROSupport.TestROSupport):
    """
    Test basic ro commands
    """
    def setUp(self):
        super(TestBasicCommands, self).setUp()
        return

    def tearDown(self):
        super(TestBasicCommands, self).tearDown()
        return

    # Actual tests follow

    def testNull(self):
        assert True, 'Null test failed'

    def testHelpVersion(self):
        status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, ["ro", "--version"])
        self.assertEqual(status, 0)
        return

    def testHelpOptions(self):
        with SwitchStdout(self.outstr):
            status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, ["ro", "--help"])
            self.assertEqual(status, 0)
        self.assertEqual(self.outstr.getvalue().count("help"), 2)
        return

    def testHelpCommands(self):
        with SwitchStdout(self.outstr):
            status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, ["ro", "help"])
            self.assertEqual(status, 0)
        self.assertEqual(self.outstr.getvalue().count("help"), 2)
        return

    def testInvalidCommand(self):
        with SwitchStdout(self.outstr):
            status = ro.runCommand(
                ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, 
                ["ro", "nosuchcommand"])
            self.assertEqual(status, 2)
        self.assertEqual(self.outstr.getvalue().count("unrecognized"), 1)
        self.assertEqual(self.outstr.getvalue().count("nosuchcommand"), 1)
        return

    def testConfig(self):
        """
        $ ro config \
          -r http://calatola.man.poznan.pl/robox/dropbox_accounts/1/ro_containers/2 \
          -p d41d8cd98f00b204e9800998ecf8427e \
          -b /usr/workspace/Dropbox/myROs \
          -n "Graham Klyne" \
          -e gk@example.org
        """
        ro_utils.resetconfig(ro_test_config.CONFIGDIR)
        config = ro_utils.readconfig(ro_test_config.CONFIGDIR)
        self.assertEqual(config["robase"],    None)
        self.assertEqual(config["rosrs_uri"],  None)
        self.assertEqual(config["rosrs_username"],  None)
        self.assertEqual(config["rosrs_password"],  None)
        self.assertEqual(config["username"],  None)
        self.assertEqual(config["useremail"], None)
        args = [
            "ro", "config",
            "-b", ro_test_config.ROBASEDIR,
            "-r", ro_test_config.ROSRS_URI,
            "-u", ro_test_config.ROSRS_USERNAME,
            "-p", ro_test_config.ROSRS_PASSWORD,
            "-n", ro_test_config.ROBOXUSERNAME,
            "-e", ro_test_config.ROBOXEMAIL
            ]
        with SwitchStdout(self.outstr):
            status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, args)
            assert status == 0
        self.assertEqual(self.outstr.getvalue().count("ro config"), 0)
        config = ro_utils.readconfig(ro_test_config.CONFIGDIR)
        self.assertEqual(config["robase"],          os.path.abspath(ro_test_config.ROBASEDIR))
        self.assertEqual(config["rosrs_uri"],       ro_test_config.ROSRS_URI)
        self.assertEqual(config["rosrs_username"],  ro_test_config.ROSRS_USERNAME)
        self.assertEqual(config["rosrs_password"],  ro_test_config.ROSRS_PASSWORD)
        self.assertEqual(config["username"],        ro_test_config.ROBOXUSERNAME)
        self.assertEqual(config["useremail"]        ro_test_config.ROBOXEMAIL)
        return

    def testConfigVerbose(self):
        """
        $ ro config -v \
          -r http://calatola.man.poznan.pl/robox/dropbox_accounts/1/ro_containers/2 \
          -p d41d8cd98f00b204e9800998ecf8427e \
          -b /usr/workspace/Dropbox/myROs \
          -n "Graham Klyne" \
          -e gk@example.org
        """
        ro_utils.resetconfig(ro_test_config.CONFIGDIR)
        config = ro_utils.readconfig(ro_test_config.CONFIGDIR)
        self.assertEqual(config["robase"],    None)
        self.assertEqual(config["rosrs_uri"],  None)
        self.assertEqual(config["rosrs_username"],  None)
        self.assertEqual(config["rosrs_password"],  None)
        self.assertEqual(config["username"],  None)
        self.assertEqual(config["useremail"], None)
        args = [
            "ro", "config", "-v",
            "-b", ro_test_config.ROBASEDIR,
            "-r", ro_test_config.ROSRS_URI,
            "-u", ro_test_config.ROSRS_USERNAME,
            "-p", ro_test_config.ROSRS_PASSWORD,
            "-n", ro_test_config.ROBOXUSERNAME,
            "-e", ro_test_config.ROBOXEMAIL
            ]
        with SwitchStdout(self.outstr):
            status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, args)
        assert status == 0
        self.assertEqual(self.outstr.getvalue().count("ro configuration written"), 1)
        config = ro_utils.readconfig(ro_test_config.CONFIGDIR)
        self.assertEqual(config["robase"],    os.path.abspath(ro_test_config.ROBASEDIR))
        self.assertEqual(config["rosrs_uri"],       ro_test_config.ROSRS_URI)
        self.assertEqual(config["rosrs_username"],  ro_test_config.ROSRS_USERNAME)
        self.assertEqual(config["rosrs_password"],  ro_test_config.ROSRS_PASSWORD)
        self.assertEqual(config["username"],  ro_test_config.ROBOXUSERNAME)
        self.assertEqual(config["useremail"], ro_test_config.ROBOXEMAIL)
        return

    def testCreate(self):
        """
        Create a new Research Object.

        ro create RO-name [ -d dir ] [ -i RO-ident ]
        """
        rodir = self.createRoFixture("data/ro-test-1", ro_test_config.ROBASEDIR, "ro-testCreate")
        args = [
            "ro", "create", "Test Create RO",
            "-v", 
            "-d", rodir,
            "-i", "RO-id-testCreate",
            ]
        with SwitchStdout(self.outstr):
            status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, args)
        assert status == 0
        self.assertEqual(self.outstr.getvalue().count("ro create"), 1)
        self.checkRoFixtureManifest(rodir)
        self.checkManifestContent(rodir, "Test Create RO", "RO-id-testCreate")
        self.deleteRoFixture(rodir)
        return

    def testCreateDefaults(self):
        """
        Create a new Research Object with default options

        ro create RO-name [ -d dir ] [ -i RO-ident ]
        """
        rodir = self.createRoFixture("data/ro-test-1", ro_test_config.ROBASEDIR, "ro-testCreateDefaults")
        args = [
            "ro", "create", "Test Create RO_+_defaults",
            "-v"
            ]
        configbase = os.path.abspath(ro_test_config.CONFIGDIR)
        save_cwd = os.getcwd()
        os.chdir(rodir)
        with SwitchStdout(self.outstr):
            status = ro.runCommand(configbase, ro_test_config.ROBASEDIR, args)
        os.chdir(save_cwd)
        assert status == 0
        self.assertEqual(self.outstr.getvalue().count("ro create"), 1)
        self.checkRoFixtureManifest(rodir)
        self.deleteRoFixture(rodir)
        return

    def testCreateBadDir(self):
        """
        Create a new Research Object with directory not in configured area

        ro create RO-name [ -d dir ] [ -i RO-ident ]
        """
        rodir = self.createRoFixture("data/ro-test-1", ro_test_config.NOBASEDIR, "ro-testCreateBadDir")
        args = [
            "ro", "create", "Test Create RO bad directory",
            "-d", rodir,
            "-v"
            ]
        with SwitchStdout(self.outstr):
            status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, args)
        self.assertTrue(status == 1, "Expected failure due to bad RO directory");
        self.assertEqual(self.outstr.getvalue().count("research object not"), 1)
        manifestdir = rodir+"/"+ro_test_config.ROMANIFESTDIR
        self.assertFalse(os.path.exists(manifestdir), msg="checking created RO manifest dir")
        self.deleteRoFixture(rodir)
        return

    def testStatus(self):
        """
        Display status of created RO

        ro status -d rodir
        """
        rodir = self.createTestRo("data/ro-test-1", "RO test status", "ro-testRoStatus")
        args = [
            "ro", "status",
            "-d", rodir,
            "-v"
            ]
        with SwitchStdout(self.outstr):
            status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, args)
        outtxt = self.outstr.getvalue()
        assert status == 0, outtxt
        self.assertEqual(outtxt.count("ro status"), 1)
        self.assertRegexpMatches(outtxt, "identifier.*ro-testRoStatus")
        self.assertRegexpMatches(outtxt, "title.*RO test status")
        self.assertRegexpMatches(outtxt, "path.*%s"%rodir)
        self.assertRegexpMatches(outtxt, "creator.*%s"%ro_test_config.ROBOXUSERNAME)
        self.assertRegexpMatches(outtxt, "created")
        self.deleteTestRo(rodir)
        return

    def testStatusDefault(self):
        """
        Display status of created RO

        ro status 
        """
        rodir = self.createTestRo("data/ro-test-1", "RO test status", "ro-testRoStatus")
        args = [
            "ro", "status",
            "-v"
            ]
        configbase = os.path.abspath(ro_test_config.CONFIGDIR)
        save_cwd = os.getcwd()
        os.chdir(rodir+"/subdir1/")
        with SwitchStdout(self.outstr):
            status = ro.runCommand(configbase, ro_test_config.ROBASEDIR, args)
        os.chdir(save_cwd)
        outtxt = self.outstr.getvalue()
        assert status == 0, outtxt
        self.assertEqual(outtxt.count("ro status"), 1)
        self.assertRegexpMatches(outtxt, "identifier.*ro-testRoStatus")
        self.assertRegexpMatches(outtxt, "title.*RO test status")
        self.assertRegexpMatches(outtxt, "path.*%s"%rodir)
        self.assertRegexpMatches(outtxt, "creator.*%s"%ro_test_config.ROBOXUSERNAME)
        self.assertRegexpMatches(outtxt, "created")
        self.deleteTestRo(rodir)
        return

    def testList(self):
        """
        Display contents of created RO

        ro ls -d rodir
        """
        rodir = self.createTestRo("data/ro-test-1", "RO test list", "ro-testRoList")
        args = [
            "ro", "ls",
            "-d", rodir,
            "-v"
            ]
        with SwitchStdout(self.outstr):
            status = ro.runCommand(ro_test_config.CONFIGDIR, ro_test_config.ROBASEDIR, args)
        outtxt = self.outstr.getvalue()
        assert status == 0, outtxt
        self.assertEqual(outtxt.count("ro list"), 1)
        self.assertRegexpMatches(outtxt, "README-ro-test-1")
        self.assertRegexpMatches(outtxt, "subdir1/subdir1-file.txt")
        self.assertRegexpMatches(outtxt, "subdir2/subdir2-file.txt")
        self.deleteTestRo(rodir)
        return

    def testListDefault(self):
        """
        Display contents of created RO containing current directory

        ro ls
        """
        rodir = self.createTestRo("data/ro-test-1", "RO test list", "ro-testRoList")
        args = [
            "ro", "ls",
            "-v"
            ]
        configbase = os.path.abspath(ro_test_config.CONFIGDIR)
        save_cwd = os.getcwd()
        os.chdir(rodir+"/subdir2/")
        with SwitchStdout(self.outstr):
            status = ro.runCommand(configbase, ro_test_config.ROBASEDIR, args)
        os.chdir(save_cwd)
        outtxt = self.outstr.getvalue()
        assert status == 0, outtxt
        self.assertEqual(outtxt.count("ro list"), 1)
        self.assertRegexpMatches(outtxt, "README-ro-test-1")
        self.assertRegexpMatches(outtxt, "subdir1/subdir1-file.txt")
        self.assertRegexpMatches(outtxt, "subdir2/subdir2-file.txt")
        self.deleteTestRo(rodir)
        return

    # Sentinel/placeholder tests

    def testUnits(self):
        assert (True)

    def testComponents(self):
        assert (True)

    def testIntegration(self):
        assert (True)

    def testPending(self):
        assert (False), "Pending tests follow"

# Assemble test suite

def getTestSuite(select="unit"):
    """
    Get test suite

    select  is one of the following:
            "unit"      return suite of unit tests only
            "component" return suite of unit and component tests
            "all"       return suite of unit, component and integration tests
            "pending"   return suite of pending tests
            name        a single named test to be run
    """
    testdict = {
        "unit":
            [ "testUnits"
            , "testNull"
            #, "testHelpVersion"
            #, "testHelpOptions"
            , "testHelpCommands"
            , "testInvalidCommand"
            , "testConfig"
            , "testConfigVerbose"
            , "testCreate"
            , "testCreateDefaults"
            , "testCreateBadDir"
            , "testStatus"
            , "testStatusDefault"
            , "testList"
            , "testListDefault"
            ],
        "component":
            [ "testComponents"
            ],
        "integration":
            [ "testIntegration"
            ],
        "pending":
            [ "testPending"
            ]
        }
    return TestUtils.getTestSuite(TestBasicCommands, testdict, select=select)

if __name__ == "__main__":
    TestUtils.runTests("TestBasicCommands.log", getTestSuite, sys.argv)

# End.
