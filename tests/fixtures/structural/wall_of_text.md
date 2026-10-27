The cache stores the last answer. A repeat request reads that stored answer. A miss goes to the origin and pays the full fetch. The origin's reply is written back into the cache. The next repeat then hits and skips the origin.

- This item keeps going past the limit by naming the cache, the origin, the timeout, the retry, the stampede, and the lock that serialises the refill so two misses do not both write.
