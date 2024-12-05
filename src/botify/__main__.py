import typer
import warnings
from .main import run_app

app = typer.Typer(no_args_is_help=True)


@app.command()
def run() -> None:
    run_app()


def main() -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        run_app()


if __name__ == "__main__":
    main()
