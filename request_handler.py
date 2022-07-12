from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from urllib import response
from urllib.parse import urlparse, parse_qs
from views import get_all_animals, get_single_animal, get_single_location, get_all_locations
from views import get_single_employee, get_all_employees, create_animal, create_employee
from views import create_location, get_single_customer, get_all_customers, create_customer
from views import delete_animal, delete_location, delete_employee, delete_customer
from views import update_animal, update_customer, update_employee, update_location
from views import get_customer_by_email, get_animals_by_location, get_employees_by_location
from views import get_animals_by_status

# Here's a class. It inherits from another class.
# For now, think of a class as a container for functions that
# work together for a common purpose. In this case, that
# common purpose is to respond to HTTP requests from a client.
class HandleRequests(BaseHTTPRequestHandler):
    # This is a Docstring it should be at the beginning of all classes and functions
    # It gives a description of the class or function
    """Controls the functionality of any GET, PUT, POST, DELETE requests to the server
    """

    # replace the parse_url function in the class
    def parse_url(self):
        """Parse the url into the resource and id"""
        parsed_url = urlparse(self.path)
        path_params = parsed_url.path.split('/')  # ['', 'animals', 1]
        resource = path_params[1]

        if parsed_url.query:
            query = parse_qs(parsed_url.query)
            return (resource, query)

        pk = None
        try:
            pk = int(path_params[2])
        except (IndexError, ValueError):
            pass
        return (resource, pk)

    # Here's a class function
    def _set_headers(self, status):
        # Notice this Docstring also includes information about the arguments passed to the function
        """Sets the status code, Content-Type and Access-Control-Allow-Origin
        headers on the response

        Args:
            status (number): the status code to return to the front end
        """
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    # Another method! This supports requests with the OPTIONS verb.
    def do_OPTIONS(self):
        """Sets the options headers
        """
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE')
        self.send_header('Access-Control-Allow-Headers', 'X-Requested-With, Content-Type, Accept')
        self.end_headers()

    # Here's a method on the class that overrides the parent's method.
    # It handles any GET request.
    def do_GET(self):
        """Get"""
        self._set_headers(200)

        response = {}

        # Parse URL and store entire tuple in a variable
        parsed = self.parse_url()

        # If the path does not include a query parameter, continue with the original if block
        if '?' not in self.path:
            ( resource, id ) = parsed

            if resource == "animals":
                if id is not None:
                    response = f"{get_single_animal(id)}"
                else:
                    response = f"{get_all_animals()}"
            elif resource == "customers":
                if id is not None:
                    response = f"{get_single_customer(id)}"
                else:
                    response = f"{get_all_customers()}"

        else: # There is a ? in the path, run the query param functions
            (resource, query) = parsed
            # see if the query dictionary has an email key
            if query.get('email') and resource == 'customers':
                response = get_customer_by_email(query['email'][0])
            if query.get('location_id') and resource == 'animals':
                response = get_animals_by_location(query['location_id'][0])
            if query.get('location_id') and resource == 'employees':
                response = get_employees_by_location(query['location_id'][0])
            if query.get('status') and resource == 'animals':
                response = get_animals_by_status(query['status'][0])

        self.wfile.write(response.encode())

    # Here's a method on the class that overrides the parent's method.
    # It handles any POST request.
    def do_POST(self):
        """_summary_
        """
        self._set_headers(201)
        content_len = int(self.headers.get('content-length', 0))
        post_body = self.rfile.read(content_len)

        # Convert JSON string to a Python dictionary
        post_body = json.loads(post_body)

        # Parse the URL
        (resource, id) = self.parse_url()

        # Initialize new animal
        response = None

        # Add a new animal to the list. Don't worry about
        # the orange squiggle, you'll define the create_animal
        # function next.
        if resource == "animals":
            response = create_animal(post_body)
        if resource == "employees":
            response = create_employee(post_body)
        if resource == "locations":
            response = create_location(post_body)
        if resource == "customers":
            response = create_customer(post_body)

        # Encode the new animal and send in response
        self.wfile.write(f"{response}".encode())

    # Here's a method on the class that overrides the parent's method.
    # It handles any PUT request.

    def do_PUT(self):
        """Handles PUT requests to the server
        """
        self._set_headers(204)
        content_len = int(self.headers.get('content-length', 0))
        post_body = self.rfile.read(content_len)
        post_body = json.loads(post_body)

        # Parse the URL
        (resource, id) = self.parse_url()

        # Delete a single animal from the list
        if resource == "animals":
            update_animal(id, post_body)
        if resource == "employees":
            update_employee(id, post_body)
        if resource == "customers":
            update_customer(id, post_body)
        if resource == "locations":
            update_location(id, post_body)

        # Encode the new animal and send in response
        self.wfile.write("".encode())
        self.do_POST()

    def do_DELETE(self):
        """Delete an animal"""
        # Set a 204 response code
        self._set_headers(204)

        # Parse the URL
        (resource, id) = self.parse_url()

        # Delete a single animal from the list
        if resource == "animals":
            delete_animal(id)
        if resource == "employees":
            delete_employee(id)
        if resource == "customers":
            delete_customer(id)
        if resource == "locations":
            delete_location(id)

        # Encode the new animal and send in response
        self.wfile.write("".encode())


# This function is not inside the class. It is the starting
# point of this application.
def main():
    """Starts the server on port 8088 using the HandleRequests class
    """
    host = ''
    port = 8088
    HTTPServer((host, port), HandleRequests).serve_forever()


if __name__ == "__main__":
    main()
