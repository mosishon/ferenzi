from bot.constants import (MINIMUM_CHAR_LIMIT, SUPER_SUDO_USERNAME)

# start texts
START_ADMIN = "سلام ادمین عزیز خوش آمدید"
START_USER = (" سلام کاربر عزیز. این ربات صراف جهت مدیریت گروه طب سنتی میباشد"
            "برای دریافت اطلاعات بیشتر با سودو در ارتباط باشید  ")
START_ADMIN_GROUP = "این دستور مختص سودوی ربات میباشد"
START_SUDO_GROUP  = "دستور از سمت سودوی ربات دریافت شد.\n ربات بزودی در گروه شما فعال خواهد شد"

# install/uninstall texts
BOT_ALREADY_INSTALLED = ("ربات در گروه شما فعال شده است\n"
                        "نیاز به نصب مجدد ربات نیست")
BOT_INSTALLED_SUCCESSFULLY = "ربات با موفقیت نصب شد"
BOT_UNINSTALLED_SUCCESSFULLY = "ربات با موفقیت حذف شد"
BOT_ISNOT_INSTALLED = "ربات در گروه شما فعال نیست"
I_LEAVE_GROUP = "این گروه از لیست گروه های نصب شده خارج شد.\nربات ها به زودی از گروه خارج میشوند"
MAKE_ME_ADMIN = "لطفا ابتدا برای اجرای تمامی دستورات  من را به ادمین گروه (تیک افزودن ادمین نیاز میباشد) ارتقا دهید"
IM_HERE_TO_HELP = "سلام.\nمن ربات دو قلو و کمکی فرنزی هستم." #TODO: bot name should be dynamic

# configure group texts
CONFIGURE_ADMINS = "آیا مایل به پیکربندی ربات و تنظیمات آن هستید؟\n ادمین ها شناسایی و به ادمین های ربات افزوده میشوند"
ADMINS_CONFIGURED = ("تعداد {} ادمین شناسایی و با موفقیت به ادمین های ربات افزوده شد") # param1: number of admins
# errors texts
UNKNOWN_ERROR_OCURRED = "خطای ناشناخته رخ داده است"
THIS_COMMAND_IS_NOT_AVAILABLE_FOR_YOU = "این دستور برای شما در دسترس نمیباشد"

# names texts
BOT_CLI_TITLE = "Ferenzi Cli"

#panel
    #texts
PANEL_TEXT = "پنل مدیریتی"
    # options
PANEL_TEXTS_TO_OPEN = ("/panel","پنل","panel")

#clear
CLEAR_ALL = ("پاکسازی کلی","پاکسازی کل")
CLEARING_STARTED = "فرآیند پاکسازی پیام ها شروع شد"
CLEATING_FINISHED = "پاکسازی پیام ها به پایان رسید"

#char limit
CHAT_LIMIT_PANEL = "پنل مدیریت محدودیت کارکتر"
ENTER_CHAR_LIMIT = "لطفا تعداد کاراکتر های مورد نیاز را وارد کنید"
SHOULD_BE_NUMBER = "تعداد کاراکتر ها باید عدد باشد"
SHOULD_BE_GREATER_THAN_MINIMUM_CHAR_LIMIT = "تعداد کاراکتر ها باید بزرگتر از {} باشد".format(MINIMUM_CHAR_LIMIT)
SUCCESFUL_CHAR_LIMIT_SET = "تعداد کاراکتر ها با موفقیت تنظیم شد"

# configure admins
CONFIGURE_ADMINS = ("پیکربندی","پیکربندی مدیران")