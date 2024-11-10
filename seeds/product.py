import json
import os
from langchain_openai import OpenAIEmbeddings
from sqlalchemy import update

from app.infrastructure.database import SessionLocal
from app.domain.product.models import CompanyModel, ProductModel

with open('assets/company_products.json') as json_file:
    data = json.load(json_file)

def seed_data():
    db = SessionLocal()
    try:

        name_bulk = []
        print("Start seeding Products.")
        for item in data["companies"]:
            company = CompanyModel(
                name = item["name"]
            )
            name_bulk.append(item["name"])
            db.add(company)
            db.flush()

            # bulk insert to patent_claims
            bulk = []
            for product in item['products']:
                patent_claim = ProductModel(
                    company_id=company.id,
                    name = product['name'],
                    desc = product['description']
                )
                bulk.append(patent_claim)
            db.bulk_save_objects(bulk)

        # fill in name vector
        embeddings_model = OpenAIEmbeddings(api_key=os.getenv('OPENAI_KEY'), model="text-embedding-3-small")
        embeddings = embeddings_model.embed_documents(name_bulk)
        for idx, embedding in enumerate(embeddings):
            update(CompanyModel).where(CompanyModel.id==idx).values(name_vector=embedding)

        db.commit()
        print(f"{len(data['companies'])} Companies, {len(bulk)} Products seeded successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding products: {e}")
    finally:
        db.close()

seed_data()