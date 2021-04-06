import sqlite3
import sys
import pandas as pd

path = "/eos/project/c/cmsweb/www/reco-prof/cgi-bin/data/releases/{0}/23434.21/step{1}/cpu.sql3".format(sys.argv[1],sys.argv[2])
conn = sqlite3.connect(path)
cur = conn.cursor()

cur.execute("SELECT summary.tick_period FROM summary")
tick_period = cur.fetchone()[0]
print(tick_period)

cur.execute("SELECT s.name,mr.id FROM mainrows mr INNER JOIN symbols s ON s.id IN(mr.symbol_id)")
rows = cur.fetchall()

child = []

for row in rows:

	if "doEvent" in row[0]:
		print(row[1])
		cur.execute("""SELECT c.self_id, sym.name,
				myself.cumulative_count,
				c.pct
			FROM children c
			INNER JOIN mainrows mr ON mr.id IN (c.parent_id)
			INNER JOIN mainrows myself ON myself.id IN (c.self_id)
			INNER JOIN symbols sym ON sym.id IN (myself.symbol_id)
			WHERE c.parent_id = %s
			ORDER BY c.from_parent_count DESC;
			""" % row[1])

	child += cur.fetchall()

sorted(child,key=lambda child: child[2])

child = pd.DataFrame(child)
child.columns = ['id','name','cumulative','pct']
child['cumulative'] = child['cumulative']*tick_period

child.to_csv("{0}_step{1}.csv".format(sys.argv[1],sys.argv[2]))

