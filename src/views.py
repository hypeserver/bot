from flask import Blueprint

from utils.link_helper import collect_target_channel_links

root_bp = Blueprint("root", "root_router")


@root_bp.route("/tasks/link-collector", methods=["POST"])
def collect_links_view():
    collect_target_channel_links()
    return {}
