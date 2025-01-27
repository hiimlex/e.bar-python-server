from flask import Blueprint, request, jsonify
from ..models import Waiters
from werkzeug.security import generate_password_hash
from flask_jwt_extended import jwt_required
from .. import db
from sqlalchemy import asc,desc

bp = Blueprint('waiters', __name__, url_prefix='/waiters')

@bp.route('', methods=['GET'])
@jwt_required()
def get_waiters():
    filters = request.args
    query = Waiters.query
    
    if 'sort_key' in filters:
        if 'sort' in filters:
            if filters['sort_key'] == 'name':
                if(filters['sort'] == 'desc'):
                    query = query.order_by(desc(Waiters.name))
                else:
                    query = query.order_by(asc(Waiters.name))
    else:
        query = query.order_by(asc(Waiters.name))

    if 'name' in filters:
        query = query.filter(Waiters.name.ilike(f"%{filters['name']}%"))

    if 'is_admin' in filters:
        query = query.filter(Waiters.is_admin == True)

    if 'is_active' in filters:
        query = query.filter(Waiters.active == filters['is_active'])

    waiters = query.all()

    return jsonify([waiter.as_dict() for waiter in waiters])

@bp.route('', methods=['POST'])
@jwt_required()
def create_waiter():
    data = request.get_json()

    hash_password = generate_password_hash(data['password'])

    new_waiter = Waiters(
        name=data['name'],
        email=data['email'],
        phone=data.get('phone'),
        password=hash_password,
        is_active=data.get('active', True),
        is_admin=data.get('is_admin', False)
    )
    db.session.add(new_waiter)
    db.session.commit()
    return jsonify(new_waiter.as_dict()), 201

@bp.route('/<int:waiter_id>', methods=['PUT'])
@jwt_required()
def update_waiter(waiter_id):
    data = request.get_json()
    waiter = Waiters.query.get_or_404(waiter_id)
    waiter.name = data.get('name', waiter.name)
    waiter.email = data.get('email', waiter.email)
    waiter.phone = data.get('phone', waiter.phone)
    waiter.is_active = data.get('active', waiter.is_active)
    waiter.is_admin = data.get('is_admin', waiter.is_admin)
    db.session.commit()
    return jsonify(waiter.as_dict())

@bp.route('/<int:waiter_id>', methods=['DELETE'])
@jwt_required()
def delete_waiter(waiter_id):
    waiter = Waiters.query.get_or_404(waiter_id)
    db.session.delete(waiter)
    db.session.commit()
    return '', 204
