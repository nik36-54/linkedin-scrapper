import scrapper.constants as const
from datetime import datetime
from supabase import Client, create_client
import re

supabase_client: Client = create_client(const.SUPABASE_URL, const.SUPABASE_ANON_KEY)


def clean_document_content(document: str) -> str:
    # Use regular expressions to remove 'Post X:' prefixes
    cleaned_document = re.sub(r"Post \d+:\s*", "", document)
    return cleaned_document


def store_company_posts(date: datetime, document: str):
    cleaned_document = clean_document_content(document)
    formatted_date = date.strftime("%Y-%m-%d")
    response = (
        supabase_client.from_("scrapper")
        .insert(
            [
                {
                    "date": formatted_date,
                    "document": cleaned_document,
                }
            ]
        )
        .execute()
    )

    # Check if the insertion was successful
    if response.data:
        print("Post uploaded successfully.")
        return response.data
    else:
        print("Error uploading post:", response.error)
        return None


# store_company_posts(datetime.now(), document_content)

"""
def fetch_latest_posts(limit: int = 10):
    # Query the latest posts ordered by date in descending order
    response = supabase.table("scrapper").select("*").order("date", desc=True).limit(limit).execute()
    if response.get('status_code') == 200:  # Success
        return response.get('data', [])
    else:
        print("Error fetching data:", response.get('error'))
        return []


recent_posts = fetch_latest_posts(limit=5)
for post in recent_posts:
    print(f"Date: {post['date']}, Document: {post['document']}")


def fetch_posts_by_date(date: str, limit: int = 10):
    response = supabase.table("scrapper") \
        .select("*") \
        .eq("date", date) \
        .order("date", desc=True) \
        .limit(limit) \
        .execute()

    if response.get('status_code') == 200:
        return response.get('data', [])
    else:
        print("Error fetching data:", response.get('error'))
        return []


specific_date = "2025-01-23"
posts = fetch_posts_by_date(specific_date, limit=5)
for post in posts:
    print(f"ID: {post['id']}, Date: {post['date']}, Document: {post['document']}")


def fetch_posts_in_date_range(start_date: str, end_date: str, limit: int = 10):
    response = supabase.table("scrapper") \
        .select("*") \
        .gte("date", start_date) \
        .lte("date", end_date) \
        .order("date", desc=True) \
        .limit(limit) \
        .execute()

    if response.get('status_code') == 200:
        return response.get('data', [])
    else:
        print("Error fetching data:", response.get('error'))
        return []
"""
"""

start_date = "2025-01-20"
end_date = "2025-01-23"
posts_in_range = fetch_posts_in_date_range(start_date, end_date, limit=10)
for post in posts_in_range:
    print(f"ID: {post['id']}, Date: {post['date']}, Document: {post['document']}")

"""
