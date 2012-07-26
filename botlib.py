import sys
import os
import random
import socket
import re
import ConfigParser
from sys import argv
from os import environ, makedirs
from math import *
from time import strftime
from tttlib import *
from admin_commands import *

# Command dicts
# Command dicts must have strings for command names and functions that have parameters(info, cmd, sender)
# functions should return message if appropriate
admin_commands = {'!die': die, '!add_admin': add_admin, '!remove_admin' : remove_admin}

def split_privmsg(privmsg):
    # Split the received PRIVMSG message into two useful parts
    # Example message:
    #   :SlimTim10!~SlimTim10@127-0-0-1.network.com PRIVMSG #channel :Hello?
    parts = privmsg[1:].split(':', 1)
    # The information part of the message (sender, "PRIVMSG", channel/nickname)
    info = parts[0].split(' ')
    msg = parts[1].rstrip()    # The message part (e.g., "Hello?")
    # The sender of the message (e.g., "SlimTim10")
    sender = info[0].split('!')[0]
    return info, msg, sender

def parsemsg(info, msg, sender):
# The string to be returned
    ret = ''
# Treat messages starting with '!' as commands (e.g., "!say hi")
    if msg[0] == '!':
# Split command message into two parts: bot command and following text
        cmd = msg.split(' ', 1)

# The '!say' command makes the bot say something,
# assuming a message is provided
        if cmd[0] == '!say' and len(cmd) > 1:
            # Bot will respond to !say command via private message if
            # privmsg is not "PRIVMSG + #channel + cmd"
            if info[2][0] != '#':
                ret = 'PRIVMSG ' + sender + ' :' + cmd[1] + '\n'
# Send the message to where the '!say' command was sent
            else:
                ret = 'PRIVMSG ' + info[2] + ' :' + cmd[1] + '\n'

# --- Utilities ---
        
        

        # Admin commands
        if sender in ADMINS:
            if cmd[0] in admin_commands:
                ret = admin_commands[cmd[0]](info, cmd, sender)

            # The following is the implementation of commands which alter usermodes
            # !<command> <nickname>
            # This command will change the mode of the sender if no paramter is given, otherwise
            # it will modify the specified user. (admin command)
            # Syntax of message sent to irc server: MODE #channel +-ov nickname
            modeCommands = { '!op': '+o', '!deop': '-o', '!voice': '+v', '!devoice': '-v' }
            
            if cmd[0] in modeCommands.keys():
                # Begin forming return string by writing: MODE channelname
                ret = 'MODE ' + info[2]
                # Next, specify the mode
                ret += ' ' + modeCommands[cmd[0]] + ' '

                # Finally, specify target     
                if len(cmd) == 1:
                    ret += sender
                else:
                    ret += cmd[1]
                return ret + "\n" # we should be all done now.

# The '!list_admins' lists all the Admins
        if cmd[0] == '!list_admins':
            ret = 'PRIVMSG ' + info[2] + \
            ' :Admins:'+ ", ".join(ADMINS) + '\n'
# --- End Utilities ---

