# discover table inherited from Base
from app.infrastructure.database import engine, Base
import app.domain.patent.models
import app.domain.product.models
import app.domain.llm.models
import app.domain.analysis.models

print("Dropping all tables.")
Base.metadata.drop_all(bind=engine)
print("Creating all tables.")
Base.metadata.create_all(bind=engine)

# seeding
import seeds.patent
import seeds.product

# embedding must after patent & product
import seeds.embedding
