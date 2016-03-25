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
        return dict(success=True, complaint_id=cid)
    return dict(success=False)
