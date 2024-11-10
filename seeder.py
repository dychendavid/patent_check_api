from app.infrastructure.database import engine, Base, wait_for_db
from seeds.patent import seeding_patent
from seeds.product import seeding_product
from seeds.embedding import seeding_claim_vector, seeding_product_vector
# discover table inherited from Base
import app.domain.patent.models
import app.domain.product.models
import app.domain.llm.models
import app.domain.analysis.models

# make sure db is ready
wait_for_db(60, 5)

print("Dropping all tables.")
Base.metadata.drop_all(bind=engine)
print("Creating all tables.")
Base.metadata.create_all(bind=engine)

# seeding
seeding_patent()
seeding_product()
# embedding must after patent & product
seeding_claim_vector()
seeding_product_vector()