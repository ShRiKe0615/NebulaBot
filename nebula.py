import os
import discord
import asyncio
from discord.ext import commands
from dotenv import load_dotenv
from discord.ui import View, Button
from games import TicTacToeView, Connect4View

def bot_run():

    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN_NBBT')
    if TOKEN is None:
        print("Error: DISCORD_TOKEN_NBBT is not set in the environment variables.")
        return

    intents = discord.Intents.default()
    intents.message_content = True
    client = commands.Bot(command_prefix="+", intents=intents)

    @client.event
    async def on_ready():
        print(f"{client.user.name}, I got legs so running !!!")

    @client.hybrid_command()
    async def synco(ctx: commands.Context):
        await ctx.send("Syncing the commands your majesty...")
        await client.tree.sync()

    @client.hybrid_command()
    async def hello(ctx):
        await ctx.send("Hey there!")

    @client.hybrid_command()
    async def ping(ctx: commands.Context):
        await ctx.send('Pong!')

    @client.hybrid_command()
    async def set_nickname(ctx, user: discord.Member, *, new_nickname: str):
        try:
            await user.edit(nick=new_nickname)
            await ctx.send(f"Nickname changed for {user.display_name} to {new_nickname}")
        except discord.Forbidden:
            await ctx.send("I don't have permission to change that user's nickname.")

    @client.hybrid_command()
    async def set_timer(ctx, seconds: int):
        class TimerView(View):
            def __init__(self):
                super().__init__()
                self.timer_active = True
                self.notify_users = []

            @discord.ui.button(label="Cancel Timer", style=discord.ButtonStyle.red)
            async def cancel_timer(self, interaction: discord.Interaction, button: Button):
                self.timer_active = False
                await interaction.response.send_message("Timer cancelled!", ephemeral=True)

            @discord.ui.button(label="Notify Me", style=discord.ButtonStyle.green)
            async def notify_me(self, interaction: discord.Interaction, button: Button):
                if interaction.user not in self.notify_users:
                    self.notify_users.append(interaction.user)
                    await interaction.response.send_message("You will be notified when the timer ends.", ephemeral=True)
                else:
                    await interaction.response.send_message("You are already on the notification list.", ephemeral=True)

        view = TimerView()
        embed = discord.Embed(title="Timer", description=f"Time left: {seconds} seconds", color=discord.Color.blue())
        message = await ctx.send(embed=embed, view=view)

        while seconds > 0 and view.timer_active:
            await asyncio.sleep(1)
            seconds -= 1
            embed.description = f"Time left: {seconds} seconds"
            await message.edit(embed=embed)

        if view.timer_active:
            await ctx.send(f"Time's up! {ctx.author.mention}")
            if view.notify_users:
                mentions = ", ".join(user.mention for user in view.notify_users)
                await ctx.send(f"Pinging the users who wanted to be notified: {mentions}")

    # @client.hybrid_command()
    # async def tic_tac_toe(ctx, player1: discord.User, player2: discord.User):
    #     if player1 == player2:
    #         await ctx.send("Players must be different.")
    #         return
    #     view = TicTacToeView(ctx, player1, player2)
    #     await view.start()
    @client.hybrid_command()
    async def tictactoe(ctx: commands.Context, member: discord.Member):
        if ctx.author == member:
            await ctx.send("You can't play against yourself!")
            return

        view = TicTacToeView(ctx, ctx.author, member)
        await view.start()

    @client.hybrid_command()
    async def connect4(ctx, player1: discord.User, player2: discord.User):
        if player1 == player2:
            await ctx.send("Players must be different.")
            return
        view = Connect4View(ctx, player1, player2)
        await view.start()

    client.run(TOKEN)