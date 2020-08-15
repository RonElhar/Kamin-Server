import json
from flask import Flask, abort, request, jsonify, g
from flask_cors import CORS
from flask_socketio import SocketIO, join_room, leave_room
from flask_httpauth import HTTPBasicAuth
from Controllers.discussion_controller import DiscussionController
from Controllers.user_controller import UserController
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
from Entities.user import Permission

# initialization
app = Flask(__name__)
CORS(app)
socket_io = SocketIO(app, cors_allowed_origins='*')
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy dog'
ROOMS = {}  # dict to track active rooms
simulation_indexes = {}
simulation_order = {}
simulation_control = {}
USERS = {}

# extensions
auth = HTTPBasicAuth()
user_controller = UserController()
discussion_controller = DiscussionController()


# Verify the authentication of user with the token received in the request
def verify_auth_token(token):
    s = Serializer(app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except SignatureExpired:
        return None  # valid token, but expired
    except BadSignature:
        return None  # invalid token
    user = user_controller.get_user(data['id'])
    return user

# Verify the authentication of user with the token or username and password that received in the request
@auth.verify_password
def verify_password(username_or_token, password):
    user = verify_auth_token(username_or_token)
    if not user:
        user = user_controller.get_user(username=username_or_token)
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


# Entry point for adding new user to the system
@app.route('/api/newUser', methods=['POST'])
def new_user():
    try:
        username = request.json.get('username')
        password = request.json.get('password')
        first_name = request.json.get('first_name')
        last_name = request.json.get('last_name')
        if username is None or password is None:
            raise Exception("username or password is missing, can't create new user!")
        if user_controller.get_user(username=username) is not None:
            raise Exception("username already exists, can't create new user!")
        user_id = user_controller.add_new_user(username=username, password=password, first_name=first_name,
                                               last_name=last_name)
        return jsonify({'user_id': user_id}), 200
    except Exception as e:
        app.logger.exception(e)
        abort(400, e)


# Entry point for getting user details
@app.route('/api/getUser', methods=['GET'])
def get_user():
    try:
        username = request.args.get('username')
        user = user_controller.get_user(username=username)
        if not user:
            raise Exception("username is not exist!")
        return jsonify(
            {'username': user.get_user_name(), 'password': user.get_password(), 'first_name': user.get_first_name(),
             'last_name': user.get_last_name(), 'permission': user.get_permission()}), 200
    except Exception as e:
        app.logger.exception(e)
        abort(500, e)


# Returns all the users names of the active users in the request moment of the discussion_id room
def get_active_users(discussion_id):
    active_users = []
    if len(USERS) > 0:
        active_users = list(dict(USERS[discussion_id]).keys())
    return active_users


# Returns all the moderators users names of the active moderators in the request moment of the discussion_id room
def get_active_moderators(discussion_id):
    active_moderators = []
    active_users = get_active_users(discussion_id)
    for user in active_users:
        if user_controller.get_user(user).get_permission() != 1:
            active_moderators.append(user)
    return active_moderators


# Returns all the users names of the users that write at least one comment in the discussion and can be alerted
def get_active_discussion_users(discussion_id):
    responded_users = discussion_controller.get_responded_users(discussion_id)
    return list(responded_users)


# Entry point for getting all the visualization configurations of the active users in the discussion,
# active means that they are connected and presents in the discussion in the request moment
@app.route('/api/getActiveUsersConfigurations/<string:discussion_id>', methods=['GET'])
def get_active_users_configurations(discussion_id):
    try:
        config = {}
        users_config = discussion_controller.get_all_users_discussion_configurations(discussion_id)
        for user in users_config:
            if USERS[discussion_id].__contains__(user):
                config[user] = users_config[user]
        return config, 200
    except Exception as e:
        app.logger.exception(e)
        abort(500, e)


# Entry point for getting all the users and moderators names that exist in the system
@app.route('/api/getUsers', methods=['GET'])
def get_users():
    try:
        users, moderators = user_controller.get_users()
        return jsonify(
            {'users': users, 'moderators': moderators}), 200
    except Exception as e:
        app.logger.exception(e)
        abort(500, e)


# Entry point for retrieve the statistics of user in discussion
@app.route('/api/getUserStatisticsInDiscussion', methods=['POST'])
def get_user_discussion_statistics():
    try:
        username = request.json.get('username')
        discussion_id = request.json.get('discussionId')
        if username is None or discussion_id is None:
            raise Exception("username or discussionId is Missing, can't get statistics!")
        if user_controller.get_user(username=username) is None:
            raise Exception("username is not exist, can't get statistics!")
        statistics = discussion_controller.get_user_discussion_statistics(username, discussion_id)
        if statistics is None:
            raise Exception("Statistics of username in discussionId is not exist!")
        return jsonify({"user_in_discussion_statistics": statistics}), 200
    except Exception as e:
        app.logger.exception(e)
        abort(500, e)


# Entry point for retrieve the discussion statistics
@app.route('/api/getDiscussionStatistics', methods=['POST'])
def get_discussion_statistics():
    try:
        discussion_id = request.json.get('discussionId')
        if discussion_id is None:
            raise Exception("discussionId is Missing, can't get statistics!")
        statistics = discussion_controller.get_discussion_statistics(discussion_id)
        if statistics is None:
            raise Exception("Statistics of username in discussionId is not exist!")
        return jsonify({"discussion_statistics": statistics}), 200
    except Exception as e:
        app.logger.exception(e)
        abort(500, e)


# Entry point for update the user permission
@app.route('/api/changeUserPermission', methods=['POST'])
@auth.login_required
def change_user_permission():
    try:
        user = g.user
        if user.get_permission() is not Permission.ROOT.value:
            raise Exception("Only ROOT user permitted to change permissions!")
        permission = json.loads(request.data)["permission"]
        username = json.loads(request.data)["username"]
        user = user_controller.get_user(username=username)
        if not user:
            raise Exception("username is not exist!")
        result = user_controller.change_user_permission(user, permission)
        return jsonify(result), 200
    except Exception as e:
        app.logger.exception(e)
        abort(500, e)


# Entry point for logged in to the system and get a valid token
@app.route('/api/login')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(app.config['SECRET_KEY'], 60000)
    user = g.user
    permission = user.get_permission()
    return jsonify({'token': token.decode('ascii'), 'permission': permission, 'duration': 60000})


# Entry point for getting the discussion_id tree contains all the comments and discussion details
@app.route('/api/getDiscussion/<string:discussion_id>', methods=['GET'])
@auth.login_required
def get_discussion(discussion_id):
    try:
        discussion_tree = discussion_controller.get_discussion(discussion_id)
        if discussion_tree is None:
            raise Exception("discussion_id is not exist!")
        discussion_json_dict = discussion_tree.to_json_dict()
        return jsonify({"discussion": discussion_json_dict['discussion'], "tree": discussion_json_dict['tree']})
    except IOError as e:
        app.logger.exception(e)
        abort(400)
        return

# Entry point for downloading the discussion_id tree contains all the comments and discussion details as csv file
@app.route('/api/download/<string:discussion_id>', methods=['GET'])
@auth.login_required
def download(discussion_id):
    try:
        discussion_tree = discussion_controller.get_discussion(discussion_id)
        if discussion_tree is None:
            raise Exception("discussion_id is not exist!")
        discussion_json_dict = discussion_tree.to_json_dict()
        csv = discussion_tree.to_csv()
        return jsonify(
            {"discussion": discussion_json_dict['discussion'], "tree": discussion_json_dict['tree'], "csv": csv})
    except IOError as e:
        app.logger.exception(e)
        abort(400)
        return

# Entry point for getting all the discussions ids list that are real-time or simulation depending on the
# is_simulation parameter
@app.route('/api/getDiscussions/<string:is_simulation>', methods=['GET'])
@auth.login_required
def get_discussions(is_simulation):
    try:
        is_simulation = (is_simulation == 'True')
        discussions_list = discussion_controller.get_discussions(is_simulation)
        return jsonify({"discussions": discussions_list})
    except IOError as e:
        app.logger.exception(e)
        abort(400)
        return

# Entry point for creating new discussion in the system, new discussions created as a real-time discussions
# and added to the ROOMS list as one of the real-time discussion that available for users to join
@app.route('/api/createDiscussion', methods=['POST'])
@auth.login_required
def create_discussion():
    try:
        user = g.user
        data = dict(request.json)
        if not data.keys().__contains__("title") or data["title"] is None:
            raise Exception("Title is missing, can't create discussion!")
        title = data["title"]
        if not data.keys().__contains__("categories"):
            raise Exception("Categories is missing, can't create discussion!")
        categories = data["categories"]
        if not data.keys().__contains__("root_comment_dict"):
            raise Exception("root_comment_dict Key is missing, can't create discussion!")
        root_comment = data["root_comment_dict"]
        if root_comment is None or len(root_comment) is 0 or root_comment["text"] == "" or root_comment["text"] is None:
            raise Exception("First comment is missing, can't create discussion!")
        if not data.keys().__contains__("configuration"):
            raise Exception("configuration Key is missing, can't create discussion!")
        configuration = data["configuration"]
        if configuration is None or len(configuration) is 0:
            raise Exception("configuration is missing, can't create discussion!")
        discussion_tree = discussion_controller.create_discussion(title, categories, root_comment, configuration)
        room = discussion_tree.get_id()
        ROOMS[room] = discussion_tree
        USERS[room] = {user.get_user_name(): ""}
        return jsonify(
            {'discussion_id': discussion_tree.get_id(), "root_comment_id": discussion_tree.get_root_comment_id()}), 201
    except Exception as e:
        app.logger.exception(e)
        abort(400, e)
        return

# Socket entry point for turn a real-time discussion to simulation, it block the possibility to join and add comments
# to the discussion, and it becomes to be available for watching only
@socket_io.on('end_session')
def end_real_time_session(data):
    token = data['token']
    discussion_id = data['discussionId']
    user = verify_auth_token(token)
    if user.get_permission() is not Permission.MODERATOR.value:
        socket_io.emit("error", "User not permitted to end real-time session!")
    discussion_controller.end_real_time_session(discussion_id)
    USERS.pop(discussion_id)
    ROOMS.pop(discussion_id)
    socket_io.emit("end_session")

# Socket entry point for joining a discussion, it will update all the other clients in the room
# that new user join the discussion
@socket_io.on('join')
def on_join(data):
    token = data['token']
    room = data['discussion_id']
    user = verify_auth_token(token)
    if not user:
        socket_io.emit("unauthorized", room=request.sid)
        return
    username = user.get_user_name()
    if room not in ROOMS:
        discussion = discussion_controller.get_discussion(room)
        if discussion is None:
            socket_io.emit("error", data="join Error - discussionId not exist!", room=request.sid)
            return
        ROOMS[room] = discussion
        USERS[room] = {}
    join_room(room)
    USERS[room][username] = request.sid
    discussion_controller.add_user_discussion_statistics(username, room)
    discussion_json_dict = ROOMS[room].to_json_dict()
    with open('discussion_json.txt', 'w+') as file:
        json.dump(discussion_json_dict["tree"], file)
    data = {"discussionDict": discussion_json_dict}
    if ROOMS[room].is_simulation:
        if room not in simulation_indexes:
            simulation_order[room] = "chronological"
            simulation_control[room] = "off"
            simulation_indexes[room] = 1
        data["currentIndex"] = simulation_indexes[room]
        data["simulationOrder"] = simulation_order[room]
        data["selfControl"] = simulation_control[room]
    user_config = discussion_controller.get_user_discussion_configuration(username, room)
    if user_config is None:
        user_config = ROOMS[room].get_configuration()["vis_config"]
        user = user_controller.get_user(username)
        discussion_controller.add_user_discussion_configuration(user, room, user_config)
    data["visualConfig"] = user_config
    socket_io.emit("join room", data=data, room=request.sid)
    socket_io.emit("user joined", data=username, room=room)
    disc_responded_users = get_active_discussion_users(room)
    all_users_visualizations_config = get_active_users_configurations(room)
    moderators = get_active_moderators(room)
    for moderator in moderators:
        socket_io.emit("update active users", data=disc_responded_users, room=USERS[room][moderator])
        socket_io.emit("new user config", data=all_users_visualizations_config, room=USERS[room][moderator])

# Socket entry point for leaving a discussion
@socket_io.on('leave')
def on_leave(data):
    room = data['discussionId']
    username = data['username']
    leave_room(room)
    USERS[room].pop(username)
    if len(USERS[room]) == 0:
        if room in ROOMS:
            ROOMS.pop(room)
        if room in USERS:
            USERS.pop(room)
        simulation_control.pop(room)
        simulation_order.pop(room)
        simulation_indexes.pop(room)
    socket_io.emit("user leave", data=username + " leaved the discussion", room=room)

# Socket entry point for adding new comment in discussion
@socket_io.on("add comment")
def add_comment(request_comment):
    json_string = request_comment
    comment_dict = json.loads(json_string)
    room = comment_dict['discussionId']
    response = discussion_controller.add_comment(comment_dict)
    ROOMS[room].add_comment(response["comment"])
    response["comment"] = response["comment"].to_client_dict()
    socket_io.send(response, room=room)
    disc_responded_users = get_active_discussion_users(room)
    moderators = get_active_moderators(room)
    for moderator in moderators:
        socket_io.emit("update active users", data=disc_responded_users, room=USERS[room][moderator])

# Socket entry point for adding new alert in discussion
@socket_io.on("add alert")
def add_alert(request_alert):
    alert_dict = json.loads(request_alert)
    room = alert_dict["discussionId"]
    response = discussion_controller.add_alert(alert_dict)
    ROOMS[room].add_comment(response["comment"])
    extra_data = alert_dict["extra_data"]
    if extra_data["recipients_type"] == "all":
        socket_io.emit("new alert", data=response["comment"].to_client_dict(), room=room)
    else:
        recipients_users = extra_data["users_list"]
        for user in recipients_users:
            socket_io.emit("new alert", data=response["comment"].to_client_dict(), room=USERS[room][user])
        moderators = get_active_moderators(room)
        for moderator in moderators:
            socket_io.emit("new alert", data=response["comment"].to_client_dict(), room=USERS[room][moderator])

# Socket entry point for changing user/s visualizations configuration in discussion
@socket_io.on("change configuration")
def change_configuration(request_configuration):
    configuration_dict = json.loads(request_configuration)
    room = configuration_dict["discussionId"]
    response = {}
    if not ROOMS[room].is_simulation:
        response = discussion_controller.change_configuration(configuration_dict)
    extra_data = configuration_dict["extra_data"]
    recipients_type = extra_data["recipients_type"]
    users_dict = dict(extra_data["users_list"])
    users_list = users_dict.keys()
    if recipients_type == "all":
        for user in get_active_users(room):
            discussion_controller.update_user_discussion_configuration(user, room, users_dict["all"])
        socket_io.emit("new configuration", data=users_dict["all"], room=room)
        socket_io.emit("new alert", data=response["comment"].to_client_dict(), room=room)
    else:
        for user in users_list:
            discussion_controller.update_user_discussion_configuration(user, room, users_dict[user])
            socket_io.emit("new configuration", data=users_dict[user], room=USERS[room][user])


@socket_io.on('connect')
def client_connect():
    print("client connected")


@socket_io.on('disconnect')
def client_disconnect():
    print("client disconnected")

# Socket entry point for presenting the next comment in order when running simulation by moderator control
@socket_io.on("next")
def handle_next(request_data):
    room = request_data['discussionId']
    if not ROOMS[room].is_simulation:
        socket_io.emit("error", data="next failed - Discussion is not a simulation", room=request.sid)
        return
    if simulation_indexes[room] < ROOMS[room].total_comments_num + ROOMS[room].total_alerts_num:
        simulation_indexes[room] += 1
        socket_io.emit("next", room=room)
    else:
        socket_io.emit("error", data="back failed - out of bound", room=request.sid)

# Socket entry point for presenting the previous comment in order when running simulation
# by moderator control
@socket_io.on("back")
def handle_back(request_data):
    room = request_data['discussionId']
    if not ROOMS[room].is_simulation:
        socket_io.emit("error", data="back failed - Discussion is not a simulation", room=request.sid)
        return
    if simulation_indexes[room] > 1:
        simulation_indexes[room] -= 1
        socket_io.emit("back", room=room)
    else:
        socket_io.emit("error", data="back failed - out of bound", room=request.sid)

# Socket entry point for presenting all the comments one by one in order when running simulation
# by moderator control
@socket_io.on("all")
def handle_all(request_data):
    room = request_data['discussionId']
    if not ROOMS[room].is_simulation:
        socket_io.emit("error", data="all failed - Discussion is not a simulation", room=request.sid)
        return
    simulation_indexes[room] = ROOMS[room].total_comments_num + ROOMS[room].total_alerts_num
    socket_io.emit("all", room=room)

# Socket entry point for reset the presenting of the discussion comments when running simulation by moderator control
@socket_io.on("reset")
def handle_reset(request_data):
    room = request_data['discussionId']
    if not ROOMS[room].is_simulation:
        socket_io.emit("error", data="reset failed - Discussion is not a simulation", room=request.sid)
        return
    simulation_indexes[room] = 1
    socket_io.emit("reset", room=room)

# Socket entry point for change the presenting order of the comments when running simulation by moderator control
@socket_io.on("change_simulation_order")
def change_order(request_data):
    room = request_data['discussionId']
    if not ROOMS[room].is_simulation:
        socket_io.emit("error", data="change sim order failed - Discussion is not a simulation")
        return
    if simulation_order[room] == "regular":
        simulation_order[room] = "chronological"
    else:
        simulation_order[room] = "regular"
    simulation_indexes[room] = 1
    socket_io.emit("change_simulation_order", room=room)

# Socket entry point for change the control of the simulation running, and provide to users to control themselves on it
@socket_io.on("self control change")
def change_control(request_data):
    room = request_data['discussionId']
    if not ROOMS[room].is_simulation:
        socket_io.emit("error", data="change sim control failed - Discussion is not a simulation")
        return
    if simulation_control[room] == "on":
        simulation_control[room] = "off"
    else:
        simulation_control[room] = "on"
        simulation_indexes[room] = 1
    socket_io.emit("change_simulation_control", room=room)


if __name__ == '__main__':
    socket_io.run(app, debug=False)
    print("bla")
