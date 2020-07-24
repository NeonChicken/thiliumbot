import random
import asyncio
import json
import os
import io
import re
import discord

prefix = '!'

timeout_time = 600.0  # message.author response time in seconds
player_limit = 20  # the player limit of uno participation

# TODO THESE ARE DUPLICATED IN LEADERBORD CODE! IF YOU CHANGE THESE VALUES YOU SHOULD CHANGE THEM THERE TOO!
leaderboard_limit = 3  # the amount of players displayed on the leaderboard
leaderboard_entrypoint = 10  # the amount of UNO games you must have played before you can show up on the leaderboard

data = {}
data['games'] = []


def create_json_uno():
    with io.open(os.path.join('./resources/battle', 'uno.json'), 'w') as file:
        json.dump(data, file, indent=4)
    with open('./resources/battle/uno.json') as file:
        first_file = json.load(file)
        first_file['games'].append({'name': 'null'})
        with open('./resources/battle/uno.json', 'w') as f:
            json.dump(first_file, f, indent=4)


# Flip a coin and send the result.
async def run(client, message):
    # help message
    def help_msg():
        filename = str(os.path.basename(__file__))
        commandname = filename.replace('.py', '')
        response = "{}, welcome to **".format(message.author.mention) + prefix + "{}** ".format(
            commandname) + "database!" \
                           "\n\nAfter **" + prefix + "{}** ".format(commandname) \
                   + "you can use: " \
                     "\n**add** - add a game" \
                     "\n**dl** - request & download json data" \
                     "\n**lb** - check out the leaderboard"

        return response

    # loading save files
    if not os.path.isfile('./resources/battle/uno.json'):
        # if file not found, make uno.json with create_json_uno function
        create_json_uno()
        await message.channel.send('*uno.json has been created. Please try again.*')
        return
    else:
        with open('./resources/battle/uno.json') as file:
            uno_file = json.load(file)
            if str(uno_file) == '' or str(uno_file) == '[]' or str(uno_file) == '{}':
                create_json_uno()
                await message.channel.send('*uno.json was empty. Please try again.*')
                return

    if len(message.content.split()) < 2:
        await message.channel.send(help_msg())
        return

    def has_numbers(inputString):
        return any(char.isdigit() for char in inputString)

    if len(message.content.split()) >= 2:
        if 'add' in '{}'.format(message.content.lower()):
            if 'UNO-Datist' in str(message.author.roles):

                # Make array empty every time when adding a game (as some sort of global variable)
                player_array = []

                await message.channel.send("Input the date in this format: 2020-6-26 ("
                                           "Year-Month-Day) *\nIf you don't "
                                           "know the exact date, precisely type N/A or na")

                def check(msg):
                    return msg.author == message.author

                try:
                    msg = await client.wait_for('message', check=check, timeout=timeout_time)
                except asyncio.TimeoutError:
                    await message.channel.send(
                        "{} didn't respond in time! The game hasn't been added:zzz:".format(
                            message.author.mention))
                    return
                else:
                    if msg.content.lower() == 'n/a' or msg.content.lower() == 'na':
                        msg_date = 'N/A'
                    else:
                        temp = str(msg.content)
                        temp = temp.strip('[]')
                        temp = temp.strip("'")

                        msg_date = ''
                        r = re.compile('\d{4}-\d{1,2}-\d{1,2}')  # date format
                        if r.match(temp) is not None:
                            msg_date = temp
                        else:
                            await message.channel.send(
                                "Please try again!\nSubmit a date as N/A or in this format: 2020-6-26")
                            return

                        year_of_post = str(message.created_at)
                        year_of_post = year_of_post.split()[0]
                        year_post, month_post, day_post = year_of_post.split('-')

                        try:
                            year, month, day = temp.split('-')
                        except ValueError:
                            await message.channel.send(
                                "Please try again!\nSubmit a date as N/A or in this format: 2020-6-26")
                            return

                        # Checking if the date is possible
                        if int(year) < 2017:
                            await message.channel.send("We didn't start playing Uno until 2017!")
                            return
                        if int(month) > 12:
                            await message.channel.send("There's only 12 months in a year!")
                            return
                        if int(day) > 31:
                            await message.channel.send("There can only be a maximum of 31 days in a year!")
                            return
                        # Checking if the date input exceeds the date of submission, preventing false game reports
                        if int(year) > int(year_post) or (
                                int(month) > int(month_post) and int(year) == int(year_post)) or (
                                int(month) == int(month_post) and int(year) == int(year_post) and int(day) > int(
                            day_post)):
                            await message.channel.send("You can't submit games that haven't been played yet!")
                            return

                    await message.channel.send("Input the total amount of players for this game")

                    def check(msg):
                        return msg.author == message.author

                    try:
                        msg = await client.wait_for('message', check=check, timeout=timeout_time)
                    except asyncio.TimeoutError:
                        await message.channel.send(
                            "{} didn't respond in time! The game hasn't been added:zzz:".format(message.author.mention))
                        return
                    else:
                        if has_numbers(msg.content):
                            if int(msg.content) > 2 and int(msg.content) < player_limit:
                                msg_player_count = int(msg.content)

                                await message.channel.send("Input the total amount of rounds that were played")

                                def check(msg):
                                    return msg.author == message.author

                                try:
                                    msg = await client.wait_for('message', check=check, timeout=timeout_time)
                                except asyncio.TimeoutError:
                                    await message.channel.send(
                                        "{} didn't respond in time! The game hasn't been added:zzz:".format(
                                            message.author.mention))
                                    return
                                else:
                                    if has_numbers(msg.content):
                                        msg_round_count = int(msg.content)

                                        live_count = msg_player_count
                                        await message.channel.send(
                                            "Insert data for {} players, use **%** as a separator\nExample: Name "
                                            "20 79 79 82 % Name 0 0 7 15 % Name 15 25 72 103".format(
                                                live_count))


                                        def check(msg):
                                            return msg.author == message.author

                                        try:
                                            msg = await client.wait_for('message', check=check,
                                                                        timeout=timeout_time)
                                        except asyncio.TimeoutError:
                                            await message.channel.send(
                                                "{} didn't respond in time! The game hasn't been added:zzz:".format(
                                                    message.author.mention))
                                            return
                                        else:
                                            if msg.content:
                                                test_str = msg.content.split("%")
                                                if len(test_str) is not int(msg_player_count):
                                                    await message.channel.send(
                                                        "Not the right amount of players! There should be **{}** players, but you entered data for **{}** players!\n\n*(Perhaps a seperator* ***%*** *is present where it shouldn't)*".format(
                                                            int(msg_player_count),
                                                            len(test_str)))
                                                    return

                                                for every in test_str:
                                                    # Split[0] is the first word (name)
                                                    msg_string_player = every.lower().replace("-", "").replace(":", "").replace(".", "").split()[0]
                                                    # Split[1:len] is everything that comes after the first word & (remove dashes: -)
                                                    msg_string_score = every.lower().replace("-", "").replace(":", "").replace(".", "").split()[
                                                                   1:len(msg.content.lower().split())]

                                                    # Checking if there's only digits in the score
                                                    for ints in msg_string_score:
                                                        if not ints.isdigit():
                                                            await message.channel.send(
                                                                "You've entered a wrong character! "
                                                                "Please try again.\n"
                                                                "The character: **{}** should be a digit, it's present in **{}** their score".format(ints, msg_string_player.capitalize()))
                                                            return
                                                    # Checking if entered score equals the amount of rounds
                                                    if len(msg_string_score) is not msg_round_count:
                                                        await message.channel.send(
                                                            "You've entered the wrong amount of rounds for player *{}*!"
                                                            "\nThere should be: **{}** rounds.. "
                                                            "{} couldn't have played **{}** rounds!".format(
                                                                msg_string_player,
                                                                msg_round_count, msg_string_player.capitalize(),
                                                                len(msg_string_score)))
                                                        return
                                                    player_array.append({
                                                        'player': '{}'.format(msg_string_player),
                                                        "score": msg_string_score
                                                    })

                                                # todo add notions after score in brackets (detect brackets as string)


                                            total_games_in_file = 0
                                            # Just getting the loop, no need to store anything. For = none
                                            for none in uno_file['games']:
                                                total_games_in_file = total_games_in_file + 1

                                            # Making player_array look neat in a string
                                            player_array_msg = player_array
                                            final_msg = ''
                                            for pl in player_array_msg:
                                                str_scores = str(pl['score'])
                                                str_scores = str_scores.replace("'", "")
                                                str_scores = str_scores.replace("[", "")
                                                str_scores = str_scores.replace("]", "")
                                                final_msg = final_msg + '**{}**: *{}*\n'.format(
                                                    pl['player'].capitalize(),
                                                    str_scores)

                                            await message.channel.send("Received all player data! Do you wish to "
                                                                       "submit the following game? **Y/N**\n\n"
                                                                       "*Game ID* : **{}**\n"
                                                                       "*Submitted By* : {}\n"
                                                                       "*Submission Date* : {}\n"
                                                                       "*Total Players* : **{}**\n"
                                                                       "*Total Rounds* : **{}**\n"
                                                                       "*Game Date* : {}\n\n"
                                                                       "*Players* : \n{}".format(total_games_in_file,
                                                                                                 message.author.mention,
                                                                                                 message.created_at,
                                                                                                 msg_player_count,
                                                                                                 msg_round_count,
                                                                                                 msg_date,
                                                                                                 final_msg))

                                            def check(msg):
                                                return msg.author == message.author

                                            try:
                                                msg = await client.wait_for('message', check=check,
                                                                            timeout=timeout_time)
                                            except asyncio.TimeoutError:
                                                await message.channel.send(
                                                    "{} didn't respond in time! The game hasn't been added:zzz:".format(
                                                        message.author.mention))
                                                return
                                            else:
                                                if 'yes' in msg.content.lower() or 'ye' in msg.content.lower() or 'y' in msg.content.lower():
                                                    uno_file['games'].append({
                                                        'game_id': '{}'.format(total_games_in_file),
                                                        'submitted_by': '{}'.format(message.author.id),
                                                        'submission_date_UTC': '{}'.format(message.created_at),
                                                        'player_total': '{}'.format(msg_player_count),
                                                        'rounds': '{}'.format(msg_round_count),
                                                        'date': '{}'.format(msg_date),
                                                        'players': player_array
                                                    })
                                                    with open('./resources/battle/uno.json', 'w') as f:
                                                        json.dump(uno_file, f, indent=4)

                                                    await message.channel.send('Game has been submitted!')
                                                    return
                                                elif 'no' in msg.content.lower() or 'n' in msg.content.lower():
                                                    await message.channel.send('Sorry to hear that!')
                                                    return
                                                else:
                                                    await message.channel.send(
                                                        "I can only understand **yes**, **ye**, **y**, **n** and **no**")
                                                    return
                                    else:
                                        await message.channel.send("You can only input integers!")
                                        return

                            elif int(msg.content) >= 0 and int(msg.content) <= 2:
                                await message.channel.send(
                                    "Uno games with {} players aren't official!".format(int(msg.content)))
                            elif int(msg.content) >= player_limit:
                                await message.channel.send("{} is too many players!".format(int(msg.content)))
                            else:
                                await message.channel.send("Something went wrong...")
                        else:
                            await message.channel.send("You can only input integers!")
                            return

            else:
                response = "Only users with the **UNO-Datist** role can add data!!"
                await message.channel.send(response)

        elif 'lb' in '{}'.format(message.content.lower()):
            try:
                if message.content.split()[2].isdigit():
                    leaderboard_limit = int(message.content.split()[2])
                if message.content.split()[3].isdigit():
                    leaderboard_entrypoint = int(message.content.split()[3])
            except IndexError:
                leaderboard_limit = 3  # the amount of players displayed on the leaderboard
                leaderboard_entrypoint = 10  # the amount of UNO games you must have played before you can show up on the leaderboard

            total_player_list = []
            for i in uno_file['games']:
                # Don't count the first value because it's null
                if i is not uno_file['games'][0]:
                    # Create empty list > used for storing player names from uno.json
                    for p in i['players']:
                        if p['player'] not in str(total_player_list):
                            # Append unknown players into list
                            total_player_list.append({
                                '{}'.format(p['player']): [],
                            })

                        for idx, s in enumerate(p['score']):
                            if idx == len(p['score']) - 1:
                                for pkey in total_player_list:
                                    if p['player'] in pkey:
                                        # If name is found in array of players, append their last round score > (s)
                                        total_player_list[total_player_list.index(pkey)][p['player']].append(s)
                                        # total_player_list PRINTS:
                                        # [{'karst': ['18', '101']}, {'vincent': ['40']},
                                        # {'toon': ['104', '67']}, {'luuk': ['8', '17']}]

            # Getting all player names again
            known_players = []
            leader_names = []
            leader_games = []
            leader_average = []
            for i in uno_file['games']:
                # Don't count the first value because it's null
                if i is not uno_file['games'][0]:
                    # Create empty list > used for storing player names from uno.json
                    for p in i['players']:
                        for players in total_player_list:
                            try:
                                if players[p['player']] and p['player'] not in known_players:
                                    # Put player in a list so we can check if we already iterated over this player.
                                    known_players.append(p['player'])
                                    total_score = 0
                                    for single_score in players[p['player']]:
                                        total_score = total_score + int(single_score)
                                    if len(players[p['player']]) >= leaderboard_entrypoint:
                                        leader_names.append(p['player'].capitalize())
                                        leader_games.append(len(players[p['player']]))
                                        leader_average.append(round(total_score / len(players[p['player']])))
                            except KeyError:
                                continue

            leader_names_sorted = [x for _, x in sorted(zip(leader_average, leader_names))]
            leader_games_sorted = [x for _, x in sorted(zip(leader_average, leader_games))]
            leader_average_sorted = [x for _, x in sorted(zip(leader_average, leader_average))]
            leader_msg_final = []
            leader_count = len(leader_average)
            for l in range(leader_count):
                if l < leaderboard_limit:
                    leader_msg_final.append("**{}.** ***{}*** has played ".format(l + 1, leader_names_sorted[l]))
                    leader_msg_final.append("**{}** games with an average of: ".format(leader_games_sorted[l]))
                    leader_msg_final.append("**{}**\n".format(leader_average_sorted[l]))
            leader_msg = "".join(map(str, leader_msg_final))
            await message.channel.send("{}".format(leader_msg))
            return

        elif 'new' in '{}'.format(message.content.lower()):
            temp = 'ja'
            # Input all player names with a space > Start an Uno game with 4 players?
            # Do you have the score for the first round yet? No > I'll wait here (60 min)

        elif 'dl' in '{}'.format(message.content.lower()):
            if ('Administrator' in str(message.author.roles)) or ('Moderator' in str(message.author.roles)):
                await message.channel.send(file=discord.File('resources/battle/uno.json'))
            else:
                response = "Only Admins and Mods are able to use this command!"
                await message.channel.send(response)

        elif 'edit' in '{}'.format(message.content.lower()):
            if ('Administrator' in str(message.author.roles)) or ('Moderator' in str(message.author.roles)):
                temp = 'ja'
                # Which game do you want to edit? // Give ID
            else:
                response = "Only Admins and Mods are able to use this command!"
                await message.channel.send(response)

        elif 'delete' in '{}'.format(message.content.lower()):
            if ('Administrator' in str(message.author.roles)) or ('Moderator' in str(message.author.roles)):
                temp = 'ja'
                # Which game do you want to delete? // Give ID
            else:
                response = "Only Admins and Mods are able to use this command!"
                await message.channel.send(response)

        elif 'test' in '{}'.format(message.content.lower()):
            pass

        else:
            await message.channel.send(help_msg())
            return


# Add a restart, stop, quit command in a while loop for access at any time.
# Notions in players[player]