import sqlite3
import sys

conn = sqlite3.connect("igprofCPU_CMSSW_11_3_0_pre2.sql3")

cur = conn.cursor()

cur.execute("SELECT * FROM symbols")

cn=1

for i in cur.fetchall():
	if "edm::one::OutputModuleBase::doEvent(edm::EventTransitionInfo const&, edm::ActivityRegistry*, edm::ModuleCallingContext const*)" in i[1]:

		cur.fetchall().index(i)
		cur.execute("""SELECT c.self_id, sym.name,
		c.from_parent_count, myself.cumulative_count,
		c.from_parent_calls, myself.total_calls,
		c.from_parent_paths, myself.total_paths,
		mr.cumulative_count,
		c.pct
		FROM children c
		INNER JOIN mainrows mr ON mr.id IN (c.parent_id)
		INNER JOIN mainrows myself ON myself.id IN (c.self_id)
		INNER JOIN symbols sym ON sym.id IN (myself.symbol_id)
		WHERE c.parent_id = %s
		ORDER BY c.from_parent_count DESC;
		""" % cn)

		print(type(cur.fetchall()))
	cn+=1

