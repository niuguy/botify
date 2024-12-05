from .app import create_app
from telegram import Update


def run_app() -> None:
    app = create_app()
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    run_app()
