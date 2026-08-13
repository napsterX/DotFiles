# Model licensing

Publicly downloadable weights are not automatically approved for commercial
asset generation.

For every configured production model record:

- model/source identifier;
- license name or reference;
- known commercial-use conditions;
- attribution requirements;
- restrictions on generated outputs where known;
- review date;
- `license_approved = true|false`.

`ai-image` must refuse production generation when the selected role/model is not
explicitly approved. Unknown means not approved.

This package does not make legal conclusions about model licenses. The runtime
setup task must populate the model records based on the actual selected model
licenses and intended use.
