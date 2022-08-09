from app01 import models


def reply_record(request, issue_obj, record):
    instance = models.IssueReply.objects.create(
        issue=issue_obj,
        creator=request.tracer,
        content=record,
        type=1
    )
    result_dict = [{
        "id": instance.id,
        "content": instance.content,
        "parent_id": instance.parent_id,
        "creator__username": instance.creator.username,
        "time": instance.time.strftime("%Y-%m-%d %H:%M:%S"),
        "type": instance.type
    }]
    return result_dict