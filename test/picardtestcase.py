# -*- coding: utf-8 -*-
import json
import os
import shutil
import struct
from tempfile import (
    mkdtemp,
    mkstemp,
)
import unittest

from PyQt5 import QtCore

from picard import (
    config,
    log,
)
from picard.releasegroup import ReleaseGroup


class FakeTagger(QtCore.QObject):

    tagger_stats_changed = QtCore.pyqtSignal()

    def __init__(self):
        QtCore.QObject.__init__(self)
        QtCore.QObject.config = config
        QtCore.QObject.log = log
        self.tagger_stats_changed.connect(self.emit)
        self.exit_cleanup = []
        self.files = {}
        self.stopping = False

    def register_cleanup(self, func):
        self.exit_cleanup.append(func)

    def run_cleanup(self):
        for f in self.exit_cleanup:
            f()

    def emit(self, *args):
        pass

    def get_release_group_by_id(self, rg_id):  # pylint: disable=no-self-use
        return ReleaseGroup(rg_id)


class PicardTestCase(unittest.TestCase):
    def setUp(self):
        self.tagger = FakeTagger()
        QtCore.QObject.tagger = self.tagger
        self.addCleanup(self.tagger.run_cleanup)
        config.setting = {}

    def mktmpdir(self, ignore_errors=False):
        tmpdir = mkdtemp(suffix=self.__class__.__name__)
        self.addCleanup(shutil.rmtree, tmpdir, ignore_errors=ignore_errors)
        return tmpdir

    def copy_file_tmp(self, filepath, ext):
        fd, copy = mkstemp(suffix=ext)
        os.close(fd)
        self.addCleanup(self.remove_file_tmp, copy)
        shutil.copy(filepath, copy)
        return copy

    @staticmethod
    def remove_file_tmp(filepath):
        if os.path.isfile(filepath):
            os.unlink(filepath)


def create_fake_png(extra):
    """Creates fake PNG data that satisfies Picard's internal image type detection"""
    return b'\x89PNG\x0D\x0A\x1A\x0A' + (b'a' * 4) + b'IHDR' + struct.pack('>LL', 100, 100) + extra


def load_test_json(filename):
    with open(os.path.join('test', 'data', 'ws_data', filename), encoding='utf-8') as f:
        return json.load(f)
