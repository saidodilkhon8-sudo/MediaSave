import io
import csv
from datetime import datetime, timezone, timedelta
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile
from sqlalchemy import select, func, and_
from mediasave.app.config import settings
from mediasave.app.database.database import get_session
from mediasave.app.database.models import User, Download, DownloadStatus, Platform
from mediasave.app.services.cache_service import CacheService
from mediasave.app.i18n import get_text
from mediasave.app.bot.utils import get_user_language

router = Router()
cache_service = CacheService()


def _is_admin(user_id: int) -> bool:
    """Проверить, является ли пользователь админом"""
    return user_id in settings.admin_ids_list


def _keyboard(page: str = "main", lang: str = "ru") -> InlineKeyboardMarkup:
    """Меню админ-панели"""
    if page == "main":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(lang, "admin_view_stats"), callback_data="admin:stats")],
            [InlineKeyboardButton(text=get_text(lang, "admin_view_platforms"), callback_data="admin:platforms")],
            [InlineKeyboardButton(text=get_text(lang, "admin_view_users"), callback_data="admin:users")],
            [InlineKeyboardButton(text=get_text(lang, "admin_view_errors"), callback_data="admin:errors")],
            [InlineKeyboardButton(text=get_text(lang, "admin_cleanup"), callback_data="admin:cleanup")],
        ])
    elif page == "export":
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📄 CSV", callback_data="admin:export:csv")],
            [InlineKeyboardButton(text="📊 JSON", callback_data="admin:export:json")],
            [InlineKeyboardButton(text=get_text(lang, "back"), callback_data="admin:back")],
        ])
    else:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text(lang, "back"), callback_data="admin:back")],
        ])


async def _get_full_stats() -> dict:
    """Получить полную статистику"""
    async with get_session() as session:
        users = await session.scalar(select(func.count(User.id))) or 0
        downloads = await session.scalar(select(func.count(Download.id))) or 0
        completed = await session.scalar(
            select(func.count(Download.id)).where(Download.status == DownloadStatus.COMPLETED)
        ) or 0
        failed = await session.scalar(
            select(func.count(Download.id)).where(Download.status == DownloadStatus.FAILED)
        ) or 0
        processing = await session.scalar(
            select(func.count(Download.id)).where(Download.status == DownloadStatus.PROCESSING)
        ) or 0
        
        # Статистика по платформам
        platform_stats = {}
        for platform in Platform:
            count = await session.scalar(
                select(func.count(Download.id)).where(Download.platform == platform)
            ) or 0
            if count > 0:
                platform_stats[platform.value] = count
        
        # Размер загруженного контента
        total_size = await session.scalar(
            select(func.sum(Download.file_size))
        ) or 0
        
        # Активные пользователи (загружали в последний день)
        cutoff = datetime.now(timezone.utc) - timedelta(days=1)
        active_users = await session.scalar(
            select(func.count(User.id)).where(User.last_seen >= cutoff)
        ) or users
        
    return {
        "users": users,
        "active_users": active_users,
        "downloads": downloads,
        "completed": completed,
        "failed": failed,
        "processing": processing,
        "total_size_mb": total_size / 1024 / 1024,
        "platform_stats": platform_stats,
        "cache_size_mb": cache_service.get_cache_size() / 1024 / 1024
    }


async def _format_stats_text(stats: dict) -> str:
    """Форматировать статистику для вывода"""
    return (
        "📊 <b>MediaSave - Полная Статистика</b>\n\n"
        f"👥 <b>Пользователи:</b>\n"
        f"  • Всего: {stats['users']}\n"
        f"  • Активных: {stats['active_users']}\n\n"
        f"⬇️ <b>Загрузки:</b>\n"
        f"  • Всего: {stats['downloads']}\n"
        f"  • ✅ Успешно: {stats['completed']}\n"
        f"  • ⚙️ В процессе: {stats['processing']}\n"
        f"  • ❌ Ошибок: {stats['failed']}\n\n"
        f"💾 <b>Данные:</b>\n"
        f"  • Общий размер: {stats['total_size_mb']:.2f} MB\n"
        f"  • Кэш: {stats['cache_size_mb']:.2f} MB\n\n"
        f"🌐 <b>По платформам:</b>\n" +
        "\n".join([f"  • {p}: {c}" for p, c in sorted(stats['platform_stats'].items())]) +
        "\n"
    )


