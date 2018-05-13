# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# Copyright 2018, Andrea Fae'
#
# This file is part of "TCF" program
#
#    "TCF" is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    "TCF" is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with "TCF".  If not, see <http://www.gnu.org/licenses/>.
#
#    You can write an email to "andfae@gmail.com" to have a copy of source
#    files, according with this type of license.
#
# -------------------------------------------------------------------------
# -------------------------------------------------------------------------
# this file is released under public domain and you can use without limitations
# -------------------------------------------------------------------------
from datetime import datetime,timedelta
from gluon.debug import dbg
import csv, uuid

# funzione che recupera il giorno dell'evento a partire dall'id evento
def __data_evento(id_evento):
    # cerco la data
    query = (db.evento.id == id_evento)
    row_data = db(query).select().first()
    # print 'row_data'
    # print row_data
    return(row_data.inizio)

def __is_beach_volley(id_risorsa):
    # se la risorsa è beach volley allora nascondi il check box "doppio"
    query_risorsa = (db.risorsa.id == id_risorsa)
    tipo_risorsa = db(query_risorsa).select().first().tipologia
    return(tipo_risorsa == 'beach volley')

# funzione about
def about():
    return locals()

# funzione license
def license():
    return locals()

# funzione privacy
def privacy():
    return dict(message="Privacy")

# ---- example index page ----
def index():
    # recupera la data iniziale dell'evento
    data_evento = request.vars['data_evento']
    # print 'Tabellone = ', session.vista
    if (session.vista == None):
        session.vista = 'agendaWeek'
    # determina i campi attivi
    query = (db.risorsa.is_active == True)
    # seleziona le righe con i campi in base alla query
    rowsrisorse = db(query).select()
    # seleziona le prenotazioni dei campi attivi
    queryeventi = (db.evento.risorsa == db.risorsa.id) & (db.risorsa.is_active == True)
    rowseventi = db(queryeventi).select()
    return locals()

# ---- controller per le prenotazioni delle ore ----
@auth.requires_membership('manager')
def prenotazioni():
    # print 'Prenotazioni = ', session.vista
    # recupera la data iniziale dell'evento
    data_evento = request.vars['data_evento']
    # session.vista = 'agendaWeek'
    # print data_evento, session.vista
    # determina i campi attivi
    query = (db.risorsa.is_active == True)
    # seleziona le righe con i campi in base alla query
    rowsrisorse = db(query).select()
    # print rowsrisorse
    # seleziona le prenotazioni dei campi attivi
    queryeventi = (db.evento.risorsa == db.risorsa.id) & (db.risorsa.is_active == True)
    rowseventi = db(queryeventi).select()
    # print rowseventi
    return locals()

# funzione che serve per cambiare tipo di vista e tenerla nella variabile di sessione
def cambia_sessione_vista():
    session.vista = request.vars.tipovista
    #print 'session.vista = ',session.vista
    return locals()

