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
    // each slot in the queue contains client ip address
    register<bit<32>>(QueueSize) lock_queue;
   
    bit<1> lock_status;
    bit<32> head = 0;   // Next up in the queue (first taken slot)
    bit<32> tail = 0;   // Next available slot in the queue



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
        mark_to_drop();
    }

    action push_queue() {
        lock_queue.write(tail, hdr.ipv4.srcAddr);
        tail = (tail + 1) % QueueSize;
    }

    action pop_queue() {
        // zero out current head and then increment head
        lock_queue.write(head, (bit<32>)0);
        ++head;
    }

    action remove_netlock() {
        hdr.netlock.setInvalid();
        hdr.ethernet.etherType = TYPE_IPV4;
    }

    action swap_ip() {
        ip4Addr_t tmp = hdr.ipv4.srcAddr;
        hdr.ipv4.srcAddr = hdr.ipv4.dstAddr;
        hdr.ipv4.dstAddr = tmp;
    }

    action grant_to_next() {
        // look up ip address from head
        bit<32> hostAddr;
        queue.read(hostAddr, head);

        // then set ip addresses to send to the next host
        hdr.ipv4.srcAddr = hdr.ipv4.dstAddr;
        hdr.ipv4.dstAddr = hostAddr;
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

            if (hdr.netlock.isValid()) {                
                if (hdr.netlock.action == ACQUIRE) {
                    // If lock is unset, set it and prepare response for host
                    if (lock_status == UNSET) {
                        lock_status = SET;
                        remove_netlock();
                        swap_ip();
                    }
                    // Otherwise add host ip address to queue
                    else {
                        push_queue();
                    }
                }
                
                else {
                    // If queue is empty, unset the lock
                    if (head == tail) {
                        lock_status = UNSET;
                    }
                    // Otherwise, grant the lock to next host in queue
                    else {
                        grant_to_next();
                        pop_queue();
                        remove_netlock();
                    }
                }
            }

            // Match ip address to out port
            ipv4_lpm.apply();
        }
    }

}