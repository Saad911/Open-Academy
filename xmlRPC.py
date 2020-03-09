url = 'http://localhost:8013'
db = 'KZM'
username = 'hassini911@gmail.com'
password = 'Hassini911'
import xmlrpclib
import xmlrpc.client
#info = xmlrpc.client.ServerProxy('http://localhost:8013').start()
common =  xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
output = common.version()
print(output)
uid = common.authenticate(db, username, password, {})
print uid

models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
uid = common.authenticate(db, username, password, {})
print uid
models.execute_kw(db, uid, password,'openacademy.session', 'search',[[]])
models.execute_kw(db, uid, password,'openacademy.session', 'search',[[['course_id', '=', 'MATHS']]])
models.execute_kw(db, uid, password,'openacademy.session', 'search',[[['instructor_id', '=', 'User2'],['active', '=', True]]])
models.execute_kw(db, uid, password,'openacademy.course', 'search_count',[[['name', '=', 'PHILO'], ['responsible_id', '=', 'User1']]])
#####################################
models.execute_kw(db, uid, password,'openacademy.course', 'search',[[['responsible_id', '=', 'User2']]])
######################################################
models.execute_kw(db, uid, password,'openacademy.course', 'search',[[['responsible_id', '=', 'User2']]],{'offset': 10, 'limit': 2})
######################################################
models.execute_kw(db, uid, password,'openacademy.course', 'search_count',[[['responsible_id', '=', 'User2']]])
#######################################################
ids = models.execute_kw(db, uid, password,'openacademy.course', 'search',[[['responsible_id', '=', 'User2']]],{'limit': 1})
[record] = models.execute_kw(db, uid, password,'openacademy.course', 'read', [ids])
outlen = len(record)
################
models.execute_kw(db, uid, password,'openacademy.session', 'read',[ids], {'fields': ['name', 'course_id', 'taken_seats']})
models.execute_kw(db, uid, password,'openacademy.course', 'read',[ids], {'fields': ['name', 'responsible_id']})
################################
models.execute_kw(db, uid, password, 'openacademy.course', 'fields_get',[], {'attributes': ['string']})
########################################
models.execute_kw(db, uid, password,'openacademy.course', 'search_read',[[['responsible_id', '=', 'User2']]],{'fields': ['name'], 'limit': 5})
####Create
id = models.execute_kw(db, uid, password, 'openacademy.course', 'create', [{'name': "SOCIOLOGIE", '},])
################ADD A RECORD #########################
id = models.execute_kw(db, uid, password, 'res.partner', 'create', [{'name': "New Partner",}])

id20 = models.execute_kw(db, uid, password, 'openacademy.course', 'create', [{'name': "SOCIO", 'responsible_id' : 2}])


################update A RECORD #########################
models.execute_kw(db, uid, password, 'openacademy.course', 'write', [[id], {'name': "GEOLO"}])
#########################################################
models.execute_kw(db, uid, password,'openacademy.session', 'search',[[]])
ids = models.execute_kw(db, uid, password,'openacademy.session', 'search',[[['id', '=', 4]]])
ids_attendees = models.execute_kw(db, uid, password,'openacademy.session', 'read',[ids], {'fields': ['attendee_ids']})
models.execute_kw(db, uid, password,'res.partner', 'search_read',[[['id', 'in', ids_attendees[0]['attendee_ids']]]], {'fields': ['name']})

#############DELETE A RECORD###########"

models.execute_kw(db, uid, password, 'openacademy.session', 'unlink', [[ids[0]]])
# check if the deleted record is still in the database
models.execute_kw(db, uid, password,'openacademy.session', 'search', [[['id', '=', ids[0]]]])

###################" CREATE A MODELE##########
id = models.execute_kw(db, uid, password, 'ir.model', 'create', [{'name': "modele1",'model': "x_model1",
    'state': 'manual',
}])
models.execute_kw(db, uid, password, 'x_model1', 'fields_get',[], {'attributes': ['string', 'help', 'type']})

models.execute_kw(db, uid, password,'ir.model.fields', 'create', [{'model_id': id,'name': 'x_name',
'ttype': 'char','state':'manual','required': True,}])


record_id = models.execute_kw(db, uid, password,'x_model1', 'create', [{'x_name': "test record",}])

























