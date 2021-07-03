from django.db import models
from django.contrib.auth.models import User
from django.db import transaction
from django.db.utils import IntegrityError

import json


class QueryString(models.Model):
    class QueryStringIsAlreadyTaken(Exception):
        pass

    class TooManyObjectsException(Exception):
        pass

    class FilterPatternCannotBeChanged(Exception):
        pass

    class QueryIsNotRegistered(Exception):
        pass

    class FilterPatternHasNotSet(Exception):
        pass

    class RequiredFilterPatternDoesNotMatch(Exception):
        pass

    query_str = models.CharField(max_length=512, unique=True)
    who_created = models.ForeignKey(User, on_delete=models.CASCADE)
    when_created = models.DateTimeField(auto_now_add=True)
    filter_pattern = models.JSONField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['query_str'])
        ]

    def register(query_str, who_created, expected_filter_keys):
        if QueryString.is_registered(query_str):
            raise QueryString.QueryStringIsAlreadyTaken(
                "{} query is already taken.".format(query_str))
        else:
            return QueryString.objects.create(
                query_str=query_str, who_created=who_created, filter_pattern=expected_filter_keys)

    def get(query_str):
        return QueryString.objects.get(query_str=query_str)

    def is_registered(query_str):
        return QueryString.objects.filter(query_str=query_str).exists()

    def does_filter_pattern_match(query_str, current_filter_dict):
        registered_filter_pattern = QueryString.get(query_str).filter_pattern
        registered_filter_pattern = set(registered_filter_pattern)
        if registered_filter_pattern is None:
            raise QueryString.FilterPatternHasNotSet
        else:
            if current_filter_dict is None:
                current_filter_pattern = set([])
            else:
                current_filter_pattern = set(current_filter_dict)
            
            return registered_filter_pattern == current_filter_pattern


class Configuration(models.Model):
    class MultipleConfigurationsAreNotAllowed(Exception):
        pass

    query_str = models.CharField(max_length=512)
    attr = models.JSONField(null=True)
    value = models.JSONField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['query_str'])
        ]
        unique_together = [
            ('query_str', 'attr')]

    def try_to_get(query_str, filter_dict=None, filter_pattern_check=True):
        if filter_pattern_check:
            if not QueryString.does_filter_pattern_match(query_str, filter_dict):
                raise QueryString.RequiredFilterPatternDoesNotMatch()

        query = Configuration.get_ORM_query(query_str, filter_dict)

        query_count = query.count()
        if query_count == 0:
            # no configuration has been made under the query
            return None
        elif query_count > 1:
            # it is not possible to make same configuration because "unique together" exists.
            # however, user can query incompletely. In this case,
            raise Configuration.MultipleConfigurationsAreNotAllowed()
        else:
            # only one configuration is found
            obj = query.first()

            # return json.loads(obj.value)
            return obj.value

    def get_ORM_query(query_str, filter_dict):
        query = Configuration.objects

        if filter_dict is not None:
            for k, v in filter_dict.items():
                query = query.filter(**{"attr__{}".format(k): v})
        return query

    def create(query_str, attr, value):
        if QueryString.is_registered(query_str):
            if QueryString.does_filter_pattern_match(query_str, attr):
                query = Configuration.get_ORM_query(query_str, attr)

                return Configuration.objects.create(query_str=query_str, attr=attr, value=value)
            else:
                raise QueryString.RequiredFilterPatternDoesNotMatch
        else:
            raise QueryString.QueryIsNotRegistered(
                "Query is not registered: {}. Please run QueryString.register() first.".format(query_str))
