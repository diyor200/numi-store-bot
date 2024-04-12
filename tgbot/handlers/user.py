import logging
import os

import asyncpg

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ContentType, LabeledPrice, PreCheckoutQuery

from tgbot.loader import db

user_router = Router()
admins = os.environ.get("ADMINS")


async def create_amount_prices_by_cart_id(card_id):
    price = []
    query = await db.get_cart_products_by_cart_id(card_id)
    for i in query:
        amount = i[0] * i[2] * 10 * 100
        price.append(LabeledPrice(label=i[1], amount=amount))
    return price


@user_router.message(CommandStart())
async def user_start(message: Message, state: FSMContext):
    try:
        await db.add_user(telegram_id=message.from_user.id,
                          full_name=message.from_user.full_name,
                          username=message.from_user.username)
    except asyncpg.exceptions.UniqueViolationError:
        pass
    except:
        await message.bot.send_message(chat_id=admins, text="problem with db")
        await message.answer("an error occurred")
        return

    message_list = message.text.split(" ")
    if len(message_list) > 1:
        try:
            cart_id = int(message_list[1])
            prices = await create_amount_prices_by_cart_id(cart_id)
            await message.answer_invoice(title="Title for invoice", description="Description for invoice",
                                         payload="payload", provider_token="398062629:TEST:999999999_F91D8F69C042267444B74CC0B3C747757EB0E065",
                                         currency='UZS', prices=prices,
                                         start_parameter="order_id1")
            await state.update_data({
                f"{message.from_user.id}": cart_id
            })
        except Exception as ex:
            logging.error("error while payment. Payment id: ", message_list[1])
            await message.bot.send_message(chat_id=admins, text=f"to'lov qilishda muammo yuzaga keldi"
            f"\nUsername: {message.from_user.username}\nCart id: {message_list[1]}")
            await message.answer("To'lovni amalga oshirishda muammo yuzaga keldi. Iltimos admin bilan bog'laning")
    else:
        await message.answer("Assalomu alaykum Numi store internet do'konining rasmiy botiga xush kelibsiz !")


@user_router.pre_checkout_query(lambda query: True)
async def pre_checkout_query(query: PreCheckoutQuery):
    await query.answer(ok=True)


@user_router.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def successfully_payment(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    cart_id = data[f"{message.from_user.id}"]

    try:
        await db.change_cart_status(int(cart_id))
        await message.answer("To'lov muvaffaqiyatli amalga oshirildi."
                             " Buyurtmangizni 2 ish kunida yetkazamiz. Buyurtma holatini bilish uchun admin"
                             " bilan bog'lamishingiz mumkin")
    except:
        await message.answer("an error occurred")
        await message.bot.send_message(chat_id=admins, text=f"to'lov qilishda muammo yuzaga keldi"
f"\nUsername: {message.from_user.username}\nCart id: {cart_id}")


@user_router.message(Command("help"))
async def admin_help(message: Message):
    text = ("Buyruqlar: ",
            "/start - Botni ishga tushirish",
            "/help - Yordam",
           )

    return await message.answer(text="\n".join(text))
