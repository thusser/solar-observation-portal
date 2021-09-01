from datetime import timedelta

from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from django.core.cache import cache
from django.utils import timezone
from rest_framework.response import Response
from django_filters.rest_framework.backends import DjangoFilterBackend
from django.utils.module_loading import import_string

from observation_portal.common.configdb import configdb
from observation_portal.common.mixins import GetSerializerMixin
from observation_portal.observations.filters import LastScheduledFilter
from observation_portal.common.schema import ObservationPortalSchema
from observation_portal import settings


class LastScheduledView(APIView, GetSerializerMixin):
    """
        Returns the datetime of the last time new observations were submitted. This endpoint is expected to be polled
        frequently (~every 5 seconds) to for a client to decide if it needs to pull down the schedule or not.

        We are only updating when observations are submitted, and not when they are cancelled, because a site should
        not really care if the only change was removing things from it's schedule.
    """
    permission_classes = (IsAdminUser,)
    schema=ObservationPortalSchema(tags=['Observations'])
    filter_backends = (DjangoFilterBackend,)
    filter_class = LastScheduledFilter
    serializer_class = import_string(settings.SERIALIZERS['observations']['LastScheduled'])

    def get(self, request):
        site = request.query_params.get('site')
        cache_key = 'observation_portal_last_schedule_time'
        if site:
            cache_key += f"_{site}"
            last_schedule_time = cache.get(cache_key, timezone.now() - timedelta(days=7))
        else:
            sites = configdb.get_site_tuples()
            keys = [cache_key + "_" + s[0] for s in sites]
            cache_dict = cache.get_many(keys)
            last_schedule_time = max(list(cache_dict.values()) + [timezone.now() - timedelta(days=7)])

        response_serializer = self.serializer_class(data={'last_schedule_time': last_schedule_time})
        if response_serializer.is_valid():
            return Response(response_serializer.validated_data, status=200)
        else:
            return Response(response_serializer.errors, status=400)

    def get_endpoint_name(self):
        return 'getLastScheduled'
