# -------------------------------------------------------------------------
# Copyright 2018, Andrea Fae'
#
# This file is part of "tcf" program
#
#    "tcf" is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    "tcf" is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with "tcf".  If not, see <http://www.gnu.org/licenses/>.
#
#    You can write an email to "andfae@gmail.com" to have a copy of source
#    files, according with this type of license.
#
# -------------------------------------------------------------------------

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.title = request.application
response.subtitle = T('IT')

## read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Andrea Fae\' <andfae@gmail.com>'
response.meta.description = 'CoolApp - TCF'
response.meta.keywords = 'web2py, python, framework'
response.meta.generator = 'Web2py Web Framework'
response.meta.copyright = 'Copyright 2017'

#print 'sono nel menu'
#rows_menu = db().select(db.sede.ALL, orderby=db.sede.nome)
#print rows_menu

response.menu = [
]

# se l'utente se è loggato
if auth.user:
    # cerco a quale gruppo appartiene
    query = (db.auth_membership.user_id == auth.user.id)
    row = db(query).select(db.auth_membership.group_id).first()
    #recupero il ruolo del gruppo
    query_group = (db.auth_group.id == row.group_id)
    row_group = db(query_group).select(db.auth_group.role).first()
    if auth.has_membership('manager'):
        response.menu.append(
         (T('Gestione'), False, None,
          [
            (T('Prenotazioni'), False, URL('default','prenotazioni')),
            (T('Utenti'), False, URL('default','utenti')),
          ]
         )
        )
response.menu.append(
    (T('Info'), False, None,
     [
            (T('About'), False, URL('default', 'about')),
            (T('License'), False, URL('default', 'license')),
            (T('Privacy'), False, URL('default', 'privacy')),
     ]
     )
    )
