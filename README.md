This project is an backend for Patent Infringement Check Requirements.

---

## Outline
- [How to launch](#how-to-launch)
- [ER Diagram](#er-diagram)
- [How to pick top infringement](#how-to-pick-top-infringement)

---

## How to launch

#### A. Launch by docker-compose (for production)

- Clone this repository
  - `git clone https://github.com/dychendavid/patent_check_api`
- Put `.env.prod` in the folder
  - Sample in below
- Startup python + postgres
  - `docker compose --env-file .env.prod up -d`
- Force rebuild image if code/files update
  - `docker compose build --no-cache`
- Test db connection and api in browser
  - `http://{localhost}:8000/db_test`
- NOTE: Reset and Seed data by api call
  - `http://{localhost}:8000/seeds`
  - or this command
  - `docker compose exec python python seeder.py`

#### B. Launch native python + docker-compose (for local development)

- Clone this repository
  - `git clone https://github.com/dychendavid/patent_check_api`
- Put `.env.dev` in the folder
  - Sample in below
- Remove the _python_ service in docker-compose.yml
- Startup postgres
  - `docker compose --env-file .env.dev up -d`
- Execute your python
  - ex: `fastapi dev`
- Test db connection and api in browser
  - `http://{localhost}:8000/db_test`
- NOTE: Reset and Seed data by api call
  - `http://{localhost}:8000/seeds`
  - or this command
  - ex: `python seeder.py`

```
# .env sample

# DB_HOST needs same with service name in docker compose
DB_HOST=postgresql
DB_NAME=patent_check
DB_USER=postgres
DB_PASS=postgres

# This value reference to number of related claims
QUALIFY_DISTANCE_RANGE=0.45

# I'll glad to provide the OPENAI_API_KEY, please let me know
OPENAI_API_KEY=xxxxx

```

---

## ER Diagram

```mermaid
erDiagram

    Company ||--|{ Product : contains
    Product ||--|| ProductVector : "vertical partitioning"
    ProductVector ||--|{ ProductClaimDistance : "compared with ClaimVector"
    ProductClaimDistance ||--o{ ProductPatentScore : aggregated

    Analysis ||--o{ AnalysisProduct : contains
    Company ||--|{ Analysis : relate
    Patent ||--|{ Analysis : relate
    UserAnalysis ||--|| Analysis : relate

    Patent ||--|{ Claim : contains
    Patent ||--|| PatentExtra : "vertical partitioning"
    Claim ||--|| ClaimVector : "vertical partitioning"
    ClaimVector ||--|{ ProductClaimDistance : "compared with ProductVector"

    Company {
        int id PK
        int name UK
    }

    Product {
        int id PK
        int company_id UK "UK with name"
        str name UK "UK with company_id"
        str desc
    }

    ProductVector {
        int id PK
        int company_id 
        str product_id
        str desc
        str desc_vector
    }

    Patent {
        int id PK
        str publication_number UK
    }

    Claim {
        int id PK
        int patent_id UK "UK with num"
        str num UK "UK with patent_id"
        str desc
    }

    PatentExtra {
        int id PK
        int patent_id UK
        str abstract
        str description
    }

    ClaimVector {
        int id PK
        int patent_id
        str claim_id
        str desc
        str desc_vector
    }

    Analysis {
      int id PK
      int patent_id
      int company_id
      str assessment
      int risk_level
    }

    AnalysisProduct {
      int id PK
      int analysis_id
      int product_id
      arr claim_ids
      int likelihood
      str explanation
      arr features
    }

    UserAnalysis {
      int id PK
      int user_id UK "UK with analysis_id"
      int analysis_id UK "UK with user_id"
      bool status
    }

    ProductClaimDistance {
      int id PK
      int product_id
      str product_desc
      int patent_id
      int claim_id
      str claim_desc
      float cosine_distance
    }

    ProductPatentScore {
      int id PK
      int product_id
      int patent_id
      arr claim_ids
      float score
    }


```
---

## How to pick top infringement


```mermaid
flowchart TB
    S1[1.Get Embeddings]
    S2[2.Calculate Cosine Distance]
    S3[3.Calculate Score]
    S4[4.Call API with Top Product]
    S1 --- S2
    S2 --- S3
    S3 --- S4

```

### Step 1. Get Embeddings

- Pick up columns which most info
  - This case is Project Description, Claim Description
- Retrieve and save the embedding of picked columns by calling Open AI Embedding API

> We should keep all the embedding comes from same source and same version.

> Keep consistency is important than follow latest version.

<br />

### Step 2. Calculate Cosine Distance

- Calculate the cosine distance between vector of Product Description and Claim Description, for finding the association.
  - by using pgvector
- The table rows growth: <br />
  - 1 Company have `N` Products.<br />
  - 1 Product have distances with `M` Claims.
  - So the rows between specific company and specific patent, it will increase `N * M` rows
- The table columns

```python
company_id,      # int
product_id,      # int
product_desc,    # varchar

patent_id,       # int
claim_id,        # int
claim_desc,      # varchar

cosine_distance  # float
```

<br />

### Step 3. Calculate Infringing Possibility Score

- Find a formula to determine Possibility Score
- Smaller distance should be considered strong association, larger distance probably considered low association.

  - Filter out the distances which over threshold, since the association maybe too low and no important value for reference.<br />
  - Add up remaining distances to get a Possibility Score, maybe the future version we can higher the weight of Claims number.
    > Ex: Claim number \* 2 + Sum of distances = Possibility Score

- The table columns

```python
company_id,     # int
product_id,     # int

patent_id,      # int
product_name,   # varchar
product_desc,   # varchar
claim_ids,      # int array
claim_descs,    # varchar array

score           # float
```

<br />

### Step 4. Using LLM to do analyze

Send related info to LLM without our previously calculated distances for get more diversify analysis result, and using Langchain to make sure LLM output format.

<br />
