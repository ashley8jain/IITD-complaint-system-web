# -*- coding: utf-8 -*-
# try something like
def index():
    if len(request.args)<1:
        raise HTTP(404)
	return request.args[0]

def new():
    if auth.is_logged_in():
        description = str(request.vars["description"]).strip()
        title = str(request.vars["title"]).strip()
        level = str(request.vars["level"]).strip()
        if description!='':
            cid = db.complaint.insert(user_id=auth.user.id, description=description, title=title, type_=level);
        return dict(success=True, complaint_id=cid)
    return dict(success=False)

def getHostelMates(hostel_name):
    my_hostel_mates = [];
    rows = db(db.users.hostel_name == hostel_name).select();
    for row in rows:
        my_hostel_mates.append(row.id);
    return my_hostel_mates;

def upvote():
    comp_id = long(request.vars['complaint_id']);
    vote = int(request.vars['type']);
    initial = db((db.votes.user_id==auth.user.id)&(db.votes.complaint_id==comp_id)).select().first();
    if initial != None:
        initial = initial.upvote;
        if (initial==vote):
            vid = db((db.votes.user_id==auth.user.id)&(db.votes.complaint_id==comp_id)).update(upvote=0);
            return dict(success=True, vote_id=vid,create = "updated");
        else:
            vid = db((db.votes.user_id==auth.user.id)&(db.votes.complaint_id==comp_id)).update(upvote=vote);
            return dict(success=True, vote_id=vid,create = "updated");

