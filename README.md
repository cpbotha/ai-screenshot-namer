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

### If you're going to use OpenAI

Acquire an API key.

Set the environment variable:

```shell
export OPENAI_API_KEY=sk-proj-xxxx
```

### If you want to use macOS text extraction

This uses macOS to extract text from the target screenshot, and adds this to the image prompt to increase the model's chances of coming up with a good name.

To get this part working, [install my very simple shortcut](https://www.icloud.com/shortcuts/8ca57fbab726476f90c85f40fa7b40f2).

The tool will still work without this, just not as well.

See [the relevant section of my blog post](https://vxlabs.com/2024/05/25/ai-screenshot-renamer-with-ollama-llava-gpt-4o-and-macos-ocr/#macos-shortcut-for-command-line-extraction-of-text-from-images) for more detail.

### Install ai-screenshot-renamer

Install pipx: [How to install pipx](https://pipx.pypa.io/stable/installation/#installing-pipx)

Install ai-screenshot-namer:

```shell
pipx install git+https://github.com/cpbotha/ai-screenshot-namer.git
```

### Rename some screenshots

```shell
ai-rename --help
# ollama, suggest rename
ai-rename some-screenshot.png
# ollama, do rename
ai-rename --do-rename some-screenshot.png
# openai, rename a whole bunch of screenshots
ai-rename --use-openai --do-rename *.png
```
