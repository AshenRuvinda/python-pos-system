from src.db_setup import init_db
from src.login import login_window

if __name__ == "__main__":
    init_db()
    login_window()
