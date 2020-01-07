# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import iadelib.tools


class IadelibToolsLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=iadelib.tools)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "iadelib.tools:default")


IADELIB_TOOLS_FIXTURE = IadelibToolsLayer()


IADELIB_TOOLS_INTEGRATION_TESTING = IntegrationTesting(
    bases=(IADELIB_TOOLS_FIXTURE,), name="IadelibToolsLayer:IntegrationTesting"
)


IADELIB_TOOLS_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(IADELIB_TOOLS_FIXTURE,), name="IadelibToolsLayer:FunctionalTesting"
)


IADELIB_TOOLS_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(IADELIB_TOOLS_FIXTURE, REMOTE_LIBRARY_BUNDLE_FIXTURE, z2.ZSERVER_FIXTURE),
    name="IadelibToolsLayer:AcceptanceTesting",
)
