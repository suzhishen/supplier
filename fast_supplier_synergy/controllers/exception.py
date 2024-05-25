from werkzeug.exceptions import HTTPException
from werkzeug._internal import _get_environ
from werkzeug.wrappers import Response
import json
import logging

_logger = logging.getLogger(__name__)


class OdooCustomHTTPException(HTTPException):
    '''
    自定异常类型
    '''
    code = None
    description = None
    log_msg = None

    def __init__(self, code=None,description=None,log_msg=None):
        Exception.__init__(self)
        self.description = description
        self.code = code
        self.log_msg = log_msg if log_msg else description

    def get_headers(self, environ=None):
        """Get a list of headers."""
        return [('Content-Type', 'application/json')]

    def get_response(self, environ=None):
        """Get a response object.  If one was passed to the exception
        it's returned directly.

        :param environ: the optional environ for the request.  This
                        can be used to modify the response depending
                        on how the request looked like.
        :return: a :class:`Response` object or a subclass thereof.
        """

        if environ is not None:
            environ = _get_environ(environ)
        headers = self.get_headers(environ)
        if self.log_msg:
            logging.error(self.log_msg)
        return Response(json.dumps({'code':self.code,'message':self.description}), self.code, headers)