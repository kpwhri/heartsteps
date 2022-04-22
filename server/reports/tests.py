from unittest import TestCase

from .tasks import render_report


class ReportRenderTest(TestCase):
    def test_render_report(self):
        render_report(force_reset=True)