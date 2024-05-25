# ai-screenshot-namer

Rename screenshots using VLMs and your macOS image text extraction.

See [the vxlabs blog post](http://localhost:1313/2024/05/25/ai-screenshot-renamer-with-ollama-llava-gpt-4o-and-macos-ocr/) for more detail.

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

### If you're going to use OpenAI

Acquire an API key.

Set the environment variable:

```shell
export OPENAI_API_KEY=sk-proj-xxxx
```

### Install ai-screenshot-renamer

Install pipx: [How to install pipx](https://pipx.pypa.io/stable/installation/#installing-pipx)

Install ai-screenshot-namer:

```shell
pipx install git+https://github.com/cpbotha/ai-screenshot-namer.git
```

### Rename screenshots!

```shell
ai-rename --help
# ollama, suggest rename
ai-rename some-screenshot.png
# ollama, do rename
ai-rename --do-rename some-screenshot.png
# openai, rename a whole bunch of screenshots
ai-rename --use-openai --do-rename *.png
```
