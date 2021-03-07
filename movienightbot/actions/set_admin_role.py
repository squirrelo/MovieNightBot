from . import BaseAction
from ..db.controllers import ServerController


class SetAdminRoleAction(BaseAction):
    action_name = "set_admin_role"
    admin = True
    controller = ServerController()

    async def action(self, msg):
        admin_role = self.get_message_data(msg)
        server_roles = [r.name for r in msg.guild.roles]
        if admin_role not in server_roles:
            return (msg.channel, f"Role not found: {admin_role}.")
        with self.controller.transaction():
            server_row = self.controller.get_by_id(msg.guild.id)
            server_row.admin_role = admin_role
            self.controller.update(server_row)
        return (msg.channel, f"Admin role updated to {admin_role}")

    @property
    def help_text(self):
        return (
            "Sets the name of the role that is allowed to run admin only commands in movie night bot. "
            "Server administrators have full privileges by default"
        )

    @property
    def help_options(self):
        return ["[role]"]
