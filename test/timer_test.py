import unittest
import time

from plclib.timer import Timer


class TimerTest(unittest.TestCase):
    def test_noDelay(self):
        instance = Timer(0.0, 0.0)
        self.assertFalse(instance.output)
        instance.input(True)
        self.assertTrue(instance.output)
        instance.input(False)
        self.assertFalse(instance.output)
        instance.input(True)
        self.assertTrue(instance.output)

    def test_onDelay(self):
        instance = Timer(1.0, 0.0)
        self.assertFalse(instance.output)
        instance.input(True)
        time.sleep(0.2)
        self.assertFalse(instance.output)
        time.sleep(0.9)
        self.assertTrue(instance.output)
        instance.input(False)
        self.assertFalse(instance.output)

    def test_offDelay(self):
        instance = Timer(0.0, 1.0)
        self.assertFalse(instance.output)
        instance.input(True)
        self.assertTrue(instance.output)
        instance.input(False)
        self.assertTrue(instance.output)
        time.sleep(0.5)
        self.assertTrue(instance.output)
        time.sleep(0.6)
        self.assertFalse(instance.output)

    def test_onDelay_and_offDelay(self):
        instance = Timer(0.5, 0.5)
        self.assertFalse(instance.output)
        instance.input(True)
        self.assertFalse(instance.output)
        time.sleep(0.5)
        self.assertTrue(instance.output)
        instance.input(False)
        self.assertTrue(instance.output)
        time.sleep(0.5)
        self.assertFalse(instance.output)

