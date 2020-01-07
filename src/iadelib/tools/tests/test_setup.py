# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from Products.CMFPlone.utils import get_installer
from iadelib.tools.testing import IADELIB_TOOLS_INTEGRATION_TESTING  # noqa

import unittest


class TestSetup(unittest.TestCase):
    """Test that iadelib.tools is properly installed."""

    layer = IADELIB_TOOLS_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        self.installer = get_installer(self.portal, self.layer["request"])

    def test_product_installed(self):
        """Test if iadelib.tools is installed."""
        self.assertTrue(self.installer.is_product_installed("iadelib.tools"))

    def test_browserlayer(self):
        """Test that IIadelibToolsLayer is registered."""
        from iadelib.tools.interfaces import IIadelibToolsLayer
        from plone.browserlayer import utils

        self.assertIn(IIadelibToolsLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = IADELIB_TOOLS_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.installer = get_installer(self.portal, self.layer["request"])
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.installer.uninstall_product("iadelib.tools")
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if iadelib.tools is cleanly uninstalled."""
        self.assertFalse(self.installer.is_product_installed("iadelib.tools"))

    def test_browserlayer_removed(self):
        """Test that IIadelibToolsLayer is removed."""
        from iadelib.tools.interfaces import IIadelibToolsLayer
        from plone.browserlayer import utils

        self.assertNotIn(IIadelibToolsLayer, utils.registered_layers())
