import json
from app.infrastructure.database import SessionLocal
from app.domain.patent.models import PatentModel, PatentClaimModel, PatentExtraModel

with open('assets/patents.json') as json_file:
    data = json.load(json_file)

def seeding_patent():
    db = SessionLocal()
    try:
        print("Start seeding Patents.")
        for patent_data in data:
            # insert to patents
            patent = PatentModel(
                publication_number = patent_data['publication_number'],
                title = patent_data['title'],
                ai_summary = patent_data['ai_summary'],
                raw_source_url = patent_data['raw_source_url'],
                assignee = patent_data['assignee'],
                inventors = patent_data['inventors'],
                priority_date = patent_data['priority_date'],
                application_date = patent_data['application_date'],
                grant_date = patent_data['grant_date'],
                jurisdictions = patent_data['jurisdictions'],
                classifications = patent_data['classifications'],
                application_events = patent_data['application_events'],
                citations = patent_data['citations'],
                image_urls = patent_data['image_urls'],
                landscapes = patent_data['landscapes'],
                publish_date = patent_data['publish_date'],
                citations_non_patent = patent_data['citations_non_patent'],
                provenance = patent_data['provenance'],
                attachment_urls = patent_data['attachment_urls'],
            )
            db.add(patent)
            db.flush()



            # bulk insert to patent_claims
            claims_data = json.loads(patent_data["claims"])
            bulk = []
            for claim in claims_data:
                # claimText = json.dumps(claim['text'], ensure_ascii=True) # use dump() method to write it in file
               
                patent_claim = PatentClaimModel(
                    patent_id=patent.id,
                    num = claim['num'],
                    desc = claim['text']
                )
                bulk.append(patent_claim)
            db.bulk_save_objects(bulk)

            # insert to patent_claims
            patent_extra = PatentExtraModel(
                    patent_id=patent.id,
                    abstract = patent_data['abstract'],
                    description = patent_data['description'].strip()
            )
            db.add(patent_extra)

            db.commit()
        print(f"{len(data)} Patents seeded successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding Patent: {e}")
    finally:
        db.close()
