"""
federal_register_client.py

A small Python client to interact with the Federal Register API for:
1) Searching and retrieving metadata about rules and executive orders.
2) Retrieving document text given a document number.
"""

import requests

BASE_URL = "https://www.federalregister.gov/api/v1"

class FederalRegisterClient:
    """
    A client for retrieving data from the Federal Register API.
    
    This client handles:
        1) Searching for and retrieving metadata for 'rules' or 
           'executive orders' (or both), optionally filtering by date range, 
           president, agency, etc.
        2) Retrieving the full text of a specific document, given a 
           document number.
    """

    def __init__(self):
        """
        Initialize the client. You could add arguments for your application
        (like a user-agent string, proxies, or logging) if needed.
        """
        self.session = requests.Session()
        # You might want to set a custom User-Agent here:
        # self.session.headers.update({"User-Agent": "My FedReg Client/1.0 (contact: me@example.com)"})

    def search_documents(
        self,
        is_rule: bool = True,
        is_executive_order: bool = True,
        from_date: str = None,
        to_date: str = None,
        president: str = None,
        agency: str = None,
        per_page: int = 20,
        page: int = 1,
    ) -> dict:
        """
        Search for Federal Register documents (metadata only).
        By default, searches both 'rules' and 'executive orders'.

        :param is_rule: If True, include documents of type 'RULE'
        :param is_executive_order: If True, include Presidential Documents that are executive orders
        :param from_date: Lower bound for publication date in 'YYYY-MM-DD' format
        :param to_date: Upper bound for publication date in 'YYYY-MM-DD' format
        :param president: Slug name for president, e.g. 'joe-biden' 
                          or 'donald-trump'. Only relevant if searching executive orders.
        :param agency: Slug name for an agency, e.g. 'environmental-protection-agency'
                       Only relevant if searching rules.
        :param per_page: How many documents to return per page (max 1000).
        :param page: Which page of results to fetch.
        :return: A dictionary containing a list of documents found, 
                 with each document's metadata in a dictionary that includes:
                   {
                     "document_number": str,
                     "title": str,
                     "date": str (publication_date),
                     "description": str or None (abstract if present),
                     "raw_text_url": str or None
                   }
        """
        
        # We'll build up our conditions for the request:
        # See docs: https://www.federalregister.gov/developers/api/v1
        params = {
            "per_page": per_page,
            "page": page,
            "fields[]": [
                "document_number",
                "title",
                "abstract",        # We use this as the "description" if present
                "raw_text_url",    # So we can see how to get the text
                "publication_date",
            ],
        }

        # We'll store type filters in conditions[type][]
        # or for executive orders, we use conditions[type] = PRESDOCU
        # plus conditions[presidential_document_type] = executive_order for EOs.
        # We can pass multiple conditions[type] if we want both RULE and PRESDOCU.
        type_list = []
        if is_rule:
            type_list.append("RULE")
        if is_executive_order:
            type_list.append("PRESDOCU")
        
        # If we have no type specified, let's do nothing special,
        # but typically you'll want at least one
        if type_list:
            for t in type_list:
                # We can pass them as conditions[type][]=RULE, conditions[type][]=PRESDOCU
                # So we do something like ...&conditions[type][]=RULE
                # requests allows repeated keys as a list if we do ...
                # We'll just store them in the "conditions[type][]" param as a list
                # We'll do them after we convert param dict to a list-of-tuples approach or so.
                pass
        
        # For date range, we can do conditions[publication_date][gte], 
        # conditions[publication_date][lte].
        # Or conditions[publication_date][is]
        
        conditions = {}
        if from_date:
            conditions["publication_date[gte]"] = from_date
        if to_date:
            conditions["publication_date[lte]"] = to_date

        # If we are searching for a particular president, we do:
        # conditions[president][]=joe-biden (example)
        if president and is_executive_order:
            conditions["president[]"] = president

        # If we are searching for a particular agency, we do:
        # conditions[agencies][]= (some slug)
        if agency and is_rule:
            conditions["agencies[]"] = agency

        # We also specifically want: 
        #   if is_executive_order, add conditions[presidential_document_type][]=executive_order
        #   if we want only executive orders (not other Presidential docs).
        #   If is_executive_order, let's do that:
        if is_executive_order:
            conditions["presidential_document_type[]"] = "executive_order"

        # We'll now convert these conditions to the required params in the GET:
        # We'll add them all to "params" except for 'type' which is repeated.
        # We do "conditions[type][]" multiple times if needed.
        # So let's build up a final param dictionary carefully:
        # requests supports repeated keys by passing a list of tuples to 'params='
        
        param_tuples = []
        # existing param items
        for k, v in params.items():
            if isinstance(v, list):
                for val in v:
                    param_tuples.append((k, val))
            else:
                param_tuples.append((k, v))

        # type filters
        for doc_type in type_list:
            param_tuples.append(("conditions[type][]", doc_type))

        # other conditions
        for k, v in conditions.items():
            # if something is a list, we might do repeated keys
            # but from the above usage, we only store single strings
            param_tuples.append((f"conditions[{k}]", v))

        # Make the GET request:
        url = f"{BASE_URL}/documents.json"
        response = self.session.get(url, params=param_tuples)
        response.raise_for_status()
        data = response.json()

        # Now parse the data to produce our custom dictionary structure:
        results = []
        for item in data.get("results", []):
            doc_num = item.get("document_number")
            title = item.get("title")
            pub_date = item.get("publication_date")
            description = item.get("abstract", None)
            raw_url = item.get("raw_text_url", None)

            results.append({
                "document_number": doc_num,
                "title": title,
                "date": pub_date,
                "description": description,
                "raw_text_url": raw_url,
            })

        return {
            "count": data.get("count", 0),
            "results": results
        }

    def get_document_text(self, document_number: str) -> dict:
        """
        Retrieve the text (and minimal metadata) of a single document, 
        given its document number.
        
        This will do two things:
          1) GET /documents/{document_number}.json to see if it's a 
             rule or an executive order (check 'type'),
             also to retrieve relevant fields (president if EO, 
             agency if rule).
          2) Then fetch the raw_text_url to get the plain text.
        
        :param document_number: The FR document number, e.g. "2023-05187"
        :return: A dictionary with:
                 {
                   "title": str,
                   "date": str,
                   "president": str or None,
                   "agency": str or None,
                   "text": str (the document text itself),
                 }
        """

        # 1) Retrieve metadata from single-document endpoint
        #    GET /documents/{document_number}.{format} 
        #    We'll do .json
        fields = [
            "type",
            "document_number",
            "title",
            "publication_date",
            "president",
            "agency_names",
            "raw_text_url",
        ]
        params = []
        for f in fields:
            params.append(("fields[]", f))

        url = f"{BASE_URL}/documents/{document_number}.json"
        resp = self.session.get(url, params=params)
        resp.raise_for_status()
        doc_data = resp.json()

        doc_type = doc_data.get("type")
        # 'president' only relevant if doc_type == 'PRESDOCU'
        president = doc_data.get("president") if doc_type == "PRESDOCU" else None
        # 'agency_names' only relevant if doc_type == 'RULE' (or maybe 'PRORULE', 'NOTICE', etc.)
        agencies = doc_data.get("agency_names", [])
        # We'll just pick the first agency if we want a single string:
        agency = agencies[0] if agencies else None

        title = doc_data.get("title")
        pub_date = doc_data.get("publication_date")
        raw_url = doc_data.get("raw_text_url")

        # 2) If we have raw_url, fetch the text
        # Note that not all documents might have a raw_text_url,
        # some do have it, some might not. We'll handle if it's missing.
        text = ""
        if raw_url:
            text_resp = self.session.get(raw_url)
            text_resp.raise_for_status()
            text = text_resp.text
        else:
            text = "[No raw_text_url available for this document.]"

        # Construct the final dictionary
        result = {
            "title": title,
            "date": pub_date,
            "president": president,  # if it's an EO, this will be set
            "agency": agency,        # if it's a rule, we likely have an agency
            "text": text
        }

        return result


