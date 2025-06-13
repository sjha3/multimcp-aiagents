#from kusto_tool import run_kusto_query
import datetime, uuid,logging, json
from mcp.server.fastmcp import FastMCP
import logging

from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
from azure.kusto.data.helpers import dataframe_from_result_table
from azure.identity import DefaultAzureCredential


# Define the Kusto cluster and database
cluster = "https://recommendadxwus3test.westus3.kusto.windows.net"
database = "recommenddata"


#print("Starting MCP server...")

# This is the shared MCP server instance
review_mcp = FastMCP("review-mcp-server")

# Setup logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("review-mcp-server")
logger.info("Initializing Review MCP server...")

@review_mcp.tool()
def run_kusto_query(query: str):
    """
    Get data from kusto for a given query
    Returns:
        A json containing the results of the query.
    """
    
    # Create a Kusto connection string with Azure token credential
    kcsb = KustoConnectionStringBuilder.with_azure_token_credential(cluster, DefaultAzureCredential())

    # Create a Kusto client
    client = KustoClient(kcsb)

    # Execute the query
    response = client.execute(database, query)

    # Convert the response to a DataFrame
    df = dataframe_from_result_table(response.primary_results[0])

    return df.to_json(orient='records')

@review_mcp.tool()
def get_reviews(query: str) -> list:
    """
    Retrieve reviews from the database
    Args:
        query to get all review
    Returns:
        dict: Review data if found, else an error message.
    """
    try:
        #logger.info(f"Running query: {query}")
        result = run_kusto_query(query)
        if result:
            #logger.info(f"Query result: {result}")
            return result
        else:
            #logger.warning("No reviews found")
            return {"error": "Review not found"}
    except Exception as e:
        #logger.error(f"Error retrieving reviews: {str(e)}")
        return {"error": str(e)}

@review_mcp.tool()
def get_review(review_id: str, review_name:str) -> list: 
    """
    Retrieve a review from the database by its ID or Name.
    Args:
        review_id (str): The unique identifier of the review.
    Returns:
        dict: Review data if found, else an error message.
    """
    query = f"GetReviewsTest | where ReviewId == '{review_id}' or ReviewName contains '{review_name}'"
    try:
        #logger.info(f"Running get_review for ReviewId: {review_id} : {query}")
        result = run_kusto_query(query)
        if result:
            #logger.info(f"Review found: {result}")
            return result
        else:
            #logger.warning("Review not found")
            return {"error": "Review not found"}
    except Exception as e:
        #logger.error(f"Error retrieving review: {str(e)}")
        return {"error": str(e)}
    
@review_mcp.tool()
def create_review(review_name: str, workload_id: str, workload_name: str, owner: str) -> str:
    """
    Create a new review in the database.
    Args:
        review_name (str): Name of the review.
        workload_id (str): ID of the workload.
        workload_name (str): Name of the workload.
        owner (str): Owner of the review.
    Returns:
        str: Success or error message.
    """

    review_id = str(uuid.uuid4())  # Generate a unique ID for the review
    time_now = datetime.datetime.now()
    
    insert_query = f".append Reviews <| datatable (ReviewId: guid , ReviewName: string, WorkloadId: string, WorkloadName:string, Owner:string, ModifiedOn:datetime, IsDelete:bool)['{review_id}', '{review_name}', '{workload_id}', '{workload_name}', '{owner}', '{time_now}', False]"
    #logger.info(f"Insert query: {insert_query}")
    try:
        run_kusto_query(insert_query)
        return f"Review Created Successfully: {review_id}"
    except Exception as e:
        #logger.error(f"Error creating review: {str(e)}")
        return f"Error creating review: {str(e)}"
    
#get_reviews("GetReviewsTest")
#review = get_review("78f7a9fc-6525-4839-8715-f30e302e372e")
#print("Review is ", review)

@review_mcp.tool()
def delete_review(review_id: str):
    """
    Delete a review from the database.
    Args:
        review_id (str): The unique identifier of the review.
    Returns:
        str: Success or error message.
    """
    review = get_review(review_id)
    time_now = datetime.datetime.now()
    review = json.loads(review)[0] if review else None
    #logger.info(f"Review to delete: {review}")
    delete_query = f".append Reviews <| datatable (ReviewId: guid , ReviewName: string, WorkloadId: string, WorkloadName:string, Owner:string, ModifiedOn:datetime, IsDelete:bool)['{review_id}', '{review['ReviewName']}', '{review['WorkloadId']}', '{review['WorkloadName']}', '{review['Owner']}', '{time_now}', true]"
    #logger.info(f"Insert query: {delete_query}")
    
    try:
        run_kusto_query(delete_query)
        return "Review Created Successfully"
    except Exception as e:
        return f"Error creating review: {str(e)}"


if __name__ == "__main__":
    logger.info("Starting Review MCP server using logger...")
    review_mcp.run()