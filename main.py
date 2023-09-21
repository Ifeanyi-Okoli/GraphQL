from flask import Flask, request, jsonify
from flask_graphql import GraphQLView
from graphene import ObjectType, String, Schema, Field, Boolean
from flask_sqlalchemy import SQLAlchemy, SQLAlchemyObjectType
from graphql import GraphQLError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)



class UserType(SQLAlchemyObjectType):
    class Meta:
        model = User

class SignupUser(ObjectType):
    username = String(required=True)
    password = String(required=True)
    success = Boolean()

class LoginUser(ObjectType):
    username = String(required=True)
    password = String(required=True)
    success = Boolean()
    user = Field(UserType)


#Define your User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    


class Mutation(ObjectType):
    signup_user = Field(SignupUser, username=String(required=True), password=String(required=True))

    def resolve_signup_user(self, info, username, password):
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return SignupUser(username=username, success=True)

    login_user = Field(LoginUser, username=String(required=True), password=String(required=True))

    def resolve_login_user(self, info, username, password):
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            return LoginUser(username=username, success=True, user=user)
        else:
            raise GraphQLError("Invalid username or password")

#Define GraphQL Scheme
class Query(ObjectType):
    hello = String(name=String(default_value="world"))
    
schema = Schema(query=Query)

app.add_url_rule('graphql', view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True))

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)