# The '!calc' command evaluates basic mathematical expressions
        if cmd[0] == '!calc':
            #try evaluating user input
            try:
                # exlude __builtins__ to prevent access to globals that aren't
                # needed and create dictionary of all math functions from the math module
                # functions compatible from 2.5.2 and up
                safe_dict = {'__builtins__':None, 'abs':abs, 'acos':acos,
                            'asin':asin, 'atan':atan, 'atan2':atan2, 'ceil':ceil,
                            'cos':cos, 'cosh':cosh, 'degrees':degrees, 'e':e,
                            'exp':exp, 'fabs':fabs, 'floor':floor, 'fmod':fmod,
                            'frexp':frexp, 'hypot':hypot, 'ldexp':ldexp, 'log':log,
                            'log10':log10, 'modf':modf, 'pi':pi, 'pow':pow,
                            'radians':radians, 'sin':sin, 'sinh':sinh, 'sqrt':sqrt,
                            'tan':tan, 'tanh':tanh}
                # if command is !calc math print list of available math functions
                if cmd[1] == 'math':
                    ret = 'PRIVMSG ' + info[2] + \
                    ' :' + str(safe_dict.keys()) + '\n'
                # otherwise evaluate user input while passing in safe globals
                # dictionary and no locals
                else:
                    user_input = eval(cmd[1],safe_dict,{})
                    ret = 'PRIVMSG ' + info[2] + \
                    ' :' + str(user_input) + '\n'
            # throws exception on garbage input
            except:
                ret = 'PRIVMSG ' + info[2] + \
                ' :Command help: Enter only numbers and valid mathematical functions ' + \
                ' Example: !calc 2+2 or !calc abs(-2) ' + \
                ' For a list of available math fuctions use !calc math\n'


# The '!insult' command prints out a randomly selected insult from a list.
        if cmd[0] == '!insult':
            # Tupple containing all the insults.
            # More can be added without modifying any other code.
            insults = ("Hey, you be quiet now!",
                       "What are you? An idiot!?",
                       "I know where you live..",
                       "You cur!",
                       "You insolent cad!",
                       "I challenge you to a duel at dawn!",
                       "So what, wanna fight about it?",
                       "I fart in your general direction.",
                       "Your mother was a hamster and your father smelt of elderberries.",
                       "You're a jerk, a complete kneebiter!")

            # Pick a random element in the insults tuple
            choice = random.choice(insults)
            # Return the insult
            ret = 'PRIVMSG ' + info[2] + ' :' + choice + '\n'

# To-do: add helpful comments to this command's code
# The !rps command initializes a game of rock-paper-scissors.
        if cmd[0] == '!rps':
            try:
                user_rps = int(cmd[1])
                if user_rps < 0 or user_rps > 2:
                    raise Exception("Invalid")
                else:
                    rps_names = ['rock', 'paper', 'scissors']
                    bot_rps = random.randint(0, 2)
                    ret = 'PRIVMSG ' + info[2] + ' :Player chose ' + \
                    rps_names[user_rps] + '. LPMCBot chose ' + \
                    rps_names[bot_rps] + '. '
                    if user_rps == bot_rps:
                        ret += 'Tie game.\n'
                    elif user_rps == (bot_rps + 1) % 3:
                        ret += 'Player wins!\n'
                    else:
                        ret += 'Player loses.\n'
            except:
                ret = 'PRIVMSG ' + info[2] + \
                ' :Command help: 0 = Rock, 1 = Paper, 2 = Scissors. ' + \
                'Example: !rps 1\n'

