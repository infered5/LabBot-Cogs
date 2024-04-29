# keep the imports, ya filthy animal
import re
import discord
from redbot.core import commands
from pint import UnitRegistry
from currency_converter import CurrencyConverter

# print('RELOADING')

# TODO
# remove milligrams
# add yards
# add velocity
# add acceleration
# add volume

# populate Pint registry with default units
ureg = UnitRegistry()
ureg.default_format = ".3f"
c = CurrencyConverter()


async def wait_for_reaction(
    confirmation_message, bot, emoji="📝", confirm_time=60, delete_after=True
):
    """Reacts to message with emoji, does things on click"""
    try:
        await confirmation_message.add_reaction(emoji)
    except:
        return False, None

    def check(reaction, user):
        return (
            str(reaction.emoji) == emoji
            and user != bot
            and confirmation_message.id == reaction.message.id
        )

    # wait for reaction from user
    try:
        reaction, user = await bot.wait_for(
            "reaction_add", timeout=confirm_time, check=check
        )
        if delete_after:
            await confirmation_message.clear_reactions()
        return True, user
    except BaseException as e:
        print(e)
        if delete_after:
            await confirmation_message.clear_reactions()
        return False, None


async def convert_unit(value, unit, target_unit):
    quantity = value * ureg(unit)
    converted_quantity = quantity.to(target_unit)
    return converted_quantity.magnitude, str(converted_quantity.units)


class Conversion(commands.Cog):
    """Helps you convert units with reaction press."""

    def __init__(self, bot):
        self.bot = bot

    # listen for stuff
    @commands.Cog.listener()
    async def on_message(self, message):


        # unit pairing dictionary
        units = {
            "millimeter": "inch",
            "centimeter": "inch",
            "meter": "foot",
            "meter": "feet",
            "kilometer": "mile",
            "fahrenheit": "celsius",
            "gram": "ounce",
            "kilogram": "pound",
            "tonne": "ton",
            "liter": "gallon",
        }
        # create a new dictionary for bidirectional mapping
        bidirectional_units = {**units, **{v: k for k, v in units.items()}}

        emoji_dict = {
            "temperature": "🌡️",
            "distance": "📏",
            "weight": "🧱",
            "force": "⚖️",
            "currency": "💵",
            "volume": "🪣",
        }
        unit_shorthands = {
            "f": "fahrenheit",
            "c": "celsius",
            "inch": "inch",
            "ft": "foot",
            "miles": "mile",
            "mile": "mile",
            "mi": "mile",
            "kg": "kilogram",
            "lb": "pound",
            "t": "tonne",
            "mm": "millimeter",
            "cm": "centimeter",
            "m": "meter",
            "km": "kilometer",
            "g": "gram",
            "mg": "milligram",
            "oz": "ounce",
            "gr": "grain",
            "N": "newton",
            "lbf": "pound-force",
            "l": "liter",
            "gal": "gallon",
        }
        input_text = message.content
        patterns = {
            "temperature": r"\b(-?\d+)\s*(?:degrees?\s*)?([CF])\b",
            "volume": (
                r"(\d+\.?\d*)\s*(ml|milliliter|milliliters|l|liter|liters|"
                r"fl oz|fluid ounce|fluid ounces|gal|gallon|gallons|pt|pint|"
                r"pints|cup|cups|ft3|cubic foot|cubic feet"
                r"|m3|cubic meter|cubic meters)"
            ),
            "weight": (
                r"(\d+\.?\d*)\s*(kg|kilogram|kilograms|g|gram|grams|t|"
                r"metric ton|metric tons|lb|pound|pounds|"
                r"oz|ounce|ounces)"
            ),
            "distance": (
                r"(\d+\.?\d*)\s*(mi|miles|m|M|km|kilometer|kilometers|"
                r"kilometre|kilometres|cm|centimeter|centimeters|mm|"
                r"millimeter|millimeters|in|inch|inches|ft|foot|feet|"
                r"\'\s*\d*\"?)"
            ),
            "currency": (
                r"(\d+)\s*(USD|EUR|JPY|BGN|CZK|DKK|GBP|HUF|PLN|RON|SEK|"
                r"CHF|ISK|NOK|TRY|AUD|BRL|CAD|CNY|HKD|IDR|ILS|INR|KRW|"
                r"MXN|MYR|NZD|PHP|SGD|THB|ZAR)"
            ),
        }
        value = None
        unit = None
        converted_value = None
        converted_unit = None
        embed = discord.Embed()
        react_emoji = "💵"
        if message.author == self.bot.user:
            return
        try:
            for pattern_type, pattern in patterns.items():
                match = re.search(pattern, input_text)
                if match:
                    react_emoji = emoji_dict.get(pattern_type, "💵")
                    value = float(match.group(1))
                    if pattern_type == "temperature":
                        unit = match.group(2).lower()
                        unit = unit_shorthands.get(unit, unit)
                        converted_unit = bidirectional_units.get(unit)
                        from_unit = unit
                        to_unit = converted_unit
                        if str(from_unit) == "celsius":
                            converted_value = (value * 9 / 5) + 32
                        elif str(from_unit) == "fahrenheit":
                            converted_value = (value - 32) * 5 / 9
                    elif pattern_type == "currency":
                        unit = match.group(2).upper()
                        converted_unit = "USD" if unit != "USD" else unit
                        if unit != "USD":
                            converted_value = c.convert(value, unit, "USD")
                        else:
                            converted_value = value
                    else:
                        unit = match.group(2).lower()
                        unit = unit_shorthands.get(unit, unit)
                        converted_unit = bidirectional_units.get(unit)
                        from_unit = getattr(ureg, unit)
                        to_unit = getattr(ureg, converted_unit)
                        value_with_unit = value * from_unit
                        converted_value = value_with_unit.to(to_unit).magnitude
                    break
        #                else:
        #                    pass
        except Exception as e:
            print("Error:", e)
        if None in (value, unit, converted_value, converted_unit):
            return False
        #        else:
        output_string = f"{value} {unit} = {round(converted_value, 1)} {converted_unit}"
        embed.add_field(
            name=f"{unit.capitalize()} Conversion:", value=output_string, inline=False
        )
        if len(embed.fields) > 0:
            send_embed, user = await wait_for_reaction(
                message, self.bot, emoji=react_emoji, confirm_time=60
            )
            if send_embed:
                embed.set_footer(text=f"Unit Conversion Requested By: {user}")
                await message.channel.send(embed=embed)
