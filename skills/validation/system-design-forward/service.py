# Simplified current behavior, supplied for read-only skill testing.
requests_used = 0
def organize(paper, model, database):
    global requests_used
    if paper["folder"] is None and requests_used < 20:
        requests_used += 1
        output = model.classify(paper["abstract"])
        database.save_labels(paper["id"], output, accepted=True)
    return database.labels(paper["id"])

def reset_organization(database):
    database.delete_labels()
