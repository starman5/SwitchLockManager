# CS 145 Project 7

## Author and collaborators
### Author name
(Your name and email address)

### Collaborators
(List any other collaborators and describe help you got from other students in the class.)

## Report
For my project, I chose to implement a recent research paper in networking.  The paper I chose to work with is ["NetLock: Fast, Centralized Lock Management Using Programmable Switches"](https://courses.grainger.illinois.edu/CS598HPN/fa2020/papers/netlock.pdf).

# Introduction to NetLock
Lock managers are used to grant access to some shared resource, in order to avoid situations where there are concurrent accesses and modifications of that shared resource.  Traditionally, these requests are processed in a central lock server.  In this kind of setup, a client that wants to access the shared resource will send a request through the network to the lock server.  The lock server will grant requests based on some set of policies (ie fairness, starvation-free).  Then when the client is finished with the shared resource, it will send a message back to the server.  There are advantages to this setup of a centralized lock manager.  The main advantage is that since it has a global view of all requests, it can support complex policies.  This is in contrast to a decentralize approach, where there is no global view and therefore a decreased ability to support complex policies.  However, a disadvantage of this approach is that the lock server can be come the bottleneck.

The idea of NetLock is to fix this bottleneck by processing lock requests in the data plane, rather than in a lock server.  The reason this is effective is because switches provide significantly higher throughput and lower latency than servers.

# Simplifying Assumptions For My Project
The first simplifying assumption relates to memory.  I am assuming that there is only one lock.  In a real system, there are many locks, corresponding to many pieces of shared data.  In Netlock, not all lock requests are handled in the data plane.  The reason for this is that there are memory constraints in switches that make storing data for each lock impossible.  Instead, in a full implementation, netlock would first check if it is responsible for this lock (ie is the lock represented in memory).  If so, it would continue with the lock managing logic.  Otherwise, it would pass the request on to the lock server.  Therefore, in a real implementation, the switch and the lock server are sharing the responsibilities.  The switch is meant to offload the burden of the most popular locks, while the remainder go to the lock server.  In my implementation, there is only one lock, and it is handled in the switch.

# Implementation
Here are the desired semantics: If the lock is currently not held, then a is granted to the first host that requests it.  All subsequent requests are put into a queue.  Whenever the lock is released, the lock is granted to the next host in the queue.  Sicne there is no queue data structure with push and pop built into p4, I implement a circular buffer to make this work.

For this circular queue to work, I have a register array, which servers as the memory for the queue.  Each slot in this array stores some information about the queued request (I'll get to this later).  I also store the head and the tail of the queue in their own registers.  Whenever a new request comes in that needs to be queued, I store information about that request in the register array at tail, and then increment the tail (using the modulus of the size of the array, since I want to be able to wrap back around to the beginning when the end of the array is hit).  Whenever a request needs to be popped off the queue, I grab it from the head of the array and then increment the head (also using the modulus of the size of the array).

Now, what is stored in the array?  What information do we need for a queued request?  All we need is the ip address and udp port of the host that requested the lock.  The reason is because we grant lock requests to hosts by simply sending a UDP message back with source port 7777.  UDP port 7777 is reserved for netlock.  The host knows that it has been granted a lock if it receives a message back from the switch with this source port.  If the host receives no message from the switch, it interprets that as not having been granted the lock yet.  So when we are able to grant a lock request to a host, we need to know the destination ip address and udp port to send a message to.  This is why we store these things in the circular queue.  Practically, what this means is that there are 2 register arrays, one storing ip addresses of queued requests and one storing udp ports.  The head and tail of these are in sync at all times.

Here is another consideration: Imagine that host A holds the lock.  We want to ensure that if some other host B sends a release request to the switch, then netlock is smart enough to know that host B does not hold the lock in the first place.  So, we store the ip address of the host that currently holds the lock in "acquired_ip".  This ip address is consulted whenever a release message comes in to netlock.

Finally, let's go through the overall logic in the apply block.  For an ACQUIRE message: if the lock is currently unset, send a message back to the host, thereby granting the lock.  if the lock is currently, set, then put the hosts' ip address and udp port in the circular queue.  For a RELEASE message: If the queue is empty (signified by head = tail), then unset the lock.  If the queue is not empty, then send a message to the next host in the queue, thereby granting it the lock. 

# Testing
"sudo p4run --config topo_netlock.json"

topo_netlock.json is a very simple topology to demonstrate the netlock functionality.  It consists of three hosts connected to one switch.

In another terminal, type "python controller_netlock.py"

I have provided 3 python scripts in the directory netlock_apps.  release_lock.py and request_lock.py take a source ip address and destination ip address as arguments.  The destination ip addresses can be any address that requires passage through the switch.  receiver.py receives incoming messages and prints "lock acquired" if the message is from netlock (has udp source port 7777).  To test out netlock, here is an example of what you can do.

Have 2 terminals open.  Type "mx h1" into both terminals.  In one of the windows, type "python receiver.py".  In the other, type "python request_lock.py 10.1.1.2 10.1.2.2".  This sends a message from h1 to h2, but it will be intercepted by netlock at the switch, and netlock will grant the lock request.  You will see in the receiver window the message "lock acquired".  Type the same thing again in the sender window.  A second "lock acquired" message will not be displayed since the lock has not been released yet.  If you release the lock by saying "python release_lock.py 10.1.1.2 10.1.2.2", now the queued lock request will be granted and you will see the second "lock acquired" message in the receiver window.  Release the lock again, to release what was just acquired.  Now the lock is unset


You can also have 2 more terminal windows open, each with "mx h2".  Now you can type in "python request_lock.py 10.1.2.2 10.1.1.2" and "python release_lock.py 10.1.2.2 10.1.1.2" to have h2 request and release the lock.  You can play around with different orderings of locking and releasing to see that the semantics work.


## Citations
(List any other source code or online resources your consulted.)

## Grading notes (if any)

## Extra credit attempted (if any)
