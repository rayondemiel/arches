"""
ARCHES - a program developed to inventory and manage immovable cultural heritage.
Copyright (C) 2013 J. Paul Getty Trust and World Monuments Fund

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

from datetime import datetime

from arches import __version__
from arches.app.const import IntegrityCheck
from arches.app.models import models
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Exists, OuterRef

DELETE_QUERYSET = "delete queryset"


class Command(BaseCommand):
    """
    Validate an Arches database against a set of data integrity checks.
    Takes no action by default (other than printing a summary).

    Provide --verbosity=2 to get a richer output (list of affected nodes).

    Example: python manage.py validate --fix-all
    """
    help = "Validate an Arches database against a set of data integrity checks, and opt-in to remediation."

    def add_arguments(self, parser):
        choices = [check.value for check in IntegrityCheck]

        parser.add_argument("--fix-all", action="store_true", dest="fix_all", default=False,
                            help="Apply all fix actions.")
        parser.add_argument("--fix", action="extend", nargs="+", type=int, default=[], choices=choices,
                            help="List the error codes to fix, e.g. --fix 1001 1002 ...")
        parser.add_argument("--limit", action="store", type=int,
                            help="Maximum number of rows to print; does not affect fix actions")

    def handle(self, *args, **options):
        self.options = options
        if self.options["limit"] < 1:
            raise CommandError("Limit must be a positive integer.")
        if self.options["limit"] and self.options["verbosity"] < 2:
            # Limit is meaningless w/o the higher verbosity output
            self.options["verbosity"] = 2

        if self.options["verbosity"] > 0:
            self.stdout.write()
            self.stdout.write("Arches integrity report")
            self.stdout.write(f"Prepared by Arches {__version__} on {datetime.today().strftime('%c')}")
            self.stdout.write()
            self.stdout.write("\t".join(["", "Error", "Rows", "Fixed", "Description"]))
            self.stdout.write()

        # Add checks here in numerical order
        self.check_integrity(
            check=IntegrityCheck.NODE_HAS_ONTOLOGY_GRAPH_DOES_NOT,  # 1005
            queryset=models.Node.objects.only("ontologyclass", "graph").filter(
                ontologyclass__isnull=False).filter(graph__ontology=None),
            fix_action=None,
        )
        self.check_integrity(
            check=IntegrityCheck.NODELESS_NODE_GROUP,  # 1012
            queryset=models.NodeGroup.objects.filter(
                ~Exists(models.Node.objects.filter(nodegroup_id=OuterRef("nodegroupid")))
            ),
            fix_action=DELETE_QUERYSET,
        )

    def check_integrity(self, check, queryset, fix_action):
        needs_fix = queryset.exists()
        fix_status = ""
        # Not set as a default: None distinguishes whether verbose output implied
        limit = self.options["limit"] or 500

        if needs_fix:
            if self.options["fix_all"] or check.value in self.options["fix"]:
                if fix_action:
                    if fix_action is DELETE_QUERYSET:
                        with transaction.atomic():
                            queryset.delete()
                        fix_status = self.style.SUCCESS("FIXED")

                    # Implement other fix actions here, e.g. pass in a callable
                    else:
                        raise NotImplementedError
                else:
                    fix_status = self.style.NOTICE("N/A")
            else:
                fix_status = self.style.NOTICE("Skipped")

        if self.options["verbosity"] > 0:
            count = len(queryset)
            result = self.style.ERROR("FAIL") if count else self.style.SUCCESS("PASS")
            self.stdout.write("\t".join(str(x) for x in (result, check.value, count, fix_status, check)))

            if self.options["verbosity"] > 1:
                self.stdout.write("\t" + "-" * 36)
                if queryset:
                    for i, n in enumerate(queryset):
                        if i < limit:
                            self.stdout.write(f"\t{n.pk}")
                        else:
                            self.stdout.write("\t\t(truncated...)")
                            break

            self.stdout.write()
