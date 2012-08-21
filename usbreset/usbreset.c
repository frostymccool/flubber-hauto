/* usbreset -- send a USB port reset to a USB device */
/* source - http://marc.info/?l=linux-usb&m=121459435621262&w=2 */

#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/ioctl.h>

#include <linux/usbdevice_fs.h>


int main(int argc, char **argv)
{
	const char *filename;
	int fd;
	int rc;

	if (argc != 2) {
		fprintf(stderr, "Usage: sudo usbreset device-filename\n");
		fprintf(stderr, "       device-filename from lsusb\n");
		fprintf(stderr, "       /dev/bus/usb/BUS NUM/DEVICE NUM\n");
		return 1;
	}
	filename = argv[1];

	fd = open(filename, O_WRONLY);
	if (fd < 0) {
		perror("Error opening output file");
		return 1;
	}

	printf("Resetting USB device %s\n", filename);
	rc = ioctl(fd, USBDEVFS_RESET, 0);
	if (rc < 0) {
		perror("Error in ioctl");
		return 1;
	}
	printf("Reset successful\n");

	close(fd);
	return 0;
}

