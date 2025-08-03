from rich import print
import numpy as np

def print_check(msg):
    print(f"[green]✅ {msg}[/green]")

def print_warning(msg):
    print(f"[yellow]⚠️ {msg}[/yellow]")

def print_error(msg):
    print(f"[red]❌ {msg}[/red]")

def validate_vector(vector):
    if vector is None:
        return False
    vector = np.array(vector)
    return vector.ndim == 1 and vector.dtype.kind in {'f'} and not np.any(np.isnan(vector))




if __name__ == "__main__":
    print(validate_vector([0.0, 0.0, 0.0]))   # ❌ Expect False
    print(validate_vector([0.01, -0.02, 0.0])) # ✅ Expect True



