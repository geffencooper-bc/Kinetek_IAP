// A class to abstract away socket interactions

#ifndef SOCKET_CAN_UTIL_H
#define SOCKET_CAN_UTIL_H

#include <stdio.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <linux/can.h>
#include <stdlib.h>
#include <unistd.h> 
#include <stdlib.h> 
#include <netinet/in.h> 
#include <string.h> 
#include <linux/if.h>
#include <sys/ioctl.h>
#include <string>

using std::string;

class SocketCanUtil
{
    public:
    SocketCanUtil();

    // used to create the socket for sending can messages
    int init_socket(string interface_name); 

    // simplifies the process of creating a socket_can frame, initializes the frame passed in
    void make_socket_can_frame(uint8_t can_id, uint8_t* data, uint8_t data_size, can_frame* frame);

    // abstracts socket write, return -1 if write unsuccseful
    int send_frame(can_frame* frame);

    // abstracts socket read, return -1 if read unsuccseful
    int get_frame(can_frame* frame);


    private:
    int socket_fd;
    sockaddr_can addr;
    struct ifreq ifr;

};

#endif