import discord
from discord.ext import commands
from discord.ui import Select, View
import os

# إعدادات البوت الأساسية
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# بناء قائمة الاختيار (Select Menu)
class ROSHMenu(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="قسم الإدارة", description="أوامر التحكم بالسيرفر", emoji="🛡️"),
            discord.SelectOption(label="قسم الألعاب", description="أوامر التسلية والفعاليات", emoji="🎮"),
            discord.SelectOption(label="الدعم الفني", description="المساعدة والشكاوى", emoji="🎫")
        ]
        super().__init__(placeholder="اختر القسم الذي تريده من هنا...", options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "قسم الإدارة":
            await interaction.response.send_message("🛡️ **أوامر الإدارة المتاحة:**\n`!kick` - طرد عضو\n`!ban` - حظر عضو", ephemeral=True)
        elif self.values[0] == "قسم الألعاب":
            await interaction.response.send_message("🎮 **أوامر الألعاب:**\n`!roll` - رمي النرد\n`!coin` - ملك أم كتابة", ephemeral=True)
        elif self.values[0] == "الدعم الفني":
            await interaction.response.send_message("🎫 تم تسجيل طلبك! سيقوم الدعم الفني بمساعدتك قريباً.", ephemeral=True)

# أمر تشغيل المنيو
@bot.command()
async def menu(ctx):
    view = View()
    view.add_item(ROSHMenu())
    await ctx.send("👋 **أهلاً بك في نظام سيرفر ROSH!**\nالرجاء اختيار القسم المناسب من القائمة أدناه:", view=view)

# تشغيل البوت بأمان باستخدام التوكن من إعدادات Render
token = os.getenv('DISCORD_TOKEN')
if token:
    bot.run(token)
else:
    print("خطأ: لم يتم العثور على التوكن DISCORD_TOKEN!")
