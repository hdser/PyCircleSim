from pathlib import Path
import panel as pn
from .database_explorer import DatabaseExplorer

def find_repo_root():
    """Find the repository root by looking for setup.py file."""
    current_dir = Path(__file__).parent.parent  # Start from app's parent directory
    while current_dir.parent != current_dir:
        if (current_dir / "setup.py").exists():
            return current_dir
        current_dir = current_dir.parent
    raise FileNotFoundError("Could not find repository root (no setup.py found)")

def main():
    """Initialize and launch the database explorer application."""
    # Get the root directory and construct database path
    repo_root = find_repo_root()
    db_path = repo_root / "simulation.duckdb"
    
    if not db_path.exists():
        raise FileNotFoundError(
            f"Database not found at {db_path}. "
            "Please ensure the simulation has been run first."
        )
    
    print(f"Using database at: {db_path}")
    
    # Create and launch the application
    app = DatabaseExplorer(str(db_path))
    return pn.serve(app.show())

if __name__ == "__main__":
    main()