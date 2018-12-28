#!/usr/bin/python2
import sqlite3
import jinja2
import os
import time
import argparse
import sys, logging, datetime

import pprint
pp = pprint.PrettyPrinter(indent=2)

from jinja2 import Template
from os.path import expanduser
 
class sqlBasic:
  def dict_factory(self, curs, row):
    d = {}
    for idx, col in enumerate(curs.description):
      d[col[0]] = row[idx]
    return d
  def __init__(self, db):
    self.conn = sqlite3.connect(db)
    self.conn.row_factory = self.dict_factory 
    self.curs = self.conn.cursor()
  def run(self, query):
    self.curs.execute(query)
    return self.curs.fetchall()

myname = os.path.splitext(os.path.basename(__file__))[0]

s2s = {}
s2s['ok'] = 1
s2s['failed'] = 2
s2s['skipped'] = 3
s2s['unreachable'] = 4

def parse_args():
  '''Parse arguments'''
  parser = argparse.ArgumentParser(description='ARA host history (for Ansible)')
  parser.add_argument('--db',
                      help='Location of ARA SQLite DB')
  parser.add_argument('--out',
                      help='Output location', default="/srv/www/htdocs/"+myname+".html")
  parser.add_argument('--loglevel',
                      help='Logging level', default="INFO")
  parser.add_argument('--cmdb',
                      help='Path to ansible-cmdb output')
  parser.add_argument('--ara',
                      help='Path to ARA webserver')
  args = parser.parse_args()
  return args

def main():
  args = parse_args()

  logging_level = getattr(logging, args.loglevel.upper(), None)
  if not isinstance(logging_level, int):
    raise ValueError('Invalid log level: %s' % (conf['loglevel']))
  logging.basicConfig(stream=sys.stdout, level=logging_level, format='%(asctime)s %(levelname)s: %(message)s')

  if args.db:
    db = args.db
  else:
    db = expanduser("~") + '/.ara/ansible.sqlite'
  sql = sqlBasic(db)

  # get hosts' histories 
  hosthistory = [] 
  playbooks = sql.run('SELECT h.id AS host_id, pb.id AS playbook_id, * FROM hosts h JOIN playbooks pb ON h.playbook_id=pb.id ORDER BY time_end DESC')
  for playbook in playbooks:
    plays = sql.run('SELECT * FROM plays WHERE playbook_id="%s" ORDER BY sortkey ASC' % (playbook['playbook_id']))
    playbook_plays = []
    for play in plays:
      tasks = sql.run('SELECT * FROM tasks WHERE playbook_id="%s" AND play_id="%s" ORDER BY sortkey ASC' % (playbook['playbook_id'], play['id']))
      play_tasks = []
      for task in tasks:
        task_result = sql.run('SELECT * FROM task_results WHERE task_id="%s"' % (task['id']))
        task['task_result'] = task_result[0]
        play_tasks.append( task )
      play['tasks'] = play_tasks
      playbook_plays.append( play )
    playbook['plays'] = playbook_plays
  
    x = [k for k,v in enumerate(hosthistory) if v[0]['name']==playbook['name']]
    if x:
      logging.debug("Adding playbook %s to host %s list number %d" % (playbook['id'], playbook['name'], x[0]))
      hosthistory[x[0]].append( playbook )
    else:
      logging.debug("Creating new host %s playbook %s" % (playbook['name'], playbook['id']))
      hosthistory.append( [ playbook ] )
  
  # produce overall playbook status and reformat some values
  for i,h in enumerate(hosthistory):
    for pbk, pbv in enumerate(h):
      hosthistory[i][pbk]['time_start'] = hosthistory[i][pbk]['time_start'].split('.')[0]
      if hosthistory[i][pbk]['time_end'] != None:
        hosthistory[i][pbk]['time_end'] = hosthistory[i][pbk]['time_end'].split('.')[0]
      overall_int = s2s['ok']
      overall_out = 'ok'
      for p in pbv['plays']:
        for t in p['tasks']:
          stat = t['task_result']['status']
          if s2s[stat] > overall_int:
            overall_int = s2s[stat]
            overall_out = stat
      hosthistory[i][pbk]['_overall_status'] = overall_out
  
  logging.debug(pp.pformat(hosthistory))
  
  j = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.abspath('.'))
  )
  outfile = open(args.out, 'w')
  tpl_ov = j.get_template(myname + '.tpl')
  tpl_ov.globals['now'] = datetime.datetime.now
  flags = {}
  if args.cmdb:
    flags['cmdb'] = args.cmdb.rstrip('/')
  if args.ara:
    flags['ara'] = args.ara.rstrip('/')
  outfile.write(tpl_ov.render(history=hosthistory, fl=flags))
  outfile.close()
  
if __name__ == "__main__":
  main()

