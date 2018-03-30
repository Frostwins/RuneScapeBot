from discord import Member
from discord.ext.commands import command, Context
from cogs.utils.custom_bot import CustomBot
from cogs.utils.currency_validator import validate_currency
from cogs.utils.money_fetcher import money_fetcher
from cogs.utils.currency_checks import has_set_currency


class MoneyCommands(object):

    def __init__(self, bot:CustomBot):
        self.bot = bot


    @command()
    async def transfer(self, ctx:Context, user:Member, amount:str, currency_type:str):
        '''
        Lets you transfer some of your own money to another user
        '''

        # Make sure they're specifying a valid currency type
        currency_type = validate_currency(currency_type)
        if not currency_type:
            await ctx.send('The specified currency type is not valid.')
            return

        # Make sure they don't send off their money to bots
        if user.bot:
            await ctx.send('That user is a bot. Why are you like this.')
            return

        # Get the amount of money they want to modify by (int)
        amount = money_fetcher(amount)

        # Modify the database
        async with self.bot.database() as db:
            await db.modify_user_currency(ctx.author, -amount, currency_type)
            await db.modify_user_currency(user, amount, currency_type)
        x = "{.mention}, you have successfully transferred `{}gp` to {.mention}.".format(ctx.author, amount, user)
        await ctx.send(x)


    @command()
    async def setmode(self, ctx:Context, currency_type:str):
        '''
        Set the currency you use in your betting sessions
        '''

        # Make sure they're specifying a valid currency type
        currency_type = validate_currency(currency_type)
        if not currency_type:
            await ctx.send('The specified currency type is not valid.')
            return

        async with self.bot.database() as db:
            await db.set_user_currency_mode(ctx.author, currency_type)
        await ctx.send('Your currency mode has been updated.')


    @command(aliases=['wallet'])
    @has_set_currency()
    async def balance(self, ctx:Context):
        '''
        Gives you your current balance
        '''

        async with self.bot.database() as db:
            currency_type = await db.get_user_currency_mode(ctx.author)
            x = await db.get_user_currency(ctx.author, currency_type)
        await ctx.message.add_reaction('\N{ENVELOPE WITH DOWNWARDS ARROW ABOVE}')
        await ctx.author.send('You currently have `{}gp` in your {} wallet.'.format(x, currency_type))


def setup(bot:CustomBot):
    x = MoneyCommands(bot)
    bot.add_cog(x)
