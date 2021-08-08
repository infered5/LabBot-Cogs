import re
import discord
from typing import Optional
from redbot.core import commands

# Define numbers -> emotes tuple
nums = (":zero:", ":one:", ":two:", ":three:", ":four:", ":five:", ":six:", ":seven:", ":eight:", ":nine:")

# Define specials -> emotes dict
specials = {"!": ":exclamation:", "?": ":question:", "#": ":hash:", "'": "'", ".": ".", ",": ","}

allowed_chars = re.compile(r"[^a-z0-9!?\'.#, ]")


def convert_char(char: str) -> str:
    """Convert character to discord emoji"""
    # Double space if char is space
    if char == " ":
        return "  "

    # Convert to number emote if number
    elif char.isdigit():
        return f"{nums[int(char)]} "

    # Convert to regional indicator emote if letter
    elif char.isalpha():
        return f":regional_indicator_{char}: "

    # Convert to character emote
    else:
        return f"{specials[char]} "


async def convert_string(ctx: commands.Context, input_str: str) -> str:
    """Convert a string to discord emojis"""
    input_str = (await commands.clean_content(fix_channel_mentions=True).convert(ctx, input_str)).lower()
    # Strip unsupported characters
    if allowed_chars.search(input_str):
        input_str = allowed_chars.sub("", input_str)

    # Convert characters to Discord emojis
    letters = "".join(map(convert_char, input_str))
    # Replace >= 3 spaces with two
    letters = re.sub(" {3,}", "  ", letters)
    # Correct punctuation spacing
    letters = re.sub(r"([!?\'.#,:]) ([!?\'.#,])", r"\1\2", letters)
    # Necessary for edge cases
    letters = re.sub(r"([!?\'.#,:]) ([!?\'.#,])", r"\1\2", letters)

    return letters


def raw_flag(argument: str) -> bool:
    """Raw flag converter"""
    if argument.lower() == "-raw":
        return True
    else:
        raise commands.BadArgument


class Letters(commands.Cog):
    """Letters cog"""

    @commands.command()
    async def letters(self, ctx: commands.Context, raw: Optional[raw_flag] = False, *, msg: convert_string):
        """Outputs large emote letters (\"regional indicators\") from input text.

        The result can be outputted as raw emote code using `-raw` flag.

        Example:
        - `[p]letters I would like this text as emotes 123`
        - `[p]letters -raw I would like this text as raw emote code 123`
        """
        output = f"```{msg}```" if raw else msg

        # Ensure output isn't too long
        if len(output) > 2000:
            return await ctx.send("Input too large.")

        # Send message
        await ctx.send(output)
