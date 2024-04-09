from app.main import bp
from flask import request,jsonify
import validators
from app.models.users import Community
from app.status_codes import HTTP_400_BAD_REQUEST,HTTP_409_CONFLICT,HTTP_500_INTERNAL_SERVER_ERROR,HTTP_201_CREATED,HTTP_401_UNAUTHORIZED,HTTP_200_OK,HTTP_404_NOT_FOUND
from app.extensions import db,bcrypt
from flask_jwt_extended import jwt_required, get_jwt,current_user
from flask import request, jsonify
from app.auth import bp
from app.models.users import User ,Event,JoinRequest
from app.status_codes import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from app.extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from flask import send_file
import io
@bp.route('/')
def index():
    return 'This is The Main Blueprint'

#patch route for user
@bp.route('/users/<int:user_id>', methods=['PATCH'])
@jwt_required()
def update_user(user_id):
    try:
        data = request.get_json()
        user = User.query.get_or_404(user_id)

        # Check if the user making the request is the same as the user being updated
        current_user_id = get_jwt_identity()
        if user.id != current_user_id:
            return jsonify({'error': 'You are not authorized to update this user'}),403

        # Update the user's data
        if 'points' in data:
            user.points = data['points']
        if 'awards' in data:
            user.awards = data['awards']
        if 'hours' in data:
            user.hours = data['hours']
        if 'date_of_birth' in data:
            date_of_birth = datetime.strptime(data['date_of_birth'], '%d/%m/%Y')
            user.date_of_birth = date_of_birth
        if 'interested_in_volunteer' in data:
            user.interested_in_volunteer = data['interested_in_volunteer']
        if 'lives_in' in data:
            user.lives_in = data['lives_in']
        if 'language' in data:
            user.language = data['language']
        if 'profile_picture' in data:
            user.profile_picture = data['profile_picture']
        db.session.commit()

        return jsonify({'message': 'User updated successfully'}), HTTP_200_OK
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        return jsonify({'error': error_message}), HTTP_500_INTERNAL_SERVER_ERROR

#get User info
@bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        print(current_user.id)
        return jsonify(user.to_dict()), HTTP_200_OK
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        return jsonify({'error': error_message}), HTTP_500_INTERNAL_SERVER_ERROR

#create Community
@bp.route('/community',methods=['POST'])
@jwt_required()
def create_community():
    if current_user.role != 'admin':
        return jsonify({'error': 'You are not authorized to create this community'}),403
    
    data=request.json
    name = data.get("name")
    address = data.get("address")
    reg_id = data.get("reg_id")
    link = data.get("link")
    team = data.get("team")
    about = data.get("about")
    contact = data.get("contact")
    user_id = data.get("user_id")


    if not name or not address or not reg_id or not team or not about or not contact or not user_id:
        return jsonify({"error": "All fields are required"}), HTTP_400_BAD_REQUEST

    if Community.query.filter_by(name=name).first() is not None:
        return jsonify({"error":"name is already in use"}),HTTP_409_CONFLICT
    
    
    try:
        #creating new user in usersTable
        new_communities=Community(name =name, contact=contact,address=address,reg_id=reg_id,link=link,team=team,about=about,user_id=user_id)
        db.session.add(new_communities)
        db.session.commit()

        #username

        return jsonify({"message":name + " has been sucessfully registered","user":{
            "id":new_communities.id,
            "name":new_communities.name,
            "contact": new_communities.contact,}
            }),HTTP_201_CREATED
    except Exception as e:
        db.session.rollback()
        return jsonify({"error":str(e)}),HTTP_500_INTERNAL_SERVER_ERROR
    

    
#edit Community

