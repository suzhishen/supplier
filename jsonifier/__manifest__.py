{
    "name": "JSONifier",
    "summary": "JSON-ify data for all models",
    "version": "16.0.0.0.0",
    "category": "Fast/Fast",
    "website": "",
    "author": "fast",
    "license": "LGPL-3",
    "installable": True,
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "views/ir_exports_view.xml",
        "views/ir_exports_resolver_view.xml",
    ],
    "demo": [
        "demo/resolver_demo.xml",
        "demo/export_demo.xml",
        "demo/ir.exports.line.csv",
    ],
}
