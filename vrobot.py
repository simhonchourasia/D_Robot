# Import modules for discord py
import discord
from discord.ext import commands
import random
import datetime
# Import modules for communication with Google Sheets
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# CHANGE THIS
COURSE_NAMES = ["CS135", "CS145", "MATH135", "MATH145", "MATH137", "MATH147"]
SHEET_NAME = "UW CS Homework"
LINK = "https://docs.google.com/spreadsheets/d/1UnoDzUupSbuY4Jvb9nrSDV9iBOd5OBxhCHpKxenVeh8/edit?usp=sharing"

# Setup scope and client for Google Sheets
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file",
         "https://www.googleapis.com/auth/drive"]

# Get credentials from accompanying json file
credentials = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
sheets_client = gspread.authorize(credentials)

courseNames = COURSE_NAMES
data = {}


# Set up data from the Google Sheet
def refresh_data():
    for i in range(len(courseNames)):
        courseSheet = sheets_client.open(SHEET_NAME).get_worksheet(i)
        data[courseNames[i]] = courseSheet.get_all_records()


# Get token from accompanying text file
with open("token.txt", 'r') as f:
    DISCORD_TOKEN = f.readlines()[0].strip()

# Initialize command prefix and remove default help
client = commands.Bot(command_prefix='/')
client.remove_command('help')


@client.event
async def on_ready():
    refresh_data()
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="/help for DM"))
    print("V_RObot activated")


# Sends link to the spreadsheet using hardcoded link
@client.command(aliases=['sheet', 'sheets'])
async def link(ctx):
    await ctx.send(LINK)


# Returns user ping with the server
@client.command()
async def ping(ctx):
    await ctx.send('Your ping is ' + str(round(client.latency*1000)) + "ms")


# Randomly returns an output from the list
@client.command(aliases=["8ball", "vrobot"])
async def predict(ctx, *, question):
    responses = ["It is certain.",
                 "It is decidedly so.",
                 "Without a doubt.",
                 "Yes - definitely.",
                 "You may rely on it.",
                 "As I see it, yes.",
                 "Most likely.",
                 "Outlook good.",
                 "Yes.",
                 "Signs point to yes.",
                 "Reply hazy, try again.",
                 "Ask again later.",
                 "Better not tell you now.",
                 "Cannot predict now.",
                 "Concentrate and ask again.",
                 "Don't count on it.",
                 "My reply is no.",
                 "My sources say no.",
                 "Outlook not so good.",
                 "Very doubtful."]
    await ctx.send(random.choice(responses))


# Returns all due dates for a given course
@client.command(aliases=['due', 'duedates'])
async def due_dates(ctx, *, course):
    for item in data[course.upper()]:
        date = item['Due Date']
        due_time = item['Due Time']
        await ctx.send(item['Name'] + "; due on " + date + ", at " + due_time)


# Returns all assignments from a given course due within a week
@client.command(aliases=['duethisweek'])
async def due_this_week(ctx, *, course):
    for item in data[course.upper()]:
        date = item['Due Date']
        due_time = item['Due Time']
        DT = datetime.datetime(int(date.split('/')[2]), int(date.split('/')[0]), int(date.split('/')[1]),
                               int(due_time.split(':')[0]), int(due_time.split(':')[1]))
        timedelta = DT - datetime.datetime.now()
        days = timedelta.days
        if 7 > days >= 0:
            await ctx.send(item['Name'] + "; due on " + date + ", at " + due_time)


# Takes an assignment name and returns the time until it is due
@client.command(aliases=['procrastinate', 'whendue', 'howmuchtime', 'shouldido', 'shouldistart'])
async def when_due(ctx, *, assignment):
    for course in courseNames:
        for item in data[course]:
            if item['Name'].upper() == assignment.upper():
                date = item['Due Date']
                due_time = item['Due Time']
                DT = datetime.datetime(int(date.split('/')[2]), int(date.split('/')[0]), int(date.split('/')[1]),
                                       int(due_time.split(':')[0]), int(due_time.split(':')[1]))
                timedelta = DT - datetime.datetime.now()
                days = timedelta.days
                seconds = timedelta.seconds
                hours = seconds // 3600

                minutes = (seconds // 60) % 60
                if days > 10:
                    custom_message = "You probably don't need to worry about it yet. "
                elif days > 5:
                    custom_message = "You might want to start soon. "
                elif days > 2:
                    custom_message = "It's time to . "
                elif days > 1:
                    custom_message = "It's getting a little close. "
                elif hours > 6:
                    custom_message = "Make sure you remember to submit. "
                elif hours > 1:
                    custom_message = "Submit your work. "
                elif hours == 0:
                    custom_message = "Almost there. "
                else:
                    custom_message = "That's in the past now. "
                total_message = course + ": " + item['Name'] + " is due in "
                if days > 0:
                    total_message += str(days) + " days. "
                else:
                    if hours > 1:
                        total_message += str(hours) + " hours and "
                    elif hours == 1:
                        total_message += str(hours) + " hour and "
                    total_message += str(minutes) + " minutes. "
                total_message += custom_message
                await ctx.send(total_message)


# Command documentation list for /help command (DMed to user)
@client.command(pass_context=True)
async def help(ctx):
    author = ctx.message.author

    dm_embed = discord.Embed(colour=discord.Colour.blue())
    dm_embed.set_author(name="Hello " + asker.name + "! You can use these commands with me: ")
    dm_embed.add_field(name='/ping', value='Returns your ping', inline=False)
    dm_embed.add_field(name='/predict', value='Tells your future', inline=False)
    dm_embed.add_field(name='/link', value='Gives you the link to the Google Sheet with all the due dates', inline=False)
    dm_embed.add_field(name='/due_dates', value='Tells you all the due dates for a course', inline=False)
    dm_embed.add_field(name="/due_this_week", value='Tells you all the assignments for a course that are due this week',
                       inline=False)
    dm_embed.add_field(name="/when_due",
                       value='Tells you when an assignment is due (make sure to spell the assignment name right)',
                       inline=False)
    dm_embed.add_field(name="/add",
                       value='Lets you append a row to the spreadsheet. Make sure that date is in the format '
                             'MM/DD/YYYY, and that you use military time. Example: /add CS145 | 9/15/2020 | '
                             '22:00 | A1', inline=False)

    await author.send(embed=dm_embed)


# Command to add an assignment by course
# Format is XY135 | MM/DD/YYYY | HH:MM | Assignment Z
@client.command(aliases=['addassignment', 'addwork', 'add_work', 'add', 'append'])
async def add_assignment(ctx, *, info):
    info_list = [x.strip() for x in info.split('|')]
    course_name = info_list[0].upper()
    date = info_list[1]
    time = info_list[2]
    assignment = info_list[3]
    print(info_list)
    course_sheet = sheets_client.open(SHEET_NAME).get_worksheet(courseNames.index(course_name))
    course_sheet.append_row(info_list[1:], value_input_option='USER_ENTERED')
    refresh_data()
    await ctx.send("Added! " + info)


client.run(DISCORD_TOKEN)