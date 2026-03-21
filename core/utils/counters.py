total_votes = 0
rejected_votes = 0
def increment_total():
    global total_votes
    total_votes += 1
def increment_rejected():
    global rejected_votes
    rejected_votes += 1
def get_stats():
    return {
        "total_votes": total_votes,
        "rejected_votes": rejected_votes
    }
