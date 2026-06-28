from .base_role import Role, register_role

register_role(Role(
    name="detective",
    title="Neptun Soqchisi",
    emoji="🔱",
    team="town",
    description="Komissar. Har kecha bir o'yinchining rolini tekshiradi.",
    night_action=True,
    action_type="investigate",
    stars_cost=250,
))

register_role(Role(
    name="doctor",
    title="Qutqaruvchi Delfin",
    emoji="🐬",
    team="town",
    description="Doktor. Har kecha bir o'yinchini davolaydi (o'limdan saqlaydi).",
    night_action=True,
    action_type="heal",
    stars_cost=200,
))

register_role(Role(
    name="townsfolk",
    title="Dengizchi",
    emoji="⚓️",
    team="town",
    description="Oddiy fuqaro. Maxsus qobiliyati yo'q, faqat ovoz beradi.",
    passive=True,
    stars_cost=0,
))

register_role(Role(
    name="bodyguard",
    title="Marjon Qo'riqchisi",
    emoji="🛡",
    team="town",
    description="Serjant. Himoya qilgan o'yinchi o'rniga o'zi o'ladi.",
    night_action=True,
    action_type="guard",
    stars_cost=250,
))

register_role(Role(
    name="mayor",
    title="Donishmand Toshbaqa",
    emoji="🐢",
    team="town",
    description="Mer. Ovozi ikki hisoblanadi.",
    passive=True,
    stars_cost=300,
))

register_role(Role(
    name="priest",
    title="Dengiz Farishtasi",
    emoji="🕊",
    team="town",
    description="Ruhoniy. Bir o'yinchining tomonini ochib bera oladi.",
    night_action=True,
    action_type="reveal",
    max_uses=1,
    stars_cost=250,
))

register_role(Role(
    name="hooker",
    title="Suvparisi",
    emoji="🧜‍♀️",
    team="town",
    description="Fohisha. Kechagi harakatni bloklaydi.",
    night_action=True,
    action_type="block",
    stars_cost=200,
))

register_role(Role(
    name="journalist",
    title="Kema To'tiqushi",
    emoji="🦜",
    team="town",
    description="Jurnalist. Bir sirni e'lon qilish qobiliyatiga ega.",
    night_action=True,
    action_type="publish",
    max_uses=1,
    stars_cost=250,
))

register_role(Role(
    name="watcher",
    title="Dengiz Burguti",
    emoji="🦅",
    team="town",
    description="Kuzatuvchi. Kim kimga tashrif buyurganini ko'radi.",
    night_action=True,
    action_type="watch",
    stars_cost=250,
))

register_role(Role(
    name="jailer",
    title="Sodiq Qisqichbaqa",
    emoji="🦀",
    team="town",
    description="Qorovul. Bir o'yinchini qamab qo'yadi va himoyalaydi.",
    night_action=True,
    action_type="jail",
    stars_cost=300,
))

register_role(Role(
    name="hunter",
    title="G'avvos",
    emoji="🤿",
    team="town",
    description="Ovchi. O'lganda bir o'yinchini otib o'ldiradi.",
    passive=True,
    stars_cost=200,
))

register_role(Role(
    name="guard",
    title="Ko'k Kit",
    emoji="🐳",
    team="town",
    description="Gvardiyachi. Birinchi mafiya hujumiga chidamli.",
    passive=True,
    stars_cost=150,
))

register_role(Role(
    name="judge",
    title="Okean Qozisi",
    emoji="⚖️",
    team="town",
    description="Sudya. Bir ovozni bekor qilish qobiliyatiga ega.",
    night_action=False,
    action_type="cancel_vote",
    max_uses=1,
    stars_cost=350,
))

register_role(Role(
    name="prosecutor",
    title="Bolg'abosh Akula",
    emoji="🔨",
    team="town",
    description="Prokuror. Ovozsiz nomzodni sudga topshira oladi.",
    night_action=False,
    action_type="force_nominate",
    max_uses=1,
    stars_cost=350,
))

register_role(Role(
    name="investigator",
    title="Mayoqchi",
    emoji="🔍",
    team="town",
    description="Tekshiruvchi. Rol kategoriyasini aniqlaydi.",
    night_action=True,
    action_type="investigate_category",
    stars_cost=200,
))

register_role(Role(
    name="sponsor",
    title="Xazinabon",
    emoji="💰",
    team="town",
    description="Homiy. Bir o'yinchiga immunitet beradi.",
    night_action=True,
    action_type="grant_immunity",
    max_uses=1,
    stars_cost=300,
))

register_role(Role(
    name="veteran",
    title="Qaroqchilar Ovchisi",
    emoji="⚔️",
    team="town",
    description="Jangovar fuqaro. Hushyorlikka kirsa, tashrifchilarni o'ldiradi.",
    night_action=True,
    action_type="alert",
    max_uses=3,
    stars_cost=350,
))

register_role(Role(
    name="trapper",
    title="To'r Ustasi",
    emoji="🕸",
    team="town",
    description="Izolyatorchi. Bir o'yinchiga barcha tashriflarni bloklaydi.",
    night_action=True,
    action_type="trap",
    stars_cost=250,
))

register_role(Role(
    name="lifesaver",
    title="Hayot Qutqaruvchi",
    emoji="🛟",
    team="town",
    description="Qutqaruvchi. Ovoz berishdan chiqarilgan o'yinchini tiriltira oladi.",
    night_action=False,
    action_type="save",
    max_uses=1,
    stars_cost=350,
))

register_role(Role(
    name="lion",
    title="Dengiz Sheri",
    emoji="🦭",
    team="town",
    description="Kuchli fuqaro. Rol bloklashga immunitetli.",
    passive=True,
    stars_cost=150,
))

register_role(Role(
    name="twins",
    title="Egizak Baliqlar",
    emoji="🐟🐟",
    team="town",
    description="Egizaklar. Birga yutadi yoki yutqazadi, bir-birini taniydi.",
    passive=True,
    stars_cost=400,
))

register_role(Role(
    name="blacksmith",
    title="Langarsoz",
    emoji="⚓️",
    team="town",
    description="Temirchi. Bir o'yinchiga zirh beradi.",
    night_action=True,
    action_type="armor",
    max_uses=1,
    stars_cost=200,
))

register_role(Role(
    name="explorer",
    title="Kashfiyotchi",
    emoji="🗺",
    team="town",
    description="Sayyoh. O'yinchini kuzatib, uning nishonini ko'radi.",
    night_action=True,
    action_type="track",
    stars_cost=200,
))

register_role(Role(
    name="merchant",
    title="Savdo Kemasi",
    emoji="🛳",
    team="town",
    description="Savdogar. Ikki o'yinchining qobiliyatini almashtiradi.",
    night_action=True,
    action_type="trade",
    stars_cost=300,
))

register_role(Role(
    name="alchemist",
    title="Qadimiy Chig'anoq",
    emoji="🐚",
    team="town",
    description="Alkimyogar. Har kecha ikkisidan bir ikkirni yaratadi.",
    night_action=True,
    action_type="create_potion",
    stars_cost=250,
))
