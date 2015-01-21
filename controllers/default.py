# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - api is an example of Hypermedia API support and access control
#########################################################################

def index():
    """
    Landing page for CamsList
    """
    redirect(URL('default', 'home'))
    posts = db().select(db.camsList.ALL)

    return dict(posts=posts)


def home():
    q = db.camsList

    def generate_del_button(row):
        b = ''
        if auth.user_id == row.user_id:
            b = A('Delete', _class='btn', _href=URL('default', 'delete', args=[row.id]))
        return b
    def generate_edit_button(row):
        b = ''
        if auth.user_id == row.user_id:
            b = A('Edit', _class='btn', _href=URL('default', 'edit', args=[row.id]))
        return b

    def shorten_post(row):
        return row.clmessage[:25] + '...'

    links = [
        dict(header='', body= generate_del_button),
        dict(header='', body=generate_edit_button),
    ]

    if len(request.args) == 0:
        links.append(dict(header='Summary', body = shorten_post))
        db.camsList.clmessage.readable = False

    form = SQLFORM.grid(q,
        fields = [db.camsList.user_id, db.camsList.image, db.camsList.listTitle, db.camsList.price,  db.camsList.date_posted, db.camsList.clmessage, db.camsList.sold],
        editable=False, 
        deletable=False,
        links=links,

        )
    return dict(form=form)
    
@auth.requires_login()

def add():
    """Add a post"""
    form = SQLFORM(db.camsList)
    if form.process().accepted:
        #Successful
        session.flash = T('Added')
        redirect(URL('default', 'index'))
    return dict(form=form)

def view():
    p = db.camsList(request.args(0)) or redirect(URL('default', 'index'))
    form = SQLFORM(db.camsList, record=p, readonly=True)
    return dict(form=form)
@auth.requires_login()

def edit():
    p = db.camsList(request.args(0)) or redirect(URL('default', 'index'))
    if p.user_id != auth.user_id: #OWNER OF THE POST
        session.flash = T('not authorized')
        redirect(URL('default', 'index'))
    form = SQLFORM(db.camsList, record=p)
    if form.process().accepted:
        session.flash = T('Updated')
        redirect(URL('default', 'view', args=[p.id]))
    return dict(form=form)    

@auth.requires_login()
@auth.requires_signature()
def delete():
    p = db.camsList(request.args(0)) or redirect(URL('default', 'index'))
    if p.user_id != auth.user_id:
        session.flash = T('not authorized')
        redirect(URL('default', 'index'))
    db(db.camsList.id == p.id).delete()
    redirect(URL('default', 'index'))



def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_login() 
def api():
    """
    this is example of API with access control
    WEB2PY provides Hypermedia API (Collection+JSON) Experimental
    """
    from gluon.contrib.hypermedia import Collection
    rules = {
        '<tablename>': {'GET':{},'POST':{},'PUT':{},'DELETE':{}},
        }
    return Collection(db).process(request,response,rules)
