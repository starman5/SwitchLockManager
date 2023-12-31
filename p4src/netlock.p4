/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

//My includes
#include "include/headers.p4"
#include "include/parsers.p4"

/*************************************************************************
************   C H E C K S U M    V E R I F I C A T I O N   *************
*************************************************************************/

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply {  }
}

/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {
                

//-------------------------------------DATA-------------------------------------
    
    // These are the arrays we need to implement queueing of requests
    // Each slot in the ip queue contains client ip address
    // Each slot in the udp queue contains the client udp port
    register<bit<32>>(QueueSize) lock_queue_ip;
    register<bit<16>>(QueueSize) lock_queue_udp;

    // These contain the current head and tail of the circular queue
    register<bit<32>>(1) queue_heads;
    register<bit<32>>(1) queue_tails;
    
    // Contains whether or not the lock is already held.
    register<bit<1>>(1) lock_statuses;

    // Stores the ip address of the host that currently has the lock
    // We need this so that we don't wrongfully release the lock if a different
    // host sends a release message
    register<bit<32>>(1) acquired_ip;
   


//------------------------------------ACTIONS------------------------------------

    action set_nhop(macAddr_t dstAddr, egressSpec_t port) {
        //set the src mac address as the previous dst, this is not correct right?
        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;

        //set the destination mac address that we got from the match in the table
        hdr.ethernet.dstAddr = dstAddr;

        standard_metadata.egress_spec = port;
        
        //decrease ttl by 1
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
    }

    action drop() {
        mark_to_drop(standard_metadata);
    }

    // Get the current tail.  Read the ip address and udp port that is next in the queue, at
    // the tail.  Update the tail.
    action push_queue() {
        bit<32> tail;
        queue_tails.read(tail, (bit<32>)0);
        lock_queue_ip.write(tail, hdr.ipv4.srcAddr);
        lock_queue_udp.write(tail, hdr.udp.srcPort);
        tail = (tail + 1) % QueueSize;
        queue_tails.write((bit<32>)0, tail);
    }

    // Get the current head.  Zero out the queue at the head.  Increment the head. 
    action pop_queue() {
        // zero out current head and then increment head
        bit<32> head;
        queue_heads.read(head, (bit<32>)0);
        
        lock_queue_ip.write(head, (bit<32>)0);
        lock_queue_udp.write(head, (bit<16>)0);
        head = (head + 1) % QueueSize;
        queue_heads.write((bit<32>)0, head);
    }

    action remove_netlock() {
        hdr.netlock.setInvalid();
        hdr.ethernet.etherType = TYPE_IPV4;
    }

    // This is for sending a message back to the host, if that host can immediately
    // grab the lock
    action swap_ip() {
        ip4Addr_t tmp = hdr.ipv4.srcAddr;
        hdr.ipv4.srcAddr = hdr.ipv4.dstAddr;
        hdr.ipv4.dstAddr = tmp;
    }

    // This is for sending a message back to the host, if that host can immediately
    // grab the lock
    action swap_udp() {
        bit<16> tmp;
        tmp = hdr.udp.srcPort;
        hdr.udp.srcPort = hdr.udp.dstPort;
        hdr.udp.dstPort = hdr.udp.srcPort;
    }

    // Grab the ip address of the next request in the queue, and make this the destination
    // IP address of the packet.  This is to prepare to send a message to the next host in
    // the queue.
    action set_next_ip() {
        // look up ip address from head
        bit<32> head;
        queue_heads.read(head, (bit<32>)0);
        bit<32> hostAddr;
        lock_queue_ip.read(hostAddr, head);

        // Then set the address held by the lock
        acquired_ip.write((bit<32>)0, hostAddr);

        // then set ip addresses to send to the next host
        hdr.ipv4.srcAddr = hdr.ipv4.dstAddr;
        hdr.ipv4.dstAddr = hostAddr;
    }

    // Same as above, but with udp port
    action set_next_udp() {
        bit<16> hostPort;
        bit<32> head;
        queue_heads.read(head, (bit<32>)0);
        lock_queue_udp.read(hostPort, head);

        hdr.udp.srcPort = hdr.udp.dstPort;
        hdr.udp.dstPort = hostPort;
    }



//---------------------------------------TABLES------------------------------------
    // This table maps dstAddr to ecmp_group_id and num_nhops (the number of total output ports). The action ecmp_group is actually calculating the hash value.
    table ipv4_lpm {
        key = {
            hdr.ipv4.dstAddr: lpm;
        }

        actions = {
            set_nhop;
            drop;
            NoAction;
        }
        size = 256;
        default_action = NoAction;
    }



//-------------------------------------------APPLY--------------------------------
    apply {
        if (hdr.ipv4.isValid()) {

            if (hdr.netlock.isValid() && hdr.udp.isValid()) {                
                if (hdr.netlock.act == ACQUIRE) {
                    // If lock is unset, set it and prepare response back to host
                    bit<1> current_status;
                    lock_statuses.read(current_status, (bit<32>)0);
                    if (current_status == UNSET) {
                        lock_statuses.write((bit<32>)0, SET);
                        acquired_ip.write((bit<32>)0, hdr.ipv4.srcAddr);
                        remove_netlock();
                        swap_ip();
                        swap_udp();
                    }
                    // Otherwise add host ip address to queue
                    else {
                        push_queue();
                        remove_netlock();
                    }
                }
                
                else {
                    bit<32> correct_addr;
                    acquired_ip.read(correct_addr, (bit<32>)0);
                    if (hdr.ipv4.srcAddr == correct_addr) {
                        // If queue is empty, unset the lock
                        bit<32> head;
                        bit<32> tail;
                        queue_heads.read(head, (bit<32>)0);
                        queue_tails.read(tail, (bit<32>)0);
                        if (head == tail) {
                            // There is nothing in the queue to grant the lock to.
                            lock_statuses.write((bit<32>)0, UNSET);
                            remove_netlock();
                        }
                        // Otherwise, send a message to next host in queue, granting the lock
                        else {
                            set_next_ip();
                            set_next_udp();
                            pop_queue();
                            remove_netlock();
                        }
                    }
                }
            }

            // Match ip address to out port
            ipv4_lpm.apply();
        }
    }

}


/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    apply {

    }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

control MyComputeChecksum(inout headers hdr, inout metadata meta) {
     apply {
	update_checksum(
	    hdr.ipv4.isValid(),
            { hdr.ipv4.version,
	          hdr.ipv4.ihl,
              hdr.ipv4.dscp,
              hdr.ipv4.ecn,
              hdr.ipv4.totalLen,
              hdr.ipv4.identification,
              hdr.ipv4.flags,
              hdr.ipv4.fragOffset,
              hdr.ipv4.ttl,
              hdr.ipv4.protocol,
              hdr.ipv4.srcAddr,
              hdr.ipv4.dstAddr },
              hdr.ipv4.hdrChecksum,
              HashAlgorithm.csum16);
    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

//switch architecture
V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;