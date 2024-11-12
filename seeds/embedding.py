import numpy as np
import os
from langchain_openai import OpenAIEmbeddings

from app.infrastructure.database import SessionLocal
from app.domain.product.models import ProductModel, ProductVectorModel
from app.domain.patent.models import PatentClaimVectorModel, PatentClaimModel

def seeding_product_vector():
    db = SessionLocal()
    try:
        print("Start seeding product embedding.")

        products = db.query(ProductModel).with_entities(ProductModel.desc, ProductModel.id, ProductModel.company_id).all()

        embed = [product.desc for product in products]
        embeddings_model = OpenAIEmbeddings(api_key=os.getenv('OPENAI_API_KEY'), model="text-embedding-3-small")
        embeddings = embeddings_model.embed_documents(embed)

        bulk = []
        product:ProductModel
        for idx, product in enumerate(products):
            bulk.append(ProductVectorModel(
                company_id = product.company_id,
                product_id = product.id,
                desc = product.desc,
                # TODO vector rand for development
                # desc_vector = np.random.rand(1536)
                desc_vector = embeddings[idx],
            ))
        db.bulk_save_objects(bulk)
        db.commit()

        # print(f"{len(data['companies'])} Products seeded successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding ProductVector: {e}")
    finally:
        db.close()

def seeding_claim_vector():
    db = SessionLocal()
    try:
        print("Start seeding claim embedding.")

        claims = db.query(PatentClaimModel).with_entities(PatentClaimModel.desc, PatentClaimModel.id, PatentClaimModel.patent_id).all()

        embed = [claim.desc for claim in claims]
        embeddings_model = OpenAIEmbeddings(api_key=os.getenv('OPENAI_API_KEY'), model="text-embedding-3-small")
        embeddings = embeddings_model.embed_documents(embed)
        bulk = []
        for idx, claim in enumerate(claims):
            bulk.append(PatentClaimVectorModel(
                patent_id = claim.patent_id,
                claim_id = claim.id,
                desc = claim.desc,
                # TODO vector rand for development
                # desc_vector = np.random.rand(1536)
                desc_vector = embeddings[idx]

            ))
        db.bulk_save_objects(bulk)
        db.commit()

        # print(f"{len(data['companies'])} Products seeded successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding ClaimVector: {e}")
    finally:
        db.close()