# funzione chiamata per una nuova prenotazione
def nuovo_evento():
    # print request.vars.risorsa
    
    # imposta uniqueid
    db.evento.uniqueid.default = str(uuid.uuid4())
    # non lo fa vedere
    db.evento.uniqueid.readable=db.evento.uniqueid.writable=False
    # db.evento.note.readable=db.evento.note.writable=True

    # se la prenotazione riguarda beach volley togli il check box relativo al doppio
    if __is_beach_volley(request.vars.risorsa):
        db.evento.doppio.readable=db.evento.doppio.writable=False
    
    # prendi l'evento dal titolo
    db.evento.titolo.default = request.vars.titolo
    # e rendilo non visibile
    db.evento.titolo.readable=db.evento.titolo.writable=False
    
    # il colore dell'evento dipende dal colore della persona, quindi non lo fa cambiare
    db.evento.colore.readable=db.evento.colore.writable=False
    # prendi la risorsa da vars.risorsa
    db.evento.risorsa.default=request.vars.risorsa
    
    # imposta l'ora di inizio, di fine e le rende non modificabili
    db.evento.inizio.default=datetime.strptime(request.vars.start, "%Y-%m-%d %H:%M:%S")
    db.evento.fine.default=datetime.strptime(request.vars.end, "%Y-%m-%d %H:%M:%S")
    db.evento.inizio.writable=db.evento.fine.writable=db.evento.risorsa.writable=False

    db.evento.giorno_inizio.readable=True
    
    # seleziona gli utenti attivi
    query_utenti = (db.utente.is_active == True)

    # obbliga ad inserire un utente che fa la prenotazione
    db.evento.utente.requires=IS_IN_DB(db(query_utenti),'utente.id','%(cognome)s' ' ' '%(nome)s', zero=T('Scegli l\'utente...'))
    
    # nascondi le ripetizioni
    db.evento.ricorrenza.readable=db.evento.ricorrenza.writable=False

    # istanzia il form
    # form=SQLFORM(db.evento, labels= {'docente':'Docente/Referente:','ricorrenza':'Ricorrenza settimanale:','materia':'Materia/Argomento'})
    form = SQLFORM(db.evento, formstyle='bootstrap4_inline')
    # form['_style']='border:1px solid black'

    # se il form è stato accettato (quindi evento registrato)
    if form.process().accepted:

        #print request.vars
        # recupero l'evento appena creato
        row_evento = db(db.evento.id == form.vars.id).select().first()
        # print 'row_evento = ', row_evento
        # recupero la data dell'evento
        data_evnt = __data_evento(int(row_evento.id))
        #print data_evnt

        # recupera il colore dell'utente
        query_ut = (db.utente.id == row_evento.utente)
        # recupera il colore del'utente che è docente
        col = db(query_ut).select().first().colore
        # update del record inserendo il colore del docente corretto
        row_evento.update_record(colore = col)
        
        # imposta il titolo con il nome dell'utente che ha prenotato
        # titolo = request.vars.risorsa.last_name + " " + request.vars.risorsa.first_name
        titolo = row_evento.utente.cognome + " " + row_evento.utente.nome
        
        # print "titolo prima = ", titolo
        tit = titolo.replace("\'", "\u02BC")
        titolo = tit
        
        # se ci sono note le inserisco nel titolo
        if (row_evento.note != ''):
            titolo = titolo + " - " + row_evento.note

        # se è prenotato un doppio mettilo nel titolo
        if (row_evento.doppio == True):
            titolo = titolo + " - DOPPIO"

        # se c' la luce allora mettilo nel titolo
        if (row_evento.luce  == True):
            titolo = titolo + " - LUCE"

        # print 'ricorrenza = ', row_evento.ricorrenza, type(row_evento.ricorrenza)
        # DEVO INTERVENIRE PER FARE TANTI RECORD
        # NON VENGONO VERIFICATI CONFLITTI CON ALTRI EVENTI
        # descrizione = row_evento.descrizione
        # if (int(row_evento.ricorrenza) > 0):
        #    descrizione = 'RIPETUTO - ' + descrizione

        # update del record inserendo il titolo corretto
        # print "titolo dopo = ", titolo
        row_evento.update_record(titolo = titolo)
        """if (int(row_evento.ricorrenza) > 0):
            ricorrenze = int(row_evento.ricorrenza)
            i = 1
            while i <= ricorrenze:
                db.evento.insert(titolo=row_evento.titolo, descrizione=row_evento.descrizione, inizio=row_evento.inizio + timedelta(days=7 * i), fine=row_evento.fine + timedelta(days=7 * i), uniqueid=row_evento.uniqueid, ricorrenza=row_evento.ricorrenza, risorsa=row_evento.risorsa)
                #print rinizio
                i = i +1 """
        response.flash = 'prenotazione inserita'
        response.js = 'hide_modal("#myModal");'
        #print "sono dopo il processamento del form e quindi aggiorno la pagina"
        redirect(URL('prenotazioni.html',args=[], vars=dict(data_evento = data_evnt)),client_side=True)
    return locals()

