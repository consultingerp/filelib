# Copyright 2017-2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "MIS Builder YDDemo",
    "summary": """
        YDDemo addon for MIS Builder""",
    "version": "12.0.3.1.0",
    "license": "AGPL-3",
    "author": "E2yun",
    "website": "https://e2yun.com",
    "depends": ["mis_builder_budget", "analytic"],
    "data": [
        "security/mis_analytic.xml",
        "views/mis_analytic.xml",
    ],
    "installable": True,
    "maintainers": ["joytao"],
    "development_status": "Alpha",
}
