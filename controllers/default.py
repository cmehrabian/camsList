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
    redirect(URL('default', 'home', args=['all']))
    posts = db().select(db.camsList.ALL)
    # show_all = request.args(0) == 'all'


    return dict(posts=posts)


def home():
    show_all = request.args(0) == 'all'
    q = (db.camsList) if show_all else (db.camsList.sold == False)
 
    def generate_del_button(row):
        b = ''
        if auth.user_id == row.user_id:
            b = A('Delete', _class='btn', _href=URL('default', 'delete', args=[row.id], user_signature=True))
        return b
    def generate_edit_button(row):
        b = ''
        if auth.user_id == row.user_id:
            b = A('Edit', _class='btn', _href=URL('default', 'edit', args=[row.id]))
        return b
    def generate_toggle_button(row):
        b = ''
        if auth.user_id == row.user_id:
            b = A('Toggle', _class='btn', _href=URL('default', 'toggle_sold', args=[row.id], user_signature=True))
        return b
    def generate_view_button(row):
        b = ''
        if auth.user_id == row.user_id:
            b = A('View', _class='btn', _href=URL('default', 'view', args=[row.id]))
        return b


    def shorten_post(row):
        return row.clmessage[:25] + '...'

    links = [
        dict(header='', body= generate_del_button),
        dict(header='', body=generate_edit_button),
        dict(header='', body=generate_toggle_button),
        dict(header='', body=generate_view_button),
      #  dict(header='', body=generate_sold_toggle_button)
    ]

    if len(request.args) == 0:
        links.append(dict(header='Summary', body = shorten_post))
        db.camsList.clmessage.readable = False

    # {{if form.record.image != "":}}
    #     {{=IMG (_src=URL('download',args=form.record.image))}}
    # {{pass}}

    start_idx = 1 if show_all else 0
    form = SQLFORM.grid(q, args=request.args[:start_idx],
        fields = [db.camsList.user_id, db.camsList.image, db.camsList.listTitle, db.camsList.price, db.camsList.category,  db.camsList.date_posted, db.camsList.clmessage, db.camsList.sold],
        editable=False, 
        deletable=False,
        csv=False,
        sorter_icons=(XML('&#x2191;'), XML('&#x2193;')),
        links=links,
        details = False,
        )

    b = ''
    if show_all:
        button = A('See unsold', _class='btn', _href=URL('default', 'home'))
    else:
        button = A('See all', _class='btn', _href=URL('default', 'home', args=['all']))
    return dict(form=form, button=button)

@auth.requires_login()
def toggle_sold():
     """Toggles the sold field of an item"""
     item = db.camsList(request.args(0)) or redirect(URL('default', 'home'))
     is_sold = item.sold
     item.update_record(sold = not is_sold)
     #if URL is /all then redirect to there other wise to home
     redirect(URL('default', 'home', args=['all']))
 
    
@auth.requires_login()
def add():
    """Add a post"""
    form = SQLFORM(db.camsList)
    if form.process().accepted:
        #Successful
        session.flash = T('Added')
        redirect(URL('default', 'index'))
    return dict(form=form)

# def show_all():
#     p = db.camsList(request.args(0) == 'all')

def view():
    p = db.camsList(request.args(0)) or redirect(URL('default', 'view'))
    form = SQLFORM(db.camsList, record=p, readonly=True)
    return dict(form=form)

@auth.requires_login()
def edit():
    p = db.camsList(request.args(0)) or redirect(URL('default', 'index'))
    db.camsList.sold.writable = True
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
        redirect(URL('default', 'home'))    
    form = FORM.confirm('Are you sure?')
    if form.accepted:
        db(db.camsList.id == p.id).delete()
        redirect(URL('default', 'home'))
    return dict(form=form)



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
