# CS 145 Project 7

## Author and collaborators
### Author name
(Your name and email address)

### Collaborators
(List any other collaborators and describe help you got from other students in the class.)

## Report
For my project, I chose to implement a recent research paper in networking.  The paper I chose to work with is ["NetLock: Fast, Centralized Lock Management Using Programmable Switches"](https://courses.grainger.illinois.edu/CS598HPN/fa2020/papers/netlock.pdf).

# Introduction to NetLock
Lock managers are used to grant access to some shared resource, in order to avoid situations where there are concurrent accesses and modifications of that shared resource.  Traditionally, these requests are processed in a central lock server.  In this kind of setup, a client that wants to access the shared resource will send a request through the network to the lock server.  The lock server will grant requests based on some set of policies (ie fairness, starvation-free).  Then when the client is finished with the shared resource, it will send a message back to the server.  There are advantages to this setup of a centralized lock manager.  The main advantage is that since it has a global view of all requests, it can support complex policies.  This is in contrast to a decentralize approach, where there is no global view and therefore a decreased ability to support complex policies.  However, a disadvantage of this approach is that the server becomes a bottleneck.

The idea of NetLock is to fix this bottleneck by processing lock requests in the data plane.  The reason this is effective is because switches provide significantly higher throughput and lower latency than servers.

# Simplifying Assumptions For My Project

# Implementation


## Citations
(List any other source code or online resources your consulted.)

## Grading notes (if any)

## Extra credit attempted (if any)
