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

# -*- coding: utf-8 -*-
import calendar

# questa riga serve per dire di rappresentare tutte le volte auth_user.id con il nome ed il cognome
db.auth_user._format = '%(last_name)s %(first_name)s'

# tabella utenti
db.define_table('utente',
                Field('cognome', type='string', requires=[IS_NOT_EMPTY()]),
                Field('nome', type='string', requires=[IS_NOT_EMPTY()]),
                Field('email', type='string', requires = IS_EMPTY_OR(IS_EMAIL(error_message='email non valida formalmente')), represent=lambda v, r: '' if v is None else v),
                Field('telefono_casa', type='string', requires = IS_EMPTY_OR(IS_MATCH('^(?:[0-9] ?){6,14}[0-9]$', error_message='numero di telefono non corretto formalmente')), represent=lambda v, r: '' if v is None else v),
                Field('telefono_mobile', type='string', requires = IS_EMPTY_OR(IS_MATCH('^(?:[0-9] ?){6,14}[0-9]$', error_message='numero di telefono non corretto formalmente')), represent=lambda v, r: '' if v is None else v),
                Field('colore', 'string', default='#ff8d1c', widget=lambda f,v: SQLFORM.widgets.string.widget(f,v, _value=v, _type='color',_data_text='hidden', _hex='true')),
                auth.signature,singular="Utente",plural="Utenti",migrate='utente.table',
                format = '%(cognome)s %(nome)s'
               )
# nome non deve essere nel db a parità di cognome
db.utente.nome.requires=IS_NOT_IN_DB(db(db.utente.cognome==request.vars.cognome), 'utente.nome')

# tabella delle risorse (campi)
db.define_table('risorsa',
                Field('nome', type='string', requires=[IS_NOT_EMPTY(),IS_NOT_IN_DB(db,'risorsa.nome')]),
                Field('tipologia', type='string'),
                auth.signature,singular="Campo",plural="Campi",migrate='risorsa.table',
                format='%(nome)s'
                )

# tabella degli eventi (prenotazioni)
db.define_table('evento',
                Field('titolo', requires=[IS_NOT_EMPTY()]),
                Field('utente', 'reference utente'),
                Field('inizio', type='datetime'),
                Field('fine', type='datetime'),
                Field('uniqueid', type='string'),
                Field('ricorrenza', requires = IS_IN_SET(['0', '1', '2', '3', '4', '5'], error_message='deve essere un numero da 0 a 5'), default= '0'),
                Field.Virtual('giorno_inizio', lambda row:calendar.day_name[row.evento.inizio.weekday()]),
                Field('risorsa', 'reference risorsa'),
                Field('note', type='string'),
                Field('colore', default = '#8080ff'),
                Field('doppio', type='boolean', default='False'),
                Field('luce', type='boolean', default='False'),
                auth.signature,singular="Evento",plural="Eventi",migrate='evento.table',
                format='%(id)s'
               )
# questa impostazione serve per rappresentare inizio e fine senza i secondi
db.evento.inizio.represent = lambda value, row: value.strftime("%d/%m/%Y %H:%M")
db.evento.fine.represent = lambda value, row: value.strftime("%d/%m/%Y %H:%M")
db.evento.giorno_inizio.represent = lambda giorno_inizio, row: T(giorno_inizio)
