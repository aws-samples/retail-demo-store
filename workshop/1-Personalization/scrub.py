import boto3

account_id = boto3.client("sts").get_caller_identity()["Account"]
region = boto3.Session().region_name

def scrub(s: str) -> str:
    """ Scrubs an input string of all occurrences of the current account ID and region """
    s = s.replace(account_id, 'X' * len(account_id))
    s = s.replace(region, 'X' * len(region))
    return s
