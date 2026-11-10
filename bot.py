# Telegram-бот «Спроси студента / Зав. кафедрой» для кафедры ИСиТ
# Запуск: pip install python-telegram-bot==20.7 && python bot.py

import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

# ===== КОНФИГ =====
BOT_TOKEN = os.getenv("BOT_TOKEN")  # токен от @BotFather
CHAT_STUDENTS = int(os.getenv("CHAT_STUDENTS", "0"))      # ID группы/чата студентов-волонтёров
CHAT_TEACHERS = int(os.getenv("CHAT_TEACHERS", "0"))      # ID чата преподавателей/зав.каф.
CHAT_CAREER   = int(os.getenv("CHAT_CAREER", "0"))        # ID чата HR/карьеры/партнёров

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

# ===== КЛАВИАТУРЫ =====
MAIN_KB = InlineKeyboardMarkup([
    [InlineKeyboardButton("🎓 Спросить про учёбу", callback_data="cat_study")],
    [InlineKeyboardButton("💼 Спросить про трудоустройство", callback_data="cat_career")],
    [InlineKeyboardButton("🤖 Спросить про проекты / НИР", callback_data="cat_projects")],
    [InlineKeyboardButton("👔 Спросить у зав. кафедрой", callback_data="cat_head")],
])

BACK_KB = InlineKeyboardMarkup([
    [InlineKeyboardButton("⬅️ Назад в меню", callback_data="back_main")],
])

ANSWER_KB = lambda qid: InlineKeyboardMarkup([
    [InlineKeyboardButton("✅ Ответить", callback_data=f"ans_{qid}")],
    [InlineKeyboardButton("❌ Пропустить", callback_data=f"skip_{qid}")],
])

# ===== ХРАНИЛИЩЕ ВОПРОСОВ (в памяти, для простоты) =====
pending = {}  # qid -> {user_id, username, text, category, message_id_in_target_chat}

def fmt_q(q):
    return (
        f"❓ <b>Новый вопрос</b> #{q['id']}\n"
        f"👤 @{q['username'] or 'anon'} (id: {q['user_id']})\n"
        f"📂 Категория: {q['cat_label']}\n"
        f"💬 <i>{q['text']}</i>"
    )

# ===== ХЕНДЛЕРЫ =====
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я бот кафедры ИСиТ ВГТУ.\n"
        "Выбери тему — твой вопрос уйдёт нужным людям, они ответят прямо сюда.",
        reply_markup=MAIN_KB
    )

async def on_category(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    cat = q.data.split("_")[1]
    labels = {
        "study": ("🎓 Учёба", CHAT_STUDENTS),
        "career": ("💼 Трудоустройство", CHAT_CAREER),
        "projects": ("🤖 Проекты / НИР", CHAT_TEACHERS),
        "head": ("👔 Зав. кафедрой", CHAT_TEACHERS),
    }
    label, target = labels.get(cat, ("", 0))
    if not target:
        await q.edit_message_text("⚠️ Чат для этой категории не настроен. Обратись к админу.")
        return
    ctx.user_data["awaiting_question"] = True
    ctx.user_data["question_category"] = cat
    ctx.user_data["question_label"] = label
    ctx.user_data["question_target"] = target
    await q.edit_message_text(
        f"✍️ Напиши вопрос для <b>{label}</b>.\n"
        "Он анонимно уйдёт в чат ответственных.",
        parse_mode="HTML",
        reply_markup=BACK_KB
    )

async def on_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.user_data.get("awaiting_question"):
        return
    cat = ctx.user_data.pop("question_category")
    label = ctx.user_data.pop("question_label")
    target = ctx.user_data.pop("question_target")
    ctx.user_data.pop("awaiting_question", None)

    uid = update.effective_user.id
    uname = update.effective_user.username or f"id{uid}"
    text = update.message.text
    qid = f"{uid}_{update.message.message_id}"

    pending[qid] = {"id": qid, "user_id": uid, "username": uname, "text": text,
                    "category": cat, "cat_label": label}

    try:
        sent = await ctx.bot.send_message(
            target,
            fmt_q(pending[qid]),
            parse_mode="HTML",
            reply_markup=ANSWER_KB(qid)
        )
        pending[qid]["target_msg_id"] = sent.message_id
        await update.message.reply_text("✅ Вопрос отправлен! Ответ придёт сюда.", reply_markup=MAIN_KB)
    except Exception as e:
        log.error(f"Send to target failed: {e}")
        await update.message.reply_text("⚠️ Не удалось доставить. Попробуй позже.", reply_markup=MAIN_KB)

async def on_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data

    if data == "back_main":
        await q.edit_message_text("Главное меню:", reply_markup=MAIN_KB)
        return

    if data.startswith("ans_"):
        qid = data[4:]
        p = pending.get(qid)
        if not p:
            await q.edit_message_text("❓ Вопрос не найден (уже отвечен или устарел).")
            return
        ctx.user_data["answering"] = qid
        await q.edit_message_text(
            f"✍️ Напиши ответ для @{p['username'] or 'anon'}:\n<i>{p['text']}</i>",
            parse_mode="HTML",
            reply_markup=BACK_KB
        )
        return

    if data.startswith("skip_"):
        qid = data[5:]
        p = pending.pop(qid, None)
        if p:
            try:
                await ctx.bot.send_message(p["user_id"], "😔 К сожалению, на твой вопрос никто не ответил. Попробуй переформулировать или задать позже.", reply_markup=MAIN_KB)
            except: pass
        await q.edit_message_text("⏭ Пропущено.")
        return

async def on_answer_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    qid = ctx.user_data.pop("answering", None)
    if not qid:
        return
    p = pending.pop(qid, None)
    if not p:
        await update.message.reply_text("❓ Вопрос уже обработан.")
        return
    answer = update.message.text
    try:
        await ctx.bot.send_message(p["user_id"], f"💬 <b>Ответ на твой вопрос:</b>\n\n{answer}", parse_mode="HTML", reply_markup=MAIN_KB)
        await update.message.reply_text("✅ Ответ доставлен абитуриенту.")
    except Exception as e:
        log.error(f"Answer send failed: {e}")
        await update.message.reply_text("⚠️ Не удалось доставить ответ.")

async def help_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Бот кафедры ИСиТ\n"
        "/start — главное меню\n"
        "/help — это сообщение\n\n"
        "Абитуриент задаёт вопрос → уходит в чат ответственных → ответ возвращается ему."
    )

# ===== MAIN =====
def main():
    if not BOT_TOKEN:
        raise RuntimeError("Set BOT_TOKEN env var")
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CallbackQueryHandler(on_category, pattern=r"^cat_"))
    app.add_handler(CallbackQueryHandler(on_callback, pattern=r"^(ans_|skip_|back_)"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))       # вопросы
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_answer_text)) # ответы (после ans_)

    log.info("Bot started")
    app.run_polling()

if __name__ == "__main__":
    main()