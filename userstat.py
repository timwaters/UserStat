#!/usr/bin/python

"""userstat.py - Creates user 'career stats' web page from user summary database
    Copyright (C) 2012 Richard Weait

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

Required:
-f, --filename   output file basename - .html will be appended 
-u, --uid        UID                  - integer
-d, --database   database name

Optional:
--dbhost         database hostname    - defaults to localhost
--dbuser         database username    - defaults to user running script
-p, --password   database password    

"""

import os, sys, pwd
from datetime import datetime
from Cheetah.Template import Template
import argparse
import psycopg2, psycopg2.extras
from time import gmtime, strftime
import shutil
import queries

def debug():
    page.content += '\n === Debug output begins === \n\n'
    page.content += '                 UID =: %s \n'%args.userId
    page.content += 'Output file basename =: %s \n'%args.fileName
    page.content += '      Using DB named =: %s \n'%args.dbName
    page.content += '          Debug set? =: %s \n'%args.debug
    page.content += '\n ===  Debug output ends  === \n'

if __name__ == '__main__':
    argParser = argparse.ArgumentParser(description="Parse OSM Changeset metadata into a database")
    argParser.add_argument('--dbhost', action='store', dest='dbHost',
                           help='Database hostname')
    argParser.add_argument('--dbuser', action='store', dest='dbUser',
                           default=pwd.getpwuid(os.getuid())[0],
                           help='Database username (default: OS username)')
    argParser.add_argument('-p', '--password', action='store',
                           dest='dbPass', default='',
                           help='Database password (default: blank)')
    argParser.add_argument('-d', '--database', action='store',
                           dest='dbName', help='Target database', required=True)
    argParser.add_argument('--debug', action='store_true',default=False,
                           dest='debug', help='print extra debug info')
    argParser.add_argument('-u', '--uid', action = 'store',dest='userId',
                           help = 'UserID - integer', required = True)
    argParser.add_argument('-f', '--filename', action = 'store',dest='fileName',
                           help = 'Output file basename', required = True)
    args = argParser.parse_args()

    if args.dbHost:
        conn = psycopg2.connect(database=args.dbName, user=args.dbUser,
                                password=args.dbPass, host=args.dbHost)
    else:
        conn = psycopg2.connect(database=args.dbName, user=args.dbUser,
                                password=args.dbPass)

cursor = conn.cursor()

page = Template( file = './templates/simple-user.tmpl' )

page.sparkstart = """    $(function() {"""
page.sparkbody = ""
page.sparkstop = """    });"""

page.title = "Mapper career statistics for '%s'"%args.userId
page.content = ''
page.swVersion = '0.01'
page.now = datetime.now()
page.year = page.now.year

print "Debug? ::%s"%args.debug

if args.debug:
    debug()

page.userId = args.userId
page.filename = args.fileName
page.dbname = args.dbName

def datalicense():
    page.datalicense = Template( file='./templates/legal.tmpl')
    page.datalicense.year = page.now.year
    page.datalicense.time = page.now.strftime("%Y-%m-%d %H:%M")
    page.datalicense.swVersion = '0.01'

def editorpiechart():
    """ create table and piechart of editors used by mapper """
    # select the editors and numbers of changesets per editor from the database
    cursor.execute(queries.editorpiechart, (args.userId,))
    dbresult=dict()
    dblist = cursor.fetchall()
    print "dblist:: %s"%dblist
    for v,k in dblist:
        dbresult[k]=v
        editorpiechartstring=(',').join([str(x[0]) for x in dblist])
    conn.commit()
    print 'DB result :: \n %s'%dbresult
    page.sparkbody += "$('.inlinesparkpie').sparkline('html', {type: 'pie', sliceColors: ['#999','#ccc','#333','#aaa','#ddd','#666','#bbb','#eee'], height: '6em'});" '\n'
    page.editorpiechart = Template( file = './templates/editorpiechart.tmpl')
    page.editorpiechart.editorpiechartstring = editorpiechartstring
    page.editorpiechart.editors = dbresult

def username(userId):
    cursor.execute(queries.username, (userId,))
    userName = str(cursor.fetchall()).strip('[]').strip('(),')
    conn.commit()
    return userName

page.userName = username(args.userId)
editorpiechart()
datalicense()

conn.close()

print page

s = str(page)

f = open('./html/%s.html'%args.fileName, 'w')
f.write(s)
f.close()