# sono autorizzati i manager
@auth.requires_membership('manager')
def mostra_evento():
    #recupera l'id dell'evento
    evento_id=request.args(0)
    # recupera i dati dell'evento
    evento=db.evento[evento_id] or redirect(error_page)
    
    db.evento.id.readable=db.evento.uniqueid.readable=db.evento.ricorrenza.readable=db.evento.colore.readable=False
    db.evento.giorno_inizio.readable=True
         
    form=SQLFORM(db.evento,evento, deletable=False, readonly=True)
    # l'attributo se si scrive con l'underscore lo inserisce direttamente nella pagina html
    form.components.append(BUTTON('Modifica', _class='btn btn-default', _onclick="document.location='%s';return false" % URL('modifica_evento',args=request.args(0))))
    form.components.append(BUTTON('Elimina', _class='btn btn-default', _onclick="document.location='%s';return false" % URL('delete_evento',args=request.args(0))))
    form.components.append(A('Indietro', _class='btn btn-secondary', _onclick="window.history.back()"))
    return dict(form=form, evento=evento)

# sono autorizzati i manager
@auth.requires_membership('manager')
def modifica_evento():
    #prendi l'id del record dell'evento - questa recupera tutto il record per intero - cfr DAL chapter - paragrafo Shortcuts
    record = db.evento(request.args(0)) or redirect(URL('error'))
    # non fare modificare alcuni campi
    # print 'posso modificare evento'
    db.evento.id.readable=db.evento.id.writable=False
    db.evento.utente.writable=False
    db.evento.inizio.writable=db.evento.fine.writable=db.evento.risorsa.writable=False
    db.evento.uniqueid.readable=db.evento.uniqueid.writable=False
    db.evento.colore.readable=db.evento.colore.writable=False
    db.evento.ricorrenza.writable=db.evento.doppio.writable=db.evento.luce.writable=False
    # istanzia il form
    form=SQLFORM(db.evento, record, deletable=False)
    if form.process().accepted:
        # recupero l'evento appena creato
        row_evento = db(db.evento.id == form.vars.id).select().first()
        # se il record non viene cancellato ma solo aggiornato
        response.flash = 'evento modificato/cancellato'
        redirect(URL('default','prenotazioni', args=[]))
    elif form.errors:
        response.flash = 'errori!'
    else:
        response.flash = 'per favore modifica i dati'
    return dict(form=form)

# sono autorizzati i manager
@auth.requires_membership('manager')
def sposta_evento():
    row = db(db.evento.id == request.vars.id_evento).select().first()
    row.update_record(risorsa=request.vars.id_risorsa,inizio=request.vars.start,fine=request.vars.end)
    return locals()

# sono autorizzati i manager
@auth.requires_membership('manager')
def elimina_evento():
    # recupero la data dell'evento
    data_evnt = __data_evento(int(request.vars.id_evento))
    if (request.vars.tipoevento == 'btn-single-conferma-unico'):
        # evento singolo da eliminare
        db(db.evento.id == int(request.vars.id_evento)).delete()
        response.flash = 'prenotazione singola eliminata'
    else:
        # evento ricorrente da eliminare
        if (request.vars.tipo == 'btn-recurrent-conferma-unico'):
            # se l'evento è ricorrente ma va eliminato solo questo singolo evento ricorrente
            db(db.evento.id == int(request.vars.id_evento)).delete()
            response.flash = 'solo questo prenotazione ripetuta è stata eliminata'
        else:
            # vanno eliminati tutti gli eventi ricorrenti con lo stesso uniqueid
            # prendo lo uniqueid dell'evento
            uniq_id = db(db.evento.id == int(request.vars.id_evento)).select().first().uniqueid
            # elimino tutti gli eventi con quell'uniq_id
            db(db.evento.uniqueid == uniq_id).delete()
    # fai il redirect per aggiornare la pagina
    # le 2 righe seguenti sono equivalenti
    # redirect(URL('prenotazioni.html',args=[], vars={'data_evento':data_evnt}),client_side=True)
    redirect(URL('prenotazioni.html',args=[], vars=dict(data_evento = data_evnt)),client_side=True)
    return locals()

# sono autorizzati i manager
@auth.requires_membership('manager')
def delete_evento():
    evento = request.args(0)
    print evento
    return locals()
