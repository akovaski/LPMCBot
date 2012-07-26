# Admin name(s) for certain commands
# Usage:
#       if sender in ADMINS:
#           myfunc()
ADMINS = ["SlimTim10", "Z_Mass", "intothev01d", "naxir"]

# The '!die' command makes the bot quit (admin command)
def die(info, cmd, sender):
    return 'QUIT\n'

# The '!add_admin' command adds an admin
def add_admin(info, cmd, sender):
    try:
        user_to_add = cmd[1]
        ADMINS.append(user_to_add)
        return 'PRIVMSG ' + info[2] + \
        ' :'+user_to_add+' added as admin\n'

    except:
        return 'PRIVMSG ' + info[2] + \
        ' :Command help: Specify a user\n'

# The '!remove_admin' command removes an admin
def remove_admin(info, cmd, sender):
    try:
        user_to_remove = cmd[1]
        ADMINS.remove(user_to_remove)
        return 'PRIVMSG ' + info[2] + \
        ' :'+user_to_remove+' removed as admin\n'

    except:
        return 'PRIVMSG ' + info[2] + \
        ' :Command help: Specify an admin\n'