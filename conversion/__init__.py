from .conversion import Conversion

async def setup(bot):
    await bot.add_cog(Conversion(bot))
