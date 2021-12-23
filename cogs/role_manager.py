from enum import Enum

import discord
from discord.commands import Option, slash_command
from discord.ext import commands

import botconfig as conf

from views.confirm import Confirm

class OperationType(Enum):
	CREATE = 'added'
	DELETE = 'removed'

#These two have to be outside the class so the autocomplete can reach them.
def get_roles(ctx: discord.AutocompleteContext | discord.ApplicationContext):
	rolesets = conf.get_object(ctx.interaction.guild, 'rolesets')
	roles = {}
	for roleset_name, roleset in rolesets.items():
		roles.update({role: roleset_name for role in roleset['roles'].keys()})
	validRoles = {role_name:value for (role_name, value) in roles.items() if role_name in [role.name for role in ctx.interaction.guild.roles]}
	return validRoles

def roles_for_autocomplete(ctx: discord.AutocompleteContext):
	return [role for role in get_roles(ctx).keys() if role.lower().startswith(ctx.value.lower())]


class RoleManager(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@slash_command(name='role')
	async def request_role(
		self,
		ctx: discord.ApplicationContext,
		rolename: Option(str, "Pick a role!", autocomplete=roles_for_autocomplete)
		):
		roles = get_roles(ctx)
		if rolename in roles.keys():
			roleset_name = roles[rolename]
			role = discord.utils.find(lambda r: r.name.lower() == rolename.lower(), ctx.guild.roles)
			changes = self.get_role_changes(ctx.user, role, roleset_name)
			confirmer = Confirm(self.do_role_changes(changes), Confirm.cancel_action )
			await ctx.respond(f"Changes:\n{self.role_changes_to_string(changes)}", view=confirmer, ephemeral=True)


	def do_role_changes(self, changes):
		async def role_change_callback(interaction: discord.Interaction):
			if changes[OperationType.CREATE]:
				await interaction.user.add_roles(*changes[OperationType.CREATE])
			if changes[OperationType.DELETE]:
				await interaction.user.remove_roles(*changes[OperationType.DELETE])
			await interaction.response.edit_message(content="Roles updated.", view=None)

		return role_change_callback

	def get_role_changes(self, member: discord.Member, role: discord.Role, roleset_name):
		roleset = conf.get_object(member.guild, 'rolesets', roleset_name)
		changes = {OperationType.DELETE: [], OperationType.CREATE: []}
		if roleset['type'] == 'toggle':
			if member.get_role(role.id) is not None:
				changes[OperationType.DELETE].append(role)
			else:
				changes[OperationType.CREATE].append(role)
		else:
			changes[OperationType.CREATE].append(role)
			for current_role in member.roles:
				if current_role.name in roleset['roles'].keys():
					changes[OperationType.DELETE].append(current_role)
		return changes

	def role_changes_to_string(self, changes):
		return '\n'.join(['\n'.join([value.name + ' will be ' + key.value + '.' for value in changes[key]]) for key in changes.keys()])