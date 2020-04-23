import json
from urllib import parse
import base64
from http import cookies
import cgi


class HttpServer:
    headers = {
        "Status": "200 OK",
    }
    STATUS_CODES = {
        100: "Continue",
        101: "Switching Protocols",
        102: "Processing",
        103: "Early Hints",
        200: "OK",
        201: "Created",
        202: "Accepted",
        203: "Non-Authoritative Information",
        204: "No Content",
        205: "Reset Content",
        206: "Partial Content",
        207: "Multi-Status",
        208: "Already Reported",
        226: "IM Used",
        300: "Multiple Choices",
        301: "Moved Permanently",
        302: "Found",
        303: "See Other",
        304: "Not Modified",
        305: "Switch Proxy",
        307: "Temporary Redirect",
        308: "Permanent Redirect",
        400: "Bad Request",
        401: "Unauthorized",
        402: "Payment Required",
        403: "Forbidden",
        404: "Not Found",
        405: "Method Not Allowed",
        406: "Not Acceptable",
        407: "Proxy Authentication Required",
        408: "Request",
        409: "Conflict",
        410: "Gone",
        411: "Length Required",
        412: "Precondition Failed",
        413: "Payload Too Large",
        414: "URI Too Long",
        415: "Unnsupported Media Type",
        416: "Range Not Satisfiable",
        417: "Expectation Failed",
        429: "Too Many Requests",

        500: "Internal Server Error",
        501: "Not Implemented",
        502: "Service Unavailable"
    }

    def __init__(self, environ, payload):
        self.environ = environ
        self.payload = payload
        self.query_string = self.environ.get("QUERY_STRING")
        self.cookies = self.get_cookies()

    def get_method(self):
        method = self.environ.get("REQUEST_METHOD")
        if method is None:
            method = "GET"
        else:
            method = method.upper()
        return method

    def get_request_header(self, key):
        return self.environ.get(key)

    def get_remote_address(self):
        return self.environ.get("REMOTE_ADDR")

    def get_authorization(self):
        authorization = {
            "type": "",
            "username": "",
            "password": ""
        }
        raw_authentication = self.environ.get("HTTP_AUTHORIZATION")
        if raw_authentication is not None and raw_authentication != "":
            split_authorization = raw_authentication.split(" ", 1)
            if len(split_authorization) > 0:
                authorization["type"] = split_authorization[0]
                user_pass = base64.decodestring(
                    split_authorization[1].encode("utf-8")
                ).decode("utf-8")
                if ":" in user_pass:
                    split_user_pass = user_pass.split(":", 1)
                    authorization["username"] = split_user_pass[0]
                    authorization["password"] = split_user_pass[1]
                else:
                    authorization["username"] = user_pass
        return authorization

    def get_query_string(self):
        query_string = self.environ.get("QUERY_STRING")
        return query_string

    def get_query_parameters(self):
        query_params = []
        if self.query_string is not None:
            raw_query_params = dict(parse.parse_qsl(
                self.query_string
            ))
            query_params = {}
            for key, value in raw_query_params.items():
                if value.lower() == "true":
                    query_params[key] = True
                elif value.lower() == "false":
                    query_params[key] = False
                else:
                    query_params[key] = value
        return query_params

    def get_post_parameters(self):
        form = cgi.FieldStorage()
        post_parameters = {}
        keys = form.keys()
        for key in keys:
            post_parameters[key] = form.getvalue(key)
        return post_parameters

    def get_post_json(self):
        post_data = {}
        try:
            post_data = json.load(self.payload)
        except:
            pass
        return post_data        

    def print_headers(self):
        for key, value in self.headers.items():
            print("{}: {}".format(key, value))
        print(self.cookies)
        print("")

    def print_json(self, data):
        print(json.dumps(data, indent=3))

    def set_header(self, key, value):
        self.headers[key] = value

    def set_status(self, code):
        self.headers["Status"] = "{} {}".format(
            str(code), self.STATUS_CODES[code]
        )

    def get_cookies(self):
        http_cookies = cookies.SimpleCookie()
        cookie_string = self.environ.get("HTTP_COOKIE")
        if cookie_string is not None and cookie_string != "":
            http_cookies.load(cookie_string)
        return http_cookies

    def get_cookie(self, key, default_value=None):
        return_value = default_value
        try:
            return_value = self.cookies[key].value
        except:
            pass
        return return_value

    def set_cookie(self, key, value):
        self.cookies[key] = value

    def delete_cookie(self, key):
        self.cookies[key] = ""
        self.cookies[key]['expires']='Thu, 01 Jan 1970 00:00:00 GMT'


class WebManager:

    HTTP_METHOD_GET = "GET"
    HTTP_METHOD_PUT = "PUT"
    HTTP_METHOD_POST = "POST"
    HTTP_METHOD_DELETE = "DELETE"

    HTTP_METHOD_HEAD = "HEAD"
    HTTP_METHOD_OPTIONS = "OPTIONS"

    HTTP_METHOD_CONNECT = "CONNECT"
    HTTP_METHOD_TRACE = "TRACE"

    http_server = None
    database_manager = None
    ip = None
    session = None
    account = None
    method_callbacks = {
        "GET": None,
        "DELETE": None,
        "PUT": None,
        "POST": None,
        "HEAD": None,
        "OPTIONS": None,
        "CONNECT": None,
        "TRACE": None,
    }
    default_method_callback = None

    def __init__(self, http_server, database_manager):
        self.http_server = http_server
        self.http_server.set_header('Content-Type', "text/html")
        self.database_manager = database_manager

    def set_method_callback(self, method, callback):
        self.method_callbacks[method] = callback
        self.set_allowed_methods()

    def run(self):
        http_server = self.http_server
        method = http_server.get_method()
        callback_found = False
        if method in self.method_callbacks:
            if self.method_callbacks[method] is not None:
                callback_found = True
                self.method_callbacks[method](
                    self.http_server,
                    self.database_manager,
                    self.session,
                    self.account
                )
        if callback_found is False:
            if method == self.HTTP_METHOD_OPTIONS:
                self.run_default_options()
            else:
                if self.default_method_callback is None:
                    self.run_default_error()
                else:
                    self.default_method_callback()

    def set_allowed_methods(self):
        http_server = self.http_server
        allowed_methods = [self.HTTP_METHOD_OPTIONS]
        for key, value in self.method_callbacks.items():
            if value is not None:
                if key not in allowed_methods:
                    allowed_methods.append(key)
        http_server.set_header(
            "Access-Control-Allow-Methods",
            ", ".join(allowed_methods)
        )

    def run_default_error(self):
        http_server = self.http_server
        http_server.set_status(405)
        http_server.print_headers()
