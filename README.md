import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View, Modal, TextInput
import os

# --- إعدادات البوت الأساسية ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# 🔔 ضع هنا آي دي (ID) الروم المخصص للرحلات بسيرفرك بدلاً من هذا الرقم الافتراضي
TRIPS_CHANNEL_ID = 123456789012345678  

# رابط شعار RH الخاص بك ليظهر بداخل الرسائل والإمبد
LOGO_URL = "https://raw.githubusercontent.com/mahdifaisalaliahmed-hub/ROSH-System/main/1000155120.png"

# --- 1. نافذة منبثقة لتجديد الرحلة (Renew a game) ---
class RenewGameModal(Modal, title="Renew a game"):
    host_id = TextInput(label="ايدي الهوست", placeholder="اكتب ايدي الهوست الجديد هنا...", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🔄 تم تجديد الرحلة والإنطلاق من جديد!",
            description="تم تجديد الفعالية بنجاح، يرجى التواجد فوراً والالتزام بالتعليمات.",
            color=discord.Color.teal()
        )
        embed.set_author(name="نظام الرحلات المتطور | RH", icon_url=LOGO_URL)
        embed.set_thumbnail(url=LOGO_URL)
        embed.add_field(name="👑 قائد الرحلة الحالي (الهوست):", value=f"```{self.host_id.value}```", inline=False)
        embed.set_footer(text="نتمنى لكم رحلة ممتعة بعد التجديد! 🛡️")
        
        channel = bot.get_channel(TRIPS_CHANNEL_ID)
        if channel:
            await channel.send(content="@everyone", embed=embed, view=UserTripView())
            await interaction.response.send_message("✅ تم تجديد الرحلة بنجاح في الروم العام!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ لم يتم العثور على روم الرحلات لتجديدها.", ephemeral=True)

# --- 2. نافذة منبثقة لإنشاء رحلة جديدة لأول مرة (Create a new game) ---
class CreateTripModal(Modal, title="Create a new game"):
    host_id = TextInput(label="ايدي الهوست", placeholder="اكتب الايدي هنا...", required=True)
    assistant = TextInput(label="مساعد الهوست", placeholder="اكتب اسم المساعد...", required=True)
    game_time = TextInput(label="وقت الرحلة", placeholder="مثلاً: 9:00 مساءً", required=True)
    alerts = TextInput(label="تنبيهات الرحلة", style=discord.TextStyle.paragraph, placeholder="اكتب ملاحظاتك وتنبيهاتك...", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        channel = bot.get_channel(TRIPS_CHANNEL_ID)
        if not channel:
            await interaction.response.send_message("❌ خطأ: لم يتم العثور على روم الرحلات، تأكد من الـ ID في الكود!", ephemeral=True)
            return

        embed = discord.Embed(
            title="📢 تم فتح رحلة جديدة! شارك معنا",
            description="• **Choose you want to make**",
            color=discord.Color.blue()
        )
        embed.set_author(name="نظام الرحلات المتطور | RH", icon_url=LOGO_URL)
        embed.set_thumbnail(url=LOGO_URL)
        
        embed.add_field(name="👑 الهوست:", value=f"```{self.host_id.value}```", inline=True)
        embed.add_field(name="🤝 المساعد:", value=f"```{self.assistant.value}```", inline=True)
        embed.add_field(name="⏰ وقت الرحلة:", value=f"```{self.game_time.value}```", inline=False)
        embed.add_field(name="📝 تنبيهات وملاحظات:", value=f"```{self.alerts.value}```", inline=False)
        
        embed.set_footer(text="© GULF BOT | 2026")
        
        await channel.send(content="@everyone", embed=embed, view=UserTripView())
        await interaction.response.send_message("✅ تم نشر تفاصيل الرحلة بنجاح في الروم العام!", ephemeral=True)

# --- 3. الأزرار التفاعلية المرفقة مع رسالة الرحلة (بدأ رحلة / إعصار / تجديد) ---
class UserTripView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="بدأ رحلة", style=discord.ButtonStyle.success, custom_id="start_trip_btn")
    async def start_trip(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.guild_permissions.administrator:
            await interaction.response.send_modal(CreateTripModal())
        else:
            await interaction.response.send_message("❌ هذا الزر مخصص للمسؤولين فقط لإطلاق الرحلات.", ephemeral=True)

    @discord.ui.button(label="إعصار", style=discord.ButtonStyle.danger, custom_id="storm_btn")
    async def storm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ هذا الإجراء مخصص للمسؤولين فقط.", ephemeral=True)
            return
            
        embed = interaction.message.embeds[0]
        embed.color = discord.Color.red()
        embed.title = "🌪️ انتهت الرحلة! تم صدور أمر الإعصار"
        embed.description = "🚨 تم إلغاء وإنهاء الرحلة الحالية نظراً لظروف الإعصار الحالية."
        
        await interaction.message.edit(embed=embed)
        await interaction.response.send_message("🌪️ تم تفعيل سر الإعصار وإنهاء الرحلة الحالية بنجاح.", ephemeral=True)

    @discord.ui.button(label="تجديد", style=discord.ButtonStyle.secondary, custom_id="renew_btn")
    async def renew(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.guild_permissions.administrator:
            await interaction.response.send_modal(RenewGameModal())
        else:
            await interaction.response.send_message("❌ هذا الزر مخصص للمسؤولين فقط لتجديد الرحلات.", ephemeral=True)

# --- 4. أحداث تشغيل البوت وأمر فتح اللوحة ---
@bot.event
async def on_ready():
    print(f'تم تشغيل البوت بنجاح باسم: {bot.user.name}')
    try:
        # مسح الذاكرة القديمة للأوامر المائلة وإعادة بنائها نظيفة
        bot.tree.clear_commands(guild=None)
        synced = await bot.tree.sync()
        print(f"تمت مزامنة {len(synced)} من الأوامر المائلة الجديدة بنجاح.")
    except Exception as e:
        print(f"خطأ أثناء المزامنة: {e}")

@bot.tree.command(name="setup_trips", description="إرسال اللوحة الرئيسية للتحكم بالرحلات (للمسؤولين فقط)")
@app_commands.checks.has_permissions(administrator=True)
async def setup_trips(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Game Selection",
        description="• **Choose you want to make**",
        color=discord.Color.blue()
    )
    embed.set_image(url=LOGO_URL)
    embed.set_footer(text="© GULF BOT | 2026")
    
    await interaction.response.send_message(embed=embed, view=UserTripView())

# تشغيل البوت بسحب التوكن من السيرفر بأمان
token = os.getenv('DISCORD_TOKEN')
bot.run(token)
