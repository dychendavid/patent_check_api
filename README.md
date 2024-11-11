This project is an backend for Patent Infringement Check Requirements.

---

### Improving Plan

- Fuzzy match for company name, probably using `pg_trgm` (Text Based Similarity), since it more suitable than `pg_vector` (Vector Similarity)
  - Cache embedding of keyword
- Enable RabbitMQ for break heavy task.
- Enable Socket.Io for non-blocking API communication

---

### How to determine which products is the top possibily infringement products?

#### Simple Flow

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
