# """
# Run once to create all tables:

#     python -m app.db.init_db

# Normally main.py also calls Base.metadata.create_all() on startup, so this
# isn't strictly required to get the app running -- but it's useful when you
# want to set up or reset the schema without booting the full API (e.g. in a
# fresh environment, or after wiping a local sqlite file).
# """
# from app.db.database import engine, Base
# from app.db import models  # noqa: F401  (import so models register on Base.metadata)


# def init_db():
#     Base.metadata.create_all(bind=engine)
#     print("All tables created (or already existed).")


# if __name__ == "__main__":
#     init_db()
