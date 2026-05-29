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

import discord
from discord.ext import commands
from discord.ui import Button, View, Modal, TextInput
import os

# --- إعدادات البوت ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# 🛠️ [إعدادات الآي دي]
ADMIN_CHANNEL_ID = 111111111111111111   # آي دي روم الإدارة
PLAYERS_CHANNEL_ID = 222222222222222222 # آي دي روم الأقيام (مستلزمات-الاقيام)

# 🛡️ [أسماء الرتب المسموح لها بالتحكم]
ALLOWED_ROLES = ["Open Values", "Founder"] #

REACTION_EMOJI = "✅"
LOGO_URL = "https://raw.githubusercontent.com/mahdifaisalaliahmed-hub/ROSH-System/main/1000155120.png"

# دالة للتحقق من الرتبة
def has_permission(user):
    return any(role.name in ALLOWED_ROLES for role in user.roles)

# --- 1. نافذة التجديد ---
class RenewGameModal(Modal, title="Renew a game"):
    host_id = TextInput(label="ايدي الهوست الجديد", placeholder="اكتب الايدي هنا...", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🔄 Games Notifications | تجديد الرحلة",
            description=f"• تم تجديد الفعالية، اضغط {REACTION_EMOJI} للحجز.",
            color=discord.Color.teal()
        )
        embed.set_author(name="نظام RH", icon_url=LOGO_URL)
        embed.add_field(name="👑 الهوست الحالي:", value=f"```{self.host_id.value}
```")
        
        channel = bot.get_channel(PLAYERS_CHANNEL_ID)
        if channel:
            msg = await channel.send(content="@everyone", embed=embed)
            await msg.add_reaction(REACTION_EMOJI)
            await interaction.response.send_message("✅ تم التجديد بنجاح!", ephemeral=True)

# --- 2. نافذة بدء رحلة ---
class CreateTripModal(Modal, title="Create a new game"):
    host_id = TextInput(label="ايدي الهوست", placeholder="اكتب الايدي...", required=True)
    assistant = TextInput(label="مساعد الهوست", placeholder="اكتب الاسم...", required=True)
    game_time = TextInput(label="وقت الرحلة", placeholder="مثلاً: الآن", required=True)
    alerts = TextInput(label="تنبيهات الرحلة", style=discord.TextStyle.paragraph, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        channel = bot.get_channel(PLAYERS_CHANNEL_ID)
        embed = discord.Embed(
            title="📢 Games Notifications | فتح رحلة جديدة",
            description=f"• اضغط على {REACTION_EMOJI} بالأسفل لحجز مقعدك.",
            color=discord.Color.blue()
        )
        embed.set_author(name="نظام RH للرحلات", icon_url=LOGO_URL)
        embed.add_field(name="👑 ايدي الهوست :", value=f"```{self.host_id.value}```", inline=False)
        embed.add_field(name="🤝 مساعد الهوست :", value=f"```{self.assistant.value}
```", inline=False)
        embed.add_field(name="⏰ وقت الرحلة :", value=f"```{self.game_time.value}```", inline=False)
        embed.add_field(name="📝 تنبيهات الرحلة :", value=f"```{self.alerts.value}
```", inline=False)
        embed.set_footer(text="© GULF BOT | 2026")
        
        msg = await channel.send(content="@everyone", embed=embed)
        await msg.add_reaction(REACTION_EMOJI)
        await interaction.response.send_message("✅ تم نشر الرحلة بنجاح!", ephemeral=True)

# --- 3. لوحة تحكم الإدارة مع فحص الرتب ---
class AdminControlPanelView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="بدأ رحلة", style=discord.ButtonStyle.success)
    async def start_trip(self, interaction: discord.Interaction, button: discord.ui.Button):
        if has_permission(interaction.user):
            await interaction.response.send_modal(CreateTripModal())
        else:
            await interaction.response.send_message("❌ عذراً، هذا الزر مخصص لرتبة Open Values أو Founder فقط.", ephemeral=True)

    @discord.ui.button(label="إعصار", style=discord.ButtonStyle.danger)
    async def storm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not has_permission(interaction.user):
            await interaction.response.send_message("❌ ليس لديك الصلاحية.", ephemeral=True)
            return
            
        players_channel = bot.get_channel(PLAYERS_CHANNEL_ID)
        async for message in players_channel.history(limit=20):
            if message.author == bot.user and message.embeds:
                embed = message.embeds[0]
                embed.color = discord.Color.red()
                embed.title = "🌪️ Games Notifications | إنهاء الرحلة"
                embed.description = "🚨 تم إنهاء الرحلة الحالية نظراً لظروف الإعصار."
                await message.edit(embed=embed)
                await interaction.response.send_message("🌪️ تم إعلان الإعصار!", ephemeral=True)
                return

    @discord.ui.button(label="تجديد", style=discord.ButtonStyle.secondary)
    async def renew(self, interaction: discord.Interaction, button: discord.ui.Button):
        if has_permission(interaction.user):
            await interaction.response.send_modal(RenewGameModal())
        else:
            await interaction.response.send_message("❌ ليس لديك الصلاحية.", ephemeral=True)

# --- 4. استدعاء اللوحة بالكلمة السرية مع فحص الرتب ---
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.lower() == "!setup":
        # التأكد من الرتبة ومن الروم الصحيح
        if has_permission(message.author) and message.channel.id == ADMIN_CHANNEL_ID:
            await message.delete()
            embed = discord.Embed(
                title="Game Selection",
                description="• **Choose you want to make**\n\nلوحة التحكم مفعّلة الآن لأصحاب الرتب العليا.",
                color=discord.Color.blue()
            )
            embed.set_image(url=LOGO_URL)
            await message.channel.send(embed=embed, view=AdminControlPanelView())
        elif message.content.lower() == "!setup":
            await message.channel.send("❌ الصلاحيات غير كافية أو المكان خاطئ.", delete_after=5)
            
    await bot.process_commands(message)

@bot.event
async def on_ready():
    print(f'البوت شغال بنظام الرتب (Open Values & Founder) باسم: {bot.user.name}')

token = os.getenv('DISCORD_TOKEN')
bot.run(token)
