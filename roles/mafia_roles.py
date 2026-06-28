from .base_role import Role, register_role

register_role(Role(
    name="don",
    title="Okean Qiroli",
    emoji="👑",
    team="mafia",
    description="Mafiya rahbari. Ovoz berishni boshqarish qobiliyatiga ega.",
    night_action=True,
    action_type="redirect_vote",
    stars_cost=500,
))

register_role(Role(
    name="mafia",
    title="Akula",
    emoji="🦈",
    team="mafia",
    description="Oddiy mafiya. Har kecha bir fuqaroni o'ldiradi.",
    night_action=True,
    action_type="kill",
    stars_cost=0,
))

register_role(Role(
    name="yakuza",
    title="Qaroqchilar Sardori",
    emoji="🏴‍☠️",
    team="mafia",
    description="Bir fuqaroni o'z tomoniga og'dira oladi.",
    night_action=True,
    action_type="convert",
    max_uses=1,
    stars_cost=300,
))

register_role(Role(
    name="fugu",
    title="Zaharli Fugu",
    emoji="🐡",
    team="mafia",
    description="Mafiya yordamchisi. Bir o'yinchini kechasi bloklaydi.",
    night_action=True,
    action_type="block",
    stars_cost=150,
))

register_role(Role(
    name="squid",
    title="Gigant Kalmar",
    emoji="🦑",
    team="mafia",
    description="Qora qaroqchi. Rol haqidagi ma'lumotni o'g'irlaydi.",
    night_action=True,
    action_type="steal_info",
    stars_cost=200,
))

register_role(Role(
    name="crab_thief",
    title="Qisqichbaqa-o'g'ri",
    emoji="🦀",
    team="mafia",
    description="O'g'ri. Boshqa rolning qobiliyatini o'g'irlaydi.",
    night_action=True,
    action_type="steal_ability",
    stars_cost=250,
))

register_role(Role(
    name="jellyfish",
    title="Ch aquvchi Meduza",
    emoji="🪼",
    team="mafia",
    description="Shantajchi. Bir o'yinchini kunduz sukut qilishga majburlaydi.",
    night_action=True,
    action_type="silence",
    stars_cost=200,
))

register_role(Role(
    name="crocodile",
    title="Sho'r suv Timsohi",
    emoji="🐊",
    team="mafia",
    description="Advokat. Mafiya a'zosini ovoz berishdan himoya qiladi.",
    night_action=True,
    action_type="protect_vote",
    stars_cost=200,
))

register_role(Role(
    name="swordfish",
    title="Qilichbaliq",
    emoji="🗡",
    team="mafia",
    description="Qotil. Kunduz o'ldirish qobiliyatiga ega.",
    night_action=False,
    action_type="day_kill",
    stars_cost=350,
))

register_role(Role(
    name="chameleon",
    title="Xameleon Baliq",
    emoji="🐠",
    team="mafia",
    description="Josus. Tekshiruvchiga fuqaro bo'lib ko'rinadi.",
    passive=True,
    stars_cost=180,
))

register_role(Role(
    name="killer_whale",
    title="Qotil Kit",
    emoji="🐋",
    team="mafia",
    description="Reketir. O'yinchini majburan birovga ovoz berishga majburlaydi.",
    night_action=True,
    action_type="force_vote",
    stars_cost=250,
))

register_role(Role(
    name="abyss",
    title="Dengiz Tubsizi",
    emoji="🕳",
    team="mafia",
    description="Ko'lanka. Kechki tekshiruvlarga ko'rinmaydi.",
    passive=True,
    stars_cost=150,
))

register_role(Role(
    name="mine_fish",
    title="Mina-baliq",
    emoji="💣",
    team="mafia",
    description="Bombachi. Chiqarilsa, yonidagini portlatadi.",
    passive=True,
    stars_cost=250,
))

register_role(Role(
    name="stingray",
    title="Zilzilaviy Skat",
    emoji="🧪",
    team="mafia",
    description="Zaharlovchi. O'yinchini zaharlaydi, keyingi kecha o'ladi.",
    night_action=True,
    action_type="poison",
    stars_cost=300,
))

register_role(Role(
    name="scorpion",
    title="Dengiz Chayoni",
    emoji="🦂",
    team="mafia",
    description="Yollanma qotil. Bir nishonni o'ldirish topshirig'ini oladi.",
    night_action=True,
    action_type="contract_kill",
    max_uses=1,
    stars_cost=350,
))

register_role(Role(
    name="rat",
    title="Kema Kalamushi",
    emoji="🐀",
    team="mafia",
    description="Sotqin. Fuqaro bo'lib ko'rinadi, lekin mafiya uchun ishlaydi.",
    passive=True,
    stars_cost=200,
))

register_role(Role(
    name="necromancer",
    title="O'lik Dengizchi",
    emoji="🦴",
    team="mafia",
    description="Nekromant. O'lgan o'yinchining qobiliyatini bir marta ishlatadi.",
    night_action=True,
    action_type="necromancy",
    max_uses=1,
    stars_cost=400,
))

register_role(Role(
    name="sea_snake",
    title="Dengiz Iloni",
    emoji="🐍",
    team="mafia",
    description="Yovuz jodugar. Ikki o'yinchining rolini almashtiradi.",
    night_action=True,
    action_type="swap_roles",
    stars_cost=350,
))

register_role(Role(
    name="piranha",
    title="Piranya",
    emoji="🩸",
    team="mafia",
    description="Odamxo'r. Har o'ldirishda kuchayadi (qo'shimcha ovoz vazni).",
    passive=True,
    stars_cost=300,
))

register_role(Role(
    name="corrupt_water",
    title="Ifloslangan Suv",
    emoji="🦠",
    team="mafia",
    description="Qora tabib. Mafiyani davolaydi, fuqaroni zaharlaydi.",
    night_action=True,
    action_type="corrupt_heal",
    stars_cost=300,
))
