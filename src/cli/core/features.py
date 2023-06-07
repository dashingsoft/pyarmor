#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
#############################################################
#                                                           #
#      Copyright @ 2023 -  Dashingsoft corp.                #
#      All rights reserved.                                 #
#                                                           #
#      Pyarmor                                              #
#                                                           #
#      Version: 8.2.4 -                                     #
#                                                           #
#############################################################
#
#
#  @File: pyarmor/core/features.py
#
#  @Author: Jondy Zhao (pyarmor@163.com)
#
#  @Create Date: Tue Jun  6 07:57:55 CST 2023
#

# Each log
#    revision, age, (new features), (changed features), (removed features)
__CHANGE_LOGS__ = (
    (1, 0, (), (), ()),
)


class PyarmorFeature(object):

    def features(self):
        '''return features list from change logs'''
        result = set()
        [result.update(item[2]) for item in __CHANGE_LOGS__]
        return result

    def life(self, feature):
        '''return first pyarmor_runtime version and last verstion to support
        this feature.'''
        minor, fin = None
        for item in __CHANGE_LOGS__:
            if feature in item[2] + item[3]:
                minor = item[0]
            if feature in item[-1]:
                fin = item[0]
        return minor, fin
