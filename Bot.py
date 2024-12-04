import websockets, discord, asyncio, random, json, uuid, os
from discord.ext import commands, tasks
from discord import app_commands
os.chdir('D:\Distopia\Bot')

client = commands.Bot(command_prefix = "!", intents=discord.Intents.all())
client.remove_command('help')
tree = client.tree

db = "db.json"

with open(db, "r+") as f:
    data = json.load(f)
    data["players"] = []
    f.seek(0)
    f.truncate()
    json.dump(data, f, indent=4)










async def handler(websocket):
    print("Connected")
    activeplayers.start()

    global send

    async def send(cmd):
        msg = {
            "header": {
                "version": 1,
                "requestId": f'{uuid.uuid4()}',
                "messagePurpose": "commandRequest",
                "messageType": "commandRequest"
            },
            "body": {
                "version": 1,
                "commandLine": cmd,
                "origin": {
                    "type": "player"
                }
            }
        }
        a = await websocket.send(json.dumps(msg))
        return a
    
    await websocket.send(
        json.dumps({
            "header": {
                "requestId": f"{uuid.uuid4()}",
                "messagePurpose": "subscribe",
                "version": 1,
                "messageType": "commandRequest"
            },
            "body": {
                "eventName": "PlayerMessage"
            }
        })
    )

    async for el in websocket:
        el = json.loads(el)
        if "message" in el["body"]:
            if el["body"]["message"].startswith("!"):
                user = el["body"]["sender"]
                command = el["body"]["message"].lstrip("!").split()
                if command[0].lower() == "link":
                    if len(command) == 2:
                        discord = command[1]
                        chars = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
                        code = random.choice(chars) + random.choice(chars) + random.choice(chars) + random.choice(chars) + random.choice(chars) + random.choice(chars)
                        with open(db, "r+") as f:
                            data = json.load(f)
                            if user not in data["links"]:
                                data["requests"][user] = {
                                    "discord": discord,
                                    "code": code
                                }
                                f.seek(0)
                                f.truncate()
                                json.dump(data, f, indent=4)
                                await send(f'/w "{user}" §eRun the §d/link §ecommand in the §9discord §eserver and use the following code: §d{code}')
                            else:
                                await send(f"""/w "{user}" §cUh-oh, seems like you've already connected a §9discord §caccount""")
                    else:
                        await send(f"""/w "{user}" §cMake sure to add your §9discord §ctag to the end of the command""")
                elif command[0].lower() == "purchase":
                    if user in ["Gytis5089", "NPC"]:
                        user = el["body"]["message"].lstrip("!purchase ").split()[0] if el["body"]["message"].count('"') == 2 else el["body"]["message"].lstrip("!purchase ").split('"')[1]
                        item = el["body"]["message"].split('"')[-2]
                        with open(db, "r+") as f:
                            data = json.load(f)
                            if data["links"][user] in data["economy"]:
                                if data["economy"][data["links"][user]] >= data["items"][item]["price"]:
                                    if item == "Colt":
                                        if user in data["permits"]:
                                            await send(f"""/give "{user}" {data["items"][item]["id"]}""")
                                            data["economy"][data["links"][user]] -= data["items"][item]["price"]
                                        else:
                                            await send(f"""/w "{user}" §cUh-oh, it looks like you don't hold a Distopia Weapons Permit""")
                                    elif item == "Weapons Permit":
                                        if user not in data["permits"]:
                                            data["economy"][data["links"][user]] -= data["items"][item]["price"]
                                            data["permits"].append(user)
                                            await send(f"""/w "{user}" §aYou have successfully been granted a Distopia Weapons Permit, but make sure not to cause any trouble as it can be §crevoked!""")
                                        else:
                                            await send(f"""/w "{user}" §cUh-oh, it looks like you already hold a Distopia Weapons Permit""")
                                    else:
                                        await send(f"""/give "{user}" {data["items"][item]["id"]}""")
                                        data["economy"][data["links"][user]] -= data["items"][item]["price"]
                                    f.seek(0)
                                    f.truncate()
                                    json.dump(data, f, indent=4)
                                else:
                                    await send(f"""/w "{user}" §cUh-oh, it looks like you can't afford that""")
                            else:
                                await send(f"""/w "{user}" §cUh-oh, it looks like you haven't connected your §9discord §cyet, do so with §d!link §9{{discord tag}}""")
        else:
            if "currentPlayerCount" in el["body"]:
                playersold = []
                with open(db, "r+") as f:
                    data = json.load(f)
                    playersold = data["players"]
                if playersold:
                    playersnew = el["body"]["players"].split(", ")
                    playersstayed = [el for el in playersnew if el in playersold]
                    with open(db, "r+") as f:
                        data = json.load(f)
                        for el in playersstayed:
                            if el in data["links"]:
                                if data["links"][el] in data["economy"]:
                                    data["economy"][data["links"][el]] += 16
                                else:
                                    data["economy"][data["links"][el]] = 16
                        data["players"] = playersnew
                        f.seek(0)
                        f.truncate()
                        json.dump(data, f, indent=4)
                else:
                    with open(db, "r+") as f:
                        data = json.load(f)
                        data["players"] = el["body"]["players"].split(", ")
                        f.seek(0)
                        f.truncate()
                        json.dump(data, f, indent=4)










@tasks.loop(minutes=2)
async def activeplayers():
    await send("/list")

@client.event
async def on_ready():
    print(f"Distopia Assistant now online running with {round(client.latency * 100)}ms ping.")

