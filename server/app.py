#!/usr/bin/env python3

from flask import request, session, make_response
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    
    def post(self):
        try:
            json = request.get_json()
            user = User(
                username=json.get('username'),
                image_url=json.get('image_url'),
                bio=json.get('bio')
            )
            user.password_hash = json['password']
            if user:
                db.session.add(user)
                db.session.commit()
                session['user_id'] = user.id
                return user.to_dict(), 201
            return {'error': 'Invalid information submitted'}, 422
        except:
            return {'error': 'Invalid user information'}, 422

class CheckSession(Resource):
    
    def get(self):
        if session['user_id']:
            user = User.query.filter(User.id == session['user_id']).first()
            return user.to_dict(), 200
        return {'error': 'Not logged in'}, 401

class Login(Resource):
    
    def post(self):
        json = request.get_json()
        user = User.query.filter(User.username == json['username']).first()
        if not user: return {'error': 'Invalid username or password'}, 401
        if user and user.authenticate(json['password']):
            session['user_id'] = user.id
            return user.to_dict(), 201
        else:
            return {'error': 'Invalid username or password'}, 401

class Logout(Resource):
    
    def delete(self):
        if session.get('user_id'): 
            session['user_id'] = None
            return {}, 204
        return {'error': 'You are not logged in'}, 401

class RecipeIndex(Resource):
    
    def get(self):
        if session.get('user_id'):
            recipes = [recipe.to_dict() for recipe in Recipe.query.filter(Recipe.user_id == session['user_id']).all()]
            return make_response(recipes, 200)
        return {'error': 'You are not logged in'}, 401
    
    def post(self):
        try:
            json=request.get_json()
            if session.get('user_id'):
                recipe = Recipe(
                    title=json.get('title'),
                    instructions=json.get('instructions'),
                    minutes_to_complete=json.get('minutes_to_complete')
                )
                user = User.query.filter(User.id == session['user_id']).first()
                recipe.user = user
                db.session.add(recipe)
                db.session.commit()
                return recipe.to_dict(), 201
            return {'error': 'You are not logged in'}, 401
        except:
            return {'error': 'Invalid recipe'}, 422


api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)