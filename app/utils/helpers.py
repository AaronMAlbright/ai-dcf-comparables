from rich import print

def print_check(msg):
    print(f"[green]✅ {msg}[/green]")

def print_warning(msg):
    print(f"[yellow]⚠️ {msg}[/yellow]")

def print_error(msg):
    print(f"[red]❌ {msg}[/red]")

def validate_vector(vector):
    """
    Validates that the given vector is a non-empty list or tensor of floats.
    """
    if vector is None:
        return False
    if isinstance(vector, list) and all(isinstance(x, (int, float)) for x in vector):
        return True
    try:
        import torch
        if isinstance(vector, torch.Tensor) and vector.numel() > 0:
            return True
    except ImportError:
        pass
    return False
