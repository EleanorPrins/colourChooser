import discord
import dotenv
import os
import re
from discord import app_commands

dotenv.load_dotenv()

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


@client.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {client.user}")


@tree.command(
    name="setcolour",
    description="Set your colour",
)
@app_commands.describe(hex="The color to set yourself as")
async def setcolour(interaction: discord.Interaction, hex: str):
    if not interaction.guild:
        await interaction.response.send_message(
            "This command can only be used in a server!", ephemeral=True
        )
        return

    if not re.match(r"^#?([a-fA-F0-9]{6}|[a-fA-F0-9]{3})$", hex):
        await interaction.response.send_message(
            "Invalid hex code! Please use a valid 3 or 6 digit hex code.",
            ephemeral=True,
        )
        return

    if hex.startswith("#"):
        hex = hex[1:]

    # check if interaction.user.roles contains a role with the name of the user
    role = discord.utils.get(interaction.guild.roles, name=str(interaction.user.id))
    if role is None:
        role = await interaction.guild.create_role(name=str(interaction.user.id))

    await role.edit(
        color=discord.Colour(int(hex, 16)),
        reason=f"Requested by {interaction.user}",
    )

    await interaction.user.add_roles(  # pyright: ignore[reportAttributeAccessIssue]
        role
    )

    if hex[0] != "#":
        hex = f"#{hex}"

    await interaction.response.send_message(
        f"Set your colour to `{hex}`! You can change it again at any time.",
        ephemeral=True,
    )


@tree.command(
    name="getcolour",
    description="Get your (or another user's) colour",
)
@app_commands.describe(user="The user to get the colour of")
async def getcolour(
    interaction: discord.Interaction, user: discord.User | discord.Member | None = None
):
    if not interaction.guild:
        await interaction.response.send_message(
            "This command can only be used in a server!", ephemeral=True
        )
        return

    if user is None:
        user = interaction.user

    role = discord.utils.get(interaction.guild.roles, name=str(user.id))
    if role is not None:
        await interaction.response.send_message(
            (
                f"Your colour is set to `{role.color}`"
                if user == interaction.user
                else f"{user.mention}'s colour is set to `{role.color}`"
            ),
            ephemeral=True,
        )
    else:
        await interaction.response.send_message(
            (
                "You don't have a colour set! You can set one using `/setcolour`."
                if user == interaction.user
                else f"{user.mention} doesn't have a colour set!"
            ),
            ephemeral=True,
        )


@tree.command(
    name="clearcolour",
    description="Clear your colour",
)
async def clearcolour(interaction: discord.Interaction):
    if not interaction.guild:
        await interaction.response.send_message(
            "This command can only be used in a server!", ephemeral=True
        )
        return
    role = discord.utils.get(interaction.guild.roles, name=str(interaction.user.id))
    if role is not None:
        await role.delete(reason=f"Requested by {interaction.user}")
        await interaction.response.send_message(
            "Cleared your colour! You can set a new one at any time.", ephemeral=True
        )
    else:
        await interaction.response.send_message(
            "You don't have a colour set! You can set one using `/setcolour`.",
            ephemeral=True,
        )


@tree.command(
    name="colourhelp",
    description="Get help with the bot",
)
async def hexhelp(interaction: discord.Interaction):

    await interaction.response.send_message(
        embed=discord.Embed(
            title="Colour Bot Help",
            description="This bot allows you to set your own colour in the server.",
            color=discord.Color.blurple(),
        )
        .add_field(
            name="Hex codes",
            value="Hex codes are a way of representing colours using numbers and letters. If you don't have a hex code in mind, you can use a website like [ColorHexa](https://www.colorhexa.com/) to find one.\n",
            inline=False,
        )
        .add_field(
            name="/setcolour",
            value="Set your colour.\nUsage: `/setcolour #RRGGBB`",
            inline=False,
        )
        .add_field(
            name="/getcolour [user]",
            value="Get your (or another user's) current colour.\nUsage: `/getcolour` or `/getcolour @user`",
            inline=False,
        )
        .add_field(
            name="/clearcolour",
            value="Clear your current colour.\nUsage: `/clearcolour`",
            inline=False,
        ),
        ephemeral=True,
    )


if __name__ == "__main__":
    if not os.getenv("TOKEN"):
        raise ValueError(
            "No token provided, please set the TOKEN environment variable."
        )

    client.run(os.getenv("TOKEN", ""))
