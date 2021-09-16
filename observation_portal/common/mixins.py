from django_filters import fields, IsoDateTimeFilter
from django.contrib.auth.mixins import UserPassesTestMixin
from django.forms import DateTimeField
from rest_framework.response import Response


class ListAsDictMixin(object):
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        json_models = [model.as_dict() for model in page]
        return self.get_paginated_response(json_models)


class DetailAsDictMixin:
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        return Response(instance.as_dict())


# from https://stackoverflow.com/questions/14666199/how-do-i-create-multiple-model-instances-with-django-rest-framework
class CreateListModelMixin(object):
    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get('data', {}), list):
            kwargs['many'] = True
        return super().get_serializer(*args, **kwargs)


class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


# Use the CustomIsoDateTimeFilterMixin in a FilterSet. Makes all IsoDateTimeFilters within the FilterSet able to parse
# ISO 8601 datetimes, as well as all the other usual formats that the DateTimeFilter can do.
# https://django-filter.readthedocs.io/en/master/ref/fields.html#isodatetimefield
class CustomIsoDateTimeField(fields.IsoDateTimeField):
    input_formats = [fields.IsoDateTimeField.ISO_8601] + list(DateTimeField.input_formats)


class CustomIsoDateTimeFilterMixin(object):
    @classmethod
    def get_filters(cls):
        filters = super().get_filters()
        for f in filters.values():
            if isinstance(f, IsoDateTimeFilter):
                f.field_class = CustomIsoDateTimeField
        return filters


class ExtraParamsFormatter(object):
    """ This should be mixed in with Serializers that have extra_params JSON fields, to ensure the float values are
        stored as float or integer values in the db instead of as strings, and to make sure booleans are treated as such
    """
    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        for field, value in data.get('extra_params', {}).items():
            if not isinstance(value, bool):
                if value == 'true' or value == 'True':
                    data['extra_params'][field] = True
                elif value == 'false' or value == 'False':
                    data['extra_params'][field] = False
                else:
                    try:
                        float_value = float(value)
                        if float_value.is_integer():
                            data['extra_params'][field] = int(float_value)
                        else:
                            data['extra_params'][field] = float_value
                    except (ValueError, TypeError):
                        pass
        return data

class GetSerializerMixin():
    """ A mixin to allow for serializer introspection by DRF OpenAPI schema generation.
    This mixin should be used for DRF view classes that don't implement get_serializer_class()
    """
    def get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def get_serializer_class(self):
        """
        Return the class to use for the serializer.
        Defaults to using `self.serializer_class`.

        You may want to override this if you need to provide different
        serializations depending on the incoming request.

        (Eg. admins get full serialization, others get basic serialization)
        """
        assert self.serializer_class is not None, (
            "'%s' should either include a `serializer_class` attribute, "
            "or override the `get_serializer_class()` method."
            % self.__class__.__name__
        )

        return self.serializer_class

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }
