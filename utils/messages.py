MAIN_MENU_TEXT = (
    "🌊 *Mafiya o'yiniga xush kelibsiz!*\n\n"
    "Bot orqali guruhlarda Mafiya o'yinini o'tkazishingiz mumkin.\n"
    "Quyidagi tugmalardan birini tanlang:"
)

PROFILE_TEXT = (
    "👤 *PROFIL*\n"
    "———————————————\n"
    "🎮 O'yinlar: {games}\n\n"
    "🏆 G'alabalar: {wins} ({winrate}%)\n\n"
    "💀 Mag'lubiyatlar: {losses}\n\n"
    "🎭 Sevimli rol: {fav_role}\n\n"
    "⚔️ Mafiya: {mafia_games} marta\n"
    "🛡 Shahar: {town_games} marta\n"
    "🌪 Neytral: {neutral_games} marta\n\n"
    "🏅 Yutuqlar: {achievements}"
)

LOBBY_STARTED = (
    "🎮 *Mafiya o'yini boshlandi!*\n\n"
    "Guruhda o'yin boshlandi. Qo'shilish uchun pastdagi tugmani bosing!\n\n"
    "👥 Qo'shilgan o'yinchilar ({count}/{max}):\n"
    "{players}\n\n"
    "⏳ Qolgan vaqt: {time} soniya\n"
    "📌 Kamida 6 o'yinchi kerak"
)

PLAYER_JOINED = (
    "✅ {name} o'yinga qo'shildi!\n\n"
    "👥 Qo'shilgan o'yinchilar ({count}/{max}):\n"
    "{players}\n\n"
    "⏳ Qolgan vaqt: {time} soniya"
)

GAME_FULL = "❌ O'yin to'la! Maksimum {max} o'yinchi."

ALREADY_JOINED = "❌ Siz allaqachon o'yinga qo'shilgansiz!"

GAME_NOT_FOUND = "❌ Faol o'yin topilmadi."

NOT_ENOUGH_PLAYERS = "❌ O'yinni boshlash uchun kamida 6 o'yinchi kerak. Hozir: {count}"

GAME_STARTING = "🎮 *O'yin boshlanmoqda!*\n\nRollar tarqatilmoqda..."

ROLE_DISTRIBUTION = (
    "🎭 *Rolingiz:* {role}\n\n"
    "{description}\n\n"
    "📖 *Tim:* {team_label}\n"
    "Qobiliyatingiz haqida batafsil ma'lumotni /role orqali olishingiz mumkin."
)

NIGHT_START = (
    "🌙 *N-kecha ({night}) keldi!*\n\n"
    "Hamma ko'zlarini yumsin...\n"
    "Faol rollar o'z harakatlarini amalga oshiradi."
)

NIGHT_WAIT = "🌙 Kechani kuting... Harakatlar amalga oshirilmoqda."

NIGHT_ACTION_PROMPT = (
    "{role}\n\n"
    "Kechagi harakatingizni tanlang:\n"
    "{description}"
)

NIGHT_ACTION_CONFIRMED = "✅ Harakatingiz qabul qilindi!"

NIGHT_TIMEOUT = "⏰ Vaqt tugadi! Harakatsiz qoldingiz."

DAY_START = (
    "🌅 *TONG KELDI* — {night}-kecha tugadi\n\n"
    "{deaths}\n"
    "🗣 *Muhokama boshlandi!* Vaqt: 5 daqiqa\n\n"
    "O'yinchilar muhokama qilishlari mumkin."
)

DEATH_ANNOUNCEMENT = (
    "☠️ Kecha *{player}* halok bo'ldi!\n\n"
    "Uning roli: {role}\n\n"
    "💀 O'lim sababi: {reason}"
)

NO_DEATHS = "☀️ Bu kecha hech kim halok bo'lmadi. Tabib yaxshi ishlamoqda!"

