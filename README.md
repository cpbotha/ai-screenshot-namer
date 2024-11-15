# ai-screenshot-namer

Rename screenshots using VLMs and your macOS image text extraction.

See [the vxlabs blog post](https://vxlabs.com/2024/05/25/ai-screenshot-renamer-with-ollama-llava-gpt-4o-and-macos-ocr/) for more detail.

## Quickstart

### If you're going to use local models

Install ollama: [Download ollama](https://ollama.com/download)

Download the llava-phi3 model:

```shell
ollama pull llava-phi3
```

Start the server:

```shell
ollama start
```

#### Configure a different local model

```shell
ollama pull llama-3.2-vision
export AISN_MODEL=llama-3.2-vision
```

### If you're going to use OpenAI

Acquire an API key.

Set the environment variable:

```shell
export AISN_OPENAI_API_KEY=sk-proj-xxxx
```

### If you're going to use an alternative provider like OpenRouter

```shell
export AISN_OPENAI_API_KEY=sk-or-v1-bleh-bleh-bleh
export AISN_OPENAI_BASE_URL=https://openrouter.ai/api/v1
export AISN_OPENAI_MODEL=openai/gpt-4o-mini
```

### If you want to use macOS text extraction

This uses macOS to extract text from the target screenshot, and adds this to the image prompt to increase the model's chances of coming up with a good name.

To get this part working, [install my very simple shortcut](https://www.icloud.com/shortcuts/8ca57fbab726476f90c85f40fa7b40f2).

The tool will still work without this, just not as well (especially the local models).

See [the relevant section of my blog post](https://vxlabs.com/2024/05/25/ai-screenshot-renamer-with-ollama-llava-gpt-4o-and-macos-ocr/#macos-shortcut-for-command-line-extraction-of-text-from-images) for more detail.

### Install ai-screenshot-renamer

Use either uv (my preference, also for dev!):

- [How to install uv](https://docs.astral.sh/uv/getting-started/installation/)
- `uv tool install git+https://github.com/cpbotha/ai-screenshot-namer.git`

... or pipx:

- [How to install pipx](https://pipx.pypa.io/stable/installation/#installing-pipx)
- `pipx install git+https://github.com/cpbotha/ai-screenshot-namer.git`

### Rename some screenshots

```shell
ai-rename --help
# ollama, suggest rename
ai-rename some-screenshot.png
# ollama, do rename
ai-rename --do-rename some-screenshot.png
# openai, rename a whole bunch of screenshots
# if ASN_OPENAI_MODEL is defined (e.g. "gpt-4o-mini" for openai or "openai/gpt-4o-mini" for openrouter), --use-openai is assumed
ai-rename --use-openai --do-rename *.png
```
