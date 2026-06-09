# 004 - learnings

The first peer-reply implementation made the live run do too much by default: even when the
operator only wanted the main post inserted, the handoff still evaluated classmates, drafted
two replies, and opened all three files. Separating intent before extraction keeps the portal
automation smaller and makes the slow part proportional to the actual job the operator chose.
