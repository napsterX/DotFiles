# Audit lenses

Apply lenses to product subsystems and trust boundaries rather than scanning files mechanically.

## Correctness
- latent bugs and invalid state transitions
- boundary conditions and missing validation
- stale assumptions and contract mismatches
- partial-success behavior

## Security
- authentication and authorization
- tenant/data isolation
- input handling and injection
- secrets and sensitive-data handling
- dependency and supply-chain exposure
- privilege boundaries

## Data integrity
- transactional boundaries
- race conditions and lost updates
- duplicate execution and idempotency
- migration safety and rollback semantics
- lifecycle invariants

## Reliability
- retries, timeouts, backoff
- crash recovery
- queue/job duplication or loss
- degraded dependencies
- restart behavior
- resource exhaustion

## Architecture
- boundary violations
- hidden coupling
- cyclic dependencies
- duplicated domain logic
- architecture/documentation drift
- complexity with demonstrated operational/product cost

## Performance
- algorithmic hotspots
- N+1/database query behavior
- cache correctness and invalidation
- network chatter
- large payloads
- memory/resource leaks
- unnecessary serialization

## Testing
- critical invariants without executable coverage
- tests that mock away the real failure mode
- flaky/non-deterministic tests
- missing negative/adversarial cases
- mismatch between documented gates and actual verification

## Operations and observability
- missing actionable telemetry
- misleading operator messages
- failure states that cannot be diagnosed
- rollback/recovery assumptions
- configuration drift

## Product and UX
- broken or confusing failure states
- unrecoverable user journeys
- accessibility failures
- inconsistent behavior across flows
- customer-visible latency/friction
- technically-correct behavior that produces an incorrect product outcome
