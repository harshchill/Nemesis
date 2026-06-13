from typing import TypedDict,Optional,Any,List

class PRReviewState(TypedDict):
    repo : str
    pr_number : int
    token : str
    pr_info : Optional[dict]
    changed_files : Optional[List[dict]]
    file_reviews : Optional[List[dict]]
    summary : Optional[str]
    posted : Optional[bool]
    error : Optional[str]