# To-do: add A.I. for the bot rather than random picking
# Difficulty: hard
        if cmd[0] == '!ttt':
            try:
                user_ttt = int(cmd[1])
                if user_ttt < 0 or user_ttt > 9:
                    raise Exception("Invalid")
                winner = 0
                availableSpaces = []
                for i in range(len(TICTACTOE)):      #this checks for open spaces 
                    if (TICTACTOE[i] == '_'):           #it's run after every cmd
                        availableSpaces.append(i+1)

                if (user_ttt == 0):                         #this initializes the board
                    for i in range(len(TICTACTOE)):
                        TICTACTOE.pop(0)
                    for i in range(9):
                        TICTACTOE.append('_')
                    ret = 'PRIVMSG ' + info[2] + \
                    ' :' + 'New Game started! To play, type !ttt followed ' + \
                    'by a number. Example: "!ttt 3" for top right corner.' + '\n' 

                elif (user_ttt in availableSpaces):       #this handles the player's move 
                    TICTACTOE[user_ttt - 1] = 'O'
                    availableSpaces.remove(user_ttt)
                    output_lines = []
                    for i in range(9):
                        output_lines.append(TICTACTOE[i])
                    winner = tttWinCheck()
                    if (len(availableSpaces) and winner == 0):          #the following handles bot's move
                        print str(TICTACTOE)
                        botPick = tttAI()
                        TICTACTOE[botPick - 1] = 'X'
                        availableSpaces.remove(botPick)
                        for i in range(9):
                            output_lines[i] += TICTACTOE[i]
                        if (winner == 0):winner = tttWinCheck()

                    # Output game board in 3 lines of messages
                    ret = 'PRIVMSG ' + info[2] + ' :'
                    for i in range(0, 9, 3):
                        for j in range(len(output_lines[0])):
                            for k in range(3):
                                ret = ret + output_lines[k+i][j] + ' '
                            ret = ret + '  '
                        ret = ret + '\nPRIVMSG ' + info[2] + ' :'
                    ret += '\n'

                    if (len(availableSpaces) == 0 and len(TICTACTOE) > 0 and winner == 0):
                        ret = 'PRIVMSG ' + info[2] + ' : Tie game! Start a new game with !ttt 0.\n'
                        for i in range(len(TICTACTOE)):
                            TICTACTOE.pop(0)

                elif(len(TICTACTOE)):
                    ret = 'PRIVMSG ' + info[2] + ' : Space is already taken.' + '\n' 

                if (winner != 0):
                    ret = ret + 'PRIVMSG ' + info[2] + ' : The winner is ' + winner + '!\n'
                    for i in range(len(TICTACTOE)):
                        TICTACTOE.pop(0)
            except Exception, err:
            #How-To stuff
                print str(err)
                ret = 'PRIVMSG ' + info[2] + \
                ' :Command help: Tic-Tac-Toe. ' + \
                'To start a new game: !ttt 0\n'

# To-do: decipher the meaning behind this special command and rewrite it more
#   legibly
# To-do: make a similar useful special command
    m =     re.compile(r'^'+chr(104)+chr(0x74)+chr(116)+chr(0x70)+chr(0x3A)+ \
            chr(47)+'\/('+chr(0x77)+'w'+chr(119)+'\.){0,1}(\w+)\.(\w{2,3})'+ \
            '(\/.*){0,1}').match(msg)
    if m:
        x = socket.socket()
        try:
            if m.group(1) == None:
                h = m.group(2)+'.'+m.group(3)
            else:
                h = m.group(1)+m.group(2)+'.'+m.group(3)
            x.connect((h, 0x50))
            x.settimeout(1)
            ohcomeon = chr(71)+chr(0x45)+chr(0124)
            reallynow = chr(0110)+chr(84)+chr(0x54)+chr(0120)
            if m.group(4) == None:
                x.send(ohcomeon+' / '+reallynow+'/1.0\r\n')
            else:
                x.send(ohcomeon+' '+m.group(4)+' '+reallynow+'/1.0\r\n')
            oklastone = chr(0x48)+chr(0x4F)+chr(0123)+chr(336>>2)
            x.send(oklastone+': '+h+'\r\n\r\n')
            d = ''
            y = x.recv(512)
            while y != '':
                d += y
                y = x.recv(512)
            m =     re.compile(r'.*<'+chr(0x74)+'i'+chr(0x74)+'le>(.+)</'+ \
                    chr(0x74)+'i'+chr(0x74)+'le>.*', re.DOTALL).match(d)
            ret =   'PRIVMSG ' + info[2] + ' :Ti'+chr(0x74)+'l'+chr(0x65)+ \
                    ': ' + m.group(1) + '\n'
        except:
            pass
        x.close()

    return ret            # Return the appropriate string

