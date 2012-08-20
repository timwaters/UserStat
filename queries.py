""" queries.py 
    auxilliary file for SQL quries
"""

editorpiechart = """SELECT count(changeset_id) AS count,substring(value from '^[^ /]*') 
FROM osm_changeset, osm_changeset_tags 
WHERE user_id=%s 
  AND changeset_id=id 
  AND key='created_by' 
GROUP BY substring(value from '^[^ /]*') 
ORDER BY count DESC;"""

username = """SELECT DISTINCT user_name
FROM osm_changeset 
WHERE user_id=%s;
"""
