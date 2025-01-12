# Prompt Builder User Guide

A comprehensive guide to using the Prompt Builder library for dynamic template management.

## Overview

The Prompt Builder is a tool that manages template files containing placeholders and builds complete prompts by replacing these placeholders with specified values.

## Getting Started

### 1. Directory Structure

First, create your prompt template files following this structure:

```bash
prompts/
└── example/
    ├── info/
    │   ├── general.md
    │   ├── name.md
    │   └── version.md
    └── main.md
```

> **Note**:
    The important thing is to place the files and folders under `/prompts`, the rest is up to you.

### 2. Creating Template Files

#### Main Prompt Template (`prompts/example/main.md`)
```md
@__symbol__:version
@__symbol__:general
User name is @__parameter__:username
```

#### Supporting Templates
- `prompts/example/info/general.md`:

```md
This is a general documentation.
Project is named @__symbol__:name
```

- `prompts/example/info/version.md`:

```md
**Version:** 1.0.0
```

- `prompts/example/info/name.md`:

```md
**Prompter**
```

### 3. Template Configuration

Define the mapping between symbols and file paths in `config/templates.yaml`:

```yaml
templates:
  - flag_name: "symbol"
    var_name: "name"
    template: "example/info/name.md"
  
  - flag_name: "symbol"
    var_name: "version"
    template: "example/info/version.md"
  
  - flag_name: "symbol"
    var_name: "general"
    template: "example/info/general.md"
  
  - flag_name: "symbol"
    var_name: "example_prompt"
    template: "example/main.md"
```

> **Note:** Each `var_name` must be unique within the configuration.

### 4. Using the Builder

```python
from .builder import PromptBuilder, PromptBuildError

builder = PromptBuilder()
try:
    prompt = builder.build("example_prompt", username="John")
    print(prompt)
    
except PromptBuildError as e:
    print("Error building prompt:")
    print(e)
```

#### Expected output
```md
**Version:** 1.0.0
This is a general documentation.
Project is named **Prompter**
User name is John
```

## Advanced Usage: Dynamic Folders

### Template Structure with Multiple Similar Folders

You can use parameterized paths for similar folder structures:

```bash
prompts/
└── example/
    ├── folder1/
    │   └── prompt.md
    └── folder2/
        └── prompt.md
```

### Configuration with Dynamic Paths

Configure templates using path parameters in `config/templates.yaml`:

```yaml
templates:
  - flag_name: "symbol"
    var_name: "example_prompt"
    template: "example/{folder_name}/prompt.md"
```

### Implementation

```python
builder = PromptBuilder()
try:
    # Specify the folder name as a parameter
    prompt = builder.build("example_prompt", folder_name="folder1")
    print(prompt)
    
except PromptBuildError as e:
    print("Error building prompt:")
    print(e)
```

## Template Syntax

- Symbol placeholders: `@__symbol__:name`
- Parameter placeholders: `@__parameter__:parameter_name`

The builder will replace these placeholders with their corresponding values during the build process.
