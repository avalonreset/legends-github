# DataForSEO setup

Live research now uses the public legends-dataforseo-kit Python dependency.
Run `python -m pip install -r requirements-dataforseo.txt` from the toolkit root.
Set `DATAFORSEO_LOGIN` (or `DATAFORSEO_USERNAME`) and `DATAFORSEO_PASSWORD` in
your environment. No MCP server or model-specific configuration is required.

Follow [the measured research workflow](../../../docs/SEO-RESEARCH.md).
The extension installer paths remain as compatibility wrappers around this
package installation. They never request or store credentials.

Existing MCP configuration is left untouched; remove it yourself if no other
workflow uses it. The toolkit no longer installs or invokes it. Paid calls
require an explicit research execution flag and an estimated spending ceiling.
