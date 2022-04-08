from flask import request, json
from flask_restful import Resource

from common import logger
from common.exception import NotFoundException, NotMatchingException, NotUniqueException, InternalServerException
from .models import Label
from .validators import validate_add_label, validate_if_label_exists
from flask_jwt_extended import get_jwt_identity, jwt_required


class Label_API(Resource):
    @jwt_required()
    def post(self):
        data = json.loads(request.data)
        decoded_data = get_jwt_identity()
        user_id = decoded_data
        label = data.get('label')
        validate_data = validate_add_label(data)
        try:
            if not user_id:
                raise InternalServerException('Token is missing', 400)
            if validate_data:
                return validate_data
            lb = Label(label=label, user_id=user_id)


            lb.save()
            logger.logging.info('label added')
            return {'message': 'label added', 'status code': 200}
        except InternalServerException as e:
            logger.logging.info('Some error occurred')
            return e.__dict__

    @jwt_required()
    def get(self):
        user_labels = []
        user_id = get_jwt_identity()
        labels = Label.objects.filter(user_id=user_id)
        try:
            if not labels:
                raise NotFoundException('label could not be found', 400)
            for label in labels:
                dict_itr = label.to_dict()
                user_labels.append(dict_itr)
            logger.logging.info('notes displayed')
            return {user_id: user_labels, 'status code': 200}
        except NotFoundException as e:
            logger.logging.info('Some error occurred')
            return e.__dict__


class LabelFunctionalityAPI(Resource):
    def delete(self, id):
        validate_data = validate_if_label_exists(id)
        if validate_data:
            return validate_data
        lb = Label.objects.get(id=id)
        try:
            if not lb:
                raise NotFoundException('label could not be found', 400)
            lb.delete()
            return {'message': 'label deleted', 'status code': 200}
        except NotFoundException as e:
            logger.logging.info('Some error occurred')
            return e.__dict__

    @jwt_required()
    def patch(self, id):
        data = json.loads(request.data)
        updated_label = data.get('updated_label')
        validate_data = validate_if_label_exists(id)
        if validate_data:
            return validate_data
        lb = Label.objects.get(id=id)
        lb['label'] = updated_label
        try:
            if not updated_label:
                raise NotFoundException('updated label field is empty', 400)
            lb.save()
            return {
                'label': lb['label'],
                'status code': 200
            }
        except NotFoundException as e:
            logger.logging.info('Some error occurred')
            return e.__dict__

    @jwt_required()
    def get(self, id):
        validate_data = validate_if_label_exists(id)
        try:
            if validate_data:
                return validate_data
            lb = Label.objects.get(id=id)
            if not lb:
                raise NotFoundException('label does not exist', 400)
            return {
                'id': lb['id'],
                'label': lb['label'],
                'user_id': lb['user_id']
            }
        except NotFoundException as e:
            logger.logging.info('Some error occurred')
            return e.__dict__
