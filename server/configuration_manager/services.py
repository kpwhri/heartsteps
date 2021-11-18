from enum import Enum

from django.contrib.auth.models import User

from participants.models import Study, Cohort, Participant

from .models import Configuration, QueryString


class ConfigurationManagerService:
    class LEVEL(Enum):
        SYSTEM_LEVEL = 0
        STUDY_LEVEL = 1
        COHORT_LEVEL = 2
        PARTICIPANT_LEVEL = 3
        USER_LEVEL = 4
        TIMESPAN_LEVEL = 5
        TIME_OF_DAY_LEVEL = 6

    class NoSuchQueryException(Exception):
        pass

    def __init__(self, prefix):
        self.prefix = prefix

    def __handle_multiple_values(self, value_list):
        if len(value_list) == 1:
            return value_list[0]
        if len(value_list) == 0:
            return None
        if len(value_list) > 1:
            # if there are multiple configurations
            all_same = True

            for i in range(0, len(value_list) - 1):
                all_same = all_same and (
                    value_list[i] == value_list[i+1])

            if all_same:
                return value_list[0]
            else:
                raise Configuration.MultipleConfigurationsAreNotAllowed()

    def query(self, query_str, filter):
        if self.prefix is not None:
            query_str = "{}.{}".format(self.prefix, query_str)

        query_level = QueryString.get_level(query_str)

        # if query_level is None:
        #     raise ConfigurationManagerService.NoSuchQueryException(
        #         "{} is not defined anywhere.".format(query_str))
        # else:
        #     if query_level == ConfigurationManagerService.LEVEL.SYSTEM_LEVEL:
        #         return Configuration.try_to_get(query_str)
        #     elif query_level == ConfigurationManagerService.LEVEL.STUDY_LEVEL:
        #         return self.__handle_multiple_values(
        #             list(
        #                 map(
        #                     lambda participant: Configuration.try_to_get(
        #                         query_str=query_str, object1=participant.cohort.study.id),
        #                     Participant.objects.filter(user=user)
        #                 )
        #             )
        #         )
        #     elif query_level == ConfigurationManagerService.LEVEL.COHORT_LEVEL:
        #         return self.__handle_multiple_values(
        #             list(
        #                 map(
        #                     lambda participant: Configuration.try_to_get(
        #                         query_str=query_str, object1=participant.cohort.id),
        #                     Participant.objects.filter(user=user)
        #                 )
        #             )
        #         )
        #     elif query_level == ConfigurationManagerService.LEVEL.PARTICIPANT_LEVEL:
        #         return self.__handle_multiple_values(
        #             list(
        #                 map(
        #                     lambda participant: Configuration.try_to_get(
        #                         query_str=query_str, object1=participant.id),
        #                     Participant.objects.filter(user=user)
        #                 )
        #             )
        #         )
        #     elif query_level == ConfigurationManagerService.LEVEL.USER_LEVEL:
        #         return Configuration.try_to_get(query_str, object1=user.id)
            