import os
import mimetypes
from flask import render_template, abort, jsonify, send_file, current_app, g, request
from .utils import write_file, dir_tree, get_file_extension
from . import blueprint


@blueprint.route('/<string:resource_dir>')
def index(resource_dir):
    dtree = dir_tree(g.resource_dir_path, g.resource_dir_path + '/')
    return render_template('flaskcode/index.html', resource_dir=resource_dir, dtree=dtree)


@blueprint.route('/resource-data/<string:resource_dir>/<path:file_path>.txt', methods=['GET', 'HEAD'])
def resource_data(resource_dir, file_path):
    file_path = os.path.join(g.resource_dir_path, file_path)
    if not (os.path.exists(file_path) and os.path.isfile(file_path)):
        abort(404)
    response = send_file(file_path, mimetype='text/plain', cache_timeout=0)
    mimetype, encoding = mimetypes.guess_type(file_path, False)
    if mimetype:
        response.headers.set('X-File-Mimetype', mimetype)
        extension = mimetypes.guess_extension(mimetype, False) or get_file_extension(file_path)
        if extension:
            response.headers.set('X-File-Extension', extension.lower().lstrip('.'))
    if encoding:
        response.headers.set('X-File-Encoding', encoding)
    return response


@blueprint.route('/update-resource-data/<string:resource_dir>/<path:file_path>', methods=['POST'])
def update_resource_data(resource_dir, file_path):
    file_path = os.path.join(g.resource_dir_path, file_path)
    new_resource = bool(int(request.form.get('new_resource', 0)))
    if not new_resource and not (os.path.exists(file_path) and os.path.isfile(file_path)):
        abort(404)
    success = True
    message = 'File saved successfully'
    resource_data = request.form.get('resource_data', None)
    if resource_data:
        success, message = write_file(resource_data, file_path)
    else:
        success = False
        message = 'File data not uploaded'
    return jsonify({'success': success, 'message': message})