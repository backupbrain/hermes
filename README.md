# Hermes

Are you seeing this on GitHub? You can view this on it's [Home page](https://backupbrain.github.io/hermes/).

Hermes is a lightweight  [CGI](https://en.wikipedia.org/wiki/Common_Gateway_Interface) web application framework. It is designed to make getting started quick and easy, with the ability to scale up to complex applications. It began as an easy way to make database-driven APIs and web applications without the need for complex server configuration.

### Friendly and Unopinionated

Hermes doesn't enforce conventions and doesn't have dependencies. It works with many existing tools such as [Jinja](https://jinja.palletsprojects.com/en/2.11.x/), but doesn't require them. It is as simple or as complex as your project wants it to be.

### Small Footprint

Because it uses CGI, the standard protocol for dynamic web server content, no modules such as WSGI are required to run. Also because of this, it allows the web server to do what it does best - routing and caching. Because it is designed to be import-driven, dependencies can be loaded on each page as needed, reducing the CPU time, memory requirements, and dependencies required for each page or API call.

### A Part of a Team

Hermes lets other programs do their job, so you'll have to configure your other programs as needed to work with Hermes. This is great if you have a team where each person has a different role. For instance a sys-admin, a front-end engineer, back-end engineer, and a database technician. Each person can work on their part of the project without disrupting the each others' workflow.

This is because it doesn't replace the web server's routing and security, and it doesn't try to replace the database's schema management.

### Live-deployment

Since Hermes uses CGI, each request is handled by the server at on its own terms. This means that changes you make to your website code are deployed live, such as when pulling code from git as a result of a post-commit hook. It also means that the server's buil-in routing and security can be used on a per-page or per-folder basis, such as with `.htaccess` in Apache. 

### React-compatible

It also makes for easy integration with [ReactJS](https://reactjs.org/) and [VueJs](https://vuejs.org/) since there is no need to define routes in Hermes. If React says that `/folder` exists, Hermes doesn't fight it. Plus obviously Hermes can create REST and GraphQL APIs.

### Static-Asset compatible

Since Hermes uses the web server's built-in CGI protocol, dynamic content can live side-by-side with static content. That means that static assets can be in the same folder structure as Python files. There's no need to serve files separately or create route conditions to access static content from the browser.

### Testing
Hermes doesn't read data directly from CGI. Instead, you must tell it what data to parse. This makes it possible to put dummy data in for testing at any time.

The native format is HTTP text from the web server's CGI input, something ilke this:

```data
GET /index.py HTTP/1.1
User-Agent: Mozilla/4.0 (compatible; MSIE5.01; Windows NT)
Host: example.com
Content-Type: text/html
Content-Length: 0
Accept-Language: en-us
Accept-Encoding: gzip, deflate
Connection: Keep-Alive


```

#### Live Data
To feed CGI data directly from your web server into Hermes, do this:

```python3
#!/usr/bin/env python3
import sys
from os import environ
http_server = HttpServer(environ, sys.stdin)
```

### Test Data

To feed test data into Hermes, do this:

```python3
#!/usr/bin/env python3
from os import environ

test_http_request = """
GET /index.py HTTP/1.1
User-Agent: Mozilla/4.0 (compatible; MSIE5.01; Windows NT)
Host: example.com
Content-Type: text/html
Content-Length: 0
Accept-Language: en-us
Accept-Encoding: gzip, deflate
Connection: Keep-Alive


"""
http_server = HttpServer(environ, test_http_request)
```

## Why This Exists

Hermes was created as an alternative to Django and Flask, the dominant Python web frameworks. Django is monolithic opinionated, which can be a problem for small projects or ones that integrate with legacy code. Flask has a complex way of dealing with database objects. Both require WSGI which is a challenge to set up on Apache and requires a web server restart every time a change is made to the web application code. Sometimes it's convenient to have something lightweight to use in a small project.

Hermes is named after the messenger god in Greek mythology. Hermes' job was to pass messages between gods, humans, and animals.


## Installing

Download code using Git:
```console
git clone https://github.com/backupbrain/hermes
```

## Set-up

Hermes works on a variety of web servers. 

### Apache

Make sure CGI is enabled in Apache2
```console
$ sudo a2enmod cgi
```

In your Apache VirtualHost, enable `ExecCGI` and add the `.py` handler.

```apache
<Directory /var/www/example.com/www>
	Options +ExecCGI
	AddHandler cgi-script .py
</Directory>
```

Create your first Hermes web page in `/var/www/example.com/www/index.py`:

```python3
#!/usr/bin/env python3
import sys
from os import environ
from hermes import HttpServer
from hermes import WebManager

# Initialize a CGI processor
http_server = HttpServer(environ, sys.stdin)

def handle_get(http_server):
    '''Respond to a GET request with static HTML content."""
    http_server.print_headers()  # Print HTTP headers
    output = "<html><body><h1>Hello world</h1><body></html>"
    http_server.print_json(output)  # Print output

# Create a web manager
web_manager = WebManager(http_server, database_manager)

# Tell the manager to respond to GET requests.
web_manager.set_method_callback(
    WebManager.HTTP_METHOD_GET,
    handle_get
)
web_manager.run()
```

Make sure this file is executable
```console
chmod +x /var/www/example.com/www/index.py
```

Restart Apache2 to make sure the folder is active and the settings took effect.
```console
$ sudo systemctl restart apache  # or whatever your flavor of *nix prefers
```

Remove `.py` extension by adding .htaccess in the `/var/www/example.com/www` folder:
```.htaccess
# check if a /path/to/file.py file exist
# and rewrite it as /path/to/file
# otherwise - leave it alone, it's a static file or folder
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-d
RewriteCond %{REQUEST_FILENAME} !-f
RewriteRule (.*) $1.py [L]
```


## Ngnx

Enable Fastcgi the virtual host config
```data
server {
[...]
   location /cgi-bin/ {
     # Disable gzip (it makes scripts feel slower since they have to complete
     # before getting gzipped)
     gzip off;
     # Set the root to /usr/lib (inside this location this means that we are
     # giving access to the files under /usr/lib/cgi-bin)
     root  /var/www/www.example.com;
     # Fastcgi socket
     fastcgi_pass  unix:/var/run/fcgiwrap.socket;
     # Fastcgi parameters, include the standard ones
     include /etc/nginx/fastcgi_params;
     # Adjust non standard parameters (SCRIPT_FILENAME)
     fastcgi_param SCRIPT_FILENAME  $document_root$fastcgi_script_name;
   }
[...]
}
```

Reload nginx:
```console
/etc/init.d/nginx reload  # or whatever your flavor of *nix prefers
```

## Including in a Project
Hermes can be included in any way you want. It can be a file in your virtual host root folder, or from another folder. It just needs to be included in the file that's being served.

Therefore your project structure can to your tastes. I happen to like this for a web site that serves both a top level domain (e.g. `https://example.com`) and an api subdomain (e.g. `https://api.example.com`):

```bash
/var/www/example.com/    # This is the example.com virtualhost folder
├── api/                 # https://api.example.com via Apache <Directory> setting
│   ├── path/
│   │   ├── endpoint.py
│   ├── endpoint.py
│   ├── index.html       # documentation
│   ├── .htaccess        # turn off .py extension
├── modules              # Custom classes, not accessible via HTTP
│   ├── lib/
│   │   ├── hermes.py    # HERMES!
│   │   ├── hades.py
│   ├── myobjectclasses.py
├── templates            # jinja templates, not accessible via HTTP
│   ├── www/
│   │   ├── file.jinja.htm
│   │   ├── subfolder/
│   │   │   ├── file.jinja.htm
├── www/                 # http://www.example.com via Apache <Directory> setting
│   ├── index.py
│   ├── subfolder/
│   │   ├── file.py
│   ├── .htaccess        # turn off .py extension
├── requirements.txt     # For easy installing of python dependencies
└── .gitignore
```

# Serving Content

### GET, POST, PATCH, and DELETE

Hermes connects HTTP methods with callback functions in your code. So if you want to support POST and PATCH, just tell hermes to connect that method to a function. In case you are making an API, Hermes will automatically update your `OPTIONS` method with the appropriate `Access-Control-Allow-Methods` header.

For example:

`/var/www/example.com/www/index.py`:

```python3
import sys
from os import environ
from hermes import HttpServer, WebManager

http_server = HttpServer(environ, sys.stdin)
web_manager = WebManager(http_server, database_manager)


def handle_get(http_server, database_manager):
    http_server.print_headers()
    print("<html><body><h1>GET method</h1></body></html>")

def handle_put_post(http_server, database_manager):
	# get form-encoded POST body - assume "name=John"
    post_parameters = http_server.get_post_parameters()
    name = post_parameters["name"]

    http_server.print_headers()
    print("<html><body>")
    print("<h1>POST or PUT method</h1>")
    print("<p>POST name=" + name + "</p>")
    print("</body></html>")


# connect GET HTTP method to local handle_get function
web_manager.set_method_callback(
    WebManager.HTTP_METHOD_GET,
    handle_get
)
# connect PUT and POST HTTP method to local handle_put_post function
web_manager.set_method_callback(
    WebManager.HTTP_METHOD_PUT,
    handle_put_post
)
web_manager.set_method_callback(
    WebManager.HTTP_METHOD_POST,
    handle_put_post
)
# unsupported methods will result in an 
# HTTP 405 Method not allowed error response
#web_manager.set_method_callback(
#    WebManager.HTTP_METHOD_DELETE,
#    handle_delete
#)
web_manager.run()
```



### Using a template library
If you are serving web content, you'll want a template library. You can use any one you want, but Jinja happens to be popular. Just follow the documentation for your favorite template library.

Here's an example of how to integrate with Jinja.

Your Jinja template might look like this:

`/var/www/example.com/templates/index.jinja.html`:
```markup 
<!DOCTYPE html>
<html>
	<head>
    	<title>Welcome {{ name }}</title>
    </head>
    <body>
        <h1>Welcome {{ name }}</h1>
    </body>
</html>
```

Your hermes file will import jinja2 libraries and have a way to fetch a template file, like this:

`/var/www/example.com/www/index.py`:
```python3
import sys
from os import environ
from hermes import HttpServer, WebManager
# Import jinja libraries
from jinja2 import Environment, select_autoescape, FileSystemLoader

http_server = HttpServer(environ, sys.stdin)
web_manager = WebManager(http_server, database_manager)


def fetch_template(template_file):
	"""Try to get a Jinja template."""
    template_loader = FileSystemLoader(
        settings["login_page"]["templates_folder"]
    )
    env = Environment(
        loader=template_loader,
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template(template_file)
    return template


def handle_get(http_server, database_manager):
	# Define what variables to populate in the template
    keys = {
        "name": "John",
    }
    # render the template to a string
    output = template.render(keys)
    # output the resulting HTML to your web server
    http_server.print_headers()
    print(output)


web_manager.set_method_callback(
    WebManager.HTTP_METHOD_GET,
    handle_get
)
web_manager.run()
```


### Using a database

Hermes is database agnostic, so you can attach any database you like. If you want a database that's designed with Hermes in mind, check out [Hades](https://github.com/backupbrain/hades), a lightweight MySQL database that creates objects from a detected table structure.

Let's assume you have a table with the following structure:
```sql
CREATE TABLE `person_info` {
	`id` UNSIGNED INT AUTO_INCREMENT PRIMARY_KEY,
    `name` VARCHAR(100) NOT NULL,
    `age` UNSIGNED INT,
    `created` DATETIME DEFAULT CURRENT_TIMESTAMP  
}
```
And assume you the table is populated with the following data:
|id|name|age|created            |
|-:|----|--:|------------------:|
|1 |John|32 |2019-04-12 12:23:33|
|1 |Mary|41 |2019-02-21 05:07:53|


Your Hades object will look like this:
`/var/www/example.com/modules.py`
```
from hades import DatabaseObject

class PersonInfo(DatabaseObject):

    def __init__(self, database_manager):
        self.database_manager = database_manager

```

Create a project settings file:

`/var/www/example.com/www/settings.py`:
```python3
mysql = {
  'server': '127.0.0.1',
  'port': '3306',
  'username': 'mysql_username',
  'password': 'mysql_password',
  'db': 'project_database',
  'charset': 'utf-8'
}

```

You may want to use Jinja to make templating easier:

`/var/www/example.com/templates/person.jinja.html;
```markup 
<!DOCTYPE html>
<html>
	<head>
    	<title>Welcome {{ person.name }}</title>
    </head>
    <body>
        <h1>Welcome {{ person.name }}</h1>
        <p>I see you are {{ person.age }} years old this year!</p>
    </body>
</html>
```

Your Hermes file will need to load Hades libraries, connect to the database, fetch a Person object, and render the output using Jinja.

`/var/www/example.com/www/subfolder/person.py`:
```python3
import sys
# make it easier to load libraries that exist outside of this folder
# we've put the modules.py and settings.py in the parent folder, so this makes it accessible with Python's import system
sys.path.append("../")
from os import environ
from hermes import HttpServer, WebManager
from hades import DatabaseManager, DatabaseObject
from modules import Person
from jinja2 import Environment, select_autoescape, FileSystemLoader
from settings import mysql  # a shared settings file

http_server = HttpServer(environ, sys.stdin)
web_manager = WebManager(http_server, database_manager)
# get query parameters for use later. Expect "?id=1" for this example
query_parameters = http_server.get_query_parameters()
# Connect to the database using the settings file
database_manager = DatabaseManager.from_settings(mysql)


def fetch_template(template_file):
	"""Try to get a Jinja template."""
    template_loader = FileSystemLoader(
        settings["login_page"]["templates_folder"]
    )
    env = Environment(
        loader=template_loader,
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template(template_file)
    return template


def handle_get(http_server, database_manager):
	id = int(query_parameters['id'])
    person = Person.fetch_by([
    	{key: 'id', 'equivalence': '=', 'value': 1}
    ])
    template = fetch_template("templates/person.jinja.htm")
    keys = {
        "person": person,
    }
    output = template.render(keys)
    http_server.print_headers()
    print(output)


def handle_post(http_server, database_manager):
	# get JSON POST body. Assume name=John&age=32
    # However Hermes supports multipart/form-data as well
    post_parameters = http_server.get_post_json()
	id = int(query_parameters['id'])
    person = Person.fetch_by([
    	{key: 'id', 'equivalence': '=', 'value': 1}
    ])
    person.name = post_parameters["name"]
    person.age = int(post_parameters["age"]
    person.update()
    template = fetch_template("templates/person.jinja.htm")
    keys = {
        "person": person,
    }
    output = template.render(keys)
    http_server.print_headers()
    print(output)


web_manager.set_method_callback(
    WebManager.HTTP_METHOD_GET,
    handle_get
)

web_manager.set_method_callback(
    WebManager.HTTP_METHOD_POST,
    handle_post
)
web_manager.run()

```

You can then fetch this REST Resource with an HTTP GET:

*Request:*
```data
GET /subfolder/person
Accept: text/html


```
*Response:*
```
HTTP 1.1 200 OK
Content-Type: text/html; encoding=utf-8

<!DOCTYPE html>
<html>
	<head>
    	<title>Welcome John</title>
    </head>
    <body>
        <h1>Welcome John</h1>
        <p>I see you are 32 years old this year!</p>
    </body>
</html>
```

Or update this REST Resource with an HTTP POST :

*Request:*

```
POST /subfolder/person HTTP/1.1
Accept: text/html
Content-Type: x-www-form-urlencoded

name=John&age=32
```

*Response:*

```
HTTP 1.1 200 OK
Content-Type: text/html; encoding=utf-8

<!DOCTYPE html>
<html>
	<head>
    	<title>Welcome John</title>
    </head>
    <body>
        <h1>Welcome John</h1>
        <p>I see you are 32 years old this year!</p>
    </body>
</html>
```



### Serving REST APIs

For Hermes, the only difference between serving Web content and serving a REST API is that the API is JSON. It expects to deliver different headers and expects the outbound content to be JSON rather than HTML.

For this it uses the `http_server.print_json(output)` method.
`web_manager.set_method_callback()` updates the `ALLOWED_METHODS` header of the HTTP Response automatically.

Let's serve a static REST API.

To be fully REST compatible, we turn off `.py` in Apache:

Remove `.py` extension by adding .htaccess in the
`/var/www/example.com/www` folder:
```.htaccess
# check if a /path/to/file.py file exist
# and rewrite it as /path/to/file
# otherwise - leave it alone, it's a static file or folder
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-d
RewriteCond %{REQUEST_FILENAME} !-f
RewriteRule (.*) $1.py [L]
```


We create a person endpoint using Hermes:

`/var/www/example.com/www/api/1.0/person.py`:
```python3
import sys
from datetime import datetime
# make it easier to load libraries that exist outside of this folder
# we've put the modules.py and settings.py in the parent folder, so this makes it accessible with Python's import system
sys.path.append("../")
from os import environ
from hermes import HttpServer, WebManager


http_server = HttpServer(environ, sys.stdin)
web_manager = WebManager(http_server, database_manager)


def handle_get(http_server, database_manager):
    output = {
        "name": "John",
        "age": "32",
        "created": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    http_server.print_headers()
    # Output JSON to the browser
    http_server.print_json(output)



def handle_post(http_server, database_manager):
	# get JSON POST body. Assume {"name":"John","age":33}
    post_parameters = http_server.get_post_json()
    person = {
    	"name": post_parameters["name"],
        "age": post_parameters["age"],
        "created"
    ])
    person.name = post_parameters["name"]
    person.update()
    template = fetch_template("templates/person.jinja.htm")
    keys = {
        "person": person,
    }
    output = template.render(keys)
    http_server.print_headers()
    print(output)


web_manager.set_method_callback(
    WebManager.HTTP_METHOD_GET,
    handle_get
)
web_manager.set_method_callback(
    WebManager.HTTP_METHOD_POST,
    handle_post
)
# Enable CORS for any host here
http_server.set_header('Access-Control-Allow-Origin', '*')
# This will output JSON
http_server.set_header('Conten-Type', 'application/json; encoding=utf=8')
web_manager.run()
```

The resulting GET response will be:

*Request:*
```
GET /api/1.0/person HTTP/1.1
Accept: application/json
Content-Type: application/json

```
*Response:*
```
HTTP 1.1 200 OK
Access-Control-Allow-Origin: *
Content-Type: application/json; encoding=utf-8

{"name":"John","age":32","created":"2019-02-21 05:07:53"}
```

And you can POST JSON to the API as well:

*Request:*
```
POST /api/1.0/person HTTP/1.1
Accept: application/json
Content-Type: application/json

{"name":"John","age":33"}
```
*Response:*
```
HTTP 1.1 200 OK
Access-Control-Allow-Origin: *
Content-Type: application/json; encoding=utf-8

{"name":"John","age":33","created":"2019-02-21 05:07:53"}
```

### Error Handling
Hermes has some error handling features as well. By design, Hermes doesn't print errors to the browser. This is considered a security feature. You can, however catch errors however you want and print to the browser.

For Hermes, errors are just HTTP status codes, so you can output whatever standard HTTP error you want.

`/var/www/example.com/www/error.py`:
```python3
import sys
from datetime import datetime
# make it easier to load libraries that exist outside of this folder
# we've put the modules.py and settings.py in the parent folder, so this makes it accessible with Python's import system
sys.path.append("../")
from os import environ
from hermes import HttpServer, WebManager


http_server = HttpServer(environ, sys.stdin)
web_manager = WebManager(http_server, database_manager)


def handle_get(http_server):
	# tell Hermes what error to show. for example a "404 Not Found"
    http_server.set_status(404)
    http_server.print_headers()
    # Custom 404 page
	print("<html><body><h1>Not Found</h1></body></html>")

web_manager.set_method_callback(
    WebManager.HTTP_METHOD_GET,
    handle_get
)
web_manager.run()
```


Your error will be output like this:

*Request:*
```
GET /error HTTP/1.1
Accept: text/html


```
*Response:*
```
HTTP 1.1 404 Not Found
Content-Type: text/html

<html><body><h1>Not Found</h1></body></html>
```

For reference, here's list of [HTTP 1.1 Status Codes](https://en.wikipedia.org/wiki/List_of_HTTP_status_codes)

### Cookies

Hermes can work with Cookies as well.

#### Drop a Cookie
You can drop a cookie


`/var/www/example.com/www/cookies/drop.py`:
```python3
import sys
from datetime import datetime
# make it easier to load libraries that exist outside of this folder
# we've put the modules.py and settings.py in the parent folder, so this makes it accessible with Python's import system
sys.path.append("../")
from os import environ
from hermes import HttpServer, WebManager


http_server = HttpServer(environ, sys.stdin)
web_manager = WebManager(http_server, database_manager)


def handle_get(http_server):
	http_server.set_cookie("key","value")
    http_server.print_headers()
	print("<html><body><h1>Cookie Dropped</h1></body></html>")

web_manager.set_method_callback(
    WebManager.HTTP_METHOD_GET,
    handle_get
)
web_manager.run()
```


The result will look like this:

*Request:*
```
GET /cookies/drop.py HTTP/1.1
Accept: text/html


```
*Response:*
```
HTTP 1.1 404 Not Found
Content-Type: text/html
Cookie: key=value

<html><body><h1>Cookie Dropped</h1></body></html>
```

#### Read a Cookie
You can read a cookie


`/var/www/example.com/www/cookies/drop.py`:
```python3
import sys
from datetime import datetime
# make it easier to load libraries that exist outside of this folder
# we've put the modules.py and settings.py in the parent folder, so this makes it accessible with Python's import system
sys.path.append("../")
from os import environ
from hermes import HttpServer, WebManager


http_server = HttpServer(environ, sys.stdin)
web_manager = WebManager(http_server, database_manager)


def handle_get(http_server):
	# get a cookie with the default value being "unset" if not found
	cookie_value = http_server.get_cookie("key", "unset")
    http_server.print_headers()
	print(
    	"<html><body><h1>Cookie:</h1><p>{}</p></body></html>".format(
            cookie_value
        )
    )

web_manager.set_method_callback(
    WebManager.HTTP_METHOD_GET,
    handle_get
)
web_manager.run()
```


#### Delete a Cookie
You can read a cookie


`/var/www/example.com/www/cookies/drop.py`:
```python3
import sys
from datetime import datetime
# make it easier to load libraries that exist outside of this folder
# we've put the modules.py and settings.py in the parent folder, so this makes it accessible with Python's import system
sys.path.append("../")
from os import environ
from hermes import HttpServer, WebManager


http_server = HttpServer(environ, sys.stdin)
web_manager = WebManager(http_server, database_manager)


def handle_get(http_server):
	# get a cookie with the default value being "unset" if not found
	http_server.delete_cookie("key", "unset")
    http_server.print_headers()
	print(
    	"<html><body><h1>Cookie Deleted</h1></body></html>")
    )

web_manager.set_method_callback(
    WebManager.HTTP_METHOD_GET,
    handle_get
)
web_manager.run()
```

