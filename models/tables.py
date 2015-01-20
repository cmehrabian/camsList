# -*- coding: utf-8 -*-
# Seller name and contact info (email / phone / ...)
# A date posted
# A title for the listing
# A body for the listing
# If they wish, an image.  
# A category, one of: Car, Bike, Books, Music, Outdoors, For the house, Misc. 
# A price. 
# Whether the item is sold or still available. 
from datetime import datetime

def get_first_name():
	name = "noName"
	if auth.user:
		name = auth.user.first_name
	return name

CATEGORY = ['For Sale', 'Wanted', 'Trade', 'Misc']

db.define_table('camsList',
	Field('listTitle'),
	Field('clmessage', 'text'),
	Field('image'),	#add image upload api
	Field('price'),
	Field('name'),
	Field('user_id', db.auth_user),
	Field('phone'),
	Field('email'),
	Field('date_posted', 'datetime'),
	Field('category'), #with autocomplete?
	Field('sold', 'boolean'), #whether is sold or not. Use boolean with sold as default False
	)
db.camsList.listTitle.label = "Posting title"
db.camsList.clmessage.label = 'Posting body' 
db.camsList.name.default = get_first_name()
db.camsList.date_posted.default = datetime.utcnow()
db.camsList.user_id.default = auth.user_id

db.camsList.id.readable = False #not working
db.camsList.user_id.default = auth.user_id
db.camsList.user_id.writable = db.camsList.user_id.readable = False

db.camsList.email.requires = IS_EMAIL()
db.camsList.category.default = 'Trade'
db.camsList.category.required = True
db.camsList.category.requires = IS_IN_SET(CATEGORY)
db.camsList.sold.default = False #set boolean
db.camsList.price.requires = IS_NOT_EMPTY()


