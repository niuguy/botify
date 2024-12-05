import typer
import warnings
app = typer.Typer(no_args_is_help=True)

@app.command()
def run() -> None:
    print("Hello, World!")

def main() -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        app()


if __name__=="__main__":
    import uvicorn 
    

    