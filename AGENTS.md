# AGENTS.md

## General instructions

Follow these instructions when making code changes in this repository.

## Code quality

- Keep code clean, readable, and easy to understand.
- Use clear and meaningful names for variables, functions, classes, files, and modules.
- Preserve the current coding style and project structure.
- Follow existing patterns in the codebase instead of introducing new ones unnecessarily.
- Prefer simple, maintainable code over clever or complex solutions like it is written by a Senior engineer and not any coding agent. Always add one line comments over the code wherever it's necessary. The code should always be readable and beginner friendly but it should be a perfect code and should be scalable, robust and clean.

## Naming

- Use clean and descriptive names.
- Do not use a leading underscore `_` in front of function names, variable names, class names, or method names unless it is clearly required by the existing code style, framework convention, or language behavior.
- Do not rename existing symbols unless the requested change specifically requires it.
- Keep naming consistent with nearby code.

## Scope of changes

- Make the smallest safe change needed to complete the request.
- Prefer small, focused, reviewable changes over broad rewrites.
- Do not make extra code changes beyond what was asked.
- Do not perform unrelated refactoring, formatting, renaming, or cleanup.
- Do not change public APIs, behavior, configuration, or dependencies unless required for the task.
- Avoid modifying files that are unrelated to the requested change.

## Tests

- Check whether tests need to be added or updated for the change.
- Add or update tests when the change affects behavior, validation, edge cases, APIs, infrastructure logic, or bug fixes.
- Do not add unnecessary tests for purely cosmetic or documentation-only changes.
- Run the most relevant existing tests when possible.
- Do not claim that tests passed unless they were actually run.

## Manual testing instructions

After completing the change, explain how the user can manually test it.

Include:

- what behavior changed
- what command or steps to run
- what result the user should expect
- any important edge cases to verify manually

## Final response

When finished, summarize:

- what changed
- which files were changed
- whether tests were added or updated
- which tests or checks were run
- how to manually test the change
- any risks, assumptions, or follow-up items

Keep the final response clear and concise.