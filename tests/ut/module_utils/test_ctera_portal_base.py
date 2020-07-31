import unittest.mock as mock

try:
    from cterasdk import CTERAException
except ImportError:  # pragma: no cover
    pass

from ansible_collections.ctera.ctera.plugins.module_utils import ctera_portal_base
from tests.ut.mocks.gateway_ansible_module_mock import mock_gateway_ansible_module
from tests.ut.base import BaseTest


class CteraPortalTestChild(ctera_portal_base.CteraPortalBase):

    def __init__(self, success):
        super().__init__({})
        self._success = success
        self.execute_called = False
        self.generic_failure_message_called = False

    @property
    def _generic_failure_message(self):
        self.generic_failure_message_called = True
        return "Test Child"

    def _execute(self):
        self.execute_called = True
        if not self._success:
            raise CTERAException("Testing Failure")

class PortalsMock():
    def __init__(self):
        self.browse_tenant = None

    def browse(self, tenant):
        self.browse_tenant = tenant


class PortalMock():
    def __init__(self):
        self.portals = PortalsMock()

class TestCteraPortalBase(BaseTest):  #pylint: disable=too-many-public-methods

    def setUp(self):
        super().setUp()
        self._obj_mock = mock_gateway_ansible_module(self, "ansible_collections.ctera.ctera.plugins.module_utils.ctera_portal_base.PortalAnsibleModule")

    def test_run_success(self):
        runner = CteraPortalTestChild(True)
        runner.run()
        self._obj_mock.ctera_portal.assert_called_once_with(login=True)
        self.assertTrue(runner.execute_called)
        self.assertFalse(runner.generic_failure_message_called)
        self._obj_mock.ctera_logout.assert_called_once_with()
        self._obj_mock.ctera_exit.assert_called_once_with()

    def test_run_failure(self):
        runner = CteraPortalTestChild(False)
        runner.run()
        self._obj_mock.ctera_portal.assert_called_once_with(login=True)
        self.assertTrue(runner.execute_called)
        self.assertTrue(runner.generic_failure_message_called)
        self._obj_mock.ctera_logout.assert_called_once_with()
        self._obj_mock.ctera_exit.assert_called_once_with()

    def test_run_tenant(self):
        for with_tenant in [True, False]:
            self._test_run_tenant(with_tenant)

    def _test_run_tenant(self, with_tenant):
        self._obj_mock.ctera_logout.reset_mock()
        self._obj_mock.ctera_exit.reset_mock()
        portal_mock = PortalMock()
        runner = CteraPortalTestChild(True)
        if with_tenant:
            runner.parameters = dict(tenant='test')
        self._obj_mock.ctera_portal = mock.MagicMock(return_value=portal_mock)
        runner.run()
        self._obj_mock.ctera_portal.assert_called_once_with(login=True)
        if with_tenant:
            self.assertEqual(portal_mock.portals.browse_tenant, 'test')
        else:
            self.assertIsNone(portal_mock.portals.browse_tenant)
        self.assertTrue(runner.execute_called)
        self.assertFalse(runner.generic_failure_message_called)
        self._obj_mock.ctera_logout.assert_called_once_with()
        self._obj_mock.ctera_exit.assert_called_once_with()
