from django.test import TestCase

from heartsteps.tests import HeartStepsTestCase

from configuration_manager.models import QueryString as qs, Configuration as Conf


class Configuration_TestCase(HeartStepsTestCase):
    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().setUp()
        Conf.objects.all().delete()

    def test_create_conf_without_registering(self):
        # system-wide conf
        query_str = "is world alive"
        self.assertRaises(qs.QueryIsNotRegistered, Conf.create,
                          query_str, None, True)

    def test_create_conf_with_registering(self):
        query_str = "is world alive"
        qs.register(query_str, self.user, [])
        Conf.create(query_str, None, True)

    def test_create_conf(self):
        # system-wide conf
        query_str = "is world alive"
        qs.register(query_str, self.user, [])
        Conf.create(query_str, None, True)
        self.assertEqual(Conf.try_to_get(query_str, None), True)
        self.assertEqual(Conf.try_to_get(query_str), True)

    def test_create_conf_2(self):
        # study-wide conf
        query_str = "is junghwan's study"
        qs.register(query_str, self.user, ["study.PI"])
        Conf.create(query_str, {"study.PI": "junghwan"}, True)
        self.assertEqual(Conf.try_to_get(
            query_str, {"study.PI": "junghwan"}), True)
        self.assertEqual(Conf.try_to_get(
            query_str, {"study.PI": "nick"}), None)

    def test_create_conf_2_2(self):
        # study-wide conf
        query_str = "is junghwan's study"
        qs.register(query_str, self.user, ["study.PI"])
        Conf.create(query_str, {"study.PI": "junghwan"}, True)
        self.assertRaises(
            qs.RequiredFilterPatternDoesNotMatch,
            Conf.try_to_get,
            query_str,
            {"study.PI__in": ["junghwan", "nick"]}
        )

    def test_create_conf_2_3(self):
        # study-wide conf
        query_str = "is junghwan's study"
        qs.register(query_str, self.user, ["study.PI"])
        Conf.create(query_str, {"study.PI": "junghwan"}, True)
        self.assertEqual(Conf.try_to_get(
            query_str, {"study.PI": "junghwan"}), True)
        self.assertEqual(Conf.try_to_get(
            query_str, {"study.PI": "nick"}), None)
        self.assertEqual(Conf.try_to_get(query_str, {
                         "study.PI__in": ["junghwan", "nick"]}, filter_pattern_check=False), True)
        self.assertEqual(Conf.try_to_get(query_str, {
                         "study.PI__in": ["pedja", "nick"]}, filter_pattern_check=False), None)

    def test_create_conf_3(self):
        # study-wide multiple conf
        query_str = "is junghwan's study"
        qs.register(query_str, self.user, ["PI"])
        Conf.create(query_str, {"PI": "junghwan"}, True)
        Conf.create(query_str, {"PI": "nick"}, True)

        self.assertEqual(Conf.try_to_get(
            query_str, {"PI": "junghwan"}), True)
        self.assertEqual(Conf.try_to_get(
            query_str, {"PI": "nick"}), True)

    def test_create_conf_4(self):
        # participant-based conf
        query_str = "is nlm study"
        qs.register(query_str, self.user, ["study name", "enrollment token"])
        Conf.create(query_str, {
                    "study name": "nlm", "enrollment token": "test-1234"}, True)
        Conf.create(query_str, {
                    "study name": "nlm", "enrollment token": "test-2345"}, True)

        self.assertEqual(Conf.try_to_get(query_str, {
                         "study name": "nlm", "enrollment token": "test-1234"}), True)
        self.assertEqual(Conf.try_to_get(query_str, {
                         "study name": "nlm", "enrollment token": "test-3456"}), None)

    def test_create_conf_5(self):
        # incorrect query pattern
        query_str = "is nlm study"
        qs.register(query_str, self.user, ["study name", "enrollment token"])
        Conf.create(query_str, {
                    "study name": "nlm", "enrollment token": "test-1234"}, True)
        Conf.create(query_str, {
                    "study name": "nlm", "enrollment token": "test-2345"}, True)

        self.assertRaises(
            qs.RequiredFilterPatternDoesNotMatch,
            Conf.try_to_get,
            query_str,
            {"study name": "nlm"}
        )

    def test_create_conf_6(self):
        # cohort-based conf
        query_str = "is nlm study"
        qs.register(query_str, self.user, ["study name", "cohort name"])
        Conf.create(query_str, {
                    "study name": "nlm", "cohort name": "control"}, True)

        self.assertEqual(Conf.try_to_get(query_str, {
                         "study name": "nlm", "cohort name": "control"}), True)
        self.assertEqual(Conf.try_to_get(query_str, {
                         "study name": "nlm", "cohort name": "experiment"}), None)

    def test_create_conf_6_2(self):
        # cohort-based conf
        query_str = "is nlm study"
        qs.register(query_str, self.user, ["study name", "cohort name"])
        self.assertRaises(
            qs.RequiredFilterPatternDoesNotMatch,
            Conf.create,
            query_str,
            {"study name": "nlm", "enrollment token": "test-1234"}, 
            True
        )

    def test_create_conf_6_3(self):
        # cohort-based conf
        query_str = "is nlm study"
        qs.register(query_str, self.user, ["study name", "cohort name"])
        Conf.create(query_str, {
                    "study name": "nlm", "cohort name": "control"}, True)

        self.assertEqual(Conf.try_to_get(query_str, {
                         "study name": "nlm", "cohort name": "control"}), True)
        self.assertEqual(Conf.try_to_get(query_str, {
                         "study name": "nlm", "cohort name": "experiment"}), None)