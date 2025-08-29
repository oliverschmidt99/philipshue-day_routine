# web/api/bridge.py
from flask import Blueprint, jsonify
from phue import PhueException
from ..server import get_bridge

bridge_api = Blueprint("bridge_api", __name__)


@bridge_api.route("/all_items")
def get_all_bridge_items():
    """Holt alle relevanten Geräte von der Bridge."""
    bridge = get_bridge()
    if not bridge:
        return jsonify({"error": "Bridge nicht erreichbar"}), 500
    try:
        lights = bridge.get_light()
        sensors = bridge.get_sensor()
        groups = bridge.get_group()

        light_ids_in_groups = {
            lid for g in groups.values() for lid in g.get("lights", [])
        }

        return jsonify(
            {
                "grouped_lights": [
                    {
                        "id": gid,
                        "name": g["name"],
                        "lights": [
                            {"id": lid, "name": lights[lid]["name"]}
                            for lid in g.get("lights", [])
                        ],
                    }
                    for gid, g in groups.items()
                ],
                "unassigned_lights": [
                    {"id": lid, "name": l["name"]}
                    for lid, l in lights.items()
                    if lid not in light_ids_in_groups
                ],
                "sensors": [
                    {"id": sid, "name": s["name"]}
                    for sid, s in sensors.items()
                    if s.get("type") == "ZLLPresence"
                ],
            }
        )
    except PhueException as e:
        return jsonify({"error": str(e)}), 500
