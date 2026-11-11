from django.test import TestCase, Client
from django.http import QueryDict


class HealthEndpointTest(TestCase):
    def test_health_returns_ok(self):
        client = Client()
        response = client.get("/health/")
        assert response.status_code == 200
        data = response.json()
        assert set(data.keys()) == {'FILES', 
                                    'request', 
                                    'headers', 
                                    'META', 
                                    'GET', 
                                    'POST', 
                                    'status', 
                                    'COOKIES', 
                                    'user', 
                                    'session', 
                                    'body'}
        assert data["status"] == "ok"
        assert set(data["request"].keys()) == {'path', 
                                               'content_params', 
                                               'method', 
                                               'content_type', 
                                               'scheme', 
                                               'path_info', 
                                               'encoding'}
        assert data["request"]["path"] == "/health/"
        assert data["request"]["path_info"] == "/health/"
        assert data["request"]["scheme"] == "http"
        assert data["request"]["encoding"] is None
        assert data["request"]["content_type"] == ""
        assert data["request"]["content_params"] == {}
        assert data["GET"] == {}
        assert data["POST"] == {}
        assert data["body"] == ""
        assert data["headers"] == {"Cookie": ""}
        #assert data["headers"]["Content-Length"] == ""
        #assert data["headers"]["Content-Type"] == "text/plain" 
        #assert data["headers"]["Host"] == "127.0.0.1:8000"
        #assert data["headers"]["Connection"] == "keep-alive"
        #assert data["headers"]["Sec-Ch-Ua"] == "\"Not-A.Brand\";v=\"99\", \"Google Chrome\";v=\"157\", \"Chromium\";v=\"157\""
        #assert data["headers"]["Sec-Ch-Ua-Mobile"] == "?0"
        #assert data["headers"]["Sec-Ch-Ua-Platform"] == "\"Windows\""
        #assert data["headers"]["Upgrade-Insecure-Requests"] == "1"
        #assert data["headers"]["User-Agent"] == "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36"
        #assert data["headers"]["Accept"] == "text/html,application/xhtml+xml,application/xml;q=0.9,image/jxl,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
        #assert data["headers"]["Sec-Fetch-Site"] == "none"
        #assert data["headers"]["Sec-Fetch-Mode"] == "navigate"
        #assert data["headers"]["Sec-Fetch-User"] == "?1"
        #assert data["headers"]["Sec-Fetch-Dest"] == "document"
        #assert data["headers"]["Accept-Encoding"] == "gzip, deflate, br, zstd"
        #assert data["headers"]["Accept-Language"] == "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7"
        assert data["FILES"] == {}
        assert data["META"]["REQUEST_METHOD"] == "GET"
        assert data["META"]["PATH_INFO"] == "/health/"
        assert data["META"]["QUERY_STRING"] == ""
        assert data["META"]["SERVER_NAME"] == "testserver"
        assert data["META"]["SERVER_PORT"] == "80"
        assert data["META"]["REMOTE_ADDR"] == "127.0.0.1"
        assert data["META"]["HTTP_HOST"] is None
        assert data["META"]["HTTP_USER_AGENT"] is None
        assert data["META"]["HTTP_ACCEPT"] is None 
        assert data["META"]["CONTENT_TYPE"] is None
        assert data["META"]["CONTENT_LENGTH"] is None
        assert data["user"]["is_authenticated"] is False
        assert data["user"]["is_anonymous"] is True
        assert data["session"] == {}
        assert response.headers["X-API-Version"] == "1.0"
        assert b"\n    " in response.content
        assert response.request["REQUEST_METHOD"] == "GET"
        assert response.request["PATH_INFO"] == "/health/"
        #assert response.request["SCRIPT_NAME"] == ""
        assert response.request["QUERY_STRING"] == ""
        #assert response.request["SERVER_NAME"] == "testserver"
        assert response.request["SERVER_PORT"] == "80"
        #assert response.request["SERVER_PROTOCOL"] == "HTTP/1.1"
        assert response.request["wsgi.url_scheme"] == "http"
        #assert response.request["HTTP_HOST"] == "testserver"
        #assert response.request["HTTP_COOKIE"] == ""
        #assert response.request["HTTP_CONTENT_TYPE"] == "text/plain"
        #assert response.request["HTTP_CONTENT_LENGTH"] == ""
        #assert response.request["HTTP_USER_AGENT"] == "testclient"
        #assert response.request["CONTENT_TYPE"] == "text/plain"
        #assert response.request["CONTENT_LENGTH"] == ""
        #assert response.request["wsgi.version"] == (1, 0)
        #assert response.request["wsgi.multithread"] is False
        #assert response.request["wsgi.multiprocess"] is True
        #assert response.request["wsgi.run_once"] is False
        assert response.request["QUERY_STRING"] == ""
        assert set(response.request.keys()) == {
                                                    "PATH_INFO",
                                                    "REQUEST_METHOD",
                                                    "SERVER_PORT",
                                                    "wsgi.url_scheme",
                                                    "QUERY_STRING",
                                                }
        assert response.headers["Content-Type"] == "application/json"

    def test_health_with_query_parameters(self):
        client = Client()
        response = client.get("/health/?status=active&page=2")
        data = response.json()
        assert set(data.keys()) == {'headers', 
                                    'FILES', 
                                    'COOKIES', 
                                    'POST', 
                                    'status', 
                                    'body', 
                                    'session', 
                                    'request', 
                                    'user', 
                                    'GET', 
                                    'META'}
        assert data['status'] == 'ok' 
        assert data['request'] == {
                                    'method': 'GET', 
                                    'path': '/health/', 
                                    'path_info': '/health/',
                                    'scheme': 'http', 
                                    'encoding': None, 
                                    'content_type': '', 
                                    'content_params': {}} 
        assert data['GET'] == {
                                'status': ['active'], 
                                'page': ['2']
                                } 
        assert data['POST'] == {} 
        assert data['body'] == '' 
        assert data['headers'] == {
                                    'Cookie': ''
                                    } 
        assert data['COOKIES'] == {} 
        assert data['FILES'] == {} 
        assert data['META'] == {
                                'REQUEST_METHOD': 'GET', 
                                'PATH_INFO': '/health/', 
                                'QUERY_STRING': 'status=active&page=2', 
                                'SERVER_NAME': 'testserver', 
                                'SERVER_PORT': '80', 
                                'REMOTE_ADDR': '127.0.0.1', 
                                'HTTP_HOST': None,
                                'HTTP_USER_AGENT': None, 
                                'HTTP_ACCEPT': None, 
                                'CONTENT_TYPE': None, 
                                'CONTENT_LENGTH': None
                                } 
        assert data['user'] == {
                                'is_authenticated': False, 
                                'is_anonymous': True
                                } 
        assert data['session'] == {}
        assert data['GET']['status'] == ['active'] 
        assert data['GET']['page'] == ['2']
        assert data['META']['QUERY_STRING'] == 'status=active&page=2'
        assert response.request == {
                                    'PATH_INFO': '/health/', 
                                    'REQUEST_METHOD': 'GET', 
                                    'SERVER_PORT': '80', 
                                    'wsgi.url_scheme': 'http', 
                                    'QUERY_STRING': 'status=active&page=2'}
        assert response.request['QUERY_STRING'] == 'status=active&page=2'

    def test_health_with_repeated_query_parameters(self):
        client = Client()
        response = client.get("/health/?status=active&status=inactive&status=pending")
        data = response.json()
        assert data["GET"]["status"] == ['active', 'inactive', 'pending']
        assert data == {
                        'status': 'ok', 
                        'request': {
                                    'method': 'GET', 
                                    'path': '/health/', 
                                    'path_info': '/health/', 
                                    'scheme': 'http', 
                                    'encoding': None, 
                                    'content_type': '', 
                                    'content_params': {}
                                    }, 
                        'GET': 
                                {
                                    'status': 
                                            [
                                                'active', 
                                                'inactive', 
                                                'pending'
                                                ]
                                }, 
                        'POST': {}, 
                        'body': '',
                        'headers': {'Cookie': ''}, 
                        'COOKIES': {}, 
                        'FILES': {}, 
                        'META': 
                                {
                                    'REQUEST_METHOD': 'GET', 
                                    'PATH_INFO': '/health/',
                                    'QUERY_STRING': 'status=active&status=inactive&status=pending', 
                                    'SERVER_NAME': 'testserver', 
                                    'SERVER_PORT': '80', 
                                    'REMOTE_ADDR': '127.0.0.1', 
                                    'HTTP_HOST': None, 
                                    'HTTP_USER_AGENT': None,
                                    'HTTP_ACCEPT': None, 
                                    'CONTENT_TYPE': None, 
                                    'CONTENT_LENGTH': None}, 
                                    'user': {
                                                'is_authenticated': False, 
                                                'is_anonymous': True}, 'session': {}
                        }
        assert response.request == {
                                    'PATH_INFO': '/health/', 
                                    'REQUEST_METHOD': 'GET', 
                                    'SERVER_PORT': '80', 
                                    'wsgi.url_scheme': 'http',
                                    'QUERY_STRING': 'status=active&status=inactive&status=pending'
                                    }
        assert data['META']['QUERY_STRING'] == 'status=active&status=inactive&status=pending'
        assert  response.request['QUERY_STRING'] == 'status=active&status=inactive&status=pending'

    def test_querydict_methods(self):
        query = QueryDict("status=active&status=inactive&status=pending&page=2")
        assert isinstance(query, QueryDict)
        assert query.get("status") == "pending"
        assert query.get("page") == "2"
        assert query.getlist("status") == ["active", "inactive", "pending"]
        assert query.getlist("page") == ["2"]
        assert query.getlist("unknown") == []
        assert set(query.keys()) == {"status", "page"}
        assert list(query.values()) == ["pending", "2"]
        assert list(query.items()) == [
                                            ("status", "pending"),
                                            ("page", "2")
                                        ]
        
        with self.assertRaises(AttributeError):
            query["sort"] = "name"
        
        query_copy = query.copy()

        assert isinstance(query_copy, QueryDict)

        query_copy["sort"] = "name"

        assert query_copy.get("sort") == "name"

        assert query.get("sort") is None
        assert query_copy.get("sort") == "name"

        assert query.getlist("status") == ["active", "inactive", "pending"]
        assert query_copy.getlist("status") == ["active", "inactive", "pending"]

        mutable_query = QueryDict(
                                    "status=active&status=inactive&status=pending&page=2",
                                    mutable=True
                                )
        mutable_query["sort"] = "name"

        assert mutable_query.get("sort") == "name"
        assert mutable_query.getlist("status") == ["active", "inactive", "pending"]
        