from rich import print

def print_check(msg):
    print(f"[green]✅ {msg}[/green]")

def print_warning(msg):
    print(f"[yellow]⚠️ {msg}[/yellow]")

def print_error(msg):
    print(f"[red]❌ {msg}[/red]")
