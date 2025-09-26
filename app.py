from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, send, emit, join_room
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_login import LoginManager, UserMixin, login_user

# -------------------
# Flask 基础配置
# -------------------
app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
app.config["JWT_SECRET_KEY"] = "jwt-secret-string"

# 初始化扩展
socketio = SocketIO(app)
jwt = JWTManager(app)
login_manager = LoginManager()
login_manager.init_app(app)

# -------------------
# 用户模型（示例）
# -------------------
class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

# 临时用户表（模拟数据库）
users = {"miranda": "1234", "alice": "abcd"}

@login_manager.user_loader
def load_user(user_id):
    return User(user_id, user_id)

# -------------------
# 路由
# -------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.json.get("username")
    password = request.json.get("password")
    if username in users and users[username] == password:
        user = User(id=username, username=username)
        login_user(user)
        token = create_access_token(identity=username)
        return jsonify(msg="login success", token=token)
    return {"msg": "bad credentials"}, 401

@app.route("/protected")
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return {"logged_in_as": current_user}

# -------------------
# WebSocket 部分
# -------------------
user_rooms = {}  # username -> sid

# 群聊
@socketio.on("message")
def handle_message(msg):
    print(f"[Group] {msg}")
    send(msg, broadcast=True)

# 用户加入
@socketio.on("join")
def handle_join(username):
    user_rooms[username] = request.sid
    join_room(request.sid)
    print(f"{username} joined with sid {request.sid}")

# 私聊
@socketio.on("private_message")
def handle_private_message(data):
    recipient = data["to"]
    message = data["message"]
    sender = data["from"]
    if recipient in user_rooms:
        room = user_rooms[recipient]
        emit("private_message", f"[Private] {sender}: {message}", room=room)

# -------------------
# 启动
# -------------------
if __name__ == "__main__":
    print("🚀 Chat server running at http://127.0.0.1:5001")
    socketio.run(app, host="0.0.0.0", port=5001, debug=True)
