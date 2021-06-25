# Observation Portal

![Build](https://github.com/observatorycontrolsystem/observation-portal/workflows/Build/badge.svg)
[![Coverage Status](https://coveralls.io/repos/github/observatorycontrolsystem/observation-portal/badge.svg?branch=master)](https://coveralls.io/github/observatorycontrolsystem/observation-portal?branch=master)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/9846cee7c4904cae8864525101030169)](https://www.codacy.com/gh/observatorycontrolsystem/observation-portal?utm_source=github.com&utm_medium=referral&utm_content=observatorycontrolsystem/observation-portal&utm_campaign=Badge_Grade)

## An API for Astronomical Observation Management

Within an observatory control system, the observation portal provides modules for:

-   **Proposal management**: Calls for proposals, proposal creation, and time allocation
-   **Request management**: Observation request validation, submission, and cancellation, as well as views providing ancillary information about them
-   **Observation management**: Store and provide the telescope schedule, update observations, and update observation requests on observation update
-   **User identity management**: Oauth2 authenticated user management that can be used in other applications

## Prerequisites

Optional prerequisites can be skipped for reduced functionality.

-   Python >= 3.6
-   PostgreSQL >= 9.6
-   A running [Configuration Database](https://github.com/observatorycontrolsystem/configdb) 
-   (Optional) A running [Downtime Database](https://github.com/observatorycontrolsystem/downtime)
-   (Optional) A running Elasticsearch



## Environment Variables

|                        | Variable                         | Description                                                                                                                                                                 | Default                                                 |
| ---------------------- | -------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------- |
| General                | `DEBUG`                          | Whether the application should run using Django's debug mode                                                                                                                | `False`                                                 |
|                        | `SECRET_KEY`                     | The secret key used for sessions                                                                                                                                            | _`random characters`_                                   |
|                        | `ALLOWED_HOSTS`                     | Override for Django's ALLOWED_HOSTS setting                                                                                                                                            | `*`                                   |
|                        | `CSRF_TRUSTED_ORIGINS`           | Comma separated list of trusted origins allowed for CSRF                                                                                                                    | `None`
|                        | `MAX_FAILURES_PER_REQUEST` | Maximum number of times an Observation can fail per Request before the Request is marked as FAILURE_LIMIT_REACHED. 0 means there is no max. | `0` |
|                        | `MAX_IPP_VALUE` | The maximum value to be used for ipp scaling. Should be greater than 1 (1 would be no scaling) | `2.0` |
|                        | `MIN_IPP_VALUE` | The minimum value to be used for ipp scaling. Should be less than 1 but greater than 0 | `0.5` |
|                        | `PROPOSAL_TIME_OVERUSE_ALLOWANCE` | The amount of leeway in a proposals timeallocation before rejecting that request for scheduling. For example, a value of 1.1 results in allows over-scheduling by up to 10% of the total time_allocation. It is useful to allow some over-scheduling since it is likely some in progress observations will use less time then allocated, due to conservative overheads, failing, or cancelling.                | `1.1` |
| Database               | `DB_NAME`                        | The name of the database                                                                                                                                                    | `observation_portal`                                    |
|                        | `DB_USER`                        | The database user                                                                                                                                                           | `postgres`                                              |
|                        | `DB_PASSWORD`                    | The database password                                                                                                                                                       | _`Empty string`_                                        |
|                        | `DB_HOST`                        | The database host                                                                                                                                                           | `127.0.0.1`                                             |
|                        | `DB_PORT`                        | The database port                                                                                                                                                           | `5432`                                                  |
| Cache                  | `CACHE_BACKEND`                  | The remote Django cache backend                                                                                                                                             | `django.core.cache.backends.locmem.LocMemCache`         |
|                        | `CACHE_LOCATION`                 | The cache location or connection string                                                                                                                                     | `unique-snowflake`                                      |
|                        | `LOCAL_CACHE_BACKEND`            | The local Django cache backend to use                                                                                                                                       | `django.core.cache.backends.locmem.LocMemCache`         |
| Static and Media Files | `AWS_BUCKET_NAME`                | The name of the AWS bucket in which to store static and media files                                                                                                         | `observation-portal-test-bucket`                        |
|                        | `AWS_REGION`                     | The AWS region                                                                                                                                                              | `us-west-2`                                             |
|                        | `AWS_ACCESS_KEY_ID`              | The AWS user access key with read/write priveleges on the s3 bucket                                                                                                         | `None`                                                  |
|                        | `AWS_SECRET_ACCESS_KEY`          | The AWS user secret key to use with the access key                                                                                                                          | `None`                                                  |
|                        | `MEDIA_STORAGE`                  | The Django media files storage backend                                                                                                                                      | `django.core.files.storage.FileSystemStorage`           |
|                        | `MEDIAFILES_DIR`                 | The directory in which to store media files                                                                                                                                 | `media`                                                 |
|                        | `STATIC_STORAGE`                 | The Django static files storage backend                                                                                                                                     | `django.contrib.staticfiles.storage.StaticFilesStorage` |
| Email                  | `EMAIL_BACKEND`                  | The Django SMTP backend to use                                                                                                                                              | `django.core.mail.backends.console.EmailBackend`        |
|                        | `EMAIL_HOST`                     | The SMTP host                                                                                                                                                               | `localhost`                                             |
|                        | `EMAIL_HOST_USER`                | The SMTP user                                                                                                                                                               | _`Empty string`_                                        |
|                        | `EMAIL_HOST_PASSWORD`            | The SMTP password                                                                                                                                                           | _`Empty string`_                                        |
|                        | `EMAIL_PORT`                     | The SMTP port                                                                                                                                                               | `587`                                                   |
|                        | `ORGANIZATION_EMAIL`             | The reply-to email for outgoing messages                                                                                                                                                           | _`Empty string`_                                                    |
|                        | `ORGANIZATION_DDT_EMAIL`             | Email to receive ddt science application submission messages                                                                                                                                                           | _`Empty string`_                                                    |
|                        | `ORGANIZATION_ADMIN_EMAIL`             | The Django Admin email to receive http 500 reports.                                                                                                                                                           | _`Empty string`_                                                    |
|                        | `ORGANIZATION_SUPPORT_EMAIL`             | Email to receive account removal requests                                                                                                                                                            | _`Empty string`_                                                    |
|                        | `ORGANIZATION_NAME`              | The name of your organization, used within email templates                                                                                                                                                           | _`Empty string`_                                                    |
|                        | `OBSERVATION_PORTAL_BASE_URL`    | The base url of your deployed Observation Portal code, used within email templates to provide links to pages                                                                                                                                                          | `http://localhost`                                                    |
|                        | `REQUESTGROUP_DATA_DOWNLOAD_URL` | The url where a user can download requestgroup data. Optionally include `{requestgroup_id}` in the string which will be filled in with the ID of the specific requestgroup. | _`Empty string`_ |
|                        | `REQUEST_DETAIL_URL` | The url to frontend detail page for a Request. Optionally include `{request_id}` in the string which will be filled in with the ID of the specific request. | _`Empty string`_ |
|                        | `SCIENCE_APPLICATION_DETAIL_URL` | The url to frontend science application detail page. Optionally include `{sciapp_id}` in the string which will be filled in with the ID of the specific science application. | _`Empty string`_ |
| External Services      | `CONFIGDB_URL`                   | The url to the configuration database                                                                                                                                       | `http://localhost`                                      |
|                        | `DOWNTIMEDB_URL`                 | The url to the downtime database                                                                                                                                            | `http://localhost`                                      |
|                        | `ELASTICSEARCH_URL`              | The url to the elasticsearch cluster                                                                                                                                        | `http://localhost`                                      |
| Task Scheduling        | `DRAMATIQ_BROKER_HOST`           | The broker host for dramatiq                                                                                                                                                | `redis`                                                 |
|                        | `DRAMATIQ_BROKER_PORT`           | The broker port for dramatiq                                                                                                                                                | `6379`                                                  |
| Throttle Overrides     | `REQUESTGROUPS_CANCEL_DEFAULT_THROTTLE`           | Default django rest framework throttle rate string for the RequestGroups cancel endpoint                                                                                                                                              | `2000/day`                                                 |
|                        | `REQUESTGROUPS_CREATE_DEFAULT_THROTTLE`           | Default django rest framework throttle rate string for the RequestGroups create endpoint                                                                                                                                              | `5000/day`                                                 |
|                        | `REQUESTGROUPS_VALIDATE_DEFAULT_THROTTLE`           | Default django rest framework throttle rate string for the RequestGroups validate endpoint                                                                                                                                             | `20000/day`                                                 |
| Serializer Overrides   | `OBSERVATIONS_SUMMARY_SERIALIZER`           | Class dotpath for Observation's Summary serializer override                                                                                                                                             | `observation_portal.observations.serializers.SummarySerializer`                                                 |
|                        | `OBSERVATIONS_CONFIGURATIONSTATUS_SERIALIZER`           | Class dotpath for Observation's ConfigurationStatus serializer override                                                                                                                                             | `observation_portal.observations.serializers.ConfigurationStatusSerializer`                                                 |
|                        | `OBSERVATIONS_TARGET_SERIALIZER`           | Class dotpath for Observation's Target serializer override                                                                                                                                             | `observation_portal.observations.serializers.ObservationTargetSerializer`                                              |
|                        | `OBSERVATIONS_CONFIGURATION_SERIALIZER`           | Class dotpath for Observation's Configuration serializer override                                                                                                                                             | `observation_portal.observations.serializers.ObservationConfigurationSerializer`                                              |
|                        | `OBSERVATIONS_REQUEST_SERIALIZER`           | Class dotpath for Observation's Request serializer override                                                                                                                                             | `observation_portal.observations.serializers.ObserveRequestSerializer`                                              |
|                        | `OBSERVATIONS_REQUESTGROUP_SERIALIZER`           | Class dotpath for Observation's RequestGroup serializer override                                                                                                                                             | `observation_portal.observations.serializers.ObserveRequestGroupSerializer`                                              |
|                        | `OBSERVATIONS_SCHEDULE_SERIALIZER`           | Class dotpath for Observation's Schedule serializer override                                                                                                                                             | `observation_portal.observations.serializers.ScheduleSerializer`                                              |
|                        | `OBSERVATIONS_OBSERVATION_SERIALIZER`           | Class dotpath for Observation's Observation serializer override                                                                                                                                             | `observation_portal.observations.serializers.ObservationSerializer`                                              |
|                        | `OBSERVATIONS_CANCEL_SERIALIZER`           | Class dotpath for Observation's Cancel Observation serializer override                                                                                                                                             | `observation_portal.observations.serializers.CancelObservationsSerializer`                                              |
|                        | `REQUESTGROUPS_CADENCE_SERIALIZER`           | Class dotpath for RequestGroups's Cadence serializer override                                                                                                                                             | `observation_portal.requestgroups.serializers.CadenceSerializer`                                              |
|                        | `REQUESTGROUPS_CADENCEREQUEST_SERIALIZER`         | Class dotpath for RequestGroups's Cadence Request serializer override                                                                                                                                             | `observation_portal.requestgroups.serializers.CadenceRequestSerializer`                                              |
|                        | `REQUESTGROUPS_CONSTRAINTS_SERIALIZER`           | Class dotpath for RequestGroups's Constraints serializer override                                                                                                                                             | `observation_portal.requestgroups.serializers.ConstraintsSerializer`                                              |
|                        | `REQUESTGROUPS_REGIONOFINTEREST_SERIALIZER`           | Class dotpath for RequestGroups's Instrument Config ROI serializer override                                                                                                                                             | `observation_portal.requestgroups.serializers.RegionOfInterestSerializer`                                              |
|                        | `REQUESTGROUPS_INSTRUMENTCONFIG_SERIALIZER`           | Class dotpath for RequestGroups's Instrument Config serializer override                                                                                                                                             | `observation_portal.requestgroups.serializers.InstrumentConfigSerializer`                                              |
|                        | `REQUESTGROUPS_ACQUISITIONCONFIG_SERIALIZER`           | Class dotpath for RequestGroups's Acquisition Config serializer override                                                                                                                                             | `observation_portal.requestgroups.serializers.AcquisitionConfigSerializer`                                              |
|                        | `REQUESTGROUPS_GUIDINGCONFIG_SERIALIZER`           | Class dotpath for RequestGroups's Guiding Config serializer override                                                                                                                                             | `observation_portal.requestgroups.serializers.GuidingConfigSerializer`                                              |
|                        | `REQUESTGROUPS_TARGET_SERIALIZER`           | Class dotpath for RequestGroups's Target serializer override                                                                                                                                             | `observation_portal.requestgroups.serializers.TargetSerializer`                                              |
|                        | `REQUESTGROUPS_CONFIGURATION_SERIALIZER`           | Class dotpath for RequestGroups's Configuration serializer override                                                                                                                                             | `observation_portal.requestgroups.serializers.ConfigurationSerializer`                                              |
|                        | `REQUESTGROUPS_LOCATION_SERIALIZER`           | Class dotpath for RequestGroups's Location serializer override                                                                                                                                             | `observation_portal.requestgroups.serializers.LocationSerializer`                                              |
|                        | `REQUESTGROUPS_WINDOW_SERIALIZER`           | Class dotpath for RequestGroups's Window serializer override                                                                                                                                             | `observation_portal.requestgroups.serializers.WindowSerializer`                                              |
|                        | `REQUESTGROUPS_REQUEST_SERIALIZER`           | Class dotpath for RequestGroups's Request serializer override                                                                                                                                             | `observation_portal.requestgroups.serializers.RequestSerializer`                                              |
|                        | `REQUESTGROUPS_REQUESTGROUP_SERIALIZER`           | Class dotpath for RequestGroups's RequestGroup serializer override                                                                                                                                             | `observation_portal.requestgroups.serializers.RequestGroupSerializer`                                              |
|                        | `REQUESTGROUPS_DRAFTREQUESTGROUP_SERIALIZER`           | Class dotpath for RequestGroups's Draft RequestGroup serializer override                                                                                                                                             | `observation_portal.requestgroups.serializers.DraftRequestGroupSerializer`                                              |
|                        | `PROPOSALS_PROPOSAL_SERIALIZER`           | Class dotpath for Proposal's Proposal serializer override                                                                                                                                             | `observation_portal.proposals.serializers.ProposalSerializer`                                              |
|                        | `PROPOSALS_PROPOSALINVITE_SERIALIZER`           | Class dotpath for Proposal's ProposalInvite serializer override                                                                                                                                             | `observation_portal.proposals.serializers.ProposalInviteSerializer`                                              |
|                        | `PROPOSALS_SEMESTER_SERIALIZER`           | Class dotpath for Proposal's Semester serializer override                                                                                                                                             | `observation_portal.proposals.serializers.SemesterSerialzer`                                              |
|                        | `PROPOSALS_MEMBERSHIP_SERIALIZER`           | Class dotpath for Proposal's Membership serializer override                                                                                                                                             | `observation_portal.proposals.serializers.MembershipSerializer`                                              |
|                        | `PROPOSALS_PROPOSALNOTIFICATION_SERIALIZER`           | Class dotpath for Proposal's ProposalNotification serializer override                                                                                                                                             | `observation_portal.proposals.serializers.ProposalNotificationSerializer`                                              |
|                        | `PROPOSALS_TIMELIMIT_SERIALIZER`           | Class dotpath for Proposal's Proposal serializer override                                                                                                                                             | `observation_portal.proposals.serializers.TimeLimitSerializer`                                              |
|                        | `ACCOUNTS_PROFILE_SERIALIZER`           | Class dotpath for Accounts's Profile serializer override                                                                                                                                             | `observation_portal.accounts.serializers.ProfileSerializer`                                              |
|                        | `ACCOUNTS_USER_SERIALIZER`           | Class dotpath for Accounts's User serializer override                                                                                                                                             | `observation_portal.accounts.serializers.UserSerializer`                                              |
|                        | `ACCOUNTS_ACCOUNTREMOVAL_SERIALIZER`           | Class dotpath for Accounts's Account Removal serializer override                                                                                                                                             | `observation_portal.accounts.serializers.AccountRemovalSerializer`                                              |
|                        | `SCIAPPLICATIONS_CALL_SERIALIZER`           | Class dotpath for SciApplications's Call serializer override                                                                                                                                             | `observation_portal.sciapplications.serializers.CallSerializer`                                              |
|                        | `SCIAPPLICATIONS_SCIENCEAPPLICATION_SERIALIZER`           | Class dotpath for SciApplications's Science Application serializer override                                                                                                                                             | `observation_portal.sciapplications.serializers.ScienceApplicationSerializer`                                              |
| as_dict Overrides   | `OBSERVATIONS_SUMMARY_AS_DICT`           | Class dotpath for Observation's Summary as_dict override                                                                                                                                             | `observation_portal.observations.models.summary_as_dict`                                                 |
|                        | `OBSERVATIONS_CONFIGURATIONSTATUS_AS_DICT`           | Class dotpath for Observation's ConfigurationStatus as_dict override                                                                                                                                             | `observation_portal.observations.models.configurationstatus_as_dict`                                                 |
|                        | `OBSERVATIONS_OBSERVATION_AS_DICT`           | Class dotpath for Observation's Observation as_dict override                                                                                                                                             | `observation_portal.observations.models.observation_as_dict`                                              |
|                        | `REQUESTGROUPS_CONSTRAINTS_AS_DICT`           | Class dotpath for RequestGroups's Constraints as_dict override                                                                                                                                             | `observation_portal.requestgroups.models.constraints_as_dict`                                              |
|                        | `REQUESTGROUPS_REGIONOFINTEREST_AS_DICT`           | Class dotpath for RequestGroups's Instrument Config ROI as_dict override                                                                                                                                             | `observation_portal.requestgroups.models.regionofinterest_as_dict`                                              |
|                        | `REQUESTGROUPS_INSTRUMENTCONFIG_AS_DICT`           | Class dotpath for RequestGroups's Instrument Config as_dict override                                                                                                                                             | `observation_portal.requestgroups.models.instrumentconfig_as_dict`                                              |
|                        | `REQUESTGROUPS_ACQUISITIONCONFIG_AS_DICT`           | Class dotpath for RequestGroups's Acquisition Config as_dict override                                                                                                                                             | `observation_portal.requestgroups.models.acquisitionconfig_as_dict`                                              |
|                        | `REQUESTGROUPS_GUIDINGCONFIG_AS_DICT`           | Class dotpath for RequestGroups's Guiding Config as_dict override                                                                                                                                             | `observation_portal.requestgroups.models.guidingconfig_as_dict`                                              |
|                        | `REQUESTGROUPS_TARGET_AS_DICT`           | Class dotpath for RequestGroups's Target as_dict override                                                                                                                                             | `observation_portal.requestgroups.models.target_as_dict`                                              |
|                        | `REQUESTGROUPS_CONFIGURATION_AS_DICT`           | Class dotpath for RequestGroups's Configuration as_dict override                                                                                                                                             | `observation_portal.requestgroups.models.configuration_as_dict`                                              |
|                        | `REQUESTGROUPS_LOCATION_AS_DICT`           | Class dotpath for RequestGroups's Location as_dict override                                                                                                                                             | `observation_portal.requestgroups.models.location_as_dict`                                              |
|                        | `REQUESTGROUPS_WINDOW_AS_DICT`           | Class dotpath for RequestGroups's Window as_dict override                                                                                                                                             | `observation_portal.requestgroups.models.window_as_dict`                                              |
|                        | `REQUESTGROUPS_REQUEST_AS_DICT`           | Class dotpath for RequestGroups's Request as_dict override                                                                                                                                             | `observation_portal.requestgroups.models.request_as_dict`                                              |
|                        | `REQUESTGROUPS_REQUESTGROUP_AS_DICT`           | Class dotpath for RequestGroups's RequestGroup as_dict override                                                                                                                                             | `observation_portal.requestgroups.models.requestgroup_as_dict`                                              |
|                        | `PROPOSALS_PROPOSAL_AS_DICT`           | Class dotpath for Proposal's Proposal as_dict override                                                                                                                                             | `observation_portal.proposals.models.proposal_as_dict`                                              |
|                        | `PROPOSALS_TIMEALLOCATION_AS_DICT`           | Class dotpath for Proposal's TimeAllocation as_dict override                                                                                                                                             | `observation_portal.proposals.models.timeallocation_as_dict`                                              |
|                        | `PROPOSALS_MEMBERSHIP_AS_DICT`           | Class dotpath for Proposal's Membership as_dict override                                                                                                                                             | `observation_portal.proposals.models.membership_as_dict`                                              |


## Local Development

### **Set up external services**

Please refer to the [Configuration Database](https://github.com/observatorycontrolsystem/configdb) and [Downtime Database](https://github.com/observatorycontrolsystem/downtime) projects for instructions on how to get those running, as well as the [Elasticsearch documentation](https://www.elastic.co/guide/en/elasticsearch/reference/5.6/install-elasticsearch.html) for options on how to run Elasticsearch.

### **Set up a [virtual environment](https://docs.python.org/3/tutorial/venv.html)**

Using a virtual environment is highly recommended. Run the following commands from the base of this project. `(env)`
is used to denote commands that should be run using your virtual environment.

    python3 -m venv env
    source env/bin/activate
    (env) pip install numpy && pip install -e .[test]

### **Set up the database**

This example uses the [PostgreSQL Docker image](https://hub.docker.com/_/postgres) to create a database. Make sure that the options that you use to set up your database correspond with your configured database settings.

    docker run --name observation-portal-postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=observation_portal -v/var/lib/postgresql/data -p5432:5432 -d postgres:11.1

After creating the database, migrations must be applied to set up the tables in the database.

    (env) python manage.py migrate

### **Run the tests**

    (env) python manage.py test --settings=observation_portal.test_settings

### **Run the portal**

    (env) python manage.py runserver

The observation portal should now be accessible from <http://127.0.0.1:8000>!
