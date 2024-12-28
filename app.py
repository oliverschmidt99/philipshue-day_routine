from flask import Flask, request, jsonify
from control.Room import Room
from control.Scene import Scene

app = Flask(__name__)

# Example global variables for demonstration
rooms = {"room_olli": Room([89], [5, 99], 2, "room_olli")}
scenes = {"default": Scene(status=True, bri=100, sat=150, ct=350, t_time=50)}

@app.route('/update-room', methods=['POST'])
def update_room():
    data = request.json
    room_name = data.get("room_name")
    group_ids = list(map(int, data.get("group_ids", "").split(",")))
    sensor_id = data.get("sensor_id", None)

    if room_name in rooms:
        room = rooms[room_name]
        room.group_ids = group_ids or room.group_ids
        room.sensor_id = sensor_id or room.sensor_id
        return jsonify({"message": f"Room {room_name} updated successfully!"})
    else:
        return jsonify({"message": "Room not found!"}), 404

@app.route('/update-scene', methods=['POST'])
def update_scene():
    data = request.json
    bri = data.get("bri")
    sat = data.get("sat")
    ct = data.get("ct")
    t_time = data.get("t_time")

    # Update a default scene for demonstration
    scene = scenes["default"]
    scene.bri = int(bri) if bri else scene.bri
    scene.sat = int(sat) if sat else scene.sat
    scene.ct = int(ct) if ct else scene.ct
    scene.t_time = int(t_time) if t_time else scene.t_time
    return jsonify({"message": "Scene updated successfully!"})

if __name__ == '__main__':
    app.run(debug=True)
