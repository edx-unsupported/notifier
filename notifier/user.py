"""
Functions in support of generating formatted digest emails of forums activity.
"""
import logging
import sys
import requests
import six

from django.conf import settings
from edx_rest_api_client.client import get_oauth_access_token


logger = logging.getLogger(__name__)


DIGEST_NOTIFICATION_PREFERENCE_KEY = 'notification_pref'
LANGUAGE_PREFERENCE_KEY = 'pref-lang'


class UserServiceException(Exception):
    pass


def get_access_token():
    oauth_url = settings.LMS_URL_BASE + '/oauth2/access_token'
    client_id = settings.CLIENT_ID
    client_secret = settings.CLIENT_SECRET
    token, expiration = get_oauth_access_token(oauth_url, client_id, client_secret, token_type='jwt')

    return token


def _headers():
    return {'Authorization': 'JWT {jwt}'.format(jwt=get_access_token())}


def _auth():
    auth = {}
    if settings.US_HTTP_AUTH_USER:
        auth['auth'] = (settings.US_HTTP_AUTH_USER, settings.US_HTTP_AUTH_PASS)
    return auth


def _http_get(*a, **kw):
    try:
        logger.debug('GET {} {}'.format(a[0], kw))
        response = requests.get(*a, **kw)
    except requests.exceptions.ConnectionError as e:
        _, msg, tb = sys.exc_info()
        six.reraise(UserServiceException, "request failed: {}".format(msg), tb)
    if response.status_code != 200:
        raise UserServiceException("HTTP Error {}: {}".format(
            response.status_code,
            response.reason
        ))
    return response


def get_digest_subscribers():
    """
    Generator function that calls the edX user API and yields a dict for each
    user opted in for digest notifications.

    The returned dicts will have keys "id", "name", and "email" (all strings).
    """
    api_url = settings.US_URL_BASE + '/notifier_api/v1/users/'
    params = {
        'page_size': settings.US_RESULT_PAGE_SIZE,
        'page': 1
    }

    logger.info('calling user api for digest subscribers')
    while True:
        data = _http_get(api_url, params=params, headers=_headers(), **_auth()).json()
        for result in data['results']:
            yield result
        if data['next'] is None:
            break
        params['page'] += 1


def get_user(user_id):
    api_url = '{}/notifier_api/v1/users/{}/'.format(settings.US_URL_BASE, user_id)
    logger.info('calling user api for user %s', user_id)
    r = _http_get(api_url, headers=_headers(), **_auth())
    if r.status_code == 200:
        user = r.json()
        return user
    elif r.status_code == 404:
        return None
    else:
        r.raise_for_status()
        raise Exception(
            'unhandled response from user service: %s %s' %
            (r.status_code, r.reason))