async def _export_to_csv() -> bytes:
    """Экспортировать статистику в CSV"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    async with get_session() as session:
        downloads = await session.execute(
            select(Download).order_by(Download.created_at.desc())
        )
        rows = downloads.scalars().all()
        
        writer.writerow([
            "ID", "User ID", "Platform", "Media Type", "Status", 
            "Title", "File Size (MB)", "Created", "Updated"
        ])
        
        for row in rows:
            writer.writerow([
                row.id,
                row.user_id,
                row.platform.value if row.platform else "",
                row.media_type.value if row.media_type else "",
                row.status.value if row.status else "",
                row.title or "",
                f"{row.file_size / 1024 / 1024:.2f}" if row.file_size else "0",
                row.created_at.strftime("%Y-%m-%d %H:%M"),
                row.updated_at.strftime("%Y-%m-%d %H:%M"),
            ])
    
    return output.getvalue().encode()


async def _stats_text() -> str:
    """Быстрая статистика для начального меню"""
    stats = await _get_full_stats()
    return (
        "📊 <b>MediaSave</b>\n\n"
        f"👥 Пользователей: {stats['users']}\n"
        f"⬇️ Загрузок: {stats['downloads']}\n"
        f"✅ Успешно: {stats['completed']}\n"
        f"❌ Ошибок: {stats['failed']}"
    )


@router.message(F.text == "/admin")
async def admin_menu(message: Message):
    """Начальное меню админа"""
    if not _is_admin(message.from_user.id):
        lang = await get_user_language(message)
        await message.answer(f"❌ {get_text(lang, 'access_denied')}" if "access_denied" in get_text("ru", "admin_panel") else "❌ Доступ запрещен")
        return
    
    lang = await get_user_language(message)
    text = await _stats_text()
    await message.answer(text, reply_markup=_keyboard("main", lang), parse_mode="HTML")


@router.callback_query(F.data == "admin:back")
async def admin_back(callback: CallbackQuery):
    """Вернуться в главное меню"""
    if not _is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    lang = await get_user_language(callback.message)
    text = await _stats_text()
    await callback.message.edit_text(text, reply_markup=_keyboard("main", lang), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "admin:stats")
async def admin_stats(callback: CallbackQuery):
    """Полная статистика"""
    if not _is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    lang = await get_user_language(callback.message)
    stats = await _get_full_stats()
    text = await _format_stats_text(stats)
    await callback.message.edit_text(text, reply_markup=_keyboard("stats", lang), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "admin:users")
async def admin_users(callback: CallbackQuery):
    """Статистика пользователей"""
    if not _is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    lang = await get_user_language(callback.message)
    async with get_session() as session:
        total = await session.scalar(select(func.count(User.id))) or 0
        today = await session.scalar(
            select(func.count(User.id)).where(
                User.created_at >= datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            )
        ) or 0
    
    text = f"👥 <b>{get_text(lang, 'admin_view_users')}</b>\n\n• {get_text(lang, 'admin_total_users')}: {total}\n• Сегодня: {today}"
    await callback.message.edit_text(text, reply_markup=_keyboard("stats", lang), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "admin:downloads")
async def admin_downloads(callback: CallbackQuery):
    """Статистика загрузок"""
    if not _is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    lang = await get_user_language(callback.message)
    async with get_session() as session:
        total = await session.scalar(select(func.count(Download.id))) or 0
        completed = await session.scalar(
            select(func.count(Download.id)).where(Download.status == DownloadStatus.COMPLETED)
        ) or 0
    
    text = f"⬇️ <b>{get_text(lang, 'admin_total_downloads')}</b>\n\n• Всего: {total}\n• ✅ {get_text(lang, 'admin_success_rate')}: {(completed/total*100 if total else 0):.1f}%"
    await callback.message.edit_text(text, reply_markup=_keyboard("stats", lang), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "admin:errors")
async def admin_errors(callback: CallbackQuery):
    """Статистика ошибок"""
    if not _is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    lang = await get_user_language(callback.message)
    async with get_session() as session:
        errors = await session.scalar(
            select(func.count(Download.id)).where(Download.status == DownloadStatus.FAILED)
        ) or 0
    
    text = f"❌ <b>{get_text(lang, 'admin_view_errors')}</b>\n\n• {get_text(lang, 'admin_total_errors')}: {errors}"
    await callback.message.edit_text(text, reply_markup=_keyboard("stats", lang), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "admin:platforms")
async def admin_platforms(callback: CallbackQuery):
    """Статистика по платформам"""
    if not _is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    lang = await get_user_language(callback.message)
    stats = await _get_full_stats()
    text = f"🌍 <b>{get_text(lang, 'admin_view_platforms')}</b>\n\n"
    for platform, count in sorted(stats["platform_stats"].items(), key=lambda x: x[1], reverse=True):
        text += f"• {platform}: {count}\n"
    
    await callback.message.edit_text(text, reply_markup=_keyboard("stats", lang), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "admin:cache")
async def admin_cache(callback: CallbackQuery):
    """Управление кэшем"""
    if not _is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    lang = await get_user_language(callback.message)
    cache_size = cache_service.get_cache_size() / 1024 / 1024
    text = f"💿 <b>{get_text(lang, 'admin_cache_size')}</b>\n\n• {get_text(lang, 'admin_cache_size')}: {cache_size:.2f} MB"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(lang, "admin_cleanup"), callback_data="admin:cache:clear")],
        [InlineKeyboardButton(text=get_text(lang, "back"), callback_data="admin:back")],
    ])
    
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "admin:cache:clear")
async def admin_cache_clear(callback: CallbackQuery):
    """Очистить кэш"""
    if not _is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    lang = await get_user_language(callback.message)
    cleared = cache_service.clear_all_cache()
    await callback.answer(get_text(lang, "admin_cleanup_done").format(count=cleared), show_alert=True)
    await admin_cache(callback)


@router.callback_query(F.data == "admin:export")
async def admin_export(callback: CallbackQuery):
    """Меню экспорта"""
    if not _is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    text = "📥 <b>Экспорт данных</b>\n\nВыберите формат:"
    await callback.message.edit_text(text, reply_markup=_keyboard("export"), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "admin:export:csv")
async def admin_export_csv(callback: CallbackQuery):
    """Экспортировать в CSV"""
    if not _is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    await callback.answer("⏳ Готовлю CSV...", show_alert=False)
    
    csv_data = await _export_to_csv()
    file = BufferedInputFile(csv_data, filename=f"mediasave_export_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv")
    await callback.message.answer_document(file, caption="📄 Экспорт загрузок в CSV")
    
    await admin_export(callback)
