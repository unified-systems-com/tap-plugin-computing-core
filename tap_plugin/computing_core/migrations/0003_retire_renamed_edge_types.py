"""Delete edges of the two edge types renamed in the edge-naming wave (computing-core#4).

`HOSTED_BY` became `HOSTS_DOCUMENT` (direction flipped: host -> document) and `FETCHES` became
`FETCHES_DOCUMENT`. computing_core emits neither itself, but consumers land them on a grid —
samsite's compliance collector derives the FETCHES edge id from the slug and its GRIFT seed
carries HOSTED_BY — so a renamed type is a NEW edge on the next collection or seed and the old
rows would linger as unregistered types nothing reads. This removes them (with their spine rows)
so a grid upgraded in place is not left carrying two generations of the same relation; the next
collection / seed repopulates the new types. Nodes are untouched.

Precedent: github_core migration 0013 (github-core#79). Direct ORM access is the sanctioned path
in migrations.
"""

from typing import Any

from django.db import migrations

_RETIRED_EDGE_TYPES = (
    "HOSTED_BY__computing_core",
    "FETCHES__computing_core",
)


def delete_retired_edges(apps: Any, schema_editor: Any) -> None:
    Edge = apps.get_model("tap_grid", "Edge")
    Entity = apps.get_model("tap_grid", "Entity")
    edges = Edge.objects.filter(edge_type__in=_RETIRED_EDGE_TYPES)
    entity_ids = list(edges.values_list("entity_id", flat=True))
    edges.delete()
    Entity.objects.filter(pk__in=entity_ids).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("computing_core", "0002_initial"),
        ("tap_grid", "0001_initial"),
    ]

    operations = [migrations.RunPython(delete_retired_edges, migrations.RunPython.noop)]
