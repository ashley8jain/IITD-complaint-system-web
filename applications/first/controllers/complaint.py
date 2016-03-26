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
        if description!='':
            cid = db.complaint.insert(user_id=auth.user.id, description=description, title=title)
            userId = auth.user.id
            hostelName = db(db.users.id==userId).select().first().hostel_name
            users = getHostelMates(hostelName)
            for user in users:
                if user!=auth.user.id:
                    db.notifications.insert(user_id=user, description="new <a href='/first/default/spec_complaint/%s'>complaint</a> posted"%(cid))
        return dict(success=True, complaint_id=cid)
    return dict(success=False)

def getHostelMates(hostel_name):
    my_hostel_mates = [];
    rows = db(db.users.hostel_name == hostel_name).select();
    for row in rows:
        my_hostel_mates.append(row.id);
    return my_hostel_mates;