"""    # recupero la data dell'evento
    data_evnt = __data_evento(int(request.vars.id_evento))
    if (request.vars.tipoevento == 'btn-single-conferma-unico'):
        # evento singolo da eliminare
        db(db.evento.id == int(request.vars.id_evento)).delete()
        response.flash = 'prenotazione singola eliminata'
    else:
        # evento ricorrente da eliminare
        if (request.vars.tipo == 'btn-recurrent-conferma-unico'):
            # se l'evento è ricorrente ma va eliminato solo questo singolo evento ricorrente
            db(db.evento.id == int(request.vars.id_evento)).delete()
            response.flash = 'solo questo prenotazione ripetuta è stata eliminata'
        else:
            # vanno eliminati tutti gli eventi ricorrenti con lo stesso uniqueid
            # prendo lo uniqueid dell'evento
            uniq_id = db(db.evento.id == int(request.vars.id_evento)).select().first().uniqueid
            # elimino tutti gli eventi con quell'uniq_id
            db(db.evento.uniqueid == uniq_id).delete()
    # fai il redirect per aggiornare la pagina
    # le 2 righe seguenti sono equivalenti
    # redirect(URL('prenotazioni.html',args=[], vars={'data_evento':data_evnt}),client_side=True)
    redirect(URL('prenotazioni.html',args=[], vars=dict(data_evento = data_evnt)),client_side=True)
    return locals() """

# sono autorizzati i manager
@auth.requires_membership('manager')
def utenti():
    # imposto la grid per far vedere gli utenti
    db.utente.id.readable = db.utente.id.writable = False
    db.utente.is_active.readable = db.utente.is_active.writable = True
    exportcls = dict(csv_with_hidden_cols=False, html=False, json=False, tsv_with_hidden_cols=False, tsv=False)
    db.utente.colore.readable = False
    # form = SQLFORM.grid(db.utente, args=[], formstyle='bootstrap4_inline', fields=[db.utente.nome,db.utente.cognome,db.utente.is_active],links = [lambda row: A('Elenco prenotazioni', _href=URL('prenotazioni_utente',args=row.id))],create=True, details=True, editable=True, deletable=False, maxtextlength=60, exportclasses = exportcls)
    form = SQLFORM.grid(db.utente, args=[], fields=[db.utente.nome,db.utente.cognome,db.utente.is_active],links = [lambda row: A('Elenco prenotazioni', _href=URL('prenotazioni_utente',args=row.id))],create=True, details=True, editable=True, deletable=False, maxtextlength=60, exportclasses = exportcls)
    return dict(form=form)

# sono autorizzati i manager
@auth.requires_membership('manager')
def prenotazioni_utente():
    # recupero il socio selezionato
    utente = request.args(0)
    # query per recuperare il nome  del docente
    query_nome_utente = db.utente.id == utente
    # recupero nome e cognome del'utente
    row = db(query_nome_utente).select(db.utente.nome,db.utente.cognome).first()
    # seleziono le prenotazioni del socio
    query = (db.evento.utente == utente)
    # imposto la grid per far vedere gli eventi/prenotazioni del socio
    exportcls = dict(csv_with_hidden_cols=False, html=False, json=False, tsv_with_hidden_cols=False, tsv=False)
    form = SQLFORM.grid(query, args=[utente], fields=[db.evento.titolo, db.evento.inizio, db.evento.fine, db.evento.risorsa],create=False, details=False, editable=False, deletable=False, searchable=False, maxtextlength=60, exportclasses = exportcls)
    return locals()

# ---- API (example) -----
@auth.requires_login()
def api_get_user_email():
    if not request.env.request_method == 'GET': raise HTTP(403)
    return response.json({'status':'success', 'email':auth.user.email})

# ---- Smart Grid (example) -----
@auth.requires_membership('admin') # can only be accessed by members of admin groupd
def grid():
    response.view = 'generic.html' # use a generic view
    tablename = request.args(0)
    if not tablename in db.tables: raise HTTP(403)
    grid = SQLFORM.smartgrid(db[tablename], args=[tablename], deletable=False, editable=False)
    return dict(grid=grid)

# ---- Embedded wiki (example) ----
def wiki():
    auth.wikimenu() # add the wiki to the menu
    return auth.wiki() 

# ---- Action for login/register/etc (required for auth) -----
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

# ---- action to server uploaded static content (required) ---
@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)