def example_usage():
    """
    Example usage of the FederalRegisterClient class.
    We demonstrate how you might search for certain docs, and 
    retrieve the text for a single doc.
    """
    
    # Create the client
    fr_client = FederalRegisterClient()

    # Example 1: Search for recent rules from a specific agency
    # E.g. Environmental Protection Agency: 'environmental-protection-agency'
    # from_date can be "2025-01-01", to_date can be "2025-02-21" for example
    # to get the last ~ month or so of results
    search_results = fr_client.search_documents(
        is_rule=True,
        is_executive_order=False,
        from_date="2025-01-01",
        to_date="2025-02-21",
        agency="environmental-protection-agency",
        per_page=5,
        page=1
    )
    print("Recent rules from the EPA:\n", search_results)

    # Example 2: Search for Executive Orders from Joe Biden
    eos = fr_client.search_documents(
        is_rule=False,
        is_executive_order=True,
        from_date="2023-01-01",
        to_date="2025-02-21",
        president="joe-biden",
        per_page=3,
        page=1
    )
    print("\nRecent executive orders from President Biden:\n", eos)

    # Example 3: Suppose we want to pick a document_number from the above search
    # and fetch its text:
    if eos["results"]:
        doc_number = eos["results"][0]["document_number"]
        doc_text_info = fr_client.get_document_text(doc_number)
        print(f"\nDocument text info for doc_number={doc_number}:\n", doc_text_info)

if __name__ == "__main__":
    # Optional: run the example usage if this script is executed directly
    example_usage()