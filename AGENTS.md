---
description: "Python coding conventions and guidelines"
applyTo: "**/*.py"
project-name: "esi-auth"
---

# Python Coding Conventions

## Python Instructions

- Write clear and concise comments for each function.
- Ensure functions have descriptive names and include type hints.
- Provide docstrings following PEP 257 conventions.
- Break down complex functions into smaller, more manageable functions.
- During development, use the virtual environment found at the project root - `./.venv`
- all code should be typed. eg. `foo:list[int] = [1,2,3]`
- use red/green TDD

## General Instructions

- Always prioritize readability and clarity.
- For algorithm-related code, include explanations of the approach used.
- Write code with good maintainability practices, including comments on why certain design decisions were made.
- Handle edge cases and write clear exception handling.
- For libraries or external dependencies, mention their usage and purpose in comments.
- Use consistent naming conventions and follow language-specific best practices.
- Write concise, efficient, and idiomatic code that is also easily understandable.
- use red/green TDD.

## Code Style and Formatting

- Follow the **PEP 8** style guide for Python.
- Maintain proper indentation (use 4 spaces for each level of indentation).
- Prefer lines do not exceed 88 characters.
- Use blank lines to separate functions, classes, and code blocks where appropriate.
- Code will be formatted and linted using ruff. The configuration is located in the `pyproject.toml`.

## Edge Cases and Testing

- Always include test cases for critical paths of the application.
- Account for common edge cases like empty inputs, invalid data types, and large datasets.
- Include comments for edge cases and the expected behavior in those cases.
- Write unit tests for functions and document them with docstrings explaining the test cases.
- Test data representing the SDE is avaliable at [test data](tests/resources/sde_data/__init__.py)

## Documentation

- Ensure all public functions and classes have appropriate docstrings.
- Use Google style docstrings.
- Include examples in docstrings where applicable.
- Classes with an `__init__` function should have the docstring after that `__init__` function.
- Classes without an `__init__` function should have the docstring immediately following the class definition.

# Project Specific Information

NOTE: NEEDS TO BE UPDATED.

## Project Overview

eve-static-data provides a cli interface for downloading and processing the EVE Online static data set. Information about this
data set can be found at https://developers.eveonline.com/docs/services/static-data/

### CLI Commands:
 - root
   - version - Get version information for the app.
 - sde
   - local
     - status
       Get the status of the local imported copy of the sde in a particular folder, and optionaly compare it to the latest available version.
     - print
       Print the selected dataset to the terminal
     - import
       Import a downloaded and extracted dataset to a specifed folder, with the selected language.
     - export
       Placeholder - Possibly export some tables as csv, combined tables, market-path, market categories eg. blueprints, regions-name, etc.
   - network
     - status
       Download and display the latest available sde data.
     - download
       Download the sde, defaults to latest jsonl, but yaml and/or specific builds are selectable.
     - schema-changelog
       Download and display the schema changelog.
   - dev
     - Placeholder
     - validate
       validate jsonl file against TypedDict and BaseModel
     - validate-all

### API

- Provides TypedDicts and pydantic BaseModels for the jsonl sde files.
- Provides pydantic BaseModels for the imported data.
- Provides an iterable access api for the sde jsonl files, with untyped, TypedDict, and pydantic BaseModel versions.
- Provides a lazy-loading access class for the imported data, with pydantic models.




## Project Dependencies


- pydantic-settings is used to manage application settings.
- typer is used to provide the cli interface
- whenever is used to interact with datetimes

## Conventions

- test files are located in `tests/eve_static_data/`, and the test file layout mirrors the src file layout when possible.
