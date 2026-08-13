# Technical quality and retries

Generation success means the backend completed and produced a readable output.
It does not mean the image is editorially acceptable.

## Technical checks

After generation verify:

- process exit status;
- output file exists and is non-empty;
- output extension matches requested target;
- dimensions are plausible when metadata can be read;
- metadata sidecar was written when requested;
- no temporary file was reported as the final asset;
- no secret/environment dump appears in captured output.

## Retry classes

Retry only bounded transient technical failures such as an interrupted local
process when the backend explicitly reports a retryable state. Do not retry:

- invalid configuration;
- model not installed;
- license not approved;
- unsupported role/aspect;
- missing input image;
- invalid output path;
- permanent backend error.

Quality retries must be driven by caller diagnosis and a revised brief. Do not
regenerate the same prompt hoping for luck.

## Upscaling

Upscale only when the configured upscaler exists and the caller requests it or
publication needs justify it. Never represent upscaling as recovery of factual
detail that was not present in the source.
