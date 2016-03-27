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
        dept = str(request.vars["complaint_dept"]).strip()
        if description!='':
            cid = db.complaint.insert(user_id=auth.user.id, description=description, title=title, type_=level, department=dept)
            userId = auth.user.id
            hostelName = db(db.users.id==userId).select().first().hostel_name
            if level == "1":
                users = db((db.users.type_==2)&(db.users.hostel_name == hostelName)).select()
            elif level == "2":
                users = getHostelMates(hostelName)
            else:
                users = db(db.users.username!=None).select()
            for user in users:
                if user!=auth.user.id:
                    u = auth.user
                    db.notifications.insert(user_id=user, description="new <a href='/first/default/spec_complaint/%s'>complaint</a> posted by %s"%(cid,(u.first_name+" "+u.last_name).title()))
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
    else:
        vid = db.votes.insert(user_id=auth.user.id, complaint_id=comp_id, upvote=vote);
        return dict(success=True, vote_id=vid,create = "created");

@auth.requires_login()
def edit_complaint():
    comp_id = long(request.vars['complaint_id']);
    complaint = db(db.complaint.id==comp_id).select().first();
    return locals();

@auth.requires_login()
def update_complaint():
    complaint_id = int(request.vars["complaint_id"])
    description = str(request.vars["description"]).strip()
    title = str(request.vars["title"]).strip()
    db(db.complaint.id==complaint_id).update(description = description , title = title)
    return dict(success=True)

@auth.requires_login()
def delete_complaint():
        complaint_id = int(request.vars["complaint_id"])
        complaint = db(db.complaint.id==complaint_id).select().first()
        if (complaint.user_id == auth.user.id):
            db(db.complaint.id==complaint_id).delete()
            return dict(success=True)
        else:
            return dict(success=False)
