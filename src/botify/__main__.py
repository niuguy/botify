import typer
import warnings
import asyncio
from .main import main as async_main

app = typer.Typer(no_args_is_help=True)


@app.command()
def run(
    api: bool = typer.Option(False, help="Start the API server alongside the bot"),
) -> None:
    """Run both the Telegram bot and FastAPI server"""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        asyncio.run(async_main(start_api=api))


def main() -> None:
    """Entry point for the application"""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        asyncio.run(async_main(start_api=True))


if __name__ == "__main__":
    main()
