# Python Interview Notes

## Objects, mutability, and function arguments

Python variables hold references to objects. Immutable objects such as integers,
strings, and tuples cannot be changed in place, while lists and dictionaries can.
Function arguments use object sharing: a function receives a reference to the
same object. Mutating a passed list is visible to the caller, but rebinding the
local parameter is not.

Avoid mutable default arguments such as an empty list. The default object is
created once when the function is defined and is reused by later calls. Use
None as the default and create a new list inside the function.

## Iterators and generators

An iterable can produce an iterator. An iterator keeps traversal state and
implements the iterator protocol through iter and next. A generator is a concise
way to create an iterator with yield. It pauses after yielding a value and
resumes with its local state intact. Generators are useful for large or streaming
data because they produce values lazily instead of storing every result.

## Context managers

A context manager defines setup and cleanup around a block. The with statement
guarantees cleanup even when the block raises an exception. Files, locks, and
database transactions are common examples. A class can implement enter and exit,
or a generator can be wrapped with contextlib.contextmanager.

## Threading, multiprocessing, and asyncio

Threads share one process and memory space, so communication is cheap but shared
state needs synchronization. In standard CPython, the Global Interpreter Lock
allows only one thread at a time to execute Python bytecode. Threads are still
effective for I/O-bound work because they can wait on network or disk operations
concurrently.

Multiprocessing starts separate processes with separate memory and separate
Python interpreters. It can run CPU-bound Python work across multiple cores, but
process startup and data serialization add overhead. State must be exchanged
through queues, pipes, shared memory, or another external system.

Asyncio normally runs many tasks on one thread using cooperative scheduling.
When one coroutine awaits non-blocking I/O, the event loop can run another task.
It is a good fit for many concurrent network operations, but blocking code must
be moved to a thread or process so it does not stop the event loop.

Choose threads for ordinary blocking I/O, processes for CPU-heavy Python work,
and asyncio when the libraries and workload are designed around async I/O.

## Exceptions and testing

Catch exceptions only when the program can handle them meaningfully. Prefer
specific exception types and preserve the original error when adding context.
Tests should focus on observable behavior, keep setup small, and avoid mocking
pure calculations. Mock network or model boundaries so unit tests remain fast
and deterministic.
