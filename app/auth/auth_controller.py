from app.auth import bp
from flask import request,jsonify
import validators
from app.models.users import User,TokenBlocklist
from app.status_codes import HTTP_400_BAD_REQUEST,HTTP_409_CONFLICT,HTTP_500_INTERNAL_SERVER_ERROR,HTTP_201_CREATED,HTTP_401_UNAUTHORIZED,HTTP_200_OK
from app.extensions import db,bcrypt
from flask_jwt_extended import create_access_token,jwt_required,unset_jwt_cookies,get_jwt



#User Registration
@bp.route('/register',methods=['Post'])
def register_user():
     
    data=request.json
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    contact = data.get('contact')
    email =data.get('email')
    password = data.get('password')
    role=data.get('role')
    #validations of the incoming request
    if not first_name or not last_name or not contact or not password or not email:
        return jsonify({"error": "All fields are required"}), HTTP_400_BAD_REQUEST
    
    if len(password) < 8:
        return jsonify({"error":"Password is too short"}),HTTP_400_BAD_REQUEST
    
    if not validators.email(email):
        return jsonify({"error":"Email is not valid"}),HTTP_400_BAD_REQUEST
    
    if User.query.filter_by(email=email).first() is not None:
        return jsonify({"error":"Email is already in use"}),HTTP_409_CONFLICT
    
    if User.query.filter_by(contact=contact).first() is not None:
        return jsonify({"error":"Contact is already in use"}),HTTP_409_CONFLICT
    

    try:
        #creating new user in usersTable
        hashed_password = bcrypt.generate_password_hash(password)
        new_user=User(first_name =first_name, last_name=last_name, contact=contact,  password =hashed_password , email =email,role=role)
        db.session.add(new_user)
        db.session.commit()

        #username
        username=new_user.get_fullName()

        return jsonify({"message":username + " has been sucessfully registered","user":{
            "id":new_user.id,
            "first_name":new_user.first_name,
            "last_name":new_user.last_name,
            "email": new_user.email,
            "contact": new_user.contact,
            'created_at':new_user.created_at}
            }),HTTP_201_CREATED
    except Exception as e:
        db.session.rollback()
        return jsonify({"error":str(e)}),HTTP_500_INTERNAL_SERVER_ERROR
    

#User Login
    
@bp.post('/login')
def login():

    email=request.json.get('email')
    password=request.json.get('password')

    try:
        if not password or not email:
            return jsonify({'message':'email and password are required'}),HTTP_400_BAD_REQUEST

        user=User.query.filter_by(email=email).first()

        if user:
            is_correct_password=bcrypt.check_password_hash(user.password,password)

            if is_correct_password:
                access_token=create_access_token(identity=user.id)

                return jsonify({
                    "message":" you has been sucessfully logged in",
                    "user":{
                        "id":user.id,
                        "username":user.get_fullName(),
                        "email": user.email,
                        "access_token":access_token}
                        }),HTTP_200_OK
            else:
                return jsonify({'message':'Invalid Password'}),HTTP_401_UNAUTHORIZED

        else:
            return jsonify({'message':'Invalid Email address'}),HTTP_401_UNAUTHORIZED


    except Exception as e:
        return jsonify({
            'error':str(e)
        }),HTTP_500_INTERNAL_SERVER_ERROR


#User Logout
@bp.route('/logout', methods=['POST'])
@jwt_required(verify_type=False)
def logout():
    """
    Logout route for revoking the current user's access and refresh tokens.
    """
    try:
        jwt = get_jwt()

        jti = jwt['jti']
        token_type = jwt['type']

        token_b = TokenBlocklist(jti=jti)

        token_b.save()


        # Return a success message
        return jsonify({'message': 'Logout successful'}), HTTP_200_OK

    except Exception as e:
        # Handle any exceptions that may occur
        error_message = f"An error occurred: {str(e)}"
        return jsonify({'error': error_message}), HTTP_500_INTERNAL_SERVER_ERROR
    
