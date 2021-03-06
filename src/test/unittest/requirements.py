# SPDX-License-Identifier: BSD-3-Clause
# Copyright 2020, Intel Corporation
#
"""Various requirements"""


import subprocess as sp
import ctypes
import sys
import os

import configurator as conf
import context as ctx
import futils


NDCTL_MIN_VERSION = '63'


class Requirements:
    """Various requirements"""
    def __init__(self):
        self.cfg = conf.Configurator().config

    def _check_pkgconfig(self, pkg, min_ver):
        """
        Run pkg-config to check if a package is installed
        """
        proc = sp.run(['pkg-config', pkg, '--atleast-version', min_ver],
                      stdout=sp.PIPE, stderr=sp.STDOUT)
        return proc.returncode == 0

    def _check_is_admin(self):
        if sys.platform == 'win32':
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.getuid() == 0

    def _check_ndctl_req_is_met(self, tc):
        """
        Check if all conditions for the ndctl requirement are met
        """
        require_ndctl, _ = ctx.get_requirement(tc, 'require_ndctl', ())
        if not require_ndctl:
            return True

        ndctl_enable = os.environ.get('NDCTL_ENABLE')
        if ndctl_enable == 'n':
            raise futils.Skip('libndctl is disabled (NDCTL_ENABLE == \'n\')')

        is_ndctl = self._check_pkgconfig('libndctl', NDCTL_MIN_VERSION)
        if not is_ndctl:
            raise futils.Skip('libndctl (>=v{}) is not installed'
                              .format(NDCTL_MIN_VERSION))
        return True

    def _check_admin_req_is_met(self, tc):
        """
        Check if all conditions for the admin requirement are met
        """
        require_admin, _ = ctx.get_requirement(tc, 'require_admin', ())
        if not require_admin:
            # admin is not required
            return True

        if not self.cfg.enable_admin_tests:
            raise futils.Skip('admin tests are not enabled in config '
                              '(enable_admin_tests)')

        if not self._check_is_admin():
            raise futils.Fail('Error: admin tests are enabled in config, '
                              'but the user does not have administrative '
                              'privileges')
        # user is admin
        return True

    def check_if_all_requirements_are_met(self, tc):
        if not self._check_ndctl_req_is_met(tc):
            return False
        if not self._check_admin_req_is_met(tc):
            return False
        """More requirements can be checked here"""
        return True


def require_ndctl(tc):
    """Enable test only if ndctl is installed"""
    ctx.add_requirement(tc, 'require_ndctl', True)
    return tc


def require_admin(tc):
    """
    Disable test if "enable_admin_tests" configuration is not set
    """
    ctx.add_requirement(tc, 'require_admin', True)
    return tc
