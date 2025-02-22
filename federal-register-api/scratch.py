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


    python3 -c "import tiktoken; print(len(tiktoken.get_encoding('cl100k_base').encode(open('trump_executive_orders.txt').read())))"