#create event
@bp.route('/event/<int:community_id>',methods=['POST'])
@jwt_required()
def create_event(community_id):
    # Get data from the request
    data = request.json
    name=data.get('name')
    time = data.get('time')
    date = data.get('date')
    place = data.get('place')

    # Check if all required fields are provided
    if not time or not date or not place or not community_id or not name:
        return jsonify({"error": "All fields (time, date, place, community_id) are required"}), 400
    
    # Convert date and time strings to datetime objects
    try:
        time = datetime.strptime(time, '%H:%M:%S')
        date = datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Invalid date or time format"}), 400
    
    # Check if the community_id exists and if the user is part of that community
    user_id = current_user.id  # Assuming you pass user_id in headers
    
    community = Community.query.filter_by(id=community_id).first()
    if not community:
        return jsonify({"error": "Community not found"}), 404
    
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    if community.user_id != user_id:
        return jsonify({"error": "User is not a member of this community"}), 403
    
    # Create the event
    event = Event(name=name ,time=time, date=date, place=place, community_id=community_id)
    
    try:
        db.session.add(event)
        db.session.commit()
        return jsonify({"message": "Event created successfully", "event_id": event.id}), HTTP_200_OK
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}),HTTP_500_INTERNAL_SERVER_ERROR
#edit event




#add profile for user
@bp.route('/user/profile', methods=['POST'])
@jwt_required()
def update_user_profile():
    user = current_user  # Assuming the current user is authenticated
    profile_picture = request.files.get('profile_picture')

    if not profile_picture:
        return jsonify({'error': 'Profile picture is required'}), HTTP_400_BAD_REQUEST

    # Save the profile picture to the user's profile_picture column
    try:
        user.profile_picture = profile_picture.read()
        db.session.commit()

        return jsonify({'message': 'Profile picture updated successfully'}), HTTP_200_OK
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        return jsonify({'error': error_message}), HTTP_500_INTERNAL_SERVER_ERROR


#get profile of user
@bp.route('/user/profile', methods=['GET'])
@jwt_required()
def get_profile_picture():
    user = current_user  # Fetch the user from the database by ID
    try:
        if user.profile_picture:
            return send_file(io.BytesIO(user.profile_picture), mimetype='image/jpeg'),HTTP_200_OK
        
        return jsonify({'error': 'No profile picture found'}), 404
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        return jsonify({'error': error_message}), HTTP_500_INTERNAL_SERVER_ERROR




#update profile of community
@bp.route('/profile/community/<int:community_id>', methods=['POST'])
@jwt_required()
def update_community_profile(community_id):
    community = Community.query.get_or_404(community_id)
    profile_picture = request.files.get('profile_picture')

    if not profile_picture:
        return jsonify({'error': 'Profile picture is required'}), HTTP_400_BAD_REQUEST

    # Save the profile picture to the community's profile column
    try:
        community.profile = profile_picture.read()
        db.session.commit()

        return jsonify({'message': 'Community profile picture updated successfully'}), HTTP_200_OK
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        return jsonify({'error': error_message}), HTTP_500_INTERNAL_SERVER_ERROR


#get profile of community
@bp.route('/profile/community/<int:community_id>', methods=['GET'])
@jwt_required()
def get_community_picture(community_id):
    community = Community.query.get_or_404(community_id)
    try:
        if community.profile_picture:
            return send_file(io.BytesIO(community.profile_picture), mimetype='image/jpeg'),HTTP_200_OK
        
        return jsonify({'error': 'No profile picture found'}), 404
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        return jsonify({'error': error_message}), HTTP_500_INTERNAL_SERVER_ERROR



#update profile of event
@bp.route('/profile/event/<int:event_id>', methods=['POST'])
@jwt_required()
def update_event_profile(event_id):
    event = Event.query.get_or_404(event_id)
    profile_picture = request.files.get('profile_picture')

    if not profile_picture:
        return jsonify({'error': 'Profile picture is required'}), HTTP_400_BAD_REQUEST

    # Save the profile picture to the event's profile column
    try:
        event.profile = profile_picture.read()
        db.session.commit()

        return jsonify({'message': 'Event profile picture updated successfully'}), HTTP_200_OK
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        return jsonify({'error': error_message}), HTTP_500_INTERNAL_SERVER_ERROR


#get profile of event
@bp.route('/profile/event/<int:event_id>', methods=['GET'])
@jwt_required()
def get_event_picture(event_id):
    event = Event.query.get_or_404(event_id)
    try:
        if event.profile_picture:
            return send_file(io.BytesIO(event.profile_picture), mimetype='image/jpeg'),HTTP_200_OK
        
        return jsonify({'error': 'No profile picture found'}), 404
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        return jsonify({'error': error_message}), HTTP_500_INTERNAL_SERVER_ERROR