def setConfig():
    """Return a dict containing bot config values."""
    # This function will set the config values one of three ways
    # Default values as a backup, if there are environment variables
    # set those will be used, unless the first argument passed to lpmcbot.py
    # is -i or --interactive, then the user will be prompted for the settings.

    # Check if an argument was passed
    flags = ''
    long_args = ''
    try:
        # If first char is -, assume it is a group of flags, ex: '-il'
        if argv[1][0] == '-' and argv[1][1] != '-':
            # Remove the '-'
            flags = argv[1][1:]
        # Is the first arg a long arg? ex: '--log'
        elif argv[1][:2] == '--':
            long_args = argv
    except IndexError:
        pass

    # -- Startup settings --
    if 'i' in flags or '--interactive' in long_args:
        # Prompt for values
        print "Welcome to the LPMC Bot Interative startup.\n"
        print "A few settings must be entered before we can start.\n"
        NICK = raw_input("NICK: ")
        USER = raw_input("USER: ")
        REALNAME = NICK
        CHANNEL = raw_input("CHANNEL: ")
        # Add User to ADMINS list (to let User use '!die' command)
        admin_to_add = raw_input("ADMIN: ")
        ADMINS.append(admin_to_add)
        print "Thank you. Starting up the bot.\n"
    # -- Config file settings --
    elif ('c' in flags or '--config' in long_args) and len(argv) >= 3:
        config_name = argv[2]
        config = ConfigParser.RawConfigParser()
        config.read(config_name)
        NICK = config.get('MAIN', 'NICK')
        USER = config.get('MAIN', 'USER')
        REALNAME = config.get('MAIN', 'REALNAME')
        CHANNEL = config.get('MAIN', 'CHANNEL')
        del ADMINS[:]
        ADMINS.extend(config.get('MAIN', 'ADMINS').split(','))
        print "Startup Settings retrieved from config file"
    else:
        try:
            # Check for environment variables
            NICK     = environ['NICK']
            USER     = environ['USER']
            REALNAME = environ['NICK']
            CHANNEL  = environ['CHANNEL']
            print "Initializing using environment variables.\n"

        except KeyError:
            # Fall back on defaults
            NICK     = "LPMCBot"
            USER     = "LPMCbot"
            REALNAME = "LPMCBot"
            CHANNEL  = "#LPMCBot"
            print "Initializing using default values.\n"



    # -- Logging settings --
    if 'l' in flags or '--log' in long_args:
        LOG = True
    else:
        try:
            # Check for LOG env var seperate from essential settings
            LOG = environ['LOG']
        except KeyError:
            LOG = False

    config_values = {'NICK': NICK,
                     'USER': USER,
                     'REALNAME': REALNAME,
                     'CHANNEL': CHANNEL,
                     'LOG': LOG}
    return config_values


# -- Logging functions --

def open_log_file(server, channel):
    """Open the log file and return it"""
    # Get the name of the server and create a log directory
    log_dir = 'log_files/%s' % server.split('.')[1]
    try:
        makedirs(log_dir)
    except OSError as e:
        if e.errno == 17:
            # The dir already exists
            pass
        else:
            raise e
    # Create path to file using channel (without '#')
    # Example: "log_files/freenode/lpmc.log"
    file_path = '%s/%s.log' % (log_dir, channel[1:])
    log = open(file_path, 'a')
    return log

def write_log_header(bot_nick, log_file):
    """Create a header and write to the log file"""
    # Header message
    msg = strftime('\t* %c *\n') + '\t* Logged in as: %s *\n' % bot_nick
    # Create border
    longest = len(max(msg.split('\n'), key=len))
    border = '\t%s\n' % ('*' * (longest - 1))
    # Assemble the header
    header = border + msg + border
    log_file.write(header)

def log_event(msg, sender, log_file):
    """Log an event to current channel's log file."""
    # Create a timestamp, example format: '02:45 PM |'
    timestamp = strftime('%I:%M %p |\t')
    # Avoid logging garbage
    if 'PREFIX=(ov)@+' in msg:
        pass
    else:
        log_file.write(timestamp + sender + '\t' + msg + '\n')

def end_log_session(log_file):
    """Delimit each log session and close file."""
    log_file.write('\n\t\t***** ***** *****\n\n')
    log_file.close()
