"""
External endpoints to manage the instances: create new ones, or get all the instances created by the user,
or get only one.
These endpoints have different access url, but manage the smae data entities
"""
# Import from libraries
from flask import request
from werkzeug.utils import secure_filename
from flask_restful import fields, marshal_with, marshal
from marshmallow.exceptions import ValidationError
import os
import pulp

# Import from internal modules
from .meta_resource import MetaResource
from ..models import InstanceModel
from ..schemas import InstanceSchema
from ..shared.authentication import Auth

# Initialize the schema that all endpoints are going to use
# TODO: instance_schema is not used.
instance_schema = InstanceSchema()
ALLOWED_EXTENSIONS = {'mps', 'lp'}

class InstanceEndpoint(MetaResource):
    """
    Endpoint used to create a new instance or get all the instances and their related information
    """
    resource_fields = \
        dict(
            id=fields.String,
            name=fields.String,
            description=fields.String,
            created_at=fields.String
        )

    def __init__(self):
        super().__init__()
        self.model = InstanceModel
        self.query = 'get_all_instances'
        self.schema = InstanceSchema()
        self.primary_key = 'id'

    @Auth.auth_required
    @marshal_with(resource_fields)
    def get(self):
        """
        API (GET) method to get all the instances created by the user and its related info
        It requires authentication to be passed in the form of a token that has to be linked to
        an existing session (login) made by a user

        :return: a dictionary with a message or an object (message if it an error is encountered,
          object with the data from the instances otherwise) and an integer with the HTTP status code
        :rtype: Tuple(dict, integer)
        """
        # TODO: if super_admin or admin should it be able to get any instance?
        self.user_id, self.admin, self.super_admin = Auth.return_user_info(request)
        return self.get_list(self.user_id)

    @Auth.auth_required
    # @marshal_with(resource_fields)
    def post(self):
        """
        API (POST) method to create a new instance
        It requires authentication to be passed in the form of a token that has to be linked to
        an existing session (login) made by a user

        :return: a dictionary with a message(either an error encountered during creation
          or the reference_id of the instance created if successful) and an integer with the HTTP status code
        :rtype: Tuple(dict, integer)
        """
        self.user_id, self.admin, self.super_admin = Auth.return_user_info(request)
        return self.post_list(request)


class InstanceDetailsEndpoint(InstanceEndpoint):
    """
    Endpoint used to get the information ofa single instance, edit it or delete it
    """
    resource_fields = dict(
        id=fields.String,
        name=fields.String,
        description=fields.String,
        created_at=fields.String,
        executions= fields.List(fields.Nested(
            dict(id=fields.String,
                 config=fields.Raw,
                 name=fields.String,
                 created_at=fields.String,
                 finished=fields.String)
        ))
    )
    def __init__(self):
        super().__init__()
        # TODO: should this query use user as well?
        self.query = 'get_one_instance_from_user'
        self.dependents = 'executions'

    @Auth.auth_required
    @marshal_with(resource_fields)
    def get(self, idx):
        """
        API method to get an instance created by the user and its related info.
        It requires authentication to be passed in the form of a token that has to be linked to
        an existing session (login) made by a user.

        :param str idx: ID of the instance
        :return: A dictionary with a message (error if authentication failed, or the execution does not exist or
          the data of the instance) and an integer with the HTTP status code.
        :rtype: Tuple(dict, integer)
        """
        self.user_id, self.admin, self.super_admin = Auth.return_user_info(request)
        # TODO: filter only the execution (ids, created_at, name, description) fields and not the rest of details of the execution.
        return self.get_detail(self.user_id, idx)

    @Auth.auth_required
    def put(self, idx):
        """
        API method to edit an existing instance.
        It requires authentication to be passed in the form of a token that has to be linked to
        an existing session (login) made by a user.

        :param str idx: ID of the instance
        :return: A dictionary with a message (error if authentication failed, or the execution does not exist or
          a message) and an integer with the HTTP status code.
        :rtype: Tuple(dict, integer)
        """
        self.user_id, self.admin, self.super_admin = Auth.return_user_info(request)
        return self.put_detail(request, self.user_id, idx)

    @Auth.auth_required
    def delete(self, idx):
        """
        API method to delete an existing instance.
        It requires authentication to be passed in the form of a token that has to be linked to
        an existing session (login) made by a user.

        :param str idx: ID of the instance
        :return: A dictionary with a message (error if authentication failed, or the execution does not exist or
          a message) and an integer with the HTTP status code.
        :rtype: Tuple(dict, integer)
        """
        self.user_id, self.admin, self.super_admin = Auth.return_user_info(request)
        return self.delete_detail(self.user_id, idx)


class InstanceDataEndpoint(InstanceDetailsEndpoint):
    """
    Endpoint used to get the information ofa single instance, edit it or delete it
    """
    # TODO: now sure if we should give the data schema here.
    #  it doesn't appear to accept Marshmallow schemas
    #  fields.Raw does not validation
    resource_fields = dict(
        id=fields.String,
        name=fields.String,
        data=fields.Raw,
    )
    def __init__(self):
        super().__init__()
        self.dependents = None

    @Auth.auth_required
    @marshal_with(resource_fields)
    def get(self, idx):
        """
        API method to get an instance data by the user and its related info.
        It requires authentication to be passed in the form of a token that has to be linked to
        an existing session (login) made by a user.

        :param str idx: ID of the instance
        :return: A dictionary with a message (error if authentication failed, or the execution does not exist or
          the data of the instance) and an integer with the HTTP status code.
        :rtype: Tuple(dict, integer)
        """
        self.user_id, self.admin, self.super_admin = Auth.return_user_info(request)
        # TODO: filter only the execution (ids, created_at, name, description) fields and not the rest of details of the execution.
        return self.get_detail(self.user_id, idx)


class InstanceFileEndpoint(InstanceEndpoint):
    """
    Endpoint to accept mps files to upload
    """

    @Auth.auth_required
    def post(self):
        """

        :param file:
        :return:
        :rtype: Tuple(dict, integer)
        """
        self.user_id, self.admin, self.super_admin = Auth.return_user_info(request)
        name = request.form.get('name', '')
        description = request.form.get('description', '')
        if 'file' not in request.files:
            return dict(error="No file was provided"), 400
        file = request.files['file']
        filename = secure_filename(file.filename)
        if not (file and allowed_file(filename)):
            return {'error': "Could not open file to upload. Check the extension matches {}.".
                format(ALLOWED_EXTENSIONS)}, 400
        file.save(filename)
        try:
            _vars, problem = pulp.LpProblem.fromMPS(filename)
        except:
            return {'error': "There was an error reading the file."}, 400
        try:
            os.remove(filename)
        except:
            pass

        pb_data = dict(
            data=problem.toDict()
            ,name=name
            ,description=description
            ,user_id=self.user_id
        )

        try:
            self.data = self.schema.load(pb_data)
        except ValidationError as val_err:
            return {'error': val_err.normalized_messages()}, 400

        item = self.model(self.data)
        item.save()

        return {self.primary_key: getattr(item, self.primary_key)}, 201


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
