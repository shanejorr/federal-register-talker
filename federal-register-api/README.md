# Federal Register Client

A small Python client (`federal_register_api.py`) for interacting with the Federal Register API. It allows you to:

1. **Search** for metadata about documents (rules or executive orders) by date, president, agency, etc.
2. **Retrieve** the full text of a specific document using its `document_number`.

The code uses Python's [`requests`](https://pypi.org/project/requests/) library to handle HTTP operations.

---

## Table of Contents
- [Federal Register Client](#federal-register-client)
  - [Table of Contents](#table-of-contents)
  - [Requirements](#requirements)
  - [Installation](#installation)
  - [Quick Start](#quick-start)
  - [Usage Examples](#usage-examples)
    - [Example 1: Rules from a Specific Agency](#example-1-rules-from-a-specific-agency)
    - [Example 2: Executive Orders by a President](#example-2-executive-orders-by-a-president)
    - [Example 3: Full Text for a Document](#example-3-full-text-for-a-document)
    - [Additional Example: Retrieving All Executive Orders During Donald Trump’s Second Term](#additional-example-retrieving-all-executive-orders-during-donald-trumps-second-term)
  - [API Reference](#api-reference)
  - [License](#license)

---

## Requirements

- Python 3.7+ (Should work on 3.7 and above)
- [requests](https://pypi.org/project/requests/)

---

## Installation

1. **Clone or Download** this repository (which contains `federal_register_api.py`).
2. **Install Dependencies**:

   ```bash
   pip install requests
   ```

3. **(Optional) Setup a Virtual Environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # (On Linux/Mac)
   # or
   venv\Scriptsctivate     # (On Windows)

   pip install requests
   ```

---

## Quick Start

1. **Locate the `federal_register_api.py` script**. 
2. **Run**:

   ```bash
   python federal_register_client.py
   ```

   By default, this will run a small demo (the `example_usage` function) that:
   - Searches for rules from the Environmental Protection Agency.
   - Searches for executive orders from Joe Biden.
   - Retrieves the full text of a single executive order from the search results.

---

## Usage Examples

Below are some additional usage examples. You can adapt or place them in a separate Python script. All examples assume you have:

```python
from federal_register_client import FederalRegisterClient

fr_client = FederalRegisterClient()
```

### Example 1: Rules from a Specific Agency
```python
search_results = fr_client.search_documents(
    is_rule=True,
    is_executive_order=False,
    from_date="2025-01-01",
    to_date="2025-02-21",
    agency="environmental-protection-agency",
    per_page=5,
    page=1
)

print("EPA Rules:")
for doc in search_results["results"]:
    print(f"Document Number: {doc['document_number']}")
    print(f"Title: {doc['title']}")
    print(f"Publication Date: {doc['date']}")
    print(f"Description: {doc['description']}")
    print(f"Raw Text URL: {doc['raw_text_url']}
")
```

### Example 2: Executive Orders by a President
```python
# Searching for executive orders by Joe Biden:
biden_eos = fr_client.search_documents(
    is_rule=False,
    is_executive_order=True,
    president="joe-biden",
    from_date="2023-01-01",
    to_date="2024-01021",
    per_page=3,
    page=1
)

print("Executive Orders by Joe Biden:")
for doc in biden_eos["results"]:
    print(f"Doc # {doc['document_number']} — {doc['title']}")
```

### Example 3: Full Text for a Document
```python
# Suppose we want the text of a specific doc_number from search results
some_document_number = "2023-05187"  # Example doc. number
doc_info = fr_client.get_document_text(some_document_number)

print("Title:", doc_info["title"])
print("Date:", doc_info["date"])
print("President:", doc_info["president"])
print("Agency:", doc_info["agency"])
print("Document Text:
", doc_info["text"][:500], "...")  # Print first 500 chars
```

### Additional Example: Retrieving All Executive Orders During Donald Trump’s Second Term

```python
# We'll consider the second term starting Jan. 20, 2025
# and going until Jan. 19, 2029 (4-year term).

from_date = "2025-01-20"
to_date = "2029-01-19"

# 1) Search for all Executive Orders by Donald Trump in that range
trump_eos = fr_client.search_documents(
    is_rule=False,
    is_executive_order=True,
    from_date=from_date,
    to_date=to_date,
    president="donald-trump",
    per_page=100,  # can adjust
    page=1
)

print(f"Found {trump_eos['count']} executive orders from {from_date} to {to_date}.
")

# 2) Iterate through each document number, retrieve title, date, and text
for doc_item in trump_eos["results"]:
    doc_number = doc_item["document_number"]
    # Retrieve full text
    text_info = fr_client.get_document_text(doc_number)
    
    print(f"Document Number: {doc_number}")
    print(f"Title: {text_info['title']}")
    print(f"Date: {text_info['date']}")
    # text_info['text'] can be very large, so be careful printing in full:
    print("Excerpt of text:", text_info['text'][:300], "...
")
```

One use case is to save the full texts of all executive orders in a time period or from a president and then feed the text into a large language model such as ChatGPT for analysis or summarization. Continuing with our Donald Trump example, here is how you can do that in a single python script.

```python
from federal_register_api import FederalRegisterClient
from datetime import date

def aggregate_trump_executive_orders():
    """
    Retrieve all executive orders during Donald Trump’s second term,
    aggregate their titles, dates, and full texts into a single text document,
    and save it as 'trump_executive_orders.txt'.
    """
    # Define the specified end date
    specified_to_date = date(2029, 1, 19)
    today = date.today()
    # Set to_date as today's date or the specified date, whichever is earlier
    to_date = min(specified_to_date, today).isoformat()
    from_date = "2025-01-20"  # Start of Donald Trump's second term

    # Create the Federal Register client
    fr_client = FederalRegisterClient()

    # Search for all executive orders by Donald Trump in that date range
    trump_eos = fr_client.search_documents(
        is_rule=False,
        is_executive_order=True,
        from_date=from_date,
        to_date=to_date,
        president="donald-trump",
        per_page=100,  # Adjust as needed if there are many results
        page=1
    )

    print(f"Found {trump_eos['count']} executive orders by Donald Trump in the specified date range.")

    # Start building the content for the output file
    output_lines = []
    output_lines.append("Donald Trump's Second Term Executive Orders")
    output_lines.append(f"From {from_date} to {to_date}\n")
    
    # Iterate through each executive order result
    for idx, doc_item in enumerate(trump_eos["results"], start=1):
        
        doc_number = doc_item["document_number"]

        print(f"{idx}. Retrieving details for document {doc_number}")

        # Retrieve full document details including text
        text_info = fr_client.get_document_text(doc_number)
        
        # Append details to the output
        output_lines.append("=" * 80)
        output_lines.append(f"Document Number: {doc_number}")
        output_lines.append(f"Title: {text_info['title']}")
        output_lines.append(f"Publication Date: {text_info['date']}\n")
        output_lines.append("Text:\n")
        output_lines.append(text_info['text'])
        output_lines.append("\n")
    
    # Join all lines into a single string
    all_text = "\n".join(output_lines)
    
    # Write the aggregated content to a text file
    output_filename = "trump_executive_orders.txt"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(all_text)
    
    print(f"Aggregated executive orders saved to {output_filename}")

if __name__ == "__main__":
    aggregate_trump_executive_orders()
```

---

## API Reference

- **`FederalRegisterClient`**
  - **`search_documents(...)`**  
    - **Parameters**:
      - `is_rule: bool` – If True, include `RULE` documents.
      - `is_executive_order: bool` – If True, include `PRESDOCU` with `presidential_document_type=executive_order`.
      - `from_date: str` – Lower bound publication date (`YYYY-MM-DD`).
      - `to_date: str` – Upper bound publication date (`YYYY-MM-DD`).
      - `president: str` – President slug (e.g., `joe-biden`, `donald-trump`) for executive orders.
      - `agency: str` – Agency slug (e.g., `environmental-protection-agency`) for rules.
      - `per_page: int` – Page size (max 1000).
      - `page: int` – Which page of the results to retrieve.
    - **Returns**:
      ```
      {
        "count": <total matching documents>,
        "results": [
          {
            "document_number": <str>,
            "title": <str>,
            "date": <str>,
            "description": <str or None>,
            "raw_text_url": <str or None>
          },
          ...
        ]
      }
      ```

---

## License

This example client is provided as-is without any specific license. You may modify and adapt it for your own use. The Federal Register API is subject to their [Terms of Service](https://www.federalregister.gov/developers/). Always check for any usage restrictions or guidelines before production use.
