import os
import discord

fullGaugeChar = '='
emptyGaugeChar = ' '


def check_path(name):
    if not os.path.exists(name):
        os.makedirs(name)


def draw_gauge(current_value, max_value):
    return '[' + fullGaugeChar * current_value + emptyGaugeChar * (max_value - current_value) + ']'


def find_self_member(client, server):
    return next(member for member in server.members if member.id == client.user.id)


def find_channel(channel_name, server):
    return next(
        channel for channel in server.channels if channel.name == channel_name or str(channel.id) == str(channel_name))


def embed_to_text(embed):
    text = ''
    if embed.title:
        text += '**' + embed.title + '**\n'
    if embed.description:
        text += embed.description + '\n'
    text += '\n'.join([f'{field.name}: {field.value}\n' for field in embed.fields])
    return text


async def get_pic(user, mention_target, server, argstring, **kwargs):
    embed = discord.Embed()
    if 'server' == argstring:
        embed.set_image(url=server.icon.with_static_format('png').url)
        return {'text': f"{server.name}'s icon!", 'embed': embed}
    embed.set_image(url=mention_target.avatar.with_static_format('png').url)
    return {'text': f"{mention_target.mention}'s avatar!", 'embed': embed}


def pic_help(**kwargs):
    return "Shows a bigger version of someone's avatar!"
