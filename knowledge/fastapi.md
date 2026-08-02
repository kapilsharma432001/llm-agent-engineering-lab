# FastAPI Interview Notes

## Request lifecycle and validation

FastAPI matches an incoming request to a path operation, extracts values from
the path, query string, headers, cookies, or body, and validates them using type
annotations and Pydantic models. Invalid input normally produces a structured
422 response before the endpoint function runs. The function's return value is
then serialized, optionally validated against a response model, and sent through
the ASGI server.

## Dependency injection

FastAPI dependency injection is based on callables declared with Depends. Before
calling the endpoint, FastAPI inspects the dependency graph, resolves required
sub-dependencies, validates their inputs, and passes each result into the
dependent function. Dependencies can be normal functions, async functions,
classes, or callable objects.

A dependency is normally evaluated once per request and its result is cached for
other dependants in the same request. Set use_cache to false when a dependency
must run again. Dependencies that yield a value can place cleanup logic after
yield; FastAPI runs that cleanup after the dependent work finishes. This pattern
is useful for database sessions and other scoped resources.

Dependency injection makes cross-cutting concerns explicit and testable.
Authentication, authorization, database sessions, pagination, and shared
validation can be composed without inheritance or global state. Tests can replace
a dependency through the application's dependency_overrides mapping.

## Sync and async endpoints

Use an async endpoint when it awaits async libraries such as an async database or
HTTP client. A normal def endpoint is executed in a thread pool so blocking work
does not directly block the event loop. Declaring a function async does not make
blocking code non-blocking; calling a synchronous slow library inside it can
still stall other requests.

## Middleware, dependencies, and background tasks

Middleware wraps every matching request and response. It is appropriate for
concerns such as request IDs, timing, or broad logging. Dependencies operate
closer to endpoint inputs and can return values to the endpoint, making them a
better fit for authentication and resource acquisition.

BackgroundTasks schedules small work after the response is sent, but it runs in
the application process. It is not a durable job queue. Long-running, critical,
or retryable jobs should be sent to an external worker system.

## Error handling and application design

Raise HTTPException for expected client-facing HTTP errors. Install exception
handlers when an application needs a consistent response for a domain exception.
Unexpected errors should be logged with useful request context and normally
become 500 responses without exposing internals.

Keep path operations thin. Put reusable business rules in ordinary Python
functions or services, and use FastAPI for HTTP parsing, dependency resolution,
validation, and response construction.
