# server.py

from flask import Flask, jsonify, make_response, request

from pyjas.v1_1.content_negotiation import AcceptHeaderError, ContentNegotiation, ContentTypeError

app = Flask(__name__)

# Define the list of supported extensions
SUPPORTED_EXTENSIONS = ['https://example.com/extensions/feature']

# Instantiate the ContentNegotiation helper
content_negotiation = ContentNegotiation(supported_extensions=SUPPORTED_EXTENSIONS)


@app.before_request
def before_request():
    # Validate the Content-Type header for POST, PUT, PATCH requests
    if request.method in ['POST', 'PUT', 'PATCH']:
        content_type_str = request.headers.get('Content-Type', '')
        try:
            content_negotiation.validate_content_type_header(content_type_str)
        except ContentTypeError as e:
            return make_response(jsonify({'errors': [{'detail': str(e)}]}), 415)

    # Validate the Accept header
    accept_header = request.headers.get('Accept', '*/*')
    try:
        content_negotiation.validate_accept_header(accept_header)
    except AcceptHeaderError as e:
        return make_response(jsonify({'errors': [{'detail': str(e)}]}), 406)


@app.after_request
def after_request(response):
    # Set the Vary header if needed
    response.headers['Vary'] = content_negotiation.generate_vary_header()
    return response


@app.route('/articles', methods=['GET'])
def get_articles():
    # Example response
    data = {'data': [{'type': 'articles', 'id': '1', 'attributes': {'title': 'JSON API paints my bikeshed!'}}]}
    response = jsonify(data)
    response.headers['Content-Type'] = ContentType.MEDIA_TYPE
    return response


if __name__ == '__main__':
    app.run()
