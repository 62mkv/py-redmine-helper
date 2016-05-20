# -*- coding: utf-8 -*-

tables = {}

tables['activities'] = {
    1: u'Аналитика, research',
    2: u'Прототипирование',
    3: u'Дизайн',
    4: u'Верстка',
    5: u'Разработка',
    6: u'QA',
    7: u'Документирование',
    8: u'Обсуждение',
    9: u'ПМ / team-lead',
    10: u'Поддержка, обслуживание',
    11: u'Обучение',
}

tables['trackers'] = {
    1: 'Bug',
    2: 'Improvement',
    3: 'Incident',
    4: 'User Story',
    5: 'Maintenance',
    6: 'QA',
    7: 'Other'
}

tables['users'] = {
}

redmine_user_mapping = {
    ('ER',125): 72,
    ('ER',131): 48,
    ('ER',142): 47,
    ('ER',158): 20,
    ('ER',161): 60,
    ('ER',163): 56,
    ('ER',190): 76,
    ('ER',129): 59,
    ('ER',148): 37,
    ('ER',151): 58,
    ('ER',178): 39,
    ('ER',179): 41,
    ('ER',192): 65,
    ('ER',193): 69,
    ('ER',185): 34,
    ('ER',186): 70,
    ('ER',113): 3,
    ('ER',188): 25,
    ('ER',196): 36,
    ('ER',198): 90,
    ('ER',111): 30,
    ('ER',140): 17,
    ('ER',145): 46
}

redmine_activity_mapping = { 
     ('FM',9): 5,
     ('FM',8): 1, 
     ('FM',10): 6,
     ('FM',11): 8,
     ('FM',12): 10,
     ('ER',8): 2,
     ('ER',9): 5,
     ('ER',10): 10,
     ('ER',11): 9,
     ('ER',12): 6,
     ('ER',13): 10,
     ('ER',14): 1,
     ('ER',16): 7,
     ('ER',17): 5
}

redmine_tracker_mapping = {
    ('ER',1): 1,
    ('ER',3): 2,
    ('ER',4): 4,
    ('ER',5): 3,
    ('ER',6): 5,
    ('ER',7): 6,
    ('ER',8): 7,
    ('FM',2): 2,
    ('FM',6): 2,
    ('FM',1): 1,
    ('FM',3): 5,
    ('FM',7): 6,
    ('FM',8): 7
}

mappings = {
  'activity': { 'table': 'activities', 'data': redmine_activity_mapping}, 
  'tracker': { 'table': 'trackers', 'data': redmine_tracker_mapping},
  'user': { 'table': 'users', 'data': redmine_user_mapping}
}

if __name__ == '__main__':

# print DDL/DML for detail tables
    for table in tables:
        print """
CREATE TABLE "{}" (
	`id`	INTEGER,
	`name`	TEXT
);\n""".format(table)
        for k, v in tables[table].items():
            print "INSERT OR REPLACE INTO {} ({}, {}) VALUES ({}, '{}');".format(table, 'id', 'name', k, v)

# print DDL/DML for mapping tables
    for mapping in mappings.keys():
        table_name = 'redmine_'+mappings[mapping]['table']
        field_id = mapping+'_id'
        field_redmine_id = 'redmine_'+mapping+'_id'
        print """
CREATE TABLE "{}" (
	`{}`	INTEGER,
	`redmine`	TEXT,
	`{}`	INTEGER
);\n""".format(table_name, field_id, field_redmine_id)
        print """
CREATE UNIQUE INDEX {} ON {}(redmine, {});
""".format('unique_rm_'+mappings[mapping]['table'], table_name, field_redmine_id)

        for rm, rm_id in mappings[mapping]['data'].keys():
            print "INSERT OR REPLACE INTO {} ({}, redmine, {}) VALUES ({}, '{}', {});".format(table_name, field_redmine_id, field_id, rm_id, rm, mappings[mapping]['data'][(rm, rm_id)])
