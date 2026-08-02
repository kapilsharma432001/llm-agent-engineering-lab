# System Design Interview Notes

## Scaling and load balancing

Vertical scaling gives one machine more resources and is simple but has a limit.
Horizontal scaling adds service instances and requires requests to be distributed
through a load balancer. Stateless service instances are easier to scale because
any healthy instance can handle a request. Shared state belongs in a database,
cache, object store, or another dedicated system.

Load balancers perform health checks and stop routing traffic to unhealthy
instances. Timeouts, bounded retries, and circuit breakers prevent one slow
dependency from consuming all request capacity. Retries should use backoff and
jitter and should only repeat operations that are safe or idempotent.

## Caching

Caches reduce latency and load by storing frequently used results closer to the
caller. Common placements include a browser or CDN, an application cache, and a
database cache. Cache-aside lets the application read the cache first, fetch a
miss from the source, and then populate the cache.

Every cache needs an invalidation strategy. Time-to-live limits staleness, while
explicit invalidation can be more current but is harder to coordinate. Hot keys,
cache stampedes, memory limits, and consistency requirements should be discussed
in a design interview.

## Databases and consistency

Indexes speed reads by maintaining an additional searchable structure, but they
consume storage and add work to writes. Replication improves read capacity and
availability. Sharding divides data across nodes and requires a stable shard key
that avoids uneven traffic.

Strong consistency makes the latest successful write visible according to a
defined ordering. Eventual consistency allows replicas to converge later and can
improve availability or latency. The right trade-off depends on what incorrect
or stale data would mean for the product.

## Queues and SQS

A message queue decouples a producer from a consumer in time and capacity. The
producer can finish after enqueueing work, while consumers process messages at
their own rate. This absorbs traffic spikes, isolates temporary downstream
failures, and lets consumer capacity scale independently.

Amazon SQS is useful between microservices because it is managed, durable, and
supports visibility timeouts, retries, and dead-letter queues. A consumer that
receives a message temporarily hides it. It must delete the message after
successful processing; otherwise the message becomes visible again.

Standard queues provide at-least-once delivery, so a consumer must be idempotent
and tolerate duplicates. A stable operation or message ID can be stored to avoid
applying the same side effect twice. A dead-letter queue holds messages that
repeatedly fail so they can be inspected without blocking healthy work.

Queues improve resilience but introduce asynchronous behavior, delayed results,
duplicate delivery, monitoring needs, and more complex debugging. They are not a
replacement for a synchronous call when the caller requires an immediate answer.

## Reliability and observability

Define service-level indicators such as latency, error rate, throughput, and
availability. Logs explain individual events, metrics show trends and alertable
conditions, and distributed traces connect work across service boundaries.
Include correlation IDs so one request or message can be followed across systems.

Design for partial failure. Use timeouts everywhere, cap concurrency, make
operations idempotent, expose queue depth and retry counts, and test how the
system behaves when dependencies are slow or unavailable.
