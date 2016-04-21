import cavaconn as cc
import json
import logging
import sys
import simplejson

def get_children(table_name, cursor_pg):

    query = """SELECT distinct dependee.relname
                    FROM pg_depend
                    JOIN pg_rewrite ON pg_depend.objid = pg_rewrite.oid
                    JOIN pg_class as dependee ON pg_rewrite.ev_class = dependee.oid
                    JOIN pg_class as dependent ON pg_depend.refobjid = dependent.oid
                    JOIN pg_attribute ON pg_depend.refobjid = pg_attribute.attrelid
                    AND pg_depend.refobjsubid = pg_attribute.attnum
                    WHERE dependent.relname = '{}'
                    AND pg_attribute.attnum > 0 ; """

    cursor_pg.execute(query.format(table_name))
    return cursor_pg.fetchall()

def bobby_drop_tables(table_name, table_type, cursor_pg):

    query = """drop {} {} CASCADE; """
    try:
        cursor_pg.execute(query.format(table_type, table_name))
    except:
        logging.error('Failed to Drop Table')

def build_parents(parent_type, parent_name, parent_query, cursor_pg):

    cursor_pg.execute("create {} {} as {};".format(parent_type, parent_name, parent_query))

def find_children(table_name, table_type, parent_query, cursor_pg):

    children = get_children(table_name,cursor_pg)
    children_names = []

    for child in children:
        query = """select matviewname, definition from pg_matviews where matviewname = '{}';"""
        cursor_pg.execute(query.format(child[0]))
        result = cursor_pg.fetchall()
        child_type = "materialized view"

        # If this is returning a Zero, it means the dependency is probably a view, so
        # lets now search the views to get a sense of what the definition is

        if len(result) == 0:
            query = """select viewname, definition from pg_views where viewname = '{}';"""
            cursor_pg.execute(query.format(child[0]))
            result = cursor_pg.fetchall()
            child_type = "view"

        children_names.append({'defined': result[0][1],
                               'given_name': child[0],
                               'child_type': child_type})

    safety_first =  open('safety_first.txt','w')
    simplejson.dump(children_names,safety_first)
    safety_first.close()
    return children_names

def birth_children(children_names, table_name, cursor_g):

    for child in children_names:
        cursor_pg.execute("create {} {} as {};".format(str(child['child_type']),
                                                       child['given_name'],
                                                       child['defined']))

if __name__ == '__main__':

    if len(sys.argv) > 1:
        table_name = sys.argv[1]
        table_type = sys.argv[2]
        q = open(sys.argv[3]).read()
        conn_pg  = cc.get_connection('/opt/configs/server_info.yml', sys.argv[4])
        conn_pg.set_isolation_level(0)
        cursor_pg = conn_pg.cursor()

    else:
        with open('rebirth.json') as data_file:
            data = json.load(data_file)
            table_name = data['table_name']
            table_type = data['table_type']
            q = data['replace_query']
            conn_pg  = cc.get_connection('/opt/configs/server_info.yml',data['database'])
            conn_pg.set_isolation_level(0)
            cursor_pg = conn_pg.cursor()

    children = find_children(table_name, table_type, q, cursor_pg)
    bobby_drop_tables(table_name, table_type, cursor_pg)
    build_parents(table_type, table_name, q, cursor_pg)
    birth_children(children, table_name, cursor_pg)