#join community
@bp.route('/communities/<int:community_id>/join', methods=['POST'])
@jwt_required()
def request_to_join_community(community_id):
    community = Community.query.get_or_404(community_id)
    user_id = current_user.id

    # Check if the user has already requested to join the community
    existing_request = JoinRequest.query.filter_by(user_id=user_id, community_id=community_id).first()
    if existing_request:
        return jsonify({'error': 'You have already requested to join this community'}), HTTP_400_BAD_REQUEST
    try:
        # Create a new join request
        join_request = JoinRequest(user_id=user_id, community_id=community_id)
        db.session.add(join_request)
        db.session.commit()
    
        return jsonify({'message': 'Your request to join the community has been submitted'}), HTTP_200_OK
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        return jsonify({'error': error_message}), HTTP_500_INTERNAL_SERVER_ERROR





# Community admin approves or rejects a join request
@bp.route('/communities/<int:community_id>/join_requests/<int:request_id>', methods=['PATCH'])
@jwt_required()
def approve_or_reject_join_request(community_id, request_id):
    community = Community.query.get_or_404(community_id)
    join_request = JoinRequest.query.get_or_404(request_id)

    # Check if the user is the community admin
    user_id = current_user.id
    if community.user_id != user_id:
        return jsonify({'error': 'You are not authorized to manage this community'}), HTTP_403_FORBIDDEN

    status = request.json.get('status')
    if status not in ['approved', 'rejected']:
        return jsonify({'error': 'Invalid status. Must be "approved" or "rejected"'}), HTTP_400_BAD_REQUEST
    try:
        # Update the join request status
        join_request.status = status
        db.session.commit()

        # If the request is approved, add the user to the community
        if status == 'approved':
            community.users.append(join_request.user)
            db.session.commit()

        return jsonify({'message': f'Join request {status}'}), HTTP_200_OK
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        return jsonify({'error': error_message}), HTTP_500_INTERNAL_SERVER_ERROR




# fetching events by communites 
@bp.route('/users/events', methods=['GET'])
@jwt_required()
def get_user_community_events():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)

    # Get the communities the user is a part of
    user_communities = user.communities

    # Get the events organized by those communities
    events = []
    for community in user_communities:
        events.extend(community.events.all())

    # Convert events to a list of dictionaries
    event_dicts = [event.to_dict() for event in events]

    return jsonify(event_dicts), HTTP_200_OK



#joining event
@bp.route('/events/<int:event_id>/join', methods=['POST'])
@jwt_required()
def join_event(event_id):
    try:
        user = current_user
        event = Event.query.get_or_404(event_id)

        # Check if the user is part of the community that organized the event
        if event.community not in user.communities:
            return jsonify({'error': 'You are not part of the community that organized this event'}), HTTP_400_BAD_REQUEST

        # Check if the user has already joined the event
        if user in event.users:
            return jsonify({'message': 'You have already joined this event'}), HTTP_200_OK

        # Add the user to the event
        user.events.append(event)
        db.session.commit()

        return jsonify({'message': 'You have successfully joined the event'}), HTTP_200_OK
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        return jsonify({'error': error_message}), HTTP_500_INTERNAL_SERVER_ERROR


#joined communites
@bp.route('/user/communities', methods=['GET'])
@jwt_required()
def get_user_communities():
    try:
        user_id = get_jwt_identity()
        user = User.query.get_or_404(user_id)

        # Get all communities the user is a part of
        communities = user.communities

        # Convert communities to a list of dictionaries (optional)
        community_dicts = [community.to_dict() for community in user.communities]

        return jsonify(community_dicts), HTTP_200_OK
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        return jsonify({'error': error_message}), HTTP_500_INTERNAL_SERVER_ERROR


#joined events
@bp.route('/user/joined_events', methods=['GET'])
@jwt_required()
def get_joined_events():
    try:
        user_id = get_jwt_identity()
        user = User.query.get_or_404(user_id)
        event_dicts = [event.to_dict() for event in user.events]
        return jsonify(event_dicts), HTTP_200_OK
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        return jsonify({'error': error_message}), HTTP_500_INTERNAL_SERVER_ERROR

