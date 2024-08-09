import discord
from discord.ext import commands
from discord.ui import Button, View

class TicTacToeView(View):
    def __init__(self, ctx, player1: discord.User, player2: discord.User):
        super().__init__(timeout=300)
        self.ctx = ctx
        self.board = [[' ' for _ in range(3)] for _ in range(3)]
        self.players = [player1, player2]
        self.current_player = 0
        self.message = None

    def get_embed(self):
        symbols = {'X': '❌', 'O': '⭕', ' ': '⬛'}
        board_string = '\n'.join(' '.join(symbols[cell] for cell in row) for row in self.board)
        current_player_mention = self.players[self.current_player].mention
        embed_description = (
            f"**{current_player_mention}'s Turn**\n\n"
            f"```\n{board_string}\n```"
        )
        embed = discord.Embed(title="Tic-Tac-Toe", description=embed_description, color=discord.Color.blue())
        return embed

    def check_winner(self):
        player_symbol = 'X' if self.current_player == 0 else 'O'
        for row in self.board:
            if all(cell == player_symbol for cell in row):
                return True
        for col in range(3):
            if all(self.board[row][col] == player_symbol for row in range(3)):
                return True
        if all(self.board[i][i] == player_symbol for i in range(3)) or all(self.board[i][2 - i] == player_symbol for i in range(3)):
            return True
        return False

    async def update_board(self):
        self.clear_items()
        emoji_map = {' ': '⬛', 'X': '❌', 'O': '⭕'}
        buttons = [
            Button(style=discord.ButtonStyle.primary, emoji=emoji_map[self.board[r][c]], custom_id=f'{r}-{c}')
            for r in range(3) for c in range(3)
        ]

        for button in buttons:
            button.callback = self.button_callback
            self.add_item(button)

        try:
            await self.message.edit(embed=self.get_embed(), view=self)
        except discord.HTTPException as e:
            print(f"Failed to update message: {e}")

    async def button_callback(self, interaction: discord.Interaction):
        if interaction.user != self.players[self.current_player]:
            await interaction.response.send_message(f"It's not your turn!, It's {self.players[self.current_player].mention} turn!", ephemeral=True)
            return

        row, col = map(int, interaction.data['custom_id'].split('-'))
        if self.board[row][col] == ' ':
            player_symbol = 'X' if self.current_player == 0 else 'O'
            self.board[row][col] = player_symbol
            if self.check_winner():
                await self.update_board()
                await interaction.response.send_message(f"Player {self.players[self.current_player].mention} wins!", ephemeral=True)
                self.stop()
            elif all(self.board[r][c] != ' ' for r in range(3) for c in range(3)):
                await self.update_board()
                await interaction.response.send_message("It's a tie baby!", ephemeral=True)
                self.stop()
            else:
                self.current_player = 1 - self.current_player
                await self.update_board()
        else:
            await interaction.response.send_message("Invalid move. Cell already occupied Man.", ephemeral=True)

    async def start(self):
        emoji_map = {' ': '⬛', 'X': '❌', 'O': '⭕'}
        buttons = [
            Button(style=discord.ButtonStyle.primary, emoji=emoji_map[' '], custom_id=f'{r}-{c}')
            for r in range(3) for c in range(3)
        ]

        for button in buttons:
            button.callback = self.button_callback
            self.add_item(button)

        try:
            self.message = await self.ctx.send(embed=self.get_embed(), view=self)
        except discord.HTTPException as e:
            print(f"Failed to send message: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

class Connect4View(View):
    def __init__(self, ctx, player1: discord.User, player2: discord.User):
        super().__init__()
        self.ctx = ctx
        self.rows, self.cols = 6, 7
        self.board = [[' ' for _ in range(self.cols)] for _ in range(self.rows)]
        self.players = [player1, player2]
        self.current_player = 0
        self.message = None

    def get_embed(self):
        symbols = {'X': '🔴', 'O': '🟡', ' ': '⬛'}
        board_string = '\n'.join(' '.join(symbols[cell] for cell in row) for row in self.board)
        current_player_mention = self.players[self.current_player].mention
        embed_description = (
            f"**{current_player_mention}'s Turn**\n\n"
            f"```\n{board_string}\n```"
        )
        embed = discord.Embed(title="Connect 4", description=embed_description, color=discord.Color.blue())
        return embed

    def check_winner(self):
        player = self.players[self.current_player]
        player_symbol = 'X' if player == self.players[0] else 'O'
        for r in range(self.rows):
            for c in range(self.cols - 3):
                if all(self.board[r][c + i] == player_symbol for i in range(4)):
                    return True
        for r in range(self.rows - 3):
            for c in range(self.cols):
                if all(self.board[r + i][c] == player_symbol for i in range(4)):
                    return True
        for r in range(self.rows - 3):
            for c in range(self.cols - 3):
                if all(self.board[r + i][c + i] == player_symbol for i in range(4)):
                    return True
        for r in range(3, self.rows):
            for c in range(self.cols - 3):
                if all(self.board[r - i][c + i] == player_symbol for i in range(4)):
                    return True
        return False

    def drop_piece(self, col):
        for row in reversed(range(self.rows)):
            if self.board[row][col] == ' ':
                self.board[row][col] = 'X' if self.current_player == 0 else 'O'
                return row

    async def update_board(self):
        await self.message.edit(embed=self.get_embed())

    async def button_callback(self, interaction: discord.Interaction):
        if interaction.user != self.players[self.current_player]:
            await interaction.response.send_message("It's not your turn!", ephemeral=True)
            return

        col = int(interaction.data['custom_id'])
        if self.board[0][col] == ' ':
            row = self.drop_piece(col)
            if self.check_winner():
                await self.update_board()
                await interaction.response.send_message(f"Player {self.players[self.current_player].mention} wins!", ephemeral=True)
                self.stop()
            else:
                self.current_player = 1 - self.current_player
                await self.update_board()
        else:
            await interaction.response.send_message("Invalid move. Column is full. Use different column.", ephemeral=True)

    async def start(self):
        buttons = [Button(style=discord.ButtonStyle.secondary, label=f'Column {c+1}', custom_id=str(c)) for c in range(self.cols)]
        for button in buttons:
            button.callback = self.button_callback
        view = View()
        for button in buttons:
            view.add_item(button)
        self.message = await self.ctx.send(embed=self.get_embed(), view=view)