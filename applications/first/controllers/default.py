# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################

@auth.requires_login()
def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    response.flash = T("Hello World")
    redirect(URL('home'));
    return locals();

def first():
    return dict()

def second():
    a = request.vars.visitor_name
    return dict(message=a)

@request.restful()
def api():
    response.view = 'generic.'+request.extension
    def GET(*args,**vars):
        patterns = 'auto'
        parser = db.parse_as_rest(patterns,args,vars)
        if parser.status == 200:
            return dict(content=parser.response)
        else:
            raise HTTP(parser.status,parser.error)
    def POST(table_name,**vars):
        return db[table_name].validate_and_insert(**vars)
    def PUT(table_name,record_id,**vars):
        return db(db[table_name]._id==record_id).update(**vars)
    def DELETE(table_name,record_id):
        return db(db[table_name]._id==record_id).delete()
    return dict(GET=GET, POST=POST, PUT=PUT, DELETE=DELETE)

@auth.requires_login()
def complaint():
    form = crud.create(db.complaint)
    return dict(form=form)

def complaintlist():
    complaints = db(db.complaint.id > 0).select()
    return dict(complaints=complaints)

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)

def login():
    userid = request.vars.userid
    password = request.vars.password
    user = auth.login_bare(userid,password)
    return dict(success=False if not user else True, user=user)

def logout():
    return dict(success=True, loggedout=auth.logout())


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()

def getComplaints(hostel_name, level, dept):
    me_and_my_hostelmates = [];
    rows = db(db.users.hostel_name == hostel_name).select();
    for row in rows:
        me_and_my_hostelmates.append(row.id);
    if level==2:
        level_query = (db.complaint.user_id.belongs(me_and_my_hostelmates)&(db.complaint.type_==level)); #just defining the level-wise "query"
    elif level==3:
        level_query = (db.complaint.type_==level);
    elif level==1:
        level_query = ((db.complaint.user_id==auth.user.id)&(db.complaint.type_==level));
    else:
        level_query = (db.complaint.user_id.belongs(me_and_my_hostelmates)); #.select(orderby=~db.complaint.created_at,limitby=(0,100))
    if dept==0:
        my_hostel_complaints = db(level_query).select(orderby=~db.complaint.created_at,limitby=(0,100));
    else:
        dept_query = (db.complaint.department == dept);
        my_hostel_complaints = db( level_query & dept_query ).select(orderby=~db.complaint.created_at,limitby=(0,100));
        #defining dept-wise query,combining with level-wise and performing the query

    return my_hostel_complaints;


@auth.requires_login()
def home():
    userId = auth.user.id;
    hostelName = db(db.users.id==userId).select().first().hostel_name;
    level = str(request.vars["level"]).strip();
    dept = str(request.vars["display_dept"]).strip();
    level = int(level) if (level!='None') else 0;
    dept = int(dept) if (dept!='None') else 0;
    my_hostel_complaints = getComplaints(hostelName,level,dept)
    return locals()

def notification():
    noti = db(db.notifications.user_id==auth.user.id).select(orderby=~db.notifications.created_at)
    db(db.notifications.user_id==auth.user.id).update(is_seen=1)
    return dict(notifications=noti)

def spec_complaint():
    if len(request.args)<1:
        raise HTTP(404)
    try:
        aid = request.args[0]
    except Exception, e:
        raise HTTP(404)
    complaint = db(db.complaint.id==aid).select()
    if len(complaint)<1:
        raise HTTP(404)
    else:
        complaint = complaint.first()
        comments = db(db.comments.complaint_id == complaint.id).select(orderby=~db.comments.created_at);
    return locals();

@auth.requires_login()
def post_comment():
    complaint_id = int(request.vars["complaint_id"])
    description = str(request.vars["description"]).strip()
    userName = str(auth.user.first_name) + " " + str(auth.user.last_name);
    comment_id = db.comments.insert(complaint_id=complaint_id, user_id=auth.user.id, description=description, user_name=userName)
    hostelName = db(db.users.id==auth.user.id).select().first().hostel_name
    type1 = db(db.complaint.id==complaint_id).select().first().type_
    if type1 == 1:
        users = db((db.users.type_==2)&(db.users.hostel_name == hostelName)).select()
    elif type1 == 2:
        users = getHostelMates(hostelName)
    else:
        users = db(db.users.username!=None).select()
    for user in users:
        if user!=auth.user.id:
            u = auth.user
            db.notifications.insert(user_id=user, description="new <a href='/first/default/spec_complaint/%s'>comment</a> posted by %s"%(complaint_id,(u.first_name+" "+u.last_name).title()))
    return dict(success=True,comments_id=comment_id)

def getHostelMates(hostel_name):
    my_hostel_mates = [];
    rows = db(db.users.hostel_name == hostel_name).select();
    for row in rows:
        my_hostel_mates.append(row.id);
    return my_hostel_mates;

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

@auth.requires_login()
def delete_comment():
        comment_id = int(request.vars["comment_id"])
        comment = db(db.comments.id==comment_id).select().first()
        if (comment.user_id == auth.user.id):
            db(db.comments.id==comment_id).delete()
            return dict(success=True)
        else:
            return dict(success=False)
