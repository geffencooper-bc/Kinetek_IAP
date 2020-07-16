#include "SocketCanUtil.h"
#include "HexUtil.h"

int test_can();

int main()
{
    uint8_t byte_arr[4] = {0xAA, 0xBB, 0xCC, 0xDD};
    uint32_t dest;
    memcpy(&dest, byte_arr, 4);
    printf("%08X\n", dest);
    HexUtility ut("/home/geffen.cooper/Desktop/kinetek_scripts/hex_file_copies/2.27_copy.hex");
    //ut.get_total_cs(byte_arr, 4);
    //printf("CS: %02X", ut.calc_hex_checksum(":108080001B8100081B810008C58800081B81000AF"));
    // uint8_t bytes[20];
    // int ret = ut.data_string_to_byte_list("108080001B8100081B810008C58800081B810008", bytes, 20);
    // printf("ret: %i\n", ret);
    // for(int i = 0; i < 20; i++)
    // {
    //     printf("%02X ", bytes[i]);
    // }
    
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
