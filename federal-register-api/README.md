# Federal Register API Client

This repository provides a simple Python module to query data from the [Federal Register API](https://www.federalregister.gov/developers/api/v1). Users can easily fetch final rules, proposed rules, notices, and presidential documents. Additionally, a function is provided to fetch details for a single document by its document number.

---

## Table of Contents

- [Federal Register API Client](#federal-register-api-client)
  - [Table of Contents](#table-of-contents)
  - [Requirements](#requirements)
  - [Installation](#installation)
  - [Usage Examples](#usage-examples)
    - [Fetching Final Rules](#fetching-final-rules)
    - [Fetching Proposed Rules](#fetching-proposed-rules)
    - [Fetching Notices](#fetching-notices)
    - [Fetching Presidential Documents](#fetching-presidential-documents)
    - [Fetching a Single Document by Document Number](#fetching-a-single-document-by-document-number)
    - [Fetching All Executive Orders From Donald Trump Since 2025](#fetching-all-executive-orders-from-donald-trump-since-2025)
  - [Advanced Usage](#advanced-usage)
  - [License](#license)

---

## Requirements

- **Python 3.6+**  
- **Requests** library

Install `requests` if you don't already have it:
```bash
pip install requests
```

## Installation

Clone or download this repository, then import the functions into your Python project. For example:

```bash
git clone https://github.com/example/federal-register-api-client.git
```

Then in your code:
```python
from federal_register_api import (
    get_rules,
    get_proposed_rules,
    get_notices,
    get_presidential_documents,
    get_document_details,
)
```

---

## Usage Examples

### Fetching Final Rules

```python
# Example: Fetch up to 5 final rules on "environment"
rules = get_rules(term="environment", per_page=5)

# The result is a dictionary returned by the Federal Register API
print("Number of results:", rules["count"])
for item in rules["results"]:
    print(item["document_number"], "-", item["title"])
```

- **Parameters**  
  - `term` (str): Optional search term (full text search).  
  - `per_page` (int): Number of items per page (max 1000).  
  - `page` (int): Page number (1-based).  
  - `order` (str): The order of results. Options: `"relevance"`, `"newest"`, `"oldest"`, etc.  
  - `fields` (list): A list of specific fields to return (default: None, meaning the API’s default set).

### Fetching Proposed Rules

```python
# Example: Fetch the first 3 proposed rules with the term "water"
proposed_rules = get_proposed_rules(term="water", per_page=3)

for item in proposed_rules["results"]:
    print(item["document_number"], "-", item["title"])
```

### Fetching Notices

```python
# Example: Fetch 10 notices (document type: NOTICE)
notices = get_notices(term="fishing", per_page=10)
for item in notices["results"]:
    print(item["document_number"], "-", item["title"])
```

### Fetching Presidential Documents

```python
# Example: Fetch up to 2 presidential documents matching the term "emergency"
pres_docs = get_presidential_documents(term="emergency", per_page=2)
for doc in pres_docs["results"]:
    print(doc["document_number"], "-", doc["title"])
```

### Fetching a Single Document by Document Number

```python
# Example: Fetch a single document with its document_number (e.g., "2023-10584")
doc_details = get_document_details(document_number="2023-10584")

print("Title:", doc_details["title"])
print("Document Number:", doc_details["document_number"])
print("Publication Date:", doc_details["publication_date"])
```

**Note**:  
- The `get_document_details` function also supports `format_type="csv"`. In that case, the function will return raw CSV text instead of JSON data.  
- You can pass a `fields` list if you only want certain fields (only works with `json` format), for example:
  ```python
  doc_details = get_document_details(
      document_number="2023-10584",
      fields=["document_number", "title", "html_url"]
  )
  ```

### Fetching All Executive Orders From Donald Trump Since 2025

Suppose you want to retrieve all **executive orders** (a type of presidential document) signed by **Donald Trump**, and only those published **on or after January 20, 2025**. The Federal Register API lets you filter by president, presidential document type, and publication date.

**Note**: This example uses the `requests` library directly (instead of the helper functions) to demonstrate passing advanced parameters.

```python
import requests

url = "https://www.federalregister.gov/api/v1/documents.json"

params = {
    # 'executive_order' is the subtype for Executive Orders
    "conditions[presidential_document_type][]": "executive_order",

    # Filter to President Donald Trump only
    "conditions[president][]": "donald-trump",

    # Documents on or after January 20, 2025
    "conditions[publication_date][gte]": "2025-01-20",

    # The API lets you order by "newest", "oldest", etc.
    "order": "newest",

    # How many results to retrieve per page (up to 1000)
    "per_page": 20,
}

response = requests.get(url, params=params)
response.raise_for_status()

data = response.json()

print("Total matching documents:", data["count"])
for doc in data["results"]:
    print(doc["document_number"], "-", doc["title"])
```

---

## Advanced Usage

You can customize queries with additional arguments. For instance:

```python
# Using the helper function to fetch proposed rules sorted by newest first
props_newest_first = get_proposed_rules(term="tax", per_page=5, order="newest")

# Restrict the fields returned
rules_custom_fields = get_rules(term="commerce", fields=["document_number", "title", "html_url"])
for r in rules_custom_fields["results"]:
    print(r["document_number"], r["title"], r["html_url"])
```

See the official [Federal Register API Documentation](https://www.federalregister.gov/developers/api/v1) for a complete list of supported parameters and fields.

---

## License

This project is provided under an MIT License. See the [LICENSE](LICENSE) file for details.
