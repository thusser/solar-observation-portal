from django.core.cache import cache
from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.permissions import AllowAny, IsAdminUser
from django.http import HttpResponseBadRequest
from django.utils import timezone
from django.utils.module_loading import import_string
from django.conf import settings
from dateutil.parser import parse
from datetime import timedelta
from rest_framework.views import APIView
import logging

from observation_portal import settings
from observation_portal.common.configdb import configdb
from observation_portal.common.telescope_states import ElasticSearchException
from observation_portal.requestgroups.request_utils import get_airmasses_for_request_at_sites
from observation_portal.requestgroups.contention import Contention, Pressure
from observation_portal.requestgroups.filters import TelescopeAvailabilityFilter, TelescopeStatesFilter
from observation_portal.requestgroups.serializers import TelescopeAvailabilitySerializer, TelescopeStatesSerializer
from observation_portal.common.mixins import GetSerializerMixin

logger = logging.getLogger(__name__)


def get_start_end_parameters(request, default_days_back):
    try:
        start = parse(request.query_params.get('start'))
    except TypeError:
        start = timezone.now() - timedelta(days=default_days_back)
    start = start.replace(tzinfo=timezone.utc)
    try:
        end = parse(request.query_params.get('end'))
    except TypeError:
        end = timezone.now()
    end = end.replace(tzinfo=timezone.utc)
    return start, end


class TelescopeStatesView(APIView, GetSerializerMixin):
    """
    Retrieves the telescope states for all telescopes between the start and end times
    """
    permission_classes = (AllowAny,)
    schema=AutoSchema(tags=['Utility'])
    filter_class = TelescopeStatesFilter
    filter_backends = (DjangoFilterBackend,)
    serializer_class = import_string(settings.SERIALIZERS['requestgroups']['TelescopeStates'])

    def get(self, request):
        try:
            start, end = get_start_end_parameters(request, default_days_back=0)
        except ValueError as e:
            return HttpResponseBadRequest(str(e))
        sites = request.query_params.getlist('site')
        telescopes = request.query_params.getlist('telescope')

        str_telescope_states = TelescopeStatesSerializer({'start': start,
                                                          'end': end,
                                                          'sites': sites,
                                                          'telescopes': telescopes}).data

        return Response(str_telescope_states)


class TelescopeAvailabilityView(APIView):
    """
    Retrieves the nightly percent availability of each telescope between the start and end times
    """
    permission_classes = (AllowAny,)
    schema=AutoSchema(tags=['Utility'])
    filter_class = TelescopeAvailabilityFilter
    filter_backends = (DjangoFilterBackend,)

    def get(self, request):
        try:
            start, end = get_start_end_parameters(request, default_days_back=1)
        except ValueError as e:
            return HttpResponseBadRequest(str(e))
        combine = request.query_params.get('combine')
        sites = request.query_params.getlist('site')
        telescopes = request.query_params.getlist('telescope')



        try:
            telescope_availability = TelescopeAvailabilitySerializer({'start': start,
                                                                      'end': end,
                                                                      'sites': sites,
                                                                      'telescopes': telescopes,
                                                                      'combine': combine}).data
        except ElasticSearchException:
            logger.warning('Error connecting to ElasticSearch. Is SBA reachable?')
            return Response('ConnectionError')
        return Response(telescope_availability)


class AirmassView(APIView):
    """
    Gets the airmasses for the request at available sites
    """
    permission_classes = (AllowAny,)
    schema=AutoSchema(tags=['Requests'])

    def post(self, request):
        serializer = import_string(settings.SERIALIZERS['requestgroups']['Request'])(data=request.data)
        if serializer.is_valid():
            return Response(get_airmasses_for_request_at_sites(
                serializer.validated_data, is_staff=request.user.is_staff
            ))
        else:
            return Response(serializer.errors)


class InstrumentsInformationView(APIView):
    permission_classes = (AllowAny,)
    schema=AutoSchema(tags=['Utility'])

    def get(self, request):
        info = {}
        # Staff users by default should see all instruments, but can request only schedulable instruments.
        # Non-staff users are only allowed access to schedulable instruments.
        if request.user.is_staff:
            only_schedulable = request.query_params.get('only_schedulable', False)
        else:
            only_schedulable = True

        requested_instrument_type = request.query_params.get('instrument_type', '')
        location = {
            'site': request.query_params.get('site', ''),
            'enclosure': request.query_params.get('enclosure', ''),
            'telescope_class': request.query_params.get('telescope_class', ''),
            'telescope': request.query_params.get('telescope', ''),
        }
        for instrument_type in configdb.get_instrument_type_codes(location=location, only_schedulable=only_schedulable):
            if not requested_instrument_type or requested_instrument_type.lower() == instrument_type.lower():
                info[instrument_type] = {
                    'type': configdb.get_instrument_type_category(instrument_type),
                    'class': configdb.get_instrument_type_telescope_class(instrument_type),
                    'name': configdb.get_instrument_type_full_name(instrument_type),
                    'optical_elements': configdb.get_optical_elements(instrument_type),
                    'modes': configdb.get_modes_by_type(instrument_type),
                    'default_acceptability_threshold': configdb.get_default_acceptability_threshold(instrument_type),
                    'configuration_types': configdb.get_configuration_types(instrument_type),
                    'camera_type': {
                        'science_field_of_view': configdb.get_diagonal_ccd_fov(instrument_type, autoguider=False),
                        'autoguider_field_of_view': configdb.get_diagonal_ccd_fov(instrument_type, autoguider=True),
                        'pixel_scale': configdb.get_pixel_scale(instrument_type)
                    }
                }
        return Response(info)


class ContentionView(APIView):
    permission_classes = (AllowAny,)
    schema=AutoSchema(tags=['Utility'])

    def get(self, request, instrument_type):
        if request.user.is_staff:
            contention = Contention(instrument_type, anonymous=False)
        else:
            contention = Contention(instrument_type)
        return Response(contention.data())


class PressureView(APIView):
    permission_classes = (AllowAny,)
    schema=AutoSchema(tags=['Utility'])

    def get(self, request):
        instrument_type = request.GET.get('instrument')
        site = request.GET.get('site')
        if request.user.is_staff:
            pressure = Pressure(instrument_type, site, anonymous=False)
        else:
            pressure = Pressure(instrument_type, site)
        return Response(pressure.data())


class ObservationPortalLastChangedView(APIView):
    '''
        Returns the datetime of the last status of requests change or new requests addition
    '''
    permission_classes = (IsAdminUser,)
    schema=AutoSchema(tags=['RequestGroups'])

    def get(self, request):
        telescope_classes = request.GET.getlist('telescope_class', ['all'])
        most_recent_change_time = timezone.now() - timedelta(days=7)
        for telescope_class in telescope_classes:
            most_recent_change_time = max(most_recent_change_time, cache.get(f"observation_portal_last_change_time_{telescope_class}", timezone.now() - timedelta(days=7)))

        return Response({'last_change_time': most_recent_change_time})
