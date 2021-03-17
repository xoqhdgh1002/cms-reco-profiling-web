import sqlite3
import sys

def children(cmssw,step):

	path = "/eos/project/c/cmsweb/www/reco-prof/cgi-bin/data/releases/{0}/23434.21/step{1}/cpu.sql3".format(cmssw,step)
	conn = sqlite3.connect(path)
	cur = conn.cursor()
	cur.execute("SELECT s.name,mr.id FROM mainrows mr INNER JOIN symbols s ON s.id IN(mr.symbol_id)")

	rows = cur.fetchall()

	child = []

	for row in rows:

		if "doEvent" in row[0]:
			cur.execute("""SELECT c.self_id, sym.name,
					mr.cumulative_count,
					c.pct
				FROM children c
				INNER JOIN mainrows mr ON mr.id IN (c.parent_id)
				INNER JOIN mainrows myself ON myself.id IN (c.self_id)
				INNER JOIN symbols sym ON sym.id IN (myself.symbol_id)
				WHERE c.parent_id = %s
				ORDER BY c.from_parent_count DESC;
				""" % row[1])

		child += cur.fetchall()

	return child

print(children("CMSSW_11_3_0_pre3",3)[1])
