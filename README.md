# Project 7: Final Project

You are supposed to design and implement an open-ended project. You can choose between three directions. Check with us about your project ideas to make sure they’re in scope. Think big!

## Direction 1:
We have built a data center network in the past projects. Now you are supposed to add a new feature to it. Interesting projects may become course projects for future semesters. 

In general, you can look for project ideas by revisiting the key ideas discussed in lectures and pick one idea to implement. 
Here are a few suggested topics. 

### Add new features to your FatTree topology
In project 1, we implemented a static FatTree. You can think about how to support more practical features in the topology such as:
- Expansion: How do you move links when we add a new rack
- Failure recovery: how do you detect failure and identify alternative routing? Can you try out the striping idea we talked in class and compare the performance of different striping solutions?

### Run spanning tree protocol and learning switches in Mininet

### Port link-state or distance vector protocols to FatTree setting in Mininet
Our link-state and distance vector implementation in project 2 is a standalone program. Can you try porting it to the Mininet setting so that we can run it in the data center networks we construct?

### Run BGP in Mininet
[Quagga](https://github.com/Quagga) would be a useful starting point. 
<!-- [Quagga](https://www.quagga.net/) would be a useful starting point. -->

### Run DCTCP in Mininet and compare its performance with TCP

### Implement MPLS in Mininet 

### Add P4 debugging tools
Build an innovative and useful tool that can help P4 developers visualize, identify or better understand their program's behavior and more conveniently debug it.

### Add more testing cases 
Many of our course projects can be improved with better automatic testing cases. Propose some testing scripts that would automatically catch problems in students' codes.

### Add more data structures in the switches
In a normal computer, we benefited from having a data structure library where we can store data in the right format as needed. However, in switches, it is much harder to implement various data structures. Pick your favorite data structure, and try to store packet information in them directly at switches. 
Together, we can create a library that makes future programming on the switch easier. (see [SketchLib](https://github.com/SketchLib/P4_SketchLib) for a few sketch examples).

## Direction 2:
Pick any network outage postmotem and reproduce the similar problems based on the postmortem. 

## Direction 3:
Another option is to read papers in networking and try to reproduce some results (see the [Stanford course blog](https://reproducingnetworkresearch.wordpress.com/) for examples). You can conslut Minlan if you need suggestions on papers. 

## Direction 4: Software load balancing
You are highly encouraged to take exploratory directions in 1 and 3. However, if you prefer projects with detailed instructions, you can also try out the [Software load balancing project](LoadBalancing.md). Note that this is a developing projet, so the instructions are less clear compared to previous projects. We also welcome your contributions to this project so that it can graduate as a mature one in future years. In addition to following the instructions, you should be creative in adding new features to the projects or compare the tradeoffs for different implementation alternatives. 

<!--
## Direction 4: Test network usage of an application in the cloud

You can choose one application and one cloud platform, run your applications there, measure the network usage (delay, throughput, changes, etc.), and use the knowledge you learnt from this class to explore new observations and discuss potential improvements.

Note that, for better or worse, this is an interesting time to measure cloud network usage considering the public health situation has lead to unparalleled network traffic for remote work and communication.

### Example applications
In the past, students have chosen applications such as machine learning, web services, video streaming, or simply iperf. 

### Example platforms
In the past, students have chosen GPU/TPU, serverless (lambdas), various cloud instances, across data center regions, etc in Google cloud, Microsoft Azure, and Amazon EC2.

## Submission requirements 
In addition to the code, write up your project in a file that you add to your repository. Your writeup should answer these questions:

- What was your goal?
- What’s your design?
- What code did you write (what files and functions)?
- What challenges did you encounter?
- How can we test your work?
- Provide evaluation results or performance analysis of your work
- The writeup need not be very long; 300 words can do it if you use the words well.
-->


# Featured past projects:
- Spring 2020: [P4 Network Visualizer](https://github.com/Danieltech99/P4-Network-Visualizer) by Daniel Rodrigues

- Spring 2021: Spanning tree protocol by Noel Chou


<!--
- Spring 2021: 

### Inband Network Telemetry (INT)
Telemetry we used in this course so far usually is based off of transfering data to the control plane in some way, for example, writing to registers and having controllers read the registers. This often has a large overhead and is slow.
Inbad Network Telemetry(INT) is a way to monitor and observe network events. INT operates entirely in the dataplane, allowing data to be transfered faster and at a higher granularity.
INT works by writing data that needs to be monitored into the packet header in the p4 code. The receiver host then parses the data out of the packet header, allowing for more visualization or analysis. Parsing the packet header can be done through something like [scapy](https://scapy.readthedocs.io/en/latest/).
#### Resources
[INT p4 video](https://www.youtube.com/watch?v=FOOL5BeHNVY)
[INT spec](https://p4.org/assets/INT-current-spec.pdf)
[Multi-Hop Route Inspection (MRI)](https://github.com/p4lang/tutorials/tree/master/exercises/mri)
This is a scaled down version of INT. Does not work for larger amounts of hops, as ipv4 headers have a max length because of the ihl field.
-->
