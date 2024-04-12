import asyncpg

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ContentType, LabeledPrice, PreCheckoutQuery

from tgbot.loader import db
from tgbot.keyboards.reply import builder

user_router = Router()

prices = LabeledPrice(amount=150000, label="price label")

@user_router.message(CommandStart())
async def user_start(message: Message):
    print(len(message.text.split(" ")))
    print(message.text)
    if len(message.text.split(" ")) > 1:

        await message.answer_invoice(title="Title for invoice", description="Description for invoice",
                                 payload="payload", provider_token="398062629:TEST:999999999_F91D8F69C042267444B74CC0B3C747757EB0E065",
                                 currency='UZS', prices=[prices],
                                 start_parameter="order_id")
    else:
        await message.answer("Assalomu alaykum Numi store internet do'konining rasmiy botiga xush kelibsiz !")
    # try:
    #     await db.add_user(telegram_id=message.from_user.id,
    #                              full_name=message.from_user.full_name,
    #                              username=message.from_user.username)
    # except asyncpg.exceptions.UniqueViolationError:
    #     await db.select_user(telegram_id=message.from_user.id)
    
    # await message.answer_photo("https://telegra.ph/file/9d19f625ff5734cedbb17.jpg",
    #     caption="Xush kelibsiz! Konkurs ishtirok etish uchun <code>Konkursda qatnashish</code> tugmasini bosing",
    #     reply_markup=builder.as_markup(resize_keyboard=True))
    
    # await message.answer("Xush kelibsiz! Konkurs ishtirok etish uchun <code>Konkursda qatnashish</code> tugmasini bosing",
    #                      reply_markup=builder.as_markup(resize_keyboard=True))
    


@user_router.pre_checkout_query(lambda query: True)
async def pre_checkout_query(query: PreCheckoutQuery):
    await query.answer(ok=True)


@user_router.message(F.content_type==ContentType.SUCCESSFUL_PAYMENT)
async def successfull_payment(message: Message):
    await message.answer("To'lov muvaffaqiyatli amalga oshirildi. Buyurtmangizni 2 ish kunida yetkazamiz. Buyurtma holatini bilish uchun admin bilan bog'lamishingiz mumkin")


@user_router.message(Command("help"))
async def admin_help(message: Message):
    text = ("Buyruqlar: ",
            "/start - Botni ishga tushirish",
            "/help - Yordam",
           )

    return await message.answer(text="\n".join(text))
