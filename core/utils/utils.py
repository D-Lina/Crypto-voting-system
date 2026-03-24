def convert_vote_to_int(vote):
    return int(vote)
  
def validate_vote(vote):
    if not (0 <= vote <= 10):
        raise ValueError("Vote must be between 0 and 10")