VOTE_START = (
    "⚖️ *OVOZ BERISh VAQTI!*\n\n"
    "Kim chiqarilsin? O'yinchilardan birini tanlang:\n\n"
    "⏳ Vaqt: 60 soniya"
)

VOTE_RESULT = (
    "⚖️ *Ovoz berish natijalari:*\n\n"
    "{results}\n\n"
    "{elimination}"
)

VOTE_TIED = "🤝 Ovozlar teng! Hech kim chiqarilmadi."

PLAYER_ELIMINATED = (
    "🗡 *{player}* o'yindan chiqarildi!\n\n"
    "Uning roli: {role}\n\n"
    "{dramatic_text}"
)

NOT_ALIVE = "❌ Siz o'liksiz! Faqat tirik o'yinchilar qatnasha oladi."

NOT_YOUR_TURN = "❌ Hozir sizning navbatingiz emas."

ALREADY_VOTED = "❌ Siz allaqachon ovoz bergansiz!"

VOTE_CONFIRMED = "✅ Ovozigiz qabul qilindi!"

GAME_OVER_MAFIA = (
    "🏆 *O'yin tugadi!* 🦈 *Qora Kuchlar* g'alaba qozondi!\n\n"
    "Mafiya barcha fuqarolarni yo'q qildi!\n\n"
    "{stats}"
)

GAME_OVER_TOWN = (
    "🏆 *O'yin tugadi!* 🛡 *Oq Kuchlar* g'alaba qozondi!\n\n"
    "Fuqarolar barcha yovuz kuchlarni tozaladi!\n\n"
    "{stats}"
)

GAME_OVER_NEUTRAL = (
    "🏆 *O'yin tugadi!* 🌪 *Neytral kuch* g'alaba qozondi!\n\n"
    "{winner} o'z maqsadiga erishdi!\n\n"
    "{stats}"
)

ROLES_LIST_HEADER = "🎭 *Barcha rollar:*\n\n"

ROLE_INFO = "{emoji} *{title}* ({name})\n📖 {description}\n🏷 Tim: {team}\n\n"

PLAYER_LIST = "👥 O'yinchilar ro'yxati:\n{players}"

LEAVE_GAME = "🚪 Siz o'yindan chiqdingiz."

LEFT_GAME = "🚪 {player} o'yindan chiqdi."

NOT_IN_GAME = "❌ Siz o'yinda emassiz!"

GAME_ALREADY_STARTED = "❌ O'yin allaqachon boshlangan!"

ERROR_OCCURRED = "❌ Xatolik yuz berdi. Qaytadan urinib ko'ring."

ADMIN_ONLY = "❌ Faqat guruh adminlari bu amalni bajara oladi."

HELP_TEXT = (
    "🎮 *Mafiya o'yini - Yordam*\n\n"
    "📌 *Buyruqlar:*\n"
    "/start - Bosh menyu\n"
    "/profile - Profil\n"
    "/leave - O'yindan chiqish\n"
    "/language - Til tanlash\n\n"
    "📌 *Qoidalar:*\n"
    "• Kamida 6 o'yinchi kerak\n"
    "• Har bir o'yinchi maxsus rol oladi\n"
    "• Mafiya kechasi o'ldiradi\n"
    "• Fuqarolar kunduz ovoz beradi\n"
    "• G'alaba qozonish uchun maqsadingizga yetishing!"
)

FORCE_START = "👑 Admin majburiy start berdi! O'yin boshlanmoqda..."

GAME_STATS = (
    "📊 *O'yin statistikasi:*\n\n"
    "Rollar:\n{roles}\n\n"
    "Hodisalar:\n{events}\n\n"
    "Tirik o'yinchilar ({alive}):\n{alive_list}\n\n"
    "O'lganlar:\n{dead_list}"
)

CONFIRM_LEAVE = "🚪 O'yindan chiqishni xoxlaysizmi?"

LANGUAGE_PROMPT = "🌐 *Til tanlash:*\nHozircha faqat O'zbek tili mavjud."