@tree.command(name="link", description="Link your Xbox account with your discord")
async def link(interaction : discord.Interaction, username : str, code : str):
    await interaction.response.send_message(embed=discord.Embed(title="Account Link", colour=0x57a1eb, description="**Loading...**"), ephemeral=True)
    with open(db, "r+") as f:
        data = json.load(f)
        if username in data["requests"]:
            if data["requests"][username]["discord"].lower() == interaction.user.name.lower():
                correctname = True
                if code == data["requests"][username]["code"]:
                    correctcode = True
                    del data["requests"][username]
                    data["links"][username] = str(interaction.user.id)
                    if data["links"][username] in data["economy"]:
                        data["economy"][data["links"][username]] += 1000
                    else:
                        data["economy"][data["links"][username]] = 1000
                    f.seek(0)
                    f.truncate()
                    json.dump(data, f, indent=4)
                    await interaction.edit_original_response(embed=discord.Embed(title="Link Success", colour=0xa1f7a1, description="**Accounts successfully linked**"))
                else:
                    await interaction.edit_original_response(embed=discord.Embed(title="Link Failure", colour=0xf7a1a1, description="**Uh-oh, it looks like you entered the wrong code, did you spell it wrong? Try again**"))
            else:
                await interaction.edit_original_response(embed=discord.Embed(title="Link Failure", colour=0xf7a1a1, description="**Uh-oh, your inputted discord doesn't match with this one, try again in-game**"))
        else:
            await interaction.edit_original_response(embed=discord.Embed(title="Link Failure", colour=0xf7a1a1, description="**Uh-oh, it looks like that username is invalid.**\n**Did you spell it wrong? Remember it is cAsE sEnSiTiVe, try again**"))

@tree.command(name="balance", description="Check your current balance")
async def bal(interaction : discord.Interaction):
    with open(db, "r") as f:
        data = json.load(f)
        uid = str(interaction.user.id)
        if uid in data:
            await interaction.response.send_message(embed=discord.Embed(title="Balance", colour=0x57a1eb, description=f"**Your balance is** `${data[uid]}`"), ephemeral=True)
        else:
            data[uid] = 0
            f.seek(0)
            f.truncate()
            json.dump(data, f, indent=4)
            await interaction.response.send_message(embed=discord.Embed(title="Balance", colour=0x57a1eb, description="**Your balance is** `$0`"), ephemeral=True)

@tree.command(name="pay", description="Pay another user")
async def pay(interaction : discord.Interaction, user : discord.Member, amount : int):
    with open(db, "r+") as f:
        data = json.load(f)
        sid = str(interaction.user.id)
        rid = str(user.id)
        if sid in data:
            if data[sid] >= amount:
                if rid in data:
                    data[sid] -= amount
                    data[rid] += amount
                    f.seek(0)
                    f.truncate()
                    json.dump(data, f, indent=4)
                else:
                    data[sid] -= amount
                    data[rid] = amount
                    f.seek(0)
                    f.truncate()
                    json.dump(data, f, indent=4)
                await interaction.response.send_message(embed=discord.Embed(title="Payment Success", colour=0xa1f7a1, description=f"`${amount}` **has successfully been sent over to** {user.mention}").set_thumbnail(url="https://i.ibb.co/G5pWVq6/Flag.png"), ephemeral=True)
            else:
                if rid not in data:
                    data[rid] = 0
                    f.seek(0)
                    f.truncate()
                    json.dump(data, f, indent=4)
                await interaction.response.send_message(embed=discord.Embed(title="Payment Failure", colour=0xf7a1a1, description=f"**Uh-oh, it doesn't seem like you have** `${amount}` **in your balance to send to** {user.mention}").set_thumbnail(url="https://i.ibb.co/G5pWVq6/Flag.png"), ephemeral=True)
        else:
            data[sid] = 0
            if rid not in data:
                data[rid] = 0
            f.seek(0)
            f.truncate()
            json.dump(data, f, indent=4)
            await interaction.response.send_message(embed=discord.Embed(title="Payment Failure", colour=0xf7a1a1, description=f"**Uh-oh, it doesn't seem like you have** `${amount}` **in your balance to send to** {user.mention}").set_thumbnail(url="https://i.ibb.co/G5pWVq6/Flag.png"), ephemeral=True)

@tree.command(name="ssu", description="Announce an SSU Through the bot")
@app_commands.check(lambda interaction : interaction.user.id == 301014178703998987)
async def ssu(interaction : discord.Interaction, message : str):
    channel = client.get_channel(794634829135085578)
    msg = await channel.send("||@everyone||", embed=discord.Embed(title="Server Startup", colour=0x57a1eb, description=f"{message}\n\nShouted by {interaction.user.mention}"))
    await msg.add_reaction('\U0001f44d')
    await interaction.response.send_message(embed=discord.Embed(title="SSU Announced", colour=0x57a1eb, description=f"**SSU Poll has been sent over to** <#794634829135085578>"), ephemeral=True)

@client.command()
@commands.check(lambda ctx : ctx.author.id == 301014178703998987)
async def connect(ctx):
    await tree.sync()










async def main():
    async with client:
        async with websockets.serve(handler, 'localhost', 5089):
            print("Ready")
            await client.start('ODUzNjQ2NjcwMzI3NzA5Nzc2.YMYaag.P-mTYNvV1c_AYt6xYLC4gKNQesg')
            await asyncio.Future()

asyncio.run(main())

#Green // Success
#0xa1f7a1
#Blue // Confirm
#0x57a1eb
#Red // Failure (User Error)
#0xf7a1a1
#Yellow // Failure (Server Error)
#0xf7f4a1