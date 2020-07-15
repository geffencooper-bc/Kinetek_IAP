#include "SocketCanUtil.h"
#include "HexUtil.h"

int test_can();

int main()
{
    HexUtility ut = HexUtility();
    ut.open_file("/home/geffen.cooper/Desktop/kinetek_scripts/hex_file_copies/2.28_copy.hex");
    printf("%i\n", ut.get_record_data_length(":020000040800F2"));
    printf("%i\n", ut.get_record_address(":020000040800F2"));
    printf("%i\n", ut.get_record_type(":020000040800F2"));
    uint8_t data[8];
    ut.get_record_data_bytes(":020000040800F2", data, 0, 8);
    printf("%02X %02X", data[0], data[1]);
    
    // SocketCanUtil ut2 = SocketCanUtil();
    // ut.init_socket("can0");
    // can_frame frame;
    // uint8_t data[5] = {0x1D, 0xF1, 0x04, 0x00, 0x01};
    // ut.make_socket_can_frame(0x001, data, 5, &frame);
    // ut.send_frame(&frame);
    // ut.get_frame(&frame);
    // ut.print_frame(&frame);
    
    
    // test_can();
}

int test_can()
{
    int s = socket(PF_CAN, SOCK_RAW, CAN_RAW);

    struct sockaddr_can addr;
    struct ifreq ifr;

    strcpy(ifr.ifr_name, "can0" );
    ioctl(s, SIOCGIFINDEX, &ifr);

    addr.can_family = AF_CAN;
    addr.can_ifindex = ifr.ifr_ifindex;

    bind(s, (struct sockaddr *)&addr, sizeof(addr));

    struct can_frame frame;
    printf("size: %i:", sizeof(can_frame));

    while(true)
    {
        int nbytes = read(s, &frame, sizeof(struct can_frame));

        if (nbytes < 0) {
                perror("can raw socket read");
                return 1;
        }

        /* paranoid check ... */
        if (nbytes < sizeof(struct can_frame)) {
                fprintf(stderr, "read: incomplete CAN frame\n");
                return 1;
        }

        // printf("Received a CAN frame from interface %s", ifr.ifr_name);
        printf("\ncan_id: %02X\t", frame.can_id);
        printf("data:\t");
        for(int i = 0; i < frame.can_dlc; i++)
        {
            printf("%02X ", frame.data[i]);
        }
    }
}
