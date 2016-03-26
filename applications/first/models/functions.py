# -*- coding: utf-8 -*-
def upvote():
    comp_id = request.vars['complaint_id'];
    vote = request.vars['type'];
    if (vote==1):
        db.votes.insert(user_id=auth.user.id, complaint_id=comp_id, upvote=1, downvote=0, no_ud=0);
    elif(vote==-1):
        db.votes.insert(user_id=auth.user.id, complaint_id=comp_id, upvote=0, downvote=1, no_ud=0);
    else:
        return "bad call to function upvote";
