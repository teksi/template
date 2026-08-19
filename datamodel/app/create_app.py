#!/usr/bin/env python3
import logging
import os
import re
from argparse import ArgumentParser, BooleanOptionalAction
from pathlib import Path

import psycopg
from pum import HookBase

# from triggers.set_defaults_and_triggers import set_defaults_and_triggers
# from view.vw_temp_additional_ws import vw_temp_additional_ws
# from view.vw_temp_channel import vw_temp_channel
# from view.vw_temp_damage_channel import vw_temp_damage_channel
# from view.vw_temp_infiltration_installation import vw_temp_infiltration_installation
# from view.vw_temp_measurement_series import vw_temp_measurement_series
# from view.vw_temp_reach import vw_temp_reach

logger = logging.getLogger(__name__)


class Hook(HookBase):
    def run_hook(
        self,
        connection: psycopg.Connection,
        SRID: int = 2056,
        lang_code: str = "en",
    ):
        """
        Creates the schema temp_app for TEKSI Wastewater & GEP
        :param SRID: the EPSG code for geometry columns
        """
        self.cwd = Path(__file__).parent.resolve()
        self.connection = connection

        self.variables_sql = {
            "SRID": {
                "value": f"{SRID}",
                "type": "number",
            },
            "value_lang": {
                "value": f"value_{lang_code}",
                "type": "identifier",
            },
            "abbr_lang": {
                "value": f"abbr_{lang_code}",
                "type": "identifier",
            },
            "description_lang": {
                "value": f"description_{lang_code}",
                "type": "identifier",
            },
            "display_lang": {
                "value": f"display_{lang_code}",
                "type": "identifier",
            },
        }

        self.execute("CREATE SCHEMA temp_app;")
        self.run_sql_files_in_folder(self.cwd / "sql_functions")

        # defaults = {"view_schema": "temp_app"}

        # SingleInheritances = {
        #     # structure parts
        #     "access_aid": "structure_part",
        # }

        # default values
        # self.execute(cwd / "view/set_default_value_for_views.sql")

        # Audit
        # self.execute(cwd / "audit/audit.sql")

        # Roles
        self.run_sql_files_in_folder(self.cwd / "roles")

    def run_sql_file(self, file_path: str, variables: dict = None):
        with open(file_path) as f:
            sql = f.read()
        self.run_sql(sql, variables)

    def run_sql(self, sql: str, variables: dict = None):
        if variables is None:
            variables = {}
        if (
            re.search(r"\{[A-Za-z-_]+\}", sql) and variables
        ):  # avoid formatting if no variables are present
            try:
                sql = psycopg.sql.SQL(sql).format(**variables).as_string(self.connection)

            except IndexError:
                logger.critical(sql)
                raise
        self.execute(sql)

    def run_sql_files_in_folder(self, directory: str):
        files = os.listdir(directory)
        files.sort()
        sql_vars = self.parse_variables(self.variables_sql)
        for file in files:
            filename = os.fsdecode(file)
            if filename.lower().endswith(".sql"):
                logger.info(f"Running {filename}")
                self.run_sql_file(os.path.join(directory, filename), sql_vars)

    def parse_variables(self, variables: dict) -> dict:
        """Parse variables based on their defined types in the YAML."""
        formatted_vars = {}

        for key, meta in variables.items():
            if isinstance(meta, dict) and "value" in meta and "type" in meta:
                value, var_type = meta["value"], meta["type"].lower()

                if var_type == "number":  # Directly insert SQL without escaping
                    if not re.match(r"^[\d.]*$", value):  # avoid injection
                        raise ValueError(f"Number '{value}' contains invalid characters.")
                    formatted_vars[key] = psycopg.sql.SQL(value)
                elif var_type == "identifier":  # Table/Column names
                    if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", value):  # avoid injection
                        raise ValueError(f"Identifier '{value}' contains invalid characters.")
                    formatted_vars[key] = psycopg.sql.Identifier(value)
                elif var_type == "literal":  # String/Number literals
                    formatted_vars[key] = psycopg.sql.Literal(value)
                else:
                    raise ValueError(f"Unknown type '{var_type}' for variable '{key}'")
            else:
                raise ValueError(f"Unknown type '{var_type}' for variable '{key}'.")
        return formatted_vars


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-p", "--pg_service", help="postgres service")
    parser.add_argument(
        "-s", "--srid", help="SRID EPSG code, defaults to 2056", type=int, default=2056
    )
    parser.add_argument(
        "-d",
        "--drop-schema",
        help="Drops cascaded any existing temp_app schema",
        default=False,
        action=BooleanOptionalAction,
    )
    args = parser.parse_args()

    with psycopg.connect(service=args.pg_service) as connection:
        if args.drop_schema:
            connection.execute("DROP SCHEMA IF EXISTS temp_app CASCADE;")
        hook = Hook()
        hook.run_hook(
            connection=connection,
            SRID=args.srid,
        )
