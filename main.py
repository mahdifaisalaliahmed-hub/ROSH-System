import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View, Modal, TextInput
import os

# --- إعدادات البوت ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# 🛡️ [أسماء الرتب المسموح لها بالتحكم]
ALLOWED_ROLES = ["Open Values", "Founder"] 

REACTION_EMOJI = "✅"
LOGO_URL = "https://raw.githubusercontent.com/mahdifaisalaliahmed-hub/ROSH-System/main/1000155120.png"

# متغيرات لحفظ روماتك بشكل مؤقت (سيتم تحديدها عبر السلاش)
ADMIN_CHANNEL_ID = None
PLAYERS_CHANNEL_ID = None

# دالة التحقق من الصلاحيات
def has_permission(user):
    return any(role.name in ALLOWED_ROLES for role in user.roles)

# --- نافذة بدء رحلة (Create a new game) ---
class CreateTripModal(Modal, title="Create a new game"):
    host_id = TextInput(label="ايدي الهوست", placeholder="اكتب الايدي هنا...", required=True)
    assistant = TextInput(label="مساعد الهوست", placeholder="اكتب الاسم...", required=True)
    game_time = TextInput(label="وقت الرحلة", placeholder="مثلاً: الآن", required=True)
    alerts = TextInput(label="تنبيهات الرحلة", style=discord.TextStyle.paragraph, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        global PLAYERS_CHANNEL_ID
        if not PLAYERS_CHANNEL_ID:
            await interaction.response.send_message("❌ لم يتم تحديد روم اللاعبين بعد! استخدم أمر `/تحديد_الروم` أولاً.", ephemeral=True)
            return
            
        channel = bot.get_channel(PLAYERS_CHANNEL_ID)
        embed = discord.Embed(
            title="📢 Games Notifications | فتح رحلة جديدة",
            description=f"• اضغط على {REACTION_EMOJI} بالأسفل لحجز مقعدك.",
            color=discord.Color.blue()
        )
        embed.set_author(name="نظام RH للرحلات", icon_url=LOGO_URL)
        embed.add_field(name="👑 ايدي الهوست :", value=f"```{self.host_id.value}```", inline=False)
        embed.add_field(name="🤝 مساعد الهوست :", value=f"```{self.assistant.value}```", inline=False)
        embed.add_field(name="⏰ وقت الرحلة :", value=f"```{self.game_time.value}```", inline=False)
        embed.add_field(name="📝 تنبيهات الرحلة :", value=f"```{self.alerts.value}```", inline=False)
        embed.set_footer(text="© GULF BOT | 2026")
        
        msg = await channel.send(content="@everyone", embed=embed)
        await msg.add_reaction(REACTION_EMOJI)
        await interaction.response.send_message("✅ تم إرسال الرحلة لروم اللاعبين المحدد!", ephemeral=True)

# --- نافذة التجديد ---
class RenewGameModal(Modal, title="Renew a game"):
    host_id = TextInput(label="ايدي الهوست الجديد", placeholder="اكتب الايدي...", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        global PLAYERS_CHANNEL_ID
        if not PLAYERS_CHANNEL_ID:
            await interaction.response.send_message("❌ لم يتم تحديد روم اللاعبين بعد!", ephemeral=True)
            return

        channel = bot.get_channel(PLAYERS_CHANNEL_ID)
        embed = discord.Embed(title="🔄 تجديد الرحلة", color=discord.Color.teal())
        embed.add_field(name="👑 الهوست الجديد:", value=f"```{self.host_id.value}```")
        msg = await channel.send(content="@everyone", embed=embed)
        await msg.add_reaction(REACTION_EMOJI)
        await interaction.response.send_message("✅ تم التجديد!", ephemeral=True)

# --- لوحة التحكم المركزية ---
class AdminControlPanelView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="بدأ رحلة", style=discord.ButtonStyle.success)
    async def start_trip(self, interaction: discord.Interaction, button: discord.ui.Button):
        if has_permission(interaction.user):
            await interaction.response.send_modal(CreateTripModal())
        else:
            await interaction.response.send_message("❌ ليس لديك صلاحية (Open Values / Founder)", ephemeral=True)

    @discord.ui.button(label="إعصار", style=discord.ButtonStyle.danger)
    async def storm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if has_permission(interaction.user):
            global PLAYERS_CHANNEL_ID
            if not PLAYERS_CHANNEL_ID:
                await interaction.response.send_message("❌ لم يتم تحديد روم اللاعبين.", ephemeral=True)
                return
            players_channel = bot.get_channel(PLAYERS_CHANNEL_ID)
            async for message in players_channel.history(limit=10):
                if message.author == bot.user and message.embeds:
                    embed = message.embeds[0]
                    embed.title = "🌪️ انتهت الرحلة (إعصار)"
                    embed.color = discord.Color.red()
                    await message.edit(embed=embed)
                    await interaction.response.send_message("🌪️ تم تنفيذ الإعصار!", ephemeral=True)
                    return
        else:
            await interaction.response.send_message("❌ لا تملك الصلاحية.", ephemeral=True)

    @discord.ui.button(label="تجديد", style=discord.ButtonStyle.secondary)
    async def renew(self, interaction: discord.Interaction, button: discord.ui.Button):
        if has_permission(interaction.user):
            await interaction.response.send_modal(RenewGameModal())
        else:
            await interaction.response.send_message("❌ لا تملك الصلاحية.", ephemeral=True)

# --- أوامر السلاش لتحديد الرومات ذكياً ---

@bot.tree.command(name="تحديد_الروم", description="تحديد الروم العام الذي ستظهر فيه الأقيام والرحلات للاعبين")
@app_commands.describe(روم="اختر الروم المراد إرسال الرحلات إليه")
async def set_players_room(interaction: discord.Interaction, روم: discord.TextChannel):
    if not has_permission(interaction.user):
        await interaction.response.send_message("❌ هذا الأمر مخصص للرتب العليا فقط.", ephemeral=True)
        return
    global PLAYERS_CHANNEL_ID
    PLAYERS_CHANNEL_ID = روم.id
    await interaction.response.send_message(f"✅ تم تحديد روم اللاعبين بنجاح لتكون: {روم.mention}", ephemeral=True)

@bot.tree.command(name="تحديد_روم_الادارة", description="تحديد الروم السري المخصص لكتابة أمر !setup")
@app_commands.describe(روم="اختر روم الإدارة السري")
async def set_admin_room(interaction: discord.Interaction, روم: discord.TextChannel):
    if not has_permission(interaction.user):
        await interaction.response.send_message("❌ هذا الأمر مخصص للرتب العليا فقط.", ephemeral=True)
        return
    global ADMIN_CHANNEL_ID
    ADMIN_CHANNEL_ID = روم.id
    await interaction.response.send_message(f"✅ تم تحديد روم الإدارة بنجاح لتكون: {روم.mention}", ephemeral=True)

# --- أمر الاستدعاء بالشات العادي !setup ---
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.lower() == "!setup":
        global ADMIN_CHANNEL_ID
        if not ADMIN_CHANNEL_ID:
            await message.channel.send("⚠️ يرجى تحديد روم الإدارة أولاً باستخدام أمر السلاش `/تحديد_روم_الادارة`", delete_after=5)
            return

        if has_permission(message.author) and message.channel.id == ADMIN_CHANNEL_ID:
            await message.delete()
            
            embed = discord.Embed(
                title="Game Selection",
                description="Choose you want to make\n\nنظام التحكم بالرحلات متاح الآن.",
                color=discord.Color.blue()
            )
            embed.set_image(url=LOGO_URL)
            embed.set_footer(text="© GULF BOT | 2026")
            
            await message.channel.send(embed=embed, view=AdminControlPanelView())

    await bot.process_commands(message)

@bot.event
async def on_ready():
    print(f'البوت جاهز للاستدعاء عبر !setup باسم: {bot.user.name}')
    try:
        # مزامنة أوامر السلاش الجديدة ليراها الديسكورد فوراً
        synced = await bot.tree.sync()
        print(f"تمت مزامنة {len(synced)} من أوامر السلاش بنجاح!")
    except Exception as e:
        print(f"خطأ في المزامنة: {e}")

token = os.getenv('DISCORD_TOKEN')
bot.run(token)
import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Select, View, Modal, TextInput
import os

# --- إعدادات البوت ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True 
bot = commands.Bot(command_prefix='!', intents=intents)

# 🛡️ [إعدادات المسؤولين والروابط]
# الرتبة المحددة من صورة 1000155140.jpg
OFFICER_ROLES = ["ID acceptance officers", "Founder", "Open Values"] 
LOGO_URL = "https://raw.githubusercontent.com/mahdifaisalaliahmed-hub/ROSH-System/main/1000155120.png"

# متغيرات الرومات والرتب
LOG_CHANNEL_ID = None
CITIZEN_ROLE_ID = None 

def is_officer(user):
    return any(role.name in OFFICER_ROLES for role in user.roles)

# --- 1. نافذة إدخال بيانات الهوية (Modal) ---
class IdentityModal(Modal):
    def __init__(self, char_num):
        super().__init__(title=f"إنشاء هوية جديدة - الشخصية {char_num}")
        self.char_num = char_num
        
    f_name = TextInput(label="الاسم الأول", placeholder="اكتب اسمك الأول هنا...", required=True)
    l_name = TextInput(label="اسم العائلة", placeholder="اكتب اسم العائلة هنا...", required=True)
    birthday = TextInput(label="تاريخ الميلاد", placeholder="مثال: 2006/3/4", required=True)
    birth_place = TextInput(label="مكان الميلاد", placeholder="اكتب المدينة أو الدولة...", required=True)
    gender = TextInput(label="الجنس", placeholder="ذكر / أنثى", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        if not LOG_CHANNEL_ID:
            await interaction.response.send_message("❌ لم يتم تحديد روم الإدارة (اللوج) بعد!", ephemeral=True)
            return

        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        
        # جلب رتبة المسؤولين لعمل منشن لهم
        officer_role = discord.utils.get(interaction.guild.roles, name="ID acceptance officers")
        mention = officer_role.mention if officer_role else ""

        embed = discord.Embed(title="تقديم هوية جديد! 📄", color=discord.Color.blue())
        embed.set_author(name=f"قسم مراجعة الهويات | @RH")
        embed.description = (
            f"👤 **صاحب الطلب:** {interaction.user.mention}\n\n"
            f"**الاسم الأول |** {self.f_name.value}\n"
            f"**اسم العائلة |** {self.l_name.value}\n"
            f"**تاريخ الميلاد |** {self.birthday.value}\n"
            f"**مكان الميلاد |** {self.birth_place.value}\n"
            f"**الجنس |** {self.gender.value}\n"
            f"**رقم الشخصية |** {self.char_num}"
        )
        embed.set_image(url=LOGO_URL)
        embed.set_footer(text="© GULF BOT | 2026")

        view = IdentityActionView(user=interaction.user, char_num=self.char_num)
        await log_channel.send(content=f"🔔 {mention} تقديم جديد يحتاج مراجعة", embed=embed, view=view)
        
        await interaction.response.send_message("✅ تم إرسال هويتك للمسؤولين بنجاح!", ephemeral=True)

# --- 2. لوحة اختيار الشخصية (شخصيتين فقط) ---
class IdentitySelectionView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        placeholder="Choose a character you want to create",
        options=[
            discord.SelectOption(label="الشخصية الأولى", value="1", emoji="👤"),
            discord.SelectOption(label="الشخصية الثانية", value="2", emoji="👥"),
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        await interaction.response.send_modal(IdentityModal(select.values[0]))

# --- 3. أزرار القبول والرفض للمسؤولين ---
class IdentityActionView(View):
    def __init__(self, user, char_num):
        super().__init__(timeout=None)
        self.user = user
        self.char_num = char_num

    @discord.ui.button(label="قبول ✅", style=discord.ButtonStyle.success)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_officer(interaction.user):
            await interaction.response.send_message("❌ هذا الزر مخصص لرتبة المسؤولين فقط.", ephemeral=True)
            return
            
        global CITIZEN_ROLE_ID
        if CITIZEN_ROLE_ID:
            role = interaction.guild.get_role(CITIZEN_ROLE_ID)
            if role:
                try: await self.user.add_roles(role)
                except: pass
        
        embed = discord.Embed(title="تم قبول الهوية ✅", color=discord.Color.green())
        embed.description = f"تم قبول هوية : {self.user.mention}\nرقم الشخصية : {self.char_num}\nالاداري المسؤول : {interaction.user.mention}"
        
        await interaction.message.edit(view=None)
        await interaction.response.send_message(embed=embed)
        try: await self.user.send(f"✅ تم قبول هويتك للشخصية رقم {self.char_num}!")
        except: pass

    @discord.ui.button(label="رفض ❌", style=discord.ButtonStyle.danger)
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_officer(interaction.user): return
        await interaction.message.edit(view=None)
        await interaction.response.send_message(f"❌ تم رفض هوية {self.user.mention}.")

# --- أوامر السلاش لإعداد النظام ---
@bot.tree.command(name="تحديد_روم_القبول", description="تحديد الروم الذي تظهر فيه طلبات الهوية للمسؤولين")
async def set_log(interaction: discord.Interaction, روم: discord.TextChannel):
    global LOG_CHANNEL_ID
    LOG_CHANNEL_ID = روم.id
    await interaction.response.send_message(f"✅ تم تحديد روم الإدارة: {روم.mention}", ephemeral=True)

@bot.tree.command(name="تحديد_رتبة_المواطن", description="تحديد الرتبة التي تعطى للاعب عند قبول هويته")
async def set_role(interaction: discord.Interaction, رتبة: discord.Role):
    global CITIZEN_ROLE_ID
    CITIZEN_ROLE_ID = رتبة.id
    await interaction.response.send_message(f"✅ تم ربط رتبة: {رتبة.mention}", ephemeral=True)

@bot.command()
async def setup_identity(ctx):
    """استدعاء لوحة إنشاء الهوية فقط"""
    if is_officer(ctx.author):
        await ctx.message.delete()
        embed = discord.Embed(title="Character Management", description="Character Creation\n\nاضغط أدناه لاختيار الشخصية والبدء في إنشاء الهوية.", color=discord.Color.dark_grey())
        embed.set_image(url=LOGO_URL)
        embed.set_footer(text="© GULF BOT | 2026")
        await ctx.send(embed=embed, view=IdentitySelectionView())

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'نظام الهوية الصافي جاهز باسم: {bot.user.name}')

bot.run(os.getenv('DISCORD_TOKEN'))


