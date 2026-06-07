from database import engine
from database_tables import Base

Base.metadata.create_all(bind=engine)

print("Tables created successfully")