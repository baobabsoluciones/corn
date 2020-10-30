"""
External endpoints to manage the instances: create new ones, or get all the instances created by the user,
or get only one.
These endpoints have different access url, but manage the smae data entities
"""
# Import from libraries
from flask import request
from flask_restful import Resource

# Import from internal modules
from ..models import InstanceModel
from ..schemas import InstanceSchema
from ..shared import Auth

# Initialize the schema that all endpoints are going to use
instance_schema = InstanceSchema()


class InstanceEndpoint(Resource):
    """
    Endpoint used to create a new instance or get all the instances and their related information
    """
    @Auth.auth_required
    def get(self):
        """
        API (GET) method to get all the instances created by the user and its related info
        It requires authentication to be passed in the form of a token that has to be linked to
        an existing session (login) made by a user

        :return: a dictionary with a message or an object (message if it an error is encountered,
        object with the data from the instances otherwise) and an integer with the HTTP status code
        :rtype: Tuple(dict, integer)
        """
        # TODO: if super_admin or admin should it be able to get any execution?
        # TODO: return 204 if no instances have been created by the user
        user_id, admin, super_admin = Auth.return_user_info(request)
        instances = InstanceModel.get_all_instances(user_id)
        ser_instances = instance_schema.dump(instances, many=True)

        return ser_instances, 200

    @Auth.auth_required
    def post(self):
        """
        API (POST) method to create a new instance
        It requires authentication to be passed in the form of a token that has to be linked to
        an existing session (login) made by a user

        :return: a dictionary with a message(either an error encountered during creation
        or the reference_id of the instance created if successful) and an integer with the HTTP status code
        :rtype: Tuple(dict, integer)
        """
        req_data = request.get_json()
        # TODO: catch possible validation error and process it to give back a more meaningful error message
        data = instance_schema.load(req_data, partial=True)

        data['user_id'], admin, super_admin = Auth.return_user_info(request)
        print(data)

        instance = InstanceModel(data)
        instance.save()

        ser_data = instance_schema.dump(instance)

        return {'instance_id': ser_data.get('reference_id')}, 201


# TODO: implement this new endpoint and its methods: get one instance and its related data,
#  modify one instance (data or owner?), delete one instance and its related info
class InstanceDetailsEndpoint(Resource):
    """
    Endpoint used to get the information of a certain instance
    """
    @Auth.auth_required
    def get(self, reference_id):
        """
        API (GET) method to get an instance created by the user and its related info.
        It requires authentication to be passed in the form of a token that has to be linked to
        an existing session (login) made by a user.


        :param str reference_id: ID of the instance
        :return: A dictionary with a message (error if authentication failed, or the instance does not exist or
        the data of the instance) and an integer with the HTTP status code.
        :rtype: Tuple(dict, integer)
        """
        instance = InstanceModel.get_one_instance_with_reference(reference_id)
        ser_instance = instance_schema.dump(instance, many=False)

        return ser_instance, 200

    @Auth.auth_required
    def put(self, reference_id):
        """
        NOT IMPLEMENTED
        API (PUT) method to update an instance and its related info
        It requires authentication to be passed in the form of a token that has to be linked to
        an existing session (login) made by a user.

        :param str reference_id: ID of the instance
        :return:
        :rtype:
        """
        return {'error': 'Method not allowed'}, 403

    @Auth.auth_required
    def delete(self, reference_id):
        """
        NOT IMPLEMENTED
        API (DELETE) method to delete an instance and its related info
        It requires authentication to be passed in the form of a token that has to be linked to
        an existing session (login) made by a user.

        :param str reference_id: ID of the instance
        :return:
        :rtype:
        """
        return {'error': 'Method not allowed'}, 403
