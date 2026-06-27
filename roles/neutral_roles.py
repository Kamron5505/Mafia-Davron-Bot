from .base_role import Role, register_role

register_role(Role(
    name="lovers",
    title="Marvarid Jufti",
    emoji="🐚",
    team="neutral",
    description="Oshiqlar. Ikkalasi birga yutsa yoki yutqazsa.",
    passive=True,
))

register_role(Role(
    name="serial_killer",
    title="Dengiz Bo'roni",
    emoji="🌪",
    team="neutral",
    description="Manyak. Hammani yo'q qilib, yolg'iz yutsa.",
    night_action=True,
    action_type="kill",
))

register_role(Role(
    name="joker",
    title="Ayyor Oktopus",
    emoji="🐙",
    team="neutral",
    description="Joker. Ovoz berish orqali chiqarilib yutsa.",
    passive=True,
))

register_role(Role(
    name="avenger",
    title="Suvosti Vulqoni",
    emoji="🌋",
    team="neutral",
    description="Qasoskor. Uni o'ldirgan o'yinchi chiqarilsa yutsa.",
    passive=True,
))

register_role(Role(
    name="fool",
    title="Girdob",
    emoji="🌀",
    team="neutral",
    description="Telba. Tashriflarni tasodifiy boshqa joyga yo'naltiradi.",
    passive=True,
))

register_role(Role(
    name="ghost",
    title="Cho'kkan Kema Ruhi",
    emoji="👻",
    team="neutral",
    description="Arvoh. O'lgandan keyin ham ovoz bera oladi.",
    passive=True,
))

register_role(Role(
    name="cursed",
    title="Muzlagan Dengizchi",
    emoji="🧟‍♂️",
    team="neutral",
    description="La'natlangan. Mafiya tomonidan o'ldirilsa, mafiyaga aylanadi.",
    passive=True,
))

register_role(Role(
    name="executioner",
    title="Xarpunchi",
    emoji="🪓",
    team="neutral",
    description="Jallod. Belgilangan nishonni chiqarib yutsa.",
    passive=True,
))

register_role(Role(
    name="cultist",
    title="Bermud Asiri",
    emoji="🧿",
    team="neutral",
    description="Sektant. O'yinchilarni sektaga qo'shilishga targ'ib qiladi.",
    night_action=True,
    action_type="recruit",
))

register_role(Role(
    name="arsonist",
    title="Yunon Olovi",
    emoji="🔥",
    team="neutral",
    description="Piroman. O'yinchilarni yoqib, keyin hammasini birdaniga yondiradi.",
    night_action=True,
    action_type="douse",
))

register_role(Role(
    name="vampire",
    title="Suvosti Ko'rshapalagi",
    emoji="🦇",
    team="neutral",
    description="Vampir. Har kecha bir o'yinchini o'z tomoniga og'diradi.",
    night_action=True,
    action_type="convert",
))

register_role(Role(
    name="infector",
    title="Zaharli Suvo'ti",
    emoji="🟢",
    team="neutral",
    description="Infektsiya tashuvchi. 2 kechadan keyin o'ldiradigan infektsiya yuqtiradi.",
    night_action=True,
    action_type="infect",
))

register_role(Role(
    name="kraken",
    title="Kraken",
    emoji="🐙",
    team="neutral",
    description="Iblis. Kuchli yolg'iz o'ldiruvchi, maksus immunitetga ega.",
    night_action=True,
    action_type="kill",
))

register_role(Role(
    name="gambler",
    title="Dengiz Qimorbozi",
    emoji="🎲",
    team="neutral",
    description="Qimorboz. Natijalarga garov tikadi va kuchaytirish oladi.",
    passive=True,
))

register_role(Role(
    name="illusionist",
    title="Sarob",
    emoji="🪞",
    team="neutral",
    description="Illyuziyachi. O'yinchilarni boshqa rol qilib ko'rsatadi.",
    night_action=True,
    action_type="illusion",
))
