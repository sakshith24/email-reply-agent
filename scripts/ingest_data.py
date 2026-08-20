import os
import pandas as pd
from dotenv import load_dotenv
from app.database.supabase import get_supabase_client
from app.knowledge.embeddings import generate_embedding,get_embedding_model

# Load environment variables (.env)
load_dotenv()


def ingest_csv():
    # Initialize Supabase client
    supabase = get_supabase_client()
    embedding_model = get_embedding_model()
    
    # Path to CSV file in project root
    csv_path = "dummy_dataset_150.csv"
    
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found in root directory.")
        return

    # Read CSV using pandas
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} rows from {csv_path}")

    # Prepare data payloads
    records = []
    for _, row in df.iterrows():
        # Get column values safely whether named in Title Case or snake_case
        course_name = str(row.get("Course name") or row.get("course_name") or "")
        course_link = str(row.get("Course link") or row.get("course_link") or "")
        course_desc = str(row.get("Course description") or row.get("course_description") or "")
        price = str(row.get("Price") or row.get("price") or "")
        starting_date = str(row.get("Starting date") or row.get("starting_date") or "")
        is_live = str(row.get("Is live") or row.get("is_live") or "")
        
        # Handle numeric fields safely
        try:
            lessons = int(row.get("Number of lessons") or row.get("number_of_lessons") or 0)
        except (ValueError, TypeError):
            lessons = 0
            
        try:
            duration = int(row.get("Total duration hours") or row.get("total_duration_hours") or 0)
        except (ValueError, TypeError):
            duration = 0
            
        target_audience = str(row.get("Target audience") or row.get("target_audience") or "")

        # Format combined content string for context/embeddings
        content = f"Course: {course_name}\nDescription: {course_desc}\nAudience: {target_audience}\nPrice: {price}"
        embedding = generate_embedding(content, embedding_model)

        payload = {
            "course_name": course_name,
            "course_link": course_link,
            "course_description": course_desc,
            "price": price,
            "starting_date": starting_date,
            "is_live": is_live,
            "number_of_lessons": lessons,
            "total_duration_hours": duration,
            "target_audience": target_audience,
            "content": content,
            "embedding":embedding
        }
        records.append(payload)

    # Insert rows into Supabase knowledge_base table
    try:
        response = supabase.table("knowledge_base").insert(records).execute()
        print("Successfully ingested dataset into 'knowledge_base' table!")
    except Exception as e:
        print(f"An error occurred during data ingestion: {e}")

if __name__ == "__main__":
    ingest_